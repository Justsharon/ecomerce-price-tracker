"""
You're building a pipeline that ingests customer orders. Define a Pydantic model called Order with these fields:

order_id — integer, required
customer_id — integer, required
amount — float, required
status — string, defaults to "pending"
notes — optional string, defaults to None


Test it with three cases:

A valid complete order
A valid order using defaults
An invalid order with a string amount that can't convert to float

exercise 2

Add two validators to your Order model:

amount must be greater than 0
status must be one of: "pending", "completed", "refunded"

Exercise 3 — Nested Model

Define two models:
Customer — customer_id (int), name (str), email (str), tier (str, default "basic")
OrderWithCustomer — all fields from Order plus a nested Customer

Create a valid instance and access order.customer.email.

"""

from pydantic import BaseModel, field_validator,  model_validator
from typing import Optional

class Order(BaseModel):
    order_id: int
    customer_id: int
    amount : float
    status: str  =  "pending"
    notes: Optional[str] = None
    discount: float = 0.0

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError(f"Amount cannot be zero or negative, got {value}")
        return value
    
    @field_validator("status")
    @classmethod
    def status_must_be_one_of_the_three(cls, value):
        if value not in (["pending", "completed", "refunded"]):
           raise ValueError(f"status must be one of: pending, completed, refunded")
        return value 
    
    # mode="after" means this runs after all individual field validators — so all fields are already validated and coerced when this runs.
    @model_validator(mode="after")
    def discount_cannot_exceed_amount(self):
        if self.discount > self.amount:
            raise ValueError(
                f"Discount {self.discount} cannot exceed amount {self.amount}"
            )
        return self
    

class Customer(BaseModel):
    customer_id: int
    name: str
    email: str
    tier: str = "basic"

class OrderWithCustomer(Order): # inherits all Order fields
    customer: Customer # just add the new field


o = Order(
    order_id=1,
    customer_id=20,
    amount=1234.67,
    status="refunded",
    notes="this box is sealed , if unsealed when delivered report immediately"
)

o1 = Order(
    order_id=2,
    customer_id=24,
    amount=1234.67
)

o2 = Order(
    order_id=3,
    customer_id=34,
    amount="1234.67",
    status="completed",
    notes="this box is sealed , if unsealed when delivered report immediately"
)

o3 = OrderWithCustomer(
    order_id=3,
    customer_id=34,
    amount="1234.67",
    status="completed",
    notes="this box is sealed , if unsealed when delivered report immediately",
    customer={
        "customer_id": 34,
        "name": "Hellen",
        "email":"hellen@outlook.com"
    }
)

