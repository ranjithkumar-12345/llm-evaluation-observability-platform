import json
import requests

BACKEND_URL = "http://127.0.0.1:8000"


with open("rag_eval_dataset.json", "r") as f:
    test_cases = json.load(f)

print(f"Loaded {len(test_cases)} evaluation cases. Running benchmark...\n")

total_faithfulness = 0.0
total_relevance = 0.0
total_latency = 0.0

for case in test_cases:
    payload = {
        "query": case["query"],
        "ground_truth": case["ground_truth"]
    }
    response = requests.post(f"{BACKEND_URL}/api/evaluate/query", json=payload)
    if response.status_code == 200:
        data = response.json()
        metrics = data["metrics"]
        total_faithfulness += metrics["faithfulness"]
        total_relevance += metrics["answer_relevance"]
        total_latency += data["latency_seconds"]
        print(f"Query: {case['query']} -> Faithfulness: {metrics['faithfulness']}, Latency: {data['latency_seconds']}s")

count = len(test_cases)
print("\n--- BENCHMARK REPORT ---")
print(f"Average Faithfulness: {round(total_faithfulness / count, 2)}")
print(f"Average Answer Relevance: {round(total_relevance / count, 2)}")
print(f"Average Latency: {round(total_latency / count, 2)}s")