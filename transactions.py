from dataclasses import dataclass

@dataclass
class Transaction:
    timestamp: str
    type: str
    asset: str
    quantity: float
    price: float