import os
import json
import math
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

chunk_embeddings = []
embedding_model = None

def _load_chunks() -> list[dict]:
    json_path = "data/knowledge_base.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            print(f"Loaded {len(chunks)} chunks from knowledge base")
            return chunks
    from src.ai.knowledge_base import EU_AI_ACT_CHUNKS
    print(f"Using manual knowledge base ({len(EU_AI_ACT_CHUNKS)} chunks)")
    return EU_AI_ACT_CHUNKS

ALL_CHUNKS = _load_chunks()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

chunk_embeddings = []
embedding_model = None


def _get_embedding(text: str) -> list[float]:
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0].tolist()


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def initialise_knowledge_base():
    global chunk_embeddings, embedding_model
    if chunk_embeddings:
        return
    from fastembed import TextEmbedding
    print("Loading embedding model...")
    embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    print(f"Embedding {len(ALL_CHUNKS)} chunks...")
    for chunk in ALL_CHUNKS:
        embedding = _get_embedding(chunk["content"])
        chunk_embeddings.append({
            "id": chunk["id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "embedding": embedding
        })
    print("Knowledge base ready.")


def _retrieve_relevant_chunks(question: str, top_k: int = 5) -> list[dict]:
    # Retrieve top 5 chunks instead of 3 — more context = better answers
    question_embedding = _get_embedding(question)
    scored = []
    for chunk in chunk_embeddings:
        score = _cosine_similarity(question_embedding, chunk["embedding"])
        scored.append({"chunk": chunk, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return [item["chunk"] for item in scored[:top_k]]


def answer_compliance_question(question: str) -> dict:
    if not chunk_embeddings:
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
        # llama-3.3-70b-versatile: 70 billion parameters vs 8 billion before
        # This model reasons much better about complex legal text
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        # temperature 0.2 — slightly more than before (0.1)
        # allows the model to elaborate while staying factual
        temperature=0.2,
        # 2000 tokens allows roughly 1500 words — enough for detailed answers
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