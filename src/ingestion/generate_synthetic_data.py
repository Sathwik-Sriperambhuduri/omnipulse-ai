"""Generate reproducible, relational synthetic e-commerce CSV datasets.

The generator intentionally uses only pandas, NumPy, and Python's standard
library.  A single NumPy random generator is passed through every helper so a
given configuration and seed always produce the same data.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

DATA_END_DATE = pd.Timestamp("2025-12-31")
DATASET_NAMES = (
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "inventory",
    "marketing_campaigns",
    "clickstream_events",
)

FIRST_NAMES = (
    "Aiden",
    "Amelia",
    "Aria",
    "Carlos",
    "Chloe",
    "Elena",
    "Ethan",
    "Fatima",
    "Grace",
    "Henry",
    "Isabella",
    "Jamal",
    "Jordan",
    "Kai",
    "Lena",
    "Liam",
    "Maya",
    "Mateo",
    "Noah",
    "Olivia",
    "Priya",
    "Ravi",
    "Sofia",
    "Zoe",
)
LAST_NAMES = (
    "Anderson",
    "Brown",
    "Chen",
    "Davis",
    "Garcia",
    "Hernandez",
    "Johnson",
    "Kim",
    "Lee",
    "Martinez",
    "Miller",
    "Nguyen",
    "Patel",
    "Rivera",
    "Robinson",
    "Singh",
    "Smith",
    "Taylor",
    "Thomas",
    "Williams",
)
LOCATIONS = (
    ("New York", "NY", "10001"),
    ("Los Angeles", "CA", "90001"),
    ("Chicago", "IL", "60601"),
    ("Houston", "TX", "77001"),
    ("Phoenix", "AZ", "85001"),
    ("Philadelphia", "PA", "19103"),
    ("Seattle", "WA", "98101"),
    ("Denver", "CO", "80202"),
    ("Atlanta", "GA", "30303"),
    ("Boston", "MA", "02108"),
    ("Miami", "FL", "33101"),
    ("Portland", "OR", "97201"),
)

# category, subcategory, brands, product nouns, typical retail-price range
PRODUCT_CATALOG = (
    (
        "Electronics",
        "Headphones",
        ("NovaSound", "PulseTech", "EchoWorks"),
        ("Wireless Headphones", "Noise-Canceling Earbuds", "Studio Headset"),
        (29.0, 249.0),
    ),
    (
        "Electronics",
        "Smart Home",
        ("LumaHome", "PulseTech", "Nexa"),
        ("Smart Bulb Kit", "Video Doorbell", "Smart Speaker"),
        (24.0, 219.0),
    ),
    (
        "Home & Kitchen",
        "Kitchen",
        ("Hearth & Oak", "Culina", "DailyNest"),
        ("Chef Knife", "Coffee Maker", "Cookware Set"),
        (19.0, 299.0),
    ),
    (
        "Home & Kitchen",
        "Bedding",
        ("CloudRest", "DailyNest", "Hearth & Oak"),
        ("Cotton Sheet Set", "Memory Foam Pillow", "Weighted Blanket"),
        (25.0, 189.0),
    ),
    (
        "Apparel",
        "Activewear",
        ("Momentum", "Northstar", "EverThread"),
        ("Performance Hoodie", "Training Leggings", "Running Shorts"),
        (18.0, 110.0),
    ),
    (
        "Apparel",
        "Footwear",
        ("Momentum", "TrailKind", "Northstar"),
        ("Everyday Sneakers", "Trail Shoes", "Running Shoes"),
        (45.0, 180.0),
    ),
    (
        "Beauty",
        "Skin Care",
        ("PureGlow", "Verdant", "Mira"),
        ("Hydrating Serum", "Daily Moisturizer", "Cleanser Set"),
        (12.0, 85.0),
    ),
    (
        "Sports & Outdoors",
        "Fitness",
        ("Summit", "Momentum", "TrailKind"),
        ("Yoga Mat", "Resistance Band Set", "Adjustable Dumbbell"),
        (15.0, 240.0),
    ),
    (
        "Books",
        "Nonfiction",
        ("Northwind Press", "Maple House", "BrightPage"),
        ("Leadership Handbook", "Home Cooking Guide", "Personal Finance Book"),
        (9.0, 38.0),
    ),
    (
        "Pet Supplies",
        "Dogs",
        ("HappyPaws", "TrailKind", "PetHaven"),
        ("Orthopedic Pet Bed", "Training Treats", "Adventure Leash"),
        (8.0, 120.0),
    ),
)


@dataclass(frozen=True)
class GenerationConfig:
    """User-controlled sizes and destination for one generation run."""

    customers: int = 1_000
    products: int = 200
    orders: int = 5_000
    clickstream_sessions: int = 3_000
    seed: int = 42
    output_dir: Path = Path("data/raw")

    def validate(self) -> None:
        """Reject sizes that cannot produce all nine non-empty datasets."""
        counts = {
            "customers": self.customers,
            "products": self.products,
            "orders": self.orders,
            "clickstream_sessions": self.clickstream_sessions,
        }
        invalid = [name for name, value in counts.items() if value < 1]
        if invalid:
            raise ValueError(f"Counts must be at least 1: {', '.join(invalid)}")


def _random_dates(
    rng: np.random.Generator,
    start: pd.Timestamp,
    end: pd.Timestamp,
    size: int,
) -> pd.DatetimeIndex:
    """Return uniformly distributed calendar dates including both boundaries."""
    day_count = (end - start).days
    offsets = rng.integers(0, day_count + 1, size=size)
    return pd.DatetimeIndex(start + pd.to_timedelta(offsets, unit="D"))


def _money(value: float) -> float:
    """Round monetary values to cents in one consistent place."""
    return round(float(value) + 1e-10, 2)


def generate_customers(count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create customer profiles with realistic signup and demographic fields."""
    signup_dates = _random_dates(
        rng, pd.Timestamp("2021-01-01"), DATA_END_DATE - pd.Timedelta(days=1), count
    )
    rows: list[dict[str, object]] = []
    for index in range(count):
        first_name = str(rng.choice(FIRST_NAMES))
        last_name = str(rng.choice(LAST_NAMES))
        city, state, postal_code = LOCATIONS[int(rng.integers(len(LOCATIONS)))]
        signup_date = signup_dates[index]
        age_at_signup = int(rng.integers(18, 76))
        birth_date = signup_date - pd.DateOffset(years=age_at_signup)
        birth_date -= pd.Timedelta(days=int(rng.integers(0, 365)))
        customer_number = index + 1
        rows.append(
            {
                "customer_id": f"CUST-{customer_number:06d}",
                "first_name": first_name,
                "last_name": last_name,
                "email": (
                    f"{first_name}.{last_name}.{customer_number}" "@example.com"
                ).lower(),
                "phone": f"+1-555-{customer_number % 10_000:04d}",
                "gender": rng.choice(
                    ["Female", "Male", "Non-binary", "Prefer not to say"],
                    p=[0.48, 0.46, 0.04, 0.02],
                ),
                "date_of_birth": birth_date.date().isoformat(),
                "signup_date": signup_date.date().isoformat(),
                "city": city,
                "state": state,
                "country": "United States",
                "postal_code": postal_code,
                "customer_segment": rng.choice(
                    ["New", "Regular", "Loyal", "VIP"],
                    p=[0.28, 0.43, 0.23, 0.06],
                ),
                "acquisition_channel": rng.choice(
                    [
                        "Organic Search",
                        "Paid Search",
                        "Social Media",
                        "Email",
                        "Referral",
                        "Affiliate",
                    ],
                    p=[0.28, 0.20, 0.20, 0.12, 0.13, 0.07],
                ),
            }
        )
    return pd.DataFrame(rows)


def generate_products(count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create a varied product catalog with viable retail margins."""
    launch_dates = _random_dates(rng, pd.Timestamp("2019-01-01"), DATA_END_DATE, count)
    rows: list[dict[str, object]] = []
    for index in range(count):
        category = PRODUCT_CATALOG[int(rng.integers(len(PRODUCT_CATALOG)))]
        category_name, subcategory, brands, nouns, price_range = category
        brand = str(rng.choice(brands))
        unit_price = _money(rng.uniform(*price_range))
        cost_price = _money(unit_price * rng.uniform(0.38, 0.74))
        rows.append(
            {
                "product_id": f"PROD-{index + 1:05d}",
                "product_name": (f"{brand} {rng.choice(nouns)} {index + 1}"),
                "category": category_name,
                "subcategory": subcategory,
                "brand": brand,
                "unit_price": unit_price,
                "cost_price": cost_price,
                "launch_date": launch_dates[index].date().isoformat(),
                "is_active": bool(rng.random() < 0.92),
            }
        )
    return pd.DataFrame(rows)


def generate_orders_and_items(
    count: int,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create orders and their line items while calculating consistent totals."""
    customer_records = customers.to_dict("records")
    product_records = products.to_dict("records")
    product_launch_dates = pd.to_datetime(products["launch_date"])
    first_product_launch = product_launch_dates.min()
    order_rows: list[dict[str, object]] = []
    item_rows: list[dict[str, object]] = []
    item_number = 1

    for order_number in range(1, count + 1):
        customer = customer_records[int(rng.integers(len(customer_records)))]
        signup_date = pd.Timestamp(customer["signup_date"])
        earliest_order_date = max(signup_date, first_product_launch)
        order_date = _random_dates(rng, earliest_order_date, DATA_END_DATE, 1)[0]
        status = str(
            rng.choice(
                ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"],
                p=[0.70, 0.10, 0.08, 0.08, 0.04],
            )
        )
        order_id = f"ORD-{order_number:07d}"
        eligible_product_indexes = np.flatnonzero(product_launch_dates <= order_date)
        item_count = min(
            int(rng.choice([1, 2, 3, 4, 5], p=[0.50, 0.27, 0.14, 0.06, 0.03])),
            len(eligible_product_indexes),
        )
        product_indexes = rng.choice(
            eligible_product_indexes, size=item_count, replace=False
        )
        gross_subtotal = 0.0
        item_discount_total = 0.0
        net_subtotal = 0.0

        for product_index in np.atleast_1d(product_indexes):
            product = product_records[int(product_index)]
            quantity = int(rng.choice([1, 2, 3, 4], p=[0.70, 0.20, 0.08, 0.02]))
            unit_price = float(product["unit_price"])
            gross_line = _money(quantity * unit_price)
            discount_rate = float(
                rng.choice(
                    [0.0, 0.05, 0.10, 0.15, 0.20], p=[0.55, 0.15, 0.16, 0.09, 0.05]
                )
            )
            discount_amount = _money(gross_line * discount_rate)
            line_total = _money(gross_line - discount_amount)
            item_rows.append(
                {
                    "order_item_id": f"ITEM-{item_number:08d}",
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_amount": discount_amount,
                    "line_total": line_total,
                }
            )
            item_number += 1
            gross_subtotal += gross_line
            item_discount_total += discount_amount
            net_subtotal += line_total

        shipping_cost = 0.0 if net_subtotal >= 100 else _money(rng.uniform(4.99, 12.99))
        tax_rate = float(rng.choice([0.0, 0.05, 0.06, 0.07, 0.08]))
        tax_amount = _money(net_subtotal * tax_rate)
        order_total = _money(net_subtotal + shipping_cost + tax_amount)
        order_rows.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date.date().isoformat(),
                "order_status": status,
                "shipping_city": customer["city"],
                "shipping_state": customer["state"],
                "shipping_country": customer["country"],
                "shipping_cost": shipping_cost,
                "discount_amount": _money(item_discount_total),
                "tax_amount": tax_amount,
                "order_total": order_total,
            }
        )

    return pd.DataFrame(order_rows), pd.DataFrame(item_rows)


def generate_payments(orders: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Create one status-aware payment record for every order."""
    rows: list[dict[str, object]] = []
    for index, order in enumerate(orders.to_dict("records"), start=1):
        status = str(order["order_status"])
        if status == "Cancelled":
            payment_status = str(
                rng.choice(["Failed", "Cancelled", "Refunded"], p=[0.45, 0.35, 0.20])
            )
        elif status == "Returned":
            payment_status = str(rng.choice(["Refunded", "Successful"], p=[0.88, 0.12]))
        else:
            payment_status = str(rng.choice(["Successful", "Pending"], p=[0.97, 0.03]))
        payment_date = pd.Timestamp(order["order_date"]) + pd.Timedelta(
            days=int(rng.integers(0, 3))
        )
        rows.append(
            {
                "payment_id": f"PAY-{index:07d}",
                "order_id": order["order_id"],
                "payment_date": payment_date.date().isoformat(),
                "payment_method": rng.choice(
                    [
                        "Credit Card",
                        "Debit Card",
                        "PayPal",
                        "Digital Wallet",
                        "Gift Card",
                    ],
                    p=[0.43, 0.23, 0.16, 0.14, 0.04],
                ),
                "payment_status": payment_status,
                "amount": float(order["order_total"]),
            }
        )
    return pd.DataFrame(rows)


def generate_reviews(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create reviews only for products actually bought in fulfilled orders."""
    eligible = orders[orders["order_status"].isin(["Delivered", "Returned"])]
    eligible = eligible[rng.random(len(eligible)) < 0.38]
    item_groups = order_items.groupby("order_id")
    titles = {
        1: "Disappointed",
        2: "Could be better",
        3: "Good overall",
        4: "Very pleased",
        5: "Excellent purchase",
    }
    texts = {
        1: "The product did not meet my expectations.",
        2: "It works, but the quality could be improved.",
        3: "A solid product that does what it promises.",
        4: "Good quality and I would recommend it.",
        5: "Great quality, easy to use, and worth the price.",
    }
    rows: list[dict[str, object]] = []
    review_number = 1
    for order in eligible.to_dict("records"):
        purchased_items = item_groups.get_group(order["order_id"])
        reviewed_item = purchased_items.iloc[int(rng.integers(len(purchased_items)))]
        rating = int(rng.choice([1, 2, 3, 4, 5], p=[0.03, 0.07, 0.18, 0.34, 0.38]))
        review_date = pd.Timestamp(order["order_date"]) + pd.Timedelta(
            days=int(rng.integers(3, 46))
        )
        rows.append(
            {
                "review_id": f"REV-{review_number:07d}",
                "order_id": order["order_id"],
                "product_id": reviewed_item["product_id"],
                "customer_id": order["customer_id"],
                "rating": rating,
                "review_title": titles[rating],
                "review_text": texts[rating],
                "review_date": review_date.date().isoformat(),
            }
        )
        review_number += 1

    # A one-order test run can randomly have no eligible review. Guarantee the
    # documented dataset is still non-empty by reviewing its purchased product.
    if not rows:
        order = orders.iloc[0]
        item = order_items[order_items["order_id"] == order["order_id"]].iloc[0]
        review_date = pd.Timestamp(order["order_date"]) + pd.Timedelta(days=3)
        rows.append(
            {
                "review_id": "REV-0000001",
                "order_id": order["order_id"],
                "product_id": item["product_id"],
                "customer_id": order["customer_id"],
                "rating": 4,
                "review_title": titles[4],
                "review_text": texts[4],
                "review_date": review_date.date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def generate_inventory(
    products: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """Create non-negative stock positions across three warehouses."""
    rows: list[dict[str, object]] = []
    inventory_number = 1
    warehouses = np.array(["WH-EAST", "WH-CENTRAL", "WH-WEST"])
    for product_id in products["product_id"]:
        warehouse_count = int(rng.choice([1, 2, 3], p=[0.20, 0.50, 0.30]))
        selected = rng.choice(warehouses, size=warehouse_count, replace=False)
        for warehouse_id in selected:
            rows.append(
                {
                    "inventory_id": f"INV-{inventory_number:07d}",
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "stock_quantity": int(rng.integers(0, 501)),
                    "reorder_level": int(rng.integers(10, 81)),
                    "last_updated": DATA_END_DATE.isoformat(),
                }
            )
            inventory_number += 1
    return pd.DataFrame(rows)


def generate_marketing_campaigns(
    order_count: int, rng: np.random.Generator
) -> pd.DataFrame:
    """Create campaigns whose funnel metrics decrease at every stage."""
    campaign_count = max(6, min(30, round(order_count / 300)))
    channels = ["Email", "Paid Search", "Social Media", "Affiliate", "Display"]
    segments = ["All Customers", "New", "Regular", "Loyal", "VIP"]
    rows: list[dict[str, object]] = []
    starts = _random_dates(
        rng,
        pd.Timestamp("2023-01-01"),
        DATA_END_DATE - pd.Timedelta(days=45),
        campaign_count,
    )
    for index, start_date in enumerate(starts, start=1):
        channel = str(rng.choice(channels))
        impressions = int(rng.integers(10_000, 500_001))
        clicks = int(round(impressions * rng.uniform(0.008, 0.09)))
        conversions = int(round(clicks * rng.uniform(0.01, 0.18)))
        duration = int(rng.integers(14, 46))
        rows.append(
            {
                "campaign_id": f"CAMP-{index:04d}",
                "campaign_name": f"{start_date.year} {channel} Campaign {index}",
                "channel": channel,
                "start_date": start_date.date().isoformat(),
                "end_date": (start_date + pd.Timedelta(days=duration))
                .date()
                .isoformat(),
                "budget": _money(rng.uniform(2_500, 80_000)),
                "target_segment": rng.choice(segments),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
            }
        )
    return pd.DataFrame(rows)


def generate_clickstream_events(
    session_count: int,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create anonymous and known sessions with ordered browsing funnels."""
    customer_ids = customers["customer_id"].to_numpy()
    product_ids = products["product_id"].to_numpy()
    rows: list[dict[str, object]] = []
    event_number = 1
    funnel_sequences = (
        (["page_view"], 0.15),
        (["page_view", "product_view"], 0.25),
        (["page_view", "product_view", "add_to_cart"], 0.23),
        (["page_view", "product_view", "add_to_cart", "begin_checkout"], 0.17),
        (
            [
                "page_view",
                "product_view",
                "add_to_cart",
                "begin_checkout",
                "purchase",
            ],
            0.20,
        ),
    )
    probabilities = [entry[1] for entry in funnel_sequences]
    start_times = pd.date_range("2025-01-01", DATA_END_DATE, freq="min")

    for session_number in range(1, session_count + 1):
        anonymous = bool(rng.random() < 0.32)
        customer_id = None if anonymous else str(rng.choice(customer_ids))
        product_id = str(rng.choice(product_ids))
        sequence_index = int(rng.choice(len(funnel_sequences), p=probabilities))
        sequence = funnel_sequences[sequence_index][0]
        timestamp = start_times[int(rng.integers(len(start_times)))]
        device = rng.choice(["Desktop", "Mobile", "Tablet"], p=[0.38, 0.55, 0.07])
        source = rng.choice(
            [
                "Organic Search",
                "Paid Search",
                "Social Media",
                "Email",
                "Direct",
                "Referral",
            ],
            p=[0.25, 0.18, 0.18, 0.10, 0.21, 0.08],
        )
        session_id = f"SESS-{session_number:08d}"
        for event_type in sequence:
            page_type = {
                "page_view": "home",
                "product_view": "product_detail",
                "add_to_cart": "cart",
                "begin_checkout": "checkout",
                "purchase": "confirmation",
            }[event_type]
            event_product_id = (
                product_id
                if event_type in {"product_view", "add_to_cart", "purchase"}
                else None
            )
            rows.append(
                {
                    "event_id": f"EVT-{event_number:09d}",
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "event_timestamp": timestamp.isoformat(),
                    "event_type": event_type,
                    "page_type": page_type,
                    "product_id": event_product_id,
                    "device_type": device,
                    "traffic_source": source,
                }
            )
            event_number += 1
            timestamp += pd.Timedelta(seconds=int(rng.integers(8, 181)))
    return pd.DataFrame(rows)


def generate_datasets(config: GenerationConfig) -> dict[str, pd.DataFrame]:
    """Generate all nine related datasets in memory."""
    config.validate()
    rng = np.random.default_rng(config.seed)
    customers = generate_customers(config.customers, rng)
    products = generate_products(config.products, rng)
    orders, order_items = generate_orders_and_items(
        config.orders, customers, products, rng
    )
    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": generate_payments(orders, rng),
        "reviews": generate_reviews(orders, order_items, rng),
        "inventory": generate_inventory(products, rng),
        "marketing_campaigns": generate_marketing_campaigns(config.orders, rng),
        "clickstream_events": generate_clickstream_events(
            config.clickstream_sessions, customers, products, rng
        ),
    }


def write_datasets(datasets: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    """Write generated dataframes to CSV and return their file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name in DATASET_NAMES:
        path = output_dir / f"{name}.csv"
        datasets[name].to_csv(path, index=False, lineterminator="\n")
        paths.append(path)
    return paths


def run_generation(config: GenerationConfig) -> dict[str, pd.DataFrame]:
    """Generate and save all datasets for use by the CLI and other Python code."""
    datasets = generate_datasets(config)
    write_datasets(datasets, config.output_dir)
    return datasets


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic e-commerce CSV datasets."
    )
    parser.add_argument("--customers", type=int, default=1_000)
    parser.add_argument("--products", type=int, default=200)
    parser.add_argument("--orders", type=int, default=5_000)
    parser.add_argument("--clickstream-sessions", type=int, default=3_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run data generation from command-line arguments."""
    args = build_parser().parse_args(argv)
    config = GenerationConfig(
        customers=args.customers,
        products=args.products,
        orders=args.orders,
        clickstream_sessions=args.clickstream_sessions,
        seed=args.seed,
        output_dir=args.output_dir,
    )
    try:
        datasets = run_generation(config)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(f"Generated datasets in {config.output_dir.resolve()}:")
    for name in DATASET_NAMES:
        print(f"  {name}.csv: {len(datasets[name]):,} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
