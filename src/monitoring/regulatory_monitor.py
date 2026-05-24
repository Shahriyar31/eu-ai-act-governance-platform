"""
Regulatory monitoring engine for Sprint 9.

Scrapes EUR-Lex and EU AI Office pages using Firecrawl.
Detects changes by comparing SHA256 content hashes.
When a change is found:
  - chunks and embeds the new content into pgvector
  - generates an LLM summary of what changed
  - emails all organisation admins via Resend
"""

import os
import hashlib
import logging
from datetime import datetime, timezone

from src.database.connection import SessionLocal
from src.database.models import MonitoringSource, RegulatoryUpdate, User, ChunkEmbedding

logger = logging.getLogger(__name__)

MONITORING_SOURCES = [
    {
        "url": "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32024R1689",
        "title": "EU AI Act — EUR-Lex Official Text"
    },
    {
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "title": "EU AI Office — Regulatory Framework"
    },
    {
        "url": "https://artificialintelligenceact.eu/",
        "title": "EU AI Act Reference Portal"
    }
]


def seed_monitoring_sources():
    """
    Insert the default monitoring sources into the database on first run.
    Skips URLs that already exist.
    """
    db = SessionLocal()
    try:
        for source_data in MONITORING_SOURCES:
            exists = db.query(MonitoringSource).filter(
                MonitoringSource.url == source_data["url"]
            ).first()
            if not exists:
                source = MonitoringSource(
                    url=source_data["url"],
                    title=source_data["title"],
                    is_active=True
                )
                db.add(source)
        db.commit()
        logger.info("Monitoring sources seeded")
    finally:
        db.close()


def _scrape_url(url: str) -> str:
    """
    Use Firecrawl to scrape a URL and return its markdown content.
    Returns empty string if scraping fails.
    """
    try:
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        result = app.scrape_url(url)
        if isinstance(result, dict):
            content = result.get("markdown", "")
        else:
            content = getattr(result, "markdown", "") or ""
        return content[:50000]
    except Exception as e:
        logger.error(f"Firecrawl scraping failed for {url}: {e}")
        return ""


def _hash_content(content: str) -> str:
    """SHA256 hash of text content. 64-character hex string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _chunk_content(content: str, chunk_size: int = 500) -> list[str]:
    """
    Split markdown into overlapping chunks for embedding.
    Splits on paragraph boundaries first, then by character count.
    """
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) <= chunk_size:
                current = para
            else:
                for i in range(0, len(para), chunk_size):
                    chunks.append(para[i:i + chunk_size])
                current = ""

    if current:
        chunks.append(current)

    return chunks


def _embed_and_store_chunks(content: str, title: str, url: str) -> int:
    """
    Chunk the content, embed each chunk, and store in pgvector.
    Returns the number of chunks added.
    Returns 0 if embedding fails.
    """
    try:
        from fastembed import TextEmbedding
        from src.database.connection import SessionLocal

        chunks = _chunk_content(content)
        if not chunks:
            return 0

        model = TextEmbedding("BAAI/bge-small-en-v1.5")
        db = SessionLocal()

        try:
            added = 0
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"monitor_{_hash_content(url)}_{i}"

                exists = db.query(ChunkEmbedding).filter(
                    ChunkEmbedding.id == chunk_id
                ).first()
                if exists:
                    continue

                embeddings = list(model.embed([chunk_text]))
                embedding_vector = embeddings[0].tolist()

                db_chunk = ChunkEmbedding(
                    id=chunk_id,
                    title=f"{title} [Regulatory Update]",
                    regulation="EU AI Act Monitor",
                    content=chunk_text,
                    embedding=embedding_vector
                )
                db.add(db_chunk)
                added += 1

            db.commit()
            logger.info(f"Added {added} chunks from {url}")
            return added

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Embedding failed for {url}: {e}")
        return 0


def _summarize_change(content: str, title: str) -> str:
    """
    Use the LLM to generate a short summary of what changed in the regulation.
    Falls back to a generic message if LLM fails.
    """
    try:
        from src.ai.llm_factory import get_rag_llm, ModelLogger
        from langchain_core.messages import HumanMessage

        prompt = f"""You are an EU AI Act compliance expert.

The following regulatory content was detected as changed or newly published on: {title}

Read the content and write a 3-5 sentence summary suitable for emailing to compliance officers.
Focus on: what regulation or guidance changed, what it means for organisations, and what actions may be needed.

CONTENT (first 3000 characters):
{content[:3000]}

SUMMARY FOR COMPLIANCE OFFICERS:"""

        llm = get_rag_llm()
        response = llm.invoke(
            [HumanMessage(content=prompt)],
            config={"callbacks": [ModelLogger("[Monitor]")]}
        )
        return response.content

    except Exception as e:
        logger.error(f"LLM summarization failed: {e}")
        return f"Regulatory content detected as changed at {title}. Please review the source directly."


def _notify_admins(update: RegulatoryUpdate, db):
    """
    Send an email to all admin users via Resend.
    Skips gracefully if RESEND_API_KEY is not configured.
    """
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set — skipping email notification")
        return

    try:
        admins = db.query(User).filter(User.role == "admin").all()
        if not admins:
            logger.info("No admin users found — skipping notification")
            return

        override_email = os.getenv("NOTIFICATION_EMAIL")
        if override_email:
            admin_emails = [override_email]
        else:
            admin_emails = [u.email for u in admins if u.email]

        if not admin_emails:
            return

        import resend
        resend.api_key = resend_key

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">🔔 EU AI Act Regulatory Update Detected</h2>
            <p>The EU AI Act Governance Platform monitoring system has detected a change in a tracked regulatory source.</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; width: 140px;">Source</td>
                    <td style="padding: 8px;">{update.source_title}</td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 8px; font-weight: bold;">URL</td>
                    <td style="padding: 8px;"><a href="{update.source_url}">{update.source_url}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Detected at</td>
                    <td style="padding: 8px;">{update.detected_at.strftime('%Y-%m-%d %H:%M UTC') if update.detected_at else 'Now'}</td>
                </tr>
                <tr style="background: #f5f5f5;">
                    <td style="padding: 8px; font-weight: bold;">KB chunks added</td>
                    <td style="padding: 8px;">{update.chunks_added} new entries added to knowledge base</td>
                </tr>
            </table>

            <h3>Summary of Changes</h3>
            <p style="background: #f9f9f9; padding: 16px; border-left: 4px solid #4a90e2; margin: 16px 0;">
                {update.change_summary or 'Change detected — please review the source directly.'}
            </p>

            <p>The knowledge base has been automatically updated. Your AI Compliance Assistant can now answer questions about this regulatory change.</p>

            <p style="color: #666; font-size: 12px; margin-top: 32px;">
                EU AI Act Governance Platform — Automated Regulatory Monitoring
            </p>
        </div>
        """

        resend.Emails.send({
            "from": "EU AI Governance <onboarding@resend.dev>",
            "to": admin_emails,
            "subject": f"🔔 Regulatory Update: {update.source_title}",
            "html": html
        })

        update.admins_notified = True
        db.commit()
        logger.info(f"Notified {len(admin_emails)} admins about update in {update.source_title}")

    except Exception as e:
        logger.error(f"Email notification failed: {e}")


def check_source(source: MonitoringSource, db) -> "RegulatoryUpdate | None":
    """
    Check one monitoring source for changes.
    Returns a RegulatoryUpdate if a change was detected, None otherwise.
    """
    logger.info(f"Checking source: {source.title}")

    content = _scrape_url(source.url)
    if not content:
        logger.warning(f"No content returned for {source.url}")
        source.last_checked = datetime.now(timezone.utc)
        db.commit()
        return None

    new_hash = _hash_content(content)
    source.last_checked = datetime.now(timezone.utc)

    if source.content_hash == new_hash:
        logger.info(f"No change detected in {source.title}")
        db.commit()
        return None

    logger.info(f"Change detected in {source.title}")
    source.content_hash = new_hash
    source.last_changed = datetime.now(timezone.utc)

    summary = _summarize_change(content, source.title)
    chunks_added = _embed_and_store_chunks(content, source.title, source.url)

    update = RegulatoryUpdate(
        source_id=source.id,
        source_url=source.url,
        source_title=source.title,
        change_summary=summary,
        chunks_added=chunks_added,
        admins_notified=False
    )
    db.add(update)
    db.commit()
    db.refresh(update)

    return update


def check_all_sources() -> dict:
    """
    Check all active monitoring sources.
    Called by the API endpoint and can later be called by a scheduler.
    Returns a summary of what was found.
    """
    db = SessionLocal()
    try:
        sources = db.query(MonitoringSource).filter(
            MonitoringSource.is_active == True
        ).all()

        updates_found = []

        for source in sources:
            update = check_source(source, db)
            if update:
                _notify_admins(update, db)
                updates_found.append({
                    "source": update.source_title,
                    "url": update.source_url,
                    "summary": update.change_summary,
                    "chunks_added": update.chunks_added,
                    "admins_notified": update.admins_notified
                })

        return {
            "sources_checked": len(sources),
            "updates_found": len(updates_found),
            "updates": updates_found
        }

    finally:
        db.close()