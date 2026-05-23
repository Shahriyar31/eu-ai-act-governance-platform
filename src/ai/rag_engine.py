import os
import json
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from src.ai.llm_factory import get_rag_llm, ModelLogger

load_dotenv()

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
    global _knowledge_base_ready
    if _knowledge_base_ready:
        return

    from src.database.connection import SessionLocal
    from src.database.models import ChunkEmbedding

    db = SessionLocal()
    try:
        count = db.query(ChunkEmbedding).count()

        if count > 0:
            print(f"Knowledge base ready — {count} chunks already in PostgreSQL")
            _knowledge_base_ready = True
            return

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

            if i % 50 == 0:
                db.commit()
                print(f"  Stored {i}/{len(chunks)} chunks...")

        db.commit()
        print(f"All {len(chunks)} chunks stored in PostgreSQL")
        _knowledge_base_ready = True

    finally:
        db.close()


def _retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    from src.database.connection import SessionLocal
    from src.database.models import ChunkEmbedding

    question_embedding = _get_embedding(question)

    db = SessionLocal()
    try:
        results = (
            db.query(ChunkEmbedding)
            .order_by(ChunkEmbedding.embedding.op("<=>")(question_embedding))
            .limit(top_k)
            .all()
        )
        return [
            {"id": r.id, "title": r.title, "content": r.content}
            for r in results
        ]
    finally:
        db.close()


def _call_llm(prompt: str) -> str:
    llm = get_rag_llm()
    try:
        response = llm.invoke(
            [HumanMessage(content=prompt)],
            config={"callbacks": [ModelLogger("[RAG]")]}
        )
        return response.content

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate_limit" in error_str.lower() or "quota" in error_str.lower():
            raise Exception("429_all_models")
        raise


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

    try:
        answer = _call_llm(prompt)

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate_limit" in error_str.lower() or "quota" in error_str.lower():
            answer = (
                "The AI compliance assistant is temporarily unavailable due to high demand. "
                "This is a rate limit on the underlying language model API and typically "
                "resolves within a few minutes.\n\n"
                "**In the meantime, you can:**\n"
                "- Browse the official EU AI Act text at eur-lex.europa.eu\n"
                "- Use the Risk Classifier to assess your AI system\n"
                "- Generate a DPIA or OWASP assessment from the dashboard\n\n"
                "Please try your question again shortly."
            )
        else:
            raise

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {"id": chunk["id"], "title": chunk["title"]}
            for chunk in relevant_chunks
        ]
    }