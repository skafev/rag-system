import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


URL = "http://127.0.0.1:8000/advanced_search"
CONCURRENT_REQUESTS = 10
TOTAL_REQUESTS = 30

# Sample payload
payload = {
    "query": "Alice 30 USA",
    "top_k": 3,
    "metadata_filter": {"doc_type": "pdf"},
    "w_semantic": 0.7,
    "w_keyword": 0.3
}

headers = {"Content-Type": "application/json"}


def send_request(i):
    response = requests.post(URL, json=payload, headers=headers)
    if response.status_code == 200:
        return f"Request {i}: Success, returned {len(response.json().get('results', []))} results"
    else:
        return f"Request {i}: Failed with status {response.status_code}, {response.text}"


if __name__ == "__main__":
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        for future in as_completed(futures):
            print(future.result())
