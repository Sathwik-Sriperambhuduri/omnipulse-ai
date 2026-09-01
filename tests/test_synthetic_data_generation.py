"""Fast integrity tests for the Phase 2 synthetic e-commerce data."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.ingestion.generate_synthetic_data import (
    DATASET_NAMES,
    GenerationConfig,
    run_generation,
)

REQUIRED_COLUMNS = {
    "customers": {
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "gender",
        "date_of_birth",
        "signup_date",
        "city",
        "state",
        "country",
        "postal_code",
        "customer_segment",
        "acquisition_channel",
    },
    "products": {
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "brand",
        "unit_price",
        "cost_price",
        "launch_date",
        "is_active",
    },
    "orders": {
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "shipping_city",
        "shipping_state",
        "shipping_country",
        "shipping_cost",
        "discount_amount",
        "tax_amount",
        "order_total",
    },
    "order_items": {
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_amount",
        "line_total",
    },
    "payments": {
        "payment_id",
        "order_id",
        "payment_date",
        "payment_method",
        "payment_status",
        "amount",
    },
    "reviews": {
        "review_id",
        "order_id",
        "product_id",
        "customer_id",
        "rating",
        "review_title",
        "review_text",
        "review_date",
    },
    "inventory": {
        "inventory_id",
        "product_id",
        "warehouse_id",
        "stock_quantity",
        "reorder_level",
        "last_updated",
    },
    "marketing_campaigns": {
        "campaign_id",
        "campaign_name",
        "channel",
        "start_date",
        "end_date",
        "budget",
        "target_segment",
        "impressions",
        "clicks",
        "conversions",
    },
    "clickstream_events": {
        "event_id",
        "session_id",
        "customer_id",
        "event_timestamp",
        "event_type",
        "page_type",
        "product_id",
        "device_type",
        "traffic_source",
    },
}

PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "reviews": "review_id",
    "inventory": "inventory_id",
    "marketing_campaigns": "campaign_id",
    "clickstream_events": "event_id",
}


@pytest.fixture(scope="module")
def datasets(tmp_path_factory: pytest.TempPathFactory) -> dict[str, pd.DataFrame]:
    """Generate one small dataset shared by all tests in this module."""
    output_dir = tmp_path_factory.mktemp("synthetic-data")
    return run_generation(
        GenerationConfig(
            customers=30,
            products=20,
            orders=80,
            clickstream_sessions=40,
            seed=123,
            output_dir=output_dir,
        )
    )


def test_expected_non_empty_csv_datasets_are_generated(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """All nine expected dataframes should exist and contain rows."""
    assert set(datasets) == set(DATASET_NAMES)
    assert all(not dataframe.empty for dataframe in datasets.values())


def test_expected_csv_files_are_written(tmp_path: Path) -> None:
    """The public workflow should save exactly the documented CSV names."""
    run_generation(GenerationConfig(5, 5, 8, 5, seed=9, output_dir=tmp_path))
    assert {path.name for path in tmp_path.glob("*.csv")} == {
        f"{name}.csv" for name in DATASET_NAMES
    }


def test_required_columns_exist(datasets: dict[str, pd.DataFrame]) -> None:
    """Every dataset should expose its documented schema."""
    for name, required in REQUIRED_COLUMNS.items():
        assert required.issubset(datasets[name].columns), name


def test_primary_ids_are_unique_and_present(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Primary keys should never be duplicated or null."""
    for name, key in PRIMARY_KEYS.items():
        assert datasets[name][key].notna().all(), name
        assert datasets[name][key].is_unique, name


def test_transactional_foreign_keys_are_valid(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Orders, items, and payments should reference existing parent records."""
    customers = set(datasets["customers"]["customer_id"])
    products = set(datasets["products"]["product_id"])
    orders = set(datasets["orders"]["order_id"])
    assert set(datasets["orders"]["customer_id"]) <= customers
    assert set(datasets["order_items"]["order_id"]) <= orders
    assert set(datasets["order_items"]["product_id"]) <= products
    assert set(datasets["payments"]["order_id"]) <= orders


def test_review_foreign_keys_are_valid(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Reviews should point to valid orders, customers, and products."""
    reviews = datasets["reviews"]
    assert set(reviews["order_id"]) <= set(datasets["orders"]["order_id"])
    assert set(reviews["customer_id"]) <= set(datasets["customers"]["customer_id"])
    assert set(reviews["product_id"]) <= set(datasets["products"]["product_id"])


def test_inventory_references_products_and_is_non_negative(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Every stock record should have a product and a valid quantity."""
    assert set(datasets["inventory"]["product_id"]) <= set(
        datasets["products"]["product_id"]
    )
    assert (datasets["inventory"]["stock_quantity"] >= 0).all()


def test_nullable_clickstream_foreign_keys_are_valid(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Known clickstream IDs should resolve while anonymous values may be null."""
    events = datasets["clickstream_events"]
    assert set(events["customer_id"].dropna()) <= set(
        datasets["customers"]["customer_id"]
    )
    assert set(events["product_id"].dropna()) <= set(datasets["products"]["product_id"])
    assert events["customer_id"].isna().any()


def test_product_cost_does_not_exceed_retail_price(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Normal catalog products should have a positive gross margin."""
    products = datasets["products"]
    assert (products["cost_price"] <= products["unit_price"]).all()


def test_marketing_funnel_metrics_are_logical(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """A later funnel stage cannot contain more people than an earlier one."""
    campaigns = datasets["marketing_campaigns"]
    assert (campaigns["clicks"] <= campaigns["impressions"]).all()
    assert (campaigns["conversions"] <= campaigns["clicks"]).all()


def test_review_dates_are_not_before_order_dates(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """A customer cannot review an order before placing it."""
    reviews = datasets["reviews"].merge(
        datasets["orders"][["order_id", "order_date"]], on="order_id"
    )
    assert (
        pd.to_datetime(reviews["review_date"]) >= pd.to_datetime(reviews["order_date"])
    ).all()


def test_order_dates_are_not_before_customer_signup(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Orders should occur on or after the customer's signup date."""
    orders = datasets["orders"].merge(
        datasets["customers"][["customer_id", "signup_date"]], on="customer_id"
    )
    assert (
        pd.to_datetime(orders["order_date"]) >= pd.to_datetime(orders["signup_date"])
    ).all()


def test_products_are_not_ordered_before_launch(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Every item should have been available by the date of its order."""
    items = datasets["order_items"].merge(
        datasets["orders"][["order_id", "order_date"]], on="order_id"
    )
    items = items.merge(
        datasets["products"][["product_id", "launch_date"]], on="product_id"
    )
    assert (
        pd.to_datetime(items["order_date"]) >= pd.to_datetime(items["launch_date"])
    ).all()


def test_order_totals_are_internally_consistent(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """Line values, discounts, tax, shipping, and final totals should reconcile."""
    items = datasets["order_items"].copy()
    expected_lines = items["quantity"] * items["unit_price"] - items["discount_amount"]
    assert np.allclose(items["line_total"], expected_lines, atol=0.01)

    item_totals = items.groupby("order_id").agg(
        item_total=("line_total", "sum"),
        item_discount=("discount_amount", "sum"),
    )
    orders = datasets["orders"].set_index("order_id").join(item_totals)
    expected_orders = (
        orders["item_total"] + orders["shipping_cost"] + orders["tax_amount"]
    )
    assert np.allclose(orders["order_total"], expected_orders, atol=0.01)
    assert np.allclose(orders["discount_amount"], orders["item_discount"], atol=0.01)


def test_same_seed_is_reproducible(tmp_path: Path) -> None:
    """Two in-memory runs with the same configuration should be identical."""
    config = GenerationConfig(4, 4, 5, 3, seed=77, output_dir=tmp_path)
    first = run_generation(config)
    second = run_generation(config)
    for name in DATASET_NAMES:
        pd.testing.assert_frame_equal(first[name], second[name])
