import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIR = BASE_DIR / "data" / "gold"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"

SHIPMENTS_SILVER_PATH = SILVER_DIR / "shipments_silver.csv"
WAREHOUSES_SILVER_PATH = SILVER_DIR / "warehouses_silver.csv"
SUPPLIERS_SILVER_PATH = SILVER_DIR / "suppliers_silver.csv"
DISTRIBUTION_POINTS_SILVER_PATH = SILVER_DIR / "distribution_points_silver.csv"
INVENTORY_SILVER_PATH = SILVER_DIR / "inventory_silver.csv"

BRONZE_SUMMARY_PATH = REPORTS_DIR / "bronze_validation_summary.json"
SILVER_SUMMARY_PATH = REPORTS_DIR / "silver_cleaning_summary.json"
SILVER_REJECTED_RECORDS_PATH = REPORTS_DIR / "silver_rejected_records.csv"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_silver_data():
    shipments = pd.read_csv(SHIPMENTS_SILVER_PATH)
    warehouses = pd.read_csv(WAREHOUSES_SILVER_PATH)
    suppliers = pd.read_csv(SUPPLIERS_SILVER_PATH)
    distribution_points = pd.read_csv(DISTRIBUTION_POINTS_SILVER_PATH)
    inventory = pd.read_csv(INVENTORY_SILVER_PATH)

    bronze_summary = load_json(BRONZE_SUMMARY_PATH)
    silver_summary = load_json(SILVER_SUMMARY_PATH)
    rejected_records = pd.read_csv(SILVER_REJECTED_RECORDS_PATH)

    return (
        shipments,
        warehouses,
        suppliers,
        distribution_points,
        inventory,
        bronze_summary,
        silver_summary,
        rejected_records,
    )


def create_shipment_status_summary(shipments):
    summary = (
        shipments.groupby("shipment_status", dropna=False)
        .agg(
            shipment_count=("shipment_id", "count"),
            total_quantity_shipped=("quantity_shipped", "sum"),
            delayed_shipments=("is_delayed", "sum"),
            average_delay_days=("delay_days", "mean"),
        )
        .reset_index()
    )

    summary["delayed_rate_percent"] = (
        summary["delayed_shipments"] / summary["shipment_count"] * 100
    ).round(2)

    summary["average_delay_days"] = summary["average_delay_days"].round(2)

    return summary


def create_supplier_performance(shipments, suppliers):
    supplier_df = shipments.merge(
        suppliers,
        on="supplier_id",
        how="left",
    )

    summary = (
        supplier_df.groupby(
            ["supplier_id", "supplier_name", "supplier_category", "country"],
            dropna=False,
        )
        .agg(
            shipment_count=("shipment_id", "count"),
            total_quantity_shipped=("quantity_shipped", "sum"),
            delayed_shipments=("is_delayed", "sum"),
            average_delay_days=("delay_days", "mean"),
        )
        .reset_index()
    )

    summary["delayed_rate_percent"] = (
        summary["delayed_shipments"] / summary["shipment_count"] * 100
    ).round(2)

    summary["average_delay_days"] = summary["average_delay_days"].round(2)

    summary = summary.sort_values(
        by=["delayed_rate_percent", "shipment_count"],
        ascending=[False, False],
    )

    return summary


def create_warehouse_inventory_summary(inventory, warehouses):
    inventory_df = inventory.merge(
        warehouses,
        on="warehouse_id",
        how="left",
    )

    summary = (
        inventory_df.groupby(
            [
                "warehouse_id",
                "warehouse_name",
                "country",
                "city",
                "warehouse_type",
            ],
            dropna=False,
        )
        .agg(
            item_count=("item_id", "nunique"),
            total_quantity_available=("quantity_available", "sum"),
        )
        .reset_index()
    )

    summary = summary.sort_values(
        by="total_quantity_available",
        ascending=False,
    )

    return summary


def create_distribution_point_summary(shipments, distribution_points):
    dp_df = shipments.merge(
        distribution_points,
        on="distribution_point_id",
        how="left",
    )

    summary = (
        dp_df.groupby(
            [
                "distribution_point_id",
                "distribution_point_name",
                "country",
                "city",
                "beneficiary_group",
            ],
            dropna=False,
        )
        .agg(
            shipment_count=("shipment_id", "count"),
            total_quantity_received=("quantity_shipped", "sum"),
            delayed_shipments=("is_delayed", "sum"),
            average_delay_days=("delay_days", "mean"),
        )
        .reset_index()
    )

    summary["delayed_rate_percent"] = (
        summary["delayed_shipments"] / summary["shipment_count"] * 100
    ).round(2)

    summary["average_delay_days"] = summary["average_delay_days"].round(2)

    return summary


def create_data_quality_summary(bronze_summary, silver_summary, rejected_records):
    rows = []

    bronze_issue_counts = bronze_summary.get("issue_type_counts", {})
    silver_rejection_counts = silver_summary.get("rejection_reason_counts", {})

    for issue_type, count in bronze_issue_counts.items():
        rows.append(
            {
                "stage": "bronze_validation",
                "metric_name": issue_type,
                "metric_value": count,
            }
        )

    for rejection_reason, count in silver_rejection_counts.items():
        rows.append(
            {
                "stage": "silver_rejection",
                "metric_name": rejection_reason,
                "metric_value": count,
            }
        )

    rows.append(
        {
            "stage": "silver_rejection",
            "metric_name": "rejected_unique_shipments",
            "metric_value": rejected_records["shipment_id"].nunique(),
        }
    )

    return pd.DataFrame(rows)


def create_kpi_summary(shipments, inventory, bronze_summary, silver_summary):
    total_shipments = len(shipments)
    delayed_shipments = int(shipments["is_delayed"].sum())

    delivered_shipments = int(
        (shipments["shipment_status"] == "Delivered").sum()
    )

    in_transit_shipments = int(
        (shipments["shipment_status"] == "In Transit").sum()
    )

    cancelled_shipments = int(
        (shipments["shipment_status"] == "Cancelled").sum()
    )

    delayed_status_shipments = int(
        (shipments["shipment_status"] == "Delayed").sum()
    )

    delayed_rate = 0

    if total_shipments > 0:
        delayed_rate = round(delayed_shipments / total_shipments * 100, 2)

    kpi = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_source_rows": bronze_summary["total_source_rows"],
        "silver_rows": silver_summary["silver_rows"],
        "rejected_unique_shipments": silver_summary["rejected_unique_shipments"],
        "rejected_issue_count": silver_summary["rejected_issue_count"],
        "total_shipments_in_gold": total_shipments,
        "delivered_shipments": delivered_shipments,
        "in_transit_shipments": in_transit_shipments,
        "cancelled_shipments": cancelled_shipments,
        "delayed_status_shipments": delayed_status_shipments,
        "delayed_by_date_shipments": delayed_shipments,
        "delayed_by_date_rate_percent": delayed_rate,
        "total_quantity_shipped": int(shipments["quantity_shipped"].sum()),
        "total_inventory_available": int(inventory["quantity_available"].sum()),
        "average_delay_days": round(shipments["delay_days"].mean(), 2),
    }

    return pd.DataFrame([kpi])


def create_reconciliation_report(bronze_summary, silver_summary, kpi_summary):
    source_rows = bronze_summary["total_source_rows"]
    silver_rows = silver_summary["silver_rows"]
    rejected_unique_shipments = silver_summary["rejected_unique_shipments"]

    row_balance_check = source_rows == silver_rows + rejected_unique_shipments

    report = {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline": "bronze_to_silver_to_gold",
        "source_rows": source_rows,
        "silver_rows": silver_rows,
        "gold_shipments": int(kpi_summary.loc[0, "total_shipments_in_gold"]),
        "rejected_unique_shipments": rejected_unique_shipments,
        "row_balance_check": row_balance_check,
        "row_balance_formula": (
            "source_rows should equal silver_rows + rejected_unique_shipments"
        ),
        "business_note": (
            "Delayed shipments are not rejected. They remain in Gold as KPI records."
        ),
    }

    return report


def save_gold_outputs(
    kpi_summary,
    shipment_status_summary,
    supplier_performance,
    warehouse_inventory_summary,
    distribution_point_summary,
    data_quality_summary,
    reconciliation_report,
):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    kpi_summary.to_csv(GOLD_DIR / "kpi_summary.csv", index=False)
    shipment_status_summary.to_csv(
        GOLD_DIR / "shipment_status_summary.csv",
        index=False,
    )
    supplier_performance.to_csv(
        GOLD_DIR / "supplier_performance.csv",
        index=False,
    )
    warehouse_inventory_summary.to_csv(
        GOLD_DIR / "warehouse_inventory_summary.csv",
        index=False,
    )
    distribution_point_summary.to_csv(
        GOLD_DIR / "distribution_point_summary.csv",
        index=False,
    )
    data_quality_summary.to_csv(
        GOLD_DIR / "data_quality_summary.csv",
        index=False,
    )

    with open(REPORTS_DIR / "reconciliation_report.json", "w") as f:
        json.dump(reconciliation_report, f, indent=2)


def main():
    (
        shipments,
        warehouses,
        suppliers,
        distribution_points,
        inventory,
        bronze_summary,
        silver_summary,
        rejected_records,
    ) = load_silver_data()

    shipment_status_summary = create_shipment_status_summary(shipments)
    supplier_performance = create_supplier_performance(shipments, suppliers)
    warehouse_inventory_summary = create_warehouse_inventory_summary(
        inventory,
        warehouses,
    )
    distribution_point_summary = create_distribution_point_summary(
        shipments,
        distribution_points,
    )
    data_quality_summary = create_data_quality_summary(
        bronze_summary,
        silver_summary,
        rejected_records,
    )
    kpi_summary = create_kpi_summary(
        shipments,
        inventory,
        bronze_summary,
        silver_summary,
    )

    reconciliation_report = create_reconciliation_report(
        bronze_summary,
        silver_summary,
        kpi_summary,
    )

    save_gold_outputs(
        kpi_summary=kpi_summary,
        shipment_status_summary=shipment_status_summary,
        supplier_performance=supplier_performance,
        warehouse_inventory_summary=warehouse_inventory_summary,
        distribution_point_summary=distribution_point_summary,
        data_quality_summary=data_quality_summary,
        reconciliation_report=reconciliation_report,
    )

    print("Gold layer created successfully.")
    print()
    print("Gold tables created:")
    print(f"- {GOLD_DIR / 'kpi_summary.csv'}")
    print(f"- {GOLD_DIR / 'shipment_status_summary.csv'}")
    print(f"- {GOLD_DIR / 'supplier_performance.csv'}")
    print(f"- {GOLD_DIR / 'warehouse_inventory_summary.csv'}")
    print(f"- {GOLD_DIR / 'distribution_point_summary.csv'}")
    print(f"- {GOLD_DIR / 'data_quality_summary.csv'}")
    print()
    print("Reconciliation report:")
    print(f"- {REPORTS_DIR / 'reconciliation_report.json'}")
    print()
    print("Key checks:")
    print(
        "Row balance check: "
        f"{reconciliation_report['row_balance_check']}"
    )
    print(
        "Formula: source_rows = silver_rows + rejected_unique_shipments"
    )
    print(
        f"{reconciliation_report['source_rows']} = "
        f"{reconciliation_report['silver_rows']} + "
        f"{reconciliation_report['rejected_unique_shipments']}"
    )


if __name__ == "__main__":
    main()