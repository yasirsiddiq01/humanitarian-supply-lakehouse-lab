import json
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd


RANDOM_SEED = 42
random.seed(RANDOM_SEED)


BASE_DIR = Path(__file__).resolve().parents[1]
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def make_dirs():
    folders = [
        BRONZE_DIR / "shipments",
        BRONZE_DIR / "warehouses",
        BRONZE_DIR / "inventory",
        BRONZE_DIR / "suppliers",
        BRONZE_DIR / "distribution_points",
        BRONZE_DIR / "_metadata",
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


def generate_warehouses():
    warehouses = [
        {
            "warehouse_id": "WH001",
            "warehouse_name": "Central Medical Warehouse",
            "country": "Kenya",
            "city": "Nairobi",
            "warehouse_type": "Central",
        },
        {
            "warehouse_id": "WH002",
            "warehouse_name": "Regional Food Storage",
            "country": "Uganda",
            "city": "Kampala",
            "warehouse_type": "Regional",
        },
        {
            "warehouse_id": "WH003",
            "warehouse_name": "Emergency Relief Hub",
            "country": "Ethiopia",
            "city": "Addis Ababa",
            "warehouse_type": "Emergency",
        },
        {
            "warehouse_id": "WH004",
            "warehouse_name": "Coastal Distribution Warehouse",
            "country": "Tanzania",
            "city": "Dar es Salaam",
            "warehouse_type": "Regional",
        },
        {
            "warehouse_id": "WH005",
            "warehouse_name": "Northern Field Warehouse",
            "country": "South Sudan",
            "city": "Juba",
            "warehouse_type": "Field",
        },
    ]

    return pd.DataFrame(warehouses)


def generate_suppliers():
    suppliers = [
        {
            "supplier_id": "SUP001",
            "supplier_name": "Global Health Supplies",
            "supplier_category": "Medical",
            "country": "Germany",
        },
        {
            "supplier_id": "SUP002",
            "supplier_name": "NutriAid Logistics",
            "supplier_category": "Nutrition",
            "country": "Netherlands",
        },
        {
            "supplier_id": "SUP003",
            "supplier_name": "ShelterPack International",
            "supplier_category": "Shelter",
            "country": "Turkey",
        },
        {
            "supplier_id": "SUP004",
            "supplier_name": "WaterSafe Systems",
            "supplier_category": "WASH",
            "country": "Spain",
        },
        {
            "supplier_id": "SUP005",
            "supplier_name": "EduKit Relief",
            "supplier_category": "Education",
            "country": "United Kingdom",
        },
    ]

    return pd.DataFrame(suppliers)


def generate_distribution_points():
    points = [
        {
            "distribution_point_id": "DP001",
            "distribution_point_name": "Nairobi Child Health Centre",
            "country": "Kenya",
            "city": "Nairobi",
            "beneficiary_group": "Children under 5",
        },
        {
            "distribution_point_id": "DP002",
            "distribution_point_name": "Kampala Nutrition Site",
            "country": "Uganda",
            "city": "Kampala",
            "beneficiary_group": "Pregnant women",
        },
        {
            "distribution_point_id": "DP003",
            "distribution_point_name": "Addis Emergency Camp",
            "country": "Ethiopia",
            "city": "Addis Ababa",
            "beneficiary_group": "Displaced families",
        },
        {
            "distribution_point_id": "DP004",
            "distribution_point_name": "Dar es Salaam WASH Centre",
            "country": "Tanzania",
            "city": "Dar es Salaam",
            "beneficiary_group": "School children",
        },
        {
            "distribution_point_id": "DP005",
            "distribution_point_name": "Juba Field Clinic",
            "country": "South Sudan",
            "city": "Juba",
            "beneficiary_group": "Emergency patients",
        },
    ]

    return pd.DataFrame(points)


def generate_inventory(warehouses):
    item_catalog = [
        ("ITEM001", "Vaccines", "Medical"),
        ("ITEM002", "Therapeutic Food Packs", "Nutrition"),
        ("ITEM003", "Water Purification Tablets", "WASH"),
        ("ITEM004", "Emergency Shelter Kits", "Shelter"),
        ("ITEM005", "School-in-a-Box Kits", "Education"),
    ]

    rows = []

    for _, warehouse in warehouses.iterrows():
        for item_id, item_name, item_category in item_catalog:
            rows.append(
                {
                    "inventory_id": f"INV-{warehouse['warehouse_id']}-{item_id}",
                    "warehouse_id": warehouse["warehouse_id"],
                    "item_id": item_id,
                    "item_name": item_name,
                    "item_category": item_category,
                    "quantity_available": random.randint(500, 5000),
                    "last_stock_update": "2026-06-01",
                }
            )

    return pd.DataFrame(rows)


def generate_shipments(n=120):
    warehouse_ids = ["WH001", "WH002", "WH003", "WH004", "WH005"]
    supplier_ids = ["SUP001", "SUP002", "SUP003", "SUP004", "SUP005"]
    distribution_point_ids = ["DP001", "DP002", "DP003", "DP004", "DP005"]

    items = [
        ("ITEM001", "Vaccines", "Medical"),
        ("ITEM002", "Therapeutic Food Packs", "Nutrition"),
        ("ITEM003", "Water Purification Tablets", "WASH"),
        ("ITEM004", "Emergency Shelter Kits", "Shelter"),
        ("ITEM005", "School-in-a-Box Kits", "Education"),
    ]

    statuses = ["Delivered", "In Transit", "Delayed", "Cancelled"]

    rows = []
    start_date = datetime(2026, 1, 1)

    for i in range(1, n + 1):
        item_id, item_name, item_category = random.choice(items)

        planned_ship_date = start_date + timedelta(days=random.randint(0, 120))
        planned_delivery_date = planned_ship_date + timedelta(days=random.randint(3, 20))

        status = random.choices(
            statuses,
            weights=[0.55, 0.25, 0.15, 0.05],
            k=1,
        )[0]

        if status == "Delivered":
            actual_delivery_date = planned_delivery_date + timedelta(days=random.randint(-2, 4))
        elif status == "Delayed":
            actual_delivery_date = planned_delivery_date + timedelta(days=random.randint(5, 18))
        elif status == "In Transit":
            actual_delivery_date = None
        else:
            actual_delivery_date = None

        rows.append(
            {
                "shipment_id": f"SHP{i:04d}",
                "supplier_id": random.choice(supplier_ids),
                "source_warehouse_id": random.choice(warehouse_ids),
                "distribution_point_id": random.choice(distribution_point_ids),
                "item_id": item_id,
                "item_name": item_name,
                "item_category": item_category,
                "quantity_shipped": random.randint(10, 1000),
                "shipment_status": status,
                "planned_ship_date": planned_ship_date.strftime("%Y-%m-%d"),
                "planned_delivery_date": planned_delivery_date.strftime("%Y-%m-%d"),
                "actual_delivery_date": (
                    actual_delivery_date.strftime("%Y-%m-%d")
                    if actual_delivery_date is not None
                    else None
                ),
                "transport_mode": random.choice(["Air", "Road", "Sea"]),
            }
        )

    df = pd.DataFrame(rows)

    # Intentional data-quality issues for testing later.
    issue_rows = [
        # Missing mandatory field: supplier_id
        {
            "shipment_id": "SHP_MISSING_SUPPLIER",
            "supplier_id": None,
            "source_warehouse_id": "WH001",
            "distribution_point_id": "DP001",
            "item_id": "ITEM001",
            "item_name": "Vaccines",
            "item_category": "Medical",
            "quantity_shipped": 300,
            "shipment_status": "Delivered",
            "planned_ship_date": "2026-02-01",
            "planned_delivery_date": "2026-02-08",
            "actual_delivery_date": "2026-02-07",
            "transport_mode": "Air",
        },
        # Unknown warehouse ID
        {
            "shipment_id": "SHP_UNKNOWN_WAREHOUSE",
            "supplier_id": "SUP001",
            "source_warehouse_id": "WH999",
            "distribution_point_id": "DP001",
            "item_id": "ITEM002",
            "item_name": "Therapeutic Food Packs",
            "item_category": "Nutrition",
            "quantity_shipped": 500,
            "shipment_status": "In Transit",
            "planned_ship_date": "2026-03-01",
            "planned_delivery_date": "2026-03-10",
            "actual_delivery_date": None,
            "transport_mode": "Road",
        },
        # Invalid date: delivery before shipment
        {
            "shipment_id": "SHP_INVALID_DATE",
            "supplier_id": "SUP002",
            "source_warehouse_id": "WH002",
            "distribution_point_id": "DP002",
            "item_id": "ITEM003",
            "item_name": "Water Purification Tablets",
            "item_category": "WASH",
            "quantity_shipped": 700,
            "shipment_status": "Delivered",
            "planned_ship_date": "2026-04-15",
            "planned_delivery_date": "2026-04-10",
            "actual_delivery_date": "2026-04-09",
            "transport_mode": "Road",
        },
        # Negative quantity
        {
            "shipment_id": "SHP_NEGATIVE_QTY",
            "supplier_id": "SUP003",
            "source_warehouse_id": "WH003",
            "distribution_point_id": "DP003",
            "item_id": "ITEM004",
            "item_name": "Emergency Shelter Kits",
            "item_category": "Shelter",
            "quantity_shipped": -50,
            "shipment_status": "Delivered",
            "planned_ship_date": "2026-05-01",
            "planned_delivery_date": "2026-05-12",
            "actual_delivery_date": "2026-05-15",
            "transport_mode": "Sea",
        },
        # Unknown distribution point
        {
            "shipment_id": "SHP_UNKNOWN_DP",
            "supplier_id": "SUP004",
            "source_warehouse_id": "WH004",
            "distribution_point_id": "DP999",
            "item_id": "ITEM005",
            "item_name": "School-in-a-Box Kits",
            "item_category": "Education",
            "quantity_shipped": 250,
            "shipment_status": "Delayed",
            "planned_ship_date": "2026-05-03",
            "planned_delivery_date": "2026-05-10",
            "actual_delivery_date": "2026-05-25",
            "transport_mode": "Road",
        },
    ]

    df = pd.concat([df, pd.DataFrame(issue_rows)], ignore_index=True)

    # Duplicate record: duplicate an existing shipment_id
    duplicate_row = df.iloc[10].copy()
    duplicate_row["quantity_shipped"] = 999
    df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)

    return df


def save_outputs():
    make_dirs()

    warehouses = generate_warehouses()
    suppliers = generate_suppliers()
    distribution_points = generate_distribution_points()
    inventory = generate_inventory(warehouses)
    shipments = generate_shipments(n=120)

    warehouses.to_csv(BRONZE_DIR / "warehouses" / "warehouses_raw.csv", index=False)
    suppliers.to_csv(BRONZE_DIR / "suppliers" / "suppliers_raw.csv", index=False)
    distribution_points.to_csv(
        BRONZE_DIR / "distribution_points" / "distribution_points_raw.csv",
        index=False,
    )
    inventory.to_csv(BRONZE_DIR / "inventory" / "inventory_raw.csv", index=False)

    shipments.to_csv(BRONZE_DIR / "shipments" / "shipments_raw.csv", index=False)
    shipments.to_json(
        BRONZE_DIR / "shipments" / "shipments_raw.json",
        orient="records",
        indent=2,
    )

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "random_seed": RANDOM_SEED,
        "files_created": {
            "warehouses": "data/bronze/warehouses/warehouses_raw.csv",
            "suppliers": "data/bronze/suppliers/suppliers_raw.csv",
            "distribution_points": "data/bronze/distribution_points/distribution_points_raw.csv",
            "inventory": "data/bronze/inventory/inventory_raw.csv",
            "shipments_csv": "data/bronze/shipments/shipments_raw.csv",
            "shipments_json": "data/bronze/shipments/shipments_raw.json",
        },
        "row_counts": {
            "warehouses": len(warehouses),
            "suppliers": len(suppliers),
            "distribution_points": len(distribution_points),
            "inventory": len(inventory),
            "shipments": len(shipments),
        },
        "intentional_data_quality_issues": [
            "missing supplier_id",
            "duplicate shipment_id",
            "unknown source_warehouse_id",
            "unknown distribution_point_id",
            "planned delivery date before planned ship date",
            "actual delivery date before planned ship date",
            "negative quantity_shipped",
            "delayed shipments",
        ],
    }

    with open(BRONZE_DIR / "_metadata" / "raw_generation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Synthetic humanitarian supply-chain data generated successfully.")
    print()
    print("Row counts:")
    for name, count in summary["row_counts"].items():
        print(f"- {name}: {count}")

    print()
    print("Bronze files created under:")
    print(BRONZE_DIR)


if __name__ == "__main__":
    save_outputs()