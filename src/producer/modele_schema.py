from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str
    email: str
    age: int
    gender: str
    country: str
    city: str
    membership: str
    preferred_device: str
    signup_date: datetime
    favorite_category: str

@dataclass
class Product:
    product_id: str
    name: str
    category: str
    brand: str
    price: float
    rating: float
    stock: int

@dataclass
class Cart:
    products: List[Product] = field(default_factory=list)
    total: float = 0.0

@dataclass
class Session:
    session_id: str
    user_id: str
    started_at: datetime
    current_page: str
    device: str
    browser: str
    cart: Cart
    last_search: Optional[str] = None
    viewed_product: Optional[Product] = None

@dataclass
class Event:
    event_id: str
    timestamp: datetime
    event_type: str
    session_id: str
    user_id: str
    payload: Dict[str, Any]