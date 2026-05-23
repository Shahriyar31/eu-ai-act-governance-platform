import os
import json
import re

# How many words per chunk — 600 is optimal for RAG
# Too small: not enough context. Too large: retrieval becomes imprecise
CHUNK_SIZE = 600

# Words of overlap between consecutive chunks
# Prevents losing context at chunk boundaries
OVERLAP = 100

REGULATION_METADATA = {
    "eu_ai_act": "EU AI Act (Regulation EU 2024/1689)",
    "gdpr": "GDPR (Regulation EU 2016/679)",
    "eu_data_act": "EU Data Act (Regulation EU 2023/2854)"
}

def split_into_chunks(text: str, regulation_name: str) -> list[dict]:
    """Split regulation text into overlapping chunks."""
    words = text.split()
    chunks = []
    chunk_index = 0
    position = 0

    while position < len(words):
        # take CHUNK_SIZE words starting at position
        chunk_words = words[position:position + CHUNK_SIZE]
        chunk_text = " ".join(chunk_words)

        # try to find a good article title in this chunk for labelling
        title = _extract_title(chunk_text, regulation_name, chunk_index)

        chunks.append({
            "id": f"{regulation_name}_chunk_{chunk_index}",
            "title": title,
            "regulation": REGULATION_METADATA[regulation_name],
            "content": chunk_text,
            "chunk_index": chunk_index
        })

        chunk_index += 1
        # move forward by CHUNK_SIZE minus OVERLAP
        # this creates the overlap between consecutive chunks
        position += (CHUNK_SIZE - OVERLAP)

    print(f"{regulation_name}: {len(chunks)} chunks created")
    return chunks

def _extract_title(text: str, regulation_name: str, index: int) -> str:
    """Try to find an article number in the chunk for a meaningful title."""
    # look for patterns like "Article 5" or "ARTICLE 9"
    match = re.search(r'Article\s+(\d+)', text, re.IGNORECASE)
    if match:
        return f"{REGULATION_METADATA[regulation_name]} — Article {match.group(1)}"
    return f"{REGULATION_METADATA[regulation_name]} — Section {index + 1}"

def build_knowledge_base():
    all_chunks = []

    for regulation_name in REGULATION_METADATA.keys():
        filepath = f"data/regulations/{regulation_name}.md"

        if not os.path.exists(filepath):
            print(f"Missing: {filepath} — run scrape_regulations.py first")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = split_into_chunks(content, regulation_name)
        all_chunks.extend(chunks)

    # save as JSON — the RAG engine will load this at startup
    os.makedirs("data", exist_ok=True)
    output_path = "data/knowledge_base.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Knowledge base saved to {output_path}")
    return all_chunks

if __name__ == "__main__":
    build_knowledge_base()