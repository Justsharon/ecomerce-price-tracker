from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime, timezone

class Rating(BaseModel):
    rate: float # between 0 and 5
    count: int

    @field_validator("rate")
    @classmethod

    def rate_must_be_between_0_and_5(cls, value):
        if not(0 <= value <= 5):
            raise ValueError(f"rate must be a number between 0 and 5, got{value}")
        return value

class Product(BaseModel):
    id: int
    title: str
    price : float  #must be positive
    category: str
    rating: Optional[Rating] # nested model

    @field_validator("price")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError(f"Price cannot be zero or negative, got {value}")
        return value

class PriceSnapshot(BaseModel):
    product_id: int
    title: str
    price: float
    category: str
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source:str = "fakestoreapi"