import httpx
import asyncio
import logging
from datetime import datetime
from models import Product, PriceSnapshot
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# use mock data when API is unavailable, or for testing purposes
def get_mock_snapshots() -> list[PriceSnapshot]:
    """Mock data for when API is unavailable"""
    mock_products = [
        {"id": 1, "title": "Backpack", "price": 109.95, "category": "clothing", "rating": {"rate": 3.9, "count": 120}},
        {"id": 2, "title": "Slim Fit T-Shirt", "price": 22.30, "category": "clothing", "rating": {"rate": 4.1, "count": 259}},
        {"id": 3, "title": "Cotton Jacket", "price": 55.99, "category": "clothing", "rating": {"rate": 4.7, "count": 500}},
        {"id": 4, "title": "Casual Dress", "price": 12.99, "category": "clothing", "rating": {"rate": 2.6, "count": 235}},
        {"id": 5, "title": "Gold Bracelet", "price": 695.00, "category": "jewelery", "rating": {"rate": 4.6, "count": 400}},
        {"id": 6, "title": "Silver Ring", "price": 9.99,  "category": "jewelery", "rating": {"rate": 3.8, "count": 100}},
        {"id": 7, "title": "Diamond Necklace", "price": 12.99, "category": "jewelery", "rating": {"rate": 4.3, "count": 150}},
        {"id": 8, "title": "Gold Earrings", "price": 10.99, "category": "jewelery", "rating": {"rate": 4.0, "count": 200}},
        {"id": 9, "title": "USB-C Laptop", "price": 999.99, "category": "electronics", "rating": {"rate": 4.4, "count": 617}},
        {"id": 10, "title": "SSD Drive", "price": 109.00, "category": "electronics", "rating": {"rate": 3.9, "count": 319}},
        {"id": 11, "title": "Gaming Monitor", "price": 399.99, "category": "electronics", "rating": {"rate": 2.9, "count": 250}},
        {"id": 12, "title": "Wireless Mouse", "price": 29.99, "category": "electronics", "rating": {"rate": 4.5, "count": 400}},
        {"id": 13, "title": "Mechanical Keyboard", "price": 89.99, "category": "electronics", "rating": {"rate": 4.8, "count": 523}},
        {"id": 14, "title": "Budget Headphones", "price": 9.99,  "category": "electronics", "rating": {"rate": 3.0, "count": 180}},
    ]

    snapshots = []
    for raw in mock_products:
        product = Product(**raw)
        snapshot = PriceSnapshot(
            product_id=product.id,
            title=product.title,
            price=product.price,
            category=product.category
        )
        snapshots.append(snapshot)
    return snapshots

# real API fetching and validation logic
BASE_URL = "https://fakestoreapi.com"

async def fetch_all_products() -> list[dict]:
    """Fetch all products from the API, retrying up to 3 times on failure."""
    last_error = None
    for attempt in range(1, 4):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/products", timeout=10)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            last_error = e
            logger.warning("Attempt %d/3 failed: %s", attempt, e)
            if attempt < 3:
                await asyncio.sleep(2)
    logger.error("All 3 fetch attempts failed: %s", last_error)
    raise last_error

async def fetch_and_validate() -> list[PriceSnapshot]:
    """Fetch products and convert to validated PriceSnapshots"""
    raw_products = await fetch_all_products()

    snapshots = []
    errors = []

    for raw in raw_products:
        try:
            product = Product(**raw)

            snapshot = PriceSnapshot(
                product_id=product.id,
                title=product.title,
                price=product.price,
                category=product.category
            )
            snapshots.append(snapshot)

        except ValidationError as e:
            errors.append({
                "product_id": raw.get("id"),
                "errors": [err["msg"] for err in e.errors()]
            })

    logger.info("Fetched: %d", len(raw_products))
    logger.info("Valid snapshots: %d", len(snapshots))
    if errors:
        logger.error("Validation errors: %d", len(errors))

    return snapshots

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    snapshots = asyncio.run(fetch_and_validate())
    for s in snapshots[:3]:
        logger.info(s.model_dump())
