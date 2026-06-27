from datetime import datetime, timezone
import random
import uuid

from faker import Faker

from src.producer.modele_schema import Cart, Product, Session, User

fake = Faker()

COUNTRIES = [
    ("Morocco", ["Casablanca", "Rabat", "Marrakech", "Agadir", "Tangier"]),
    ("France", ["Paris", "Lyon", "Marseille"]),
    ("Germany", ["Berlin", "Hamburg", "Munich"]),
    ("USA", ["New York", "Los Angeles", "Chicago"]),
]

DEVICES = ["Mobile", "Desktop", "Tablet"]

MEMBERSHIPS = ["Standard", "Premium", "Gold"]

CATEGORIES = [
    "Electronics",
    "Fashion",
    "Books",
    "Sports",
    "Home",
    "Gaming",
    "Beauty",
]


class UserGenerator:

    def __init__(self, num_users: int):
        self.users = {}
        self._user_list = []

        for _ in range(num_users):
            country, cities = random.choice(COUNTRIES)

            user = User(
                user_id=str(uuid.uuid4()),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                age=random.randint(18, 70),
                gender=random.choice(["Male", "Female"]),
                country=country,
                city=random.choice(cities),
                membership=random.choices(
                    MEMBERSHIPS,
                    weights=[70, 25, 5],
                    k=1,
                )[0],
                preferred_device=random.choice(DEVICES),
                signup_date=fake.date_time_between("-3y", "now"),
                favorite_category=random.choice(CATEGORIES),
            )

            self.users[user.user_id] = user
            self._user_list.append(user)

    def random_user(self):
        return random.choice(self._user_list)


PRODUCTS = {
    "Electronics": [
        "Laptop",
        "Keyboard",
        "Mouse",
        "Smartphone",
        "Monitor",
        "Tablet",
        "Camera",
    ],
    "Gaming": [
        "PlayStation",
        "Xbox",
        "Gaming Chair",
        "Gaming Mouse",
        "Gaming Keyboard",
    ],
    "Fashion": [
        "T-Shirt",
        "Shoes",
        "Jacket",
        "Jeans",
        "Hat",
    ],
    "Books": [
        "Python",
        "Terraform",
        "AWS",
        "Spark",
        "Kafka",
    ],
    "Sports": [
        "Football",
        "Basketball",
        "Tennis Racket",
        "Running Shoes",
    ],
}

PRODUCT_BRANDS = {
    "Laptop": ["Dell", "HP", "Lenovo", "Apple", "Asus"],
    "Keyboard": ["Logitech", "Corsair", "Razer"],
    "Mouse": ["Logitech", "Razer"],
    "Smartphone": ["Apple", "Samsung"],
    "Monitor": ["Dell", "LG", "Samsung", "Asus"],
    "Tablet": ["Apple", "Samsung"],
    "Camera": ["Sony", "Canon"],
    "PlayStation": ["Sony"],
    "Xbox": ["Microsoft"],
    "Gaming Chair": ["Secretlab"],
    "Gaming Mouse": ["Logitech", "Razer"],
    "Gaming Keyboard": ["Logitech", "Corsair", "Razer"],
    "T-Shirt": ["Nike", "Adidas", "Uniqlo"],
    "Shoes": ["Nike", "Adidas", "Puma"],
    "Jacket": ["The North Face", "Columbia", "Patagonia"],
    "Jeans": ["Levi's"],
    "Hat": ["Nike", "Adidas"],
    "Python": ["O'Reilly"],
    "Terraform": ["O'Reilly"],
    "AWS": ["Amazon"],
    "Spark": ["O'Reilly"],
    "Kafka": ["O'Reilly"],
    "Football": ["Nike", "Adidas"],
    "Basketball": ["Wilson"],
    "Tennis Racket": ["Wilson", "Babolat"],
    "Running Shoes": ["Nike", "ASICS", "Adidas"],
}


PRICE_RANGES = {
    "Electronics": (150, 2500),
    "Gaming": (80, 900),
    "Fashion": (20, 250),
    "Books": (20, 70),
    "Sports": (30, 400),
    "Home": (20, 300),
    "Beauty": (20, 300),
}

STOCK_RANGES = {
    "Electronics": (5, 50),
    "Gaming": (5, 40),
    "Fashion": (100, 500),
    "Books": (100, 1000),
    "Sports": (20, 200),
    "Home": (20, 150),
    "Beauty": (20, 300),
}


class ProductGenerator:

    def __init__(self):
        self.products = []

        for category, items in PRODUCTS.items():
            min_price, max_price = PRICE_RANGES.get(category, (20, 300))
            min_stock, max_stock = STOCK_RANGES.get(category, (20, 300))

            for item in items:
                self.products.append(
                    Product(
                        product_id=str(uuid.uuid4()),
                        name=item,
                        category=category,
                        brand=random.choice(PRODUCT_BRANDS[item]),
                        price=round(random.uniform(min_price, max_price), 2),
                        rating=round(random.uniform(4.0, 5.0), 1),
                        stock=random.randint(min_stock, max_stock),
                    )
                )

    def random_product(self):
        return random.choice(self.products)

    def products_by_category(self, category):
        return [p for p in self.products if p.category == category]

    def random_from_category(self, category):
        products = self.products_by_category(category)
        return random.choice(products) if products else self.random_product()

    def find_by_name(self, keyword):
        keyword = keyword.lower()

        matches = [
            p for p in self.products
            if keyword in p.name.lower()
        ]

        return random.choice(matches) if matches else None


BROWSERS = [
    "Chrome",
    "Firefox",
    "Safari",
    "Edge",
]


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def _create_session(self, user):
        return Session(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            started_at=datetime.now(timezone.utc),
            current_page="/",
            device=user.preferred_device,
            browser=random.choice(BROWSERS),
            cart=Cart(),
        )

    def get_session(self, user):
        if user.user_id not in self.sessions:
            self.sessions[user.user_id] = self._create_session(user)

        return self.sessions[user.user_id]

    def restart_session(self, user):
        self.sessions[user.user_id] = self._create_session(user)
        return self.sessions[user.user_id]