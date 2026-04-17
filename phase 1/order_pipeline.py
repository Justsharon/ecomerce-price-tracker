"""

The Scenario
Your pipeline receives raw order data from an API as a list of dictionaries. 
Some are valid, some are malformed. 
Your job is to process the entire batch, validate each order, and produce two outputs — clean orders and a rejected orders report.

"""
from pydantic import ValidationError
from models import Order 
import json

# This is your raw API data — do not modify it
raw_orders = [
    {"order_id": 1, "customer_id": 101, "amount": 250.00, "status": "completed"},
    {"order_id": 2, "customer_id": 102, "amount": -50.00, "status": "completed"},
    {"order_id": 3, "customer_id": 103, "amount": 175.50, "status": "shipped"},
    {"order_id": 4, "customer_id": 104, "amount": "not_a_number", "status": "pending"},
    {"order_id": 5, "customer_id": 105, "amount": 320.00},
    {"order_id": 6, "customer_id": 106, "amount": 0, "status": "completed"},
    {"order_id": 7, "customer_id": 107, "amount": 89.99, "status": "refunded", "notes": "damaged"},
]

def process_batch(raw_orders):
    valid_orders = []
    rejected_orders = []
    
    for raw_order in raw_orders:
        try:
            order = Order(**raw_order)
            valid_orders.append(order)
        except ValidationError as e:
            res = e.errors()
            rejected_orders.append({
                "order_id": raw_order.get("order_id", "unknown"),
                "raw_data": raw_order,
                "errors": [err["msg"] for err in res]  # clean list of messages
            })

    summary = {
        "total_received": len(raw_orders),
        "valid_count": len(valid_orders),
        "rejected_count": len(rejected_orders),
        "success_rate": round(len(valid_orders) / len(raw_orders) * 100, 1)
    }
    
    return {
        "summary": summary,
        "valid_orders": [o.model_dump() for o in valid_orders],
        "rejected_orders": rejected_orders
    }

result = process_batch(raw_orders)
print(json.dumps(result, indent=2))