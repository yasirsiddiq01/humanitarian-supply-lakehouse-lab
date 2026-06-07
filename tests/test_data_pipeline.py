import pandas as pd

from scripts.validate_bronze_data import validate_schema, validate_shipments
from scripts.create_silver_layer import clean_shipments
from scripts.create_gold_layer import create_shipment_status_summary


def sample_master_data():
    warehouses = pd.DataFrame(
        [
            {
                "warehouse_id": "WH001",
                "warehouse_name": "Central Warehouse",
            }
        ]
    )

    suppliers = pd.DataFrame(
        [
            {
                "supplier_id": "SUP001",
                "supplier_name": "Health Supplier",
            }
        ]
    )

    distribution_points = pd.DataFrame(
        [
            {
                "distribution_point_id": "DP001",
                "distribution_point_name": "Health Centre",
            }
        ]
    )

    return warehouses, suppliers, distribution_points


def valid_shipment_row(shipment_id="SHP001"):
    return {
        "shipment_id": shipment_id,
        "supplier_id": "SUP001",
        "source_warehouse_id": "WH001",
        "distribution_point_id": "DP001",
        "item_id": "ITEM001",
        "item_name": "Vaccines",
        "item_category": "Medical",
        "quantity_shipped": 100,
        "shipment_status": "Delivered",
        "planned_ship_date": "2026-01-01",
        "planned_delivery_date": "2026-01-05",
        "actual_delivery_date": "2026-01-04",
        "transport_mode": "Air",
    }


def test_validate_schema_detects_missing_column():
    shipments = pd.DataFrame(
        [
            {
                "shipment_id": "SHP001",
                "supplier_id": "SUP001",
            }
        ]
    )

    missing_columns = validate_schema(shipments)

    assert "source_warehouse_id" in missing_columns
    assert "quantity_shipped" in missing_columns


def test_bronze_validation_detects_missing_mandatory_field():
    warehouses, suppliers, distribution_points = sample_master_data()

    row = valid_shipment_row()
    row["supplier_id"] = None

    shipments = pd.DataFrame([row])

    issue_df = validate_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    assert "missing_mandatory_field" in issue_df["issue_type"].tolist()


def test_bronze_validation_detects_invalid_warehouse_reference():
    warehouses, suppliers, distribution_points = sample_master_data()

    row = valid_shipment_row()
    row["source_warehouse_id"] = "WH999"

    shipments = pd.DataFrame([row])

    issue_df = validate_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    assert "invalid_warehouse_reference" in issue_df["issue_type"].tolist()


def test_silver_pipeline_rejects_negative_quantity():
    warehouses, suppliers, distribution_points = sample_master_data()

    row = valid_shipment_row()
    row["quantity_shipped"] = -10

    shipments = pd.DataFrame([row])

    silver_shipments, rejected_records = clean_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    assert len(silver_shipments) == 0
    assert "invalid_quantity" in rejected_records["rejection_reason"].tolist()


def test_silver_pipeline_keeps_delayed_shipments_as_business_kpi():
    warehouses, suppliers, distribution_points = sample_master_data()

    row = valid_shipment_row()
    row["planned_delivery_date"] = "2026-01-05"
    row["actual_delivery_date"] = "2026-01-08"

    shipments = pd.DataFrame([row])

    silver_shipments, rejected_records = clean_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    assert len(silver_shipments) == 1
    assert len(rejected_records) == 0
    assert silver_shipments.iloc[0]["delay_days"] == 3
    assert bool(silver_shipments.iloc[0]["is_delayed"]) is True


def test_silver_pipeline_rejects_later_duplicate_shipment_id():
    warehouses, suppliers, distribution_points = sample_master_data()

    first_row = valid_shipment_row("SHP001")
    duplicate_row = valid_shipment_row("SHP001")
    duplicate_row["quantity_shipped"] = 200

    shipments = pd.DataFrame([first_row, duplicate_row])

    silver_shipments, rejected_records = clean_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    assert len(silver_shipments) == 1
    assert len(rejected_records) == 1
    assert "duplicate_shipment_id" in rejected_records["rejection_reason"].tolist()


def test_gold_status_summary_calculates_delay_rate():
    shipments = pd.DataFrame(
        [
            {
                "shipment_id": "SHP001",
                "shipment_status": "Delivered",
                "quantity_shipped": 100,
                "is_delayed": True,
                "delay_days": 3,
            },
            {
                "shipment_id": "SHP002",
                "shipment_status": "Delivered",
                "quantity_shipped": 200,
                "is_delayed": False,
                "delay_days": 0,
            },
        ]
    )

    summary = create_shipment_status_summary(shipments)

    delivered_row = summary[summary["shipment_status"] == "Delivered"].iloc[0]

    assert delivered_row["shipment_count"] == 2
    assert delivered_row["total_quantity_shipped"] == 300
    assert delivered_row["delayed_shipments"] == 1
    assert delivered_row["delayed_rate_percent"] == 50.0