import os
import json
import math
from groq import Groq
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

embedding_model = None
_knowledge_base_ready = False


def _get_embedding_model():
    global embedding_model
    if embedding_model is None:
        from fastembed import TextEmbedding
        print("Loading embedding model...")
        embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return embedding_model


def _get_embedding(text_input: str) -> list[float]:
    model = _get_embedding_model()
    embeddings = list(model.embed([text_input]))
    return embeddings[0].tolist()


def _load_chunks() -> list[dict]:
    """Load chunks from JSON file or fall back to manual knowledge base."""
    json_path = "data/knowledge_base.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            print(f"Loaded {len(chunks)} chunks from knowledge base JSON")
            return chunks
    from src.ai.knowledge_base import EU_AI_ACT_CHUNKS
    print(f"Using manual knowledge base ({len(EU_AI_ACT_CHUNKS)} chunks)")
    return EU_AI_ACT_CHUNKS


def initialise_knowledge_base():
    """
    Check if embeddings exist in PostgreSQL.
    If yes: nothing to do — retrieval queries the DB directly.
    If no: embed all chunks and store them in the DB.
    This only runs the expensive embedding process once ever.
    """
    global _knowledge_base_ready
    if _knowledge_base_ready:
        return

    from src.database.connection import SessionLocal
    from src.database.models import ChunkEmbedding

    db = SessionLocal()
    try:
        count = db.query(ChunkEmbedding).count()

        if count > 0:
            # vectors already in DB — nothing to compute
            print(f"Knowledge base ready — {count} chunks already in PostgreSQL")
            _knowledge_base_ready = True
            return

        # first time — embed everything and store in DB
        chunks = _load_chunks()
        print(f"Embedding {len(chunks)} chunks and storing in PostgreSQL...")

        _get_embedding_model()

        for i, chunk in enumerate(chunks):
            embedding = _get_embedding(chunk["content"])

            db_chunk = ChunkEmbedding(
                id=chunk["id"],
                title=chunk["title"],
                regulation=chunk.get("regulation", ""),
                content=chunk["content"],
                embedding=embedding
            )
            db.add(db_chunk)

            # commit in batches of 50 to avoid memory issues
            if i % 50 == 0:
                db.commit()
                print(f"  Stored {i}/{len(chunks)} chunks...")

        db.commit()
        print(f"All {len(chunks)} chunks stored in PostgreSQL")
        _knowledge_base_ready = True

    finally:
        db.close()


def _retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    """
    Use pgvector cosine similarity to find the most relevant chunks.
    The <=> operator computes cosine distance — lower = more similar.
    We ORDER BY distance ASC and take the top_k results.
    This query runs entirely in PostgreSQL — no Python loop needed.
    """
    from src.database.connection import SessionLocal
    from src.database.models import ChunkEmbedding

    question_embedding = _get_embedding(question)

    db = SessionLocal()
    try:
        # pgvector cosine distance operator: <=>
        # 1 - distance = similarity score
        results = (
            db.query(ChunkEmbedding)
            .order_by(ChunkEmbedding.embedding.op("<=>")(question_embedding))
            .limit(top_k)
            .all()
        )

        return [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content
            }
            for r in results
        ]
    finally:
        db.close()


def answer_compliance_question(question: str) -> dict:
    if not _knowledge_base_ready:
        initialise_knowledge_base()

    relevant_chunks = _retrieve_relevant_chunks(question)

    context = "\n\n".join([
        f"[{chunk['title']}]\n{chunk['content']}"
        for chunk in relevant_chunks
    ])

    prompt = f"""You are a senior EU AI Act compliance expert with deep knowledge of Regulation EU 2024/1689.

Your role is to provide thorough, accurate, and actionable compliance guidance to organisations deploying AI systems in the European Union.

Using the regulatory context provided below, answer the user's question in detail. Structure your answer clearly:
- Start with a direct answer to the question
- Cite specific article numbers and annex references where relevant
- Explain the practical implications for organisations
- If multiple aspects apply, address each one
- If the context does not contain enough information, say so and explain what additional articles would be relevant

REGULATORY CONTEXT:
{context}

USER QUESTION:
{question}

DETAILED COMPLIANCE ANSWER:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2000
    )

    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {"id": chunk["id"], "title": chunk["title"]}
            for chunk in relevant_chunks
        ]
    }