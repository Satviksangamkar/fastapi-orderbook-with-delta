from pydantic import BaseModel
from typing import List

class PriceLevel(BaseModel):
    price: float
    amount: float
