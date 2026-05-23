"""
RAGAS evaluation for EU AI Act Compliance RAG pipeline.

Requires:
- eval-env activated (source eval-env/bin/activate)
- API running locally (uvicorn src.api.main:app --port 8001)
- data/knowledge_base.json present

Run with:
    PYTHONPATH=. python scripts/evaluate_rag.py
"""

import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas.llms import LangchainLLMWrapper
from langchain_groq import ChatGroq

API_BASE = "http://localhost:8001"

# load knowledge base so we can look up full chunk content by ID
with open("data/knowledge_base.json", "r") as f:
    KB = {chunk["id"]: chunk for chunk in json.load(f)}

TEST_SET = [
    {
        "question": "What AI practices are prohibited under Article 5 of the EU AI Act?",
        "ground_truth": "Article 5 prohibits AI systems that use subliminal techniques to manipulate human behaviour causing harm, exploit vulnerabilities of specific groups, social scoring by public authorities, real-time remote biometric identification in public spaces by law enforcement with narrow exceptions, emotion recognition in workplaces or educational institutions, biometric categorisation inferring sensitive attributes."
    },
    {
        "question": "What are the obligations for providers of high-risk AI systems under Article 9?",
        "ground_truth": "Article 9 requires a continuous iterative risk management system throughout the AI lifecycle that identifies and analyses known and foreseeable risks, estimates risks that may emerge during use, evaluates risks from post-market monitoring data, and adopts appropriate risk mitigation measures. Residual risks must be judged acceptable."
    },
    {
        "question": "What does Article 13 require regarding transparency for high-risk AI systems?",
        "ground_truth": "Article 13 requires high-risk AI systems to be sufficiently transparent. Providers must supply instructions for use that enable deployers to interpret outputs, including provider identity, system capabilities and limitations, performance metrics, known biases, human oversight measures, and expected lifetime."
    },
    {
        "question": "What are the penalties for violating the EU AI Act prohibition on AI practices?",
        "ground_truth": "Article 99 sets fines up to 35 million euros or 7 percent of worldwide annual turnover for violations of prohibited practices under Article 5. For violations of high-risk AI obligations, fines reach up to 15 million euros or 3 percent of turnover."
    },
    {
        "question": "Who is considered a deployer under the EU AI Act and what are their main obligations?",
        "ground_truth": "A deployer is a natural or legal person who uses an AI system under their own authority. Deployers must take technical and organisational measures per instructions for use, assign competent human oversight, monitor system operation, keep logs for six months, and report serious incidents."
    },
    {
        "question": "What are the EU AI Act requirements for data governance under Article 10?",
        "ground_truth": "Article 10 requires training, validation, and testing datasets to be relevant, representative, free of errors, and complete. Data governance must cover data collection, preparation, examination for biases, and identification of data gaps."
    },
    {
        "question": "What is the scope of the EU AI Act and who does it apply to?",
        "ground_truth": "The EU AI Act applies to providers placing AI systems on the EU market regardless of establishment location, EU-based deployers, non-EU providers whose output is used in the EU, importers, distributors, and product manufacturers. Military and national security use is excluded."
    },
    {
        "question": "What obligations apply to general purpose AI models with systemic risk?",
        "ground_truth": "GPAI models exceeding 10 to the power of 25 FLOPs must conduct adversarial testing and red-teaming, report serious incidents to the European AI Office, implement cybersecurity protections proportionate to risks, and report energy consumption."
    },
    {
        "question": "What does Article 14 require for human oversight of high-risk AI systems?",
        "ground_truth": "Article 14 requires systems to allow natural persons to fully understand capabilities and limitations, monitor operation, detect anomalies, and override or interrupt operation. Humans must be able to intervene before decisions affecting individuals take effect."
    },
    {
        "question": "What is required for conformity assessment of high-risk AI systems under Article 43?",
        "ground_truth": "Most systems can use internal self-assessment documented in technical documentation. Biometric identification and safety-critical infrastructure systems require third-party assessment by a notified body. After assessment, providers must draw up an EU declaration of conformity and affix the CE marking."
    }
]


def get_rag_response(question: str) -> tuple[str, list[str]]:
    """
    Call the running API to get answer and source IDs.
    Look up full context text from knowledge_base.json by source ID.
    """
    response = requests.post(
        f"{API_BASE}/api/v1/ai/ask",
        json={"question": question},
        timeout=60
    )
    data = response.json()
    answer = data["answer"]

    # look up full content for each returned source ID
    contexts = []
    for source in data.get("sources", []):
        chunk_id = source["id"]
        if chunk_id in KB:
            contexts.append(KB[chunk_id]["content"])

    return answer, contexts


def build_dataset() -> EvaluationDataset:
    """Run all test questions through the RAG and build RAGAS dataset."""
    print(f"Running {len(TEST_SET)} questions through the RAG pipeline...")
    samples = []

    for i, item in enumerate(TEST_SET):
        print(f"  Question {i+1}/{len(TEST_SET)}: {item['question'][:60]}...")
        try:
            answer, contexts = get_rag_response(item["question"])

            sample = SingleTurnSample(
                user_input=item["question"],
                response=answer,
                retrieved_contexts=contexts,
                reference=item["ground_truth"]
            )
            samples.append(sample)

            # pause between questions to avoid Groq rate limits
            time.sleep(4)

        except Exception as e:
            print(f"  ERROR on question {i+1}: {e}")

    print(f"Built dataset with {len(samples)} samples")
    return EvaluationDataset(samples=samples)


def get_rag_response(question: str) -> tuple[str, list[str]]:
    response = requests.post(
        f"{API_BASE}/api/v1/ai/ask",
        json={"question": question},
        timeout=60
    )
    data = response.json()
    
    # show the actual response so we can debug
    if "answer" not in data:
        raise ValueError(f"Unexpected response: {data}")
    
    answer = data["answer"]
    contexts = []
    for source in data.get("sources", []):
        chunk_id = source["id"]
        if chunk_id in KB:
            contexts.append(KB[chunk_id]["content"])

    return answer, contexts

def run_evaluation():
    groq_api_key = os.getenv("GROQ_API_KEY")

    # use Groq as the judge LLM for RAGAS evaluation
    judge_llm = LangchainLLMWrapper(
        ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_api_key,
            temperature=0
        )
    )

    dataset = build_dataset()

    print("\nRunning RAGAS evaluation metrics...")
    print("Groq judges each answer for faithfulness, relevancy, precision, recall.\n")

    result = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(),
            AnswerRelevancy(),
            ContextPrecision(),
            ContextRecall()
        ],
        llm=judge_llm
    )

    print("\n" + "="*50)
    print("RAGAS EVALUATION RESULTS")
    print("="*50)
    print(f"Faithfulness:      {result['faithfulness']:.4f}")
    print(f"Answer Relevancy:  {result['answer_relevancy']:.4f}")
    print(f"Context Precision: {result['context_precision']:.4f}")
    print(f"Context Recall:    {result['context_recall']:.4f}")
    print("="*50)

    os.makedirs("data/evaluations", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/evaluations/ragas_{timestamp}.json"

    record = {
        "timestamp": timestamp,
        "model": "llama-3.3-70b-versatile",
        "evaluator": "RAGAS 0.2.15",
        "knowledge_base_chunks": 423,
        "test_questions": len(TEST_SET),
        "scores": {
            "faithfulness": round(result['faithfulness'], 4),
            "answer_relevancy": round(result['answer_relevancy'], 4),
            "context_precision": round(result['context_precision'], 4),
            "context_recall": round(result['context_recall'], 4)
        }
    }

    with open(output_path, "w") as f:
        json.dump(record, f, indent=2)

    print(f"\nResults saved to {output_path}")
    return record


if __name__ == "__main__":
    run_evaluation()