import os
import math
from groq import Groq
from dotenv import load_dotenv
from src.ai.knowledge_base import EU_AI_ACT_CHUNKS

load_dotenv()

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
    print(f"Initialising RAG knowledge base — embedding {len(EU_AI_ACT_CHUNKS)} chunks...")
    for chunk in EU_AI_ACT_CHUNKS:
        embedding = _get_embedding(chunk["content"])
        chunk_embeddings.append({
            "id": chunk["id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "embedding": embedding
        })
    print("Knowledge base ready.")

def _retrieve_relevant_chunks(question: str, top_k: int = 3) -> list[dict]:
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
        f"{chunk['title']}:\n{chunk['content']}"
        for chunk in relevant_chunks
    ])
    prompt = f"""You are an EU AI Act compliance expert assistant. 
Answer the user's question using ONLY the provided regulatory context below.
If the answer is not in the context, say so clearly — do not speculate.
Be precise, cite article numbers where relevant, and be concise.

REGULATORY CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:"""
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800
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
