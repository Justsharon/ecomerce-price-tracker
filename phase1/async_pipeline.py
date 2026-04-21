import requests
from models import Order
from pydantic import ValidationError

def fetch_todo(todo_id: int) -> dict:
    """Fetch a single todo from the JSONPLaceolder API."""
    url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"
    response = requests.get(url, timeout=5)

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code} for todo {todo_id}")
    
    return response.json()

# Async version

import httpx
import asyncio

async def fetch_todo_async(client: httpx.AsyncClient, todo_id: int) -> dict:
    """Fetch a single todo asyncronously"""
    url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"
    response = await client.get(url, timeout=5)

    if response.status_code != 200:
        raise  Exception(f"API error {response.status_code} for todo {todo_id}")
    
    return response.json()

async def fetch_all_async(todo_ids: list[int]) -> list[dict]:
    """Fetch multiple todos concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_todo_async(client, todo_id) for todo_id in todo_ids]
        results = await asyncio.gather(*tasks)
        return results
    
if __name__ ==  "__main__":
    import time

    start = time.time()
    results = []
    for i in range(1, 11):
        data = fetch_todo(i)
        results.append(data)
        print(f"Fetched todo {i}: {data['title'][:40]}")

    sequential_time = time.time() - start
    print(f"\nSequential: {len(results)} requests in {sequential_time:.2f}s")

    start = time.time()
    results = asyncio.run(fetch_all_async(list(range(1,11))))
    async_time = time.time() - start
    for r in results:
        print(f"Fetched todo {r['id']}: {r['title'][:40]}")
    print(f"\nConcurrent: {len(results)} requests in {async_time:.2f}s")

    print(f"Speedup ratio: {sequential_time / async_time}")
