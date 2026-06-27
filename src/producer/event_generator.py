import random
import uuid
from datetime import datetime, timezone

from src.producer.modele_schema import Event


class ClickstreamGenerator:

    TRANSITIONS = {
        "START": [("login", 1.0)],
        "login": [("home", 1.0)],
        "home": [
            ("search", 0.50),
            ("product_view", 0.40),
            ("logout", 0.10),
        ],
        "search": [
            ("product_view", 0.80),
            ("home", 0.20),
        ],
        "product_view": [
            ("add_to_cart", 0.45),
            ("search", 0.30),
            ("home", 0.20),
            ("logout", 0.05),
        ],
        "add_to_cart": [
            ("product_view", 0.20),
            ("remove_from_cart", 0.15),
            ("checkout", 0.50),
            ("home", 0.15),
        ],
        "remove_from_cart": [
            ("product_view", 0.70),
            ("logout", 0.30),
        ],
        "checkout": [
            ("payment", 0.90),
            ("home", 0.10),
        ],
        "payment": [
            ("purchase", 0.92),
            ("payment_failed", 0.08),
        ],
        "payment_failed": [
            ("payment", 0.60),
            ("logout", 0.40),
        ],
        "purchase": [("logout", 1.0)],
        "logout": [("START", 1.0)],
    }

    SEARCH_QUERIES = [
        "Laptop",
        "Keyboard",
        "Camera",
    ]

    PAYMENT_METHODS = [
        "Visa",
        "Mastercard",
        "PayPal",
        "Apple Pay",
    ]

    SHIPPING_COST = 10
    TAX_RATE = 0.20

    def __init__(self, product_generator):
        self.product_generator = product_generator
        self.user_states = {}

        self._processed_transitions = {
            state: ([s for s, _ in targets], [w for _, w in targets])
            for state, targets in self.TRANSITIONS.items()
        }

    def _next_state(self, current):
        states, weights = self._processed_transitions[current]
        return random.choices(states, weights)[0]

    def generate_event(self, user, session):
        current_state = self.user_states.get(user.user_id, "START")
        next_state = self._next_state(current_state)

        product = None

        if next_state == "product_view":
            product = self.product_generator.random_from_category(
                user.favorite_category
            )
            session.viewed_product = product

        elif next_state in (
            "add_to_cart",
            "checkout",
            "payment",
            "purchase",
        ):
            product = session.viewed_product

        self.user_states[user.user_id] = next_state

        return Event(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=next_state,
            session_id=session.session_id,
            user_id=user.user_id,
            payload=self._build_payload(
                next_state,
                user,
                session,
                product,
            ),
        )

    def _build_payload(self, event_type, user, session, product):

        payload = {
            "user": {
                "membership": user.membership,
                "country": user.country,
                "city": user.city,
                "favorite_category": user.favorite_category,
            },
            "session": {
                "device": session.device,
                "browser": session.browser,
                "current_page": session.current_page,
            },
        }

        if product:
            payload["product"] = {
                "product_id": product.product_id,
                "name": product.name,
                "category": product.category,
                "brand": product.brand,
                "price": product.price,
            }

        if event_type == "search":
            query = random.choice(self.SEARCH_QUERIES)
            session.last_search = query
            payload["search_query"] = query

        elif event_type == "add_to_cart":
            if product:
                session.cart.products.append(product)
                session.cart.total += product.price

            payload["cart"] = {
                "items": len(session.cart.products),
                "total": round(session.cart.total, 2),
            }

        elif event_type == "remove_from_cart":
            if session.cart.products:
                removed = session.cart.products.pop()
                session.cart.total -= removed.price

            payload["cart"] = {
                "items": len(session.cart.products),
                "total": round(session.cart.total, 2),
            }

        elif event_type == "checkout":
            payload["checkout"] = {
                "items": len(session.cart.products),
                "subtotal": round(session.cart.total, 2),
                "shipping": self.SHIPPING_COST,
                "tax": round(session.cart.total * self.TAX_RATE, 2),
            }

        elif event_type == "payment":
            payload["payment"] = {
                "method": random.choice(self.PAYMENT_METHODS),
            }

        elif event_type == "purchase":
            subtotal = session.cart.total
            tax = subtotal * self.TAX_RATE

            payload["order"] = {
                "order_id": str(uuid.uuid4()),
                "items": len(session.cart.products),
                "subtotal": round(subtotal, 2),
                "tax": round(tax, 2),
                "shipping": self.SHIPPING_COST,
                "total": round(subtotal + tax + self.SHIPPING_COST, 2),
            }

            session.cart.products.clear()
            session.cart.total = 0

        return payload