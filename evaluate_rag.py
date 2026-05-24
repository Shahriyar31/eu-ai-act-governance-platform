"""
RAGAS evaluation for the EU AI Act Compliance RAG pipeline.

Metrics: faithfulness, answer_relevancy, context_precision, context_recall
Evaluator LLM: Groq llama-3.1-8b-instant (500K tokens/day free tier)
Embedding model: BAAI/bge-small-en-v1.5

Run from project root with eval-env activated:
    source eval-env/bin/activate
    python evaluate_rag.py
"""

import os
import sys
import json
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq


TEST_CASES = [
    {
        "question": "What obligations does Article 9 of the EU AI Act impose on providers of high-risk AI systems?",
        "ground_truth": "Article 9 requires providers to establish, implement, document and maintain a risk management system throughout the entire lifecycle of the high-risk AI system, identifying and analysing known and foreseeable risks associated with each system."
    },
    {
        "question": "What AI practices are prohibited under Article 5 of the EU AI Act?",
        "ground_truth": "Article 5 prohibits AI systems that deploy subliminal techniques beyond a person's consciousness, exploit vulnerabilities of specific groups, enable social scoring by public authorities causing detrimental treatment, and real-time remote biometric identification in public spaces by law enforcement except in limited circumstances."
    },
    {
        "question": "What technical documentation must providers of high-risk AI systems maintain under Article 11?",
        "ground_truth": "Article 11 requires technical documentation drawn up before market placement covering the general description of the AI system, design specifications, development processes, monitoring information, training data details, validation and testing procedures, and expected performance metrics."
    },
    {
        "question": "What human oversight measures are required for high-risk AI systems under Article 14?",
        "ground_truth": "Article 14 requires high-risk AI systems to be designed with human oversight measures enabling natural persons to monitor operation, understand and interpret outputs appropriately, intervene or override the system, and stop or interrupt the system through a halt function."
    },
    {
        "question": "What are the data governance requirements for training datasets under Article 10 of the EU AI Act?",
        "ground_truth": "Article 10 requires training, validation and testing datasets to be subject to data governance practices ensuring they are relevant, representative, free of errors and complete, and cover the relevant population and geographic and functional settings for the intended purpose."
    },
    {
        "question": "What transparency obligations apply to high-risk AI systems under Article 13?",
        "ground_truth": "Article 13 requires high-risk AI systems to be sufficiently transparent that deployers can understand the system's capabilities and limitations, interpret outputs, and use the system appropriately. Providers must supply instructions for use containing relevant information."
    },
    {
        "question": "Which sectors and use cases are listed as high-risk in Annex III of the EU AI Act?",
        "ground_truth": "Annex III lists high-risk AI systems covering biometric identification and categorisation, critical infrastructure management, education and vocational training, employment and workers management, access to essential private and public services, law enforcement, migration and border control, and administration of justice."
    },
    {
        "question": "What conformity assessment procedures must high-risk AI systems undergo before being placed on the market?",
        "ground_truth": "Under Article 43, high-risk AI systems must undergo a conformity assessment before market placement. Most Annex III systems can use internal control by the provider. Systems involving real-time biometric identification require third-party assessment by a notified body."
    },
    {
        "question": "What obligations do providers of general-purpose AI models have under the EU AI Act?",
        "ground_truth": "Under Article 53, providers of general-purpose AI models must maintain and provide technical documentation, put in place a copyright compliance policy, publish a summary of training content, and for models with systemic risk also perform adversarial testing and report serious incidents to the AI Office."
    },
    {
        "question": "What are the maximum fines for violations of the EU AI Act under Article 99?",
        "ground_truth": "Article 99 sets administrative fines up to 35 million euros or 7 percent of global annual turnover for violations of prohibited AI practices, up to 15 million or 3 percent for violations of other obligations, and up to 7.5 million or 1.5 percent for supplying incorrect information."
    }
]


def retrieve_for_question(question: str) -> tuple[str, list[str]]:
    from src.ai.rag_engine import answer_compliance_question, _retrieve_relevant_chunks
    result = answer_compliance_question(question)
    chunks = _retrieve_relevant_chunks(question, top_k=5)
    context_texts = [chunk["content"] for chunk in chunks]
    return result["answer"], context_texts


def build_dataset() -> Dataset:
    print(f"\nRunning {len(TEST_CASES)} questions through the RAG pipeline...")
    questions, answers, contexts, ground_truths = [], [], [], []

    for i, case in enumerate(TEST_CASES):
        print(f"  [{i+1}/{len(TEST_CASES)}] {case['question'][:65]}...")
        try:
            answer, context_texts = retrieve_for_question(case["question"])
            questions.append(case["question"])
            answers.append(answer)
            contexts.append(context_texts)
            ground_truths.append(case["ground_truth"])
            print(f"         answer length: {len(answer)} chars, chunks retrieved: {len(context_texts)}")
        except Exception as e:
            print(f"         ERROR: {e}")
            questions.append(case["question"])
            answers.append("Error retrieving answer")
            contexts.append([""])
            ground_truths.append(case["ground_truth"])

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })


def main():
    print("EU AI Act RAG Pipeline — RAGAS Evaluation")
    print("=" * 55)

    print("\nConfiguring evaluator LLM (Groq llama-3.1-8b-instant)...")
    evaluator_llm = LangchainLLMWrapper(
        ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
    )

    print("Configuring embeddings (BAAI/bge-small-en-v1.5 via FastEmbed)...")
    evaluator_embeddings = None
    try:
        from langchain_community.embeddings import FastEmbedEmbeddings
        evaluator_embeddings = LangchainEmbeddingsWrapper(
            FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        )
    except Exception as e:
        print(f"  FastEmbedEmbeddings unavailable ({e}), answer_relevancy will be skipped")

    print("\nInitialising knowledge base connection...")
    from src.ai.rag_engine import initialise_knowledge_base
    initialise_knowledge_base()

    dataset = build_dataset()
    print(f"\nDataset ready: {len(dataset)} questions")

    metrics = [faithfulness, context_precision, context_recall]
    if evaluator_embeddings:
        metrics.append(answer_relevancy)

    print(f"\nRunning RAGAS evaluation on {len(metrics)} metrics...")
    print("This makes ~40 LLM calls and takes 3-6 minutes. Do not interrupt.\n")

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        raise_exceptions=False,
        show_progress=True,
    )

    df = result.to_pandas()

    print("\n" + "=" * 55)
    print("RAGAS RESULTS — EU AI Act Compliance RAG Pipeline")
    print("=" * 55)

    scores = {}
    for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric_name in df.columns:
            val = df[metric_name].mean()
            label = metric_name.replace("_", " ").title()
            if pd.isna(val):
                print(f"  {label:<22} N/A (evaluation failed)")
            else:
                scores[metric_name] = float(val)
                print(f"  {label:<22} {val:.4f}")

    print("=" * 55)
    print("\nScore guide:  > 0.8 excellent  |  0.6-0.8 good  |  < 0.6 needs work\n")

    scores.update({
        "evaluator_model": "llama-3.1-8b-instant",
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "num_questions": len(TEST_CASES),
        "knowledge_base_chunks": 423
    })

    with open("ragas_results.json", "w") as f:
        json.dump(scores, f, indent=2)

    print("Results saved to ragas_results.json")


if __name__ == "__main__":
    main()