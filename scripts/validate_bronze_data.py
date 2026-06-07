import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

BRONZE_DIR = BASE_DIR / "data" / "bronze"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"

SHIPMENTS_PATH = BRONZE_DIR / "shipments" / "shipments_raw.csv"
WAREHOUSES_PATH = BRONZE_DIR / "warehouses" / "warehouses_raw.csv"
SUPPLIERS_PATH = BRONZE_DIR / "suppliers" / "suppliers_raw.csv"
DISTRIBUTION_POINTS_PATH = (
    BRONZE_DIR / "distribution_points" / "distribution_points_raw.csv"
)


MANDATORY_SHIPMENT_FIELDS = [
    "shipment_id",
    "supplier_id",
    "source_warehouse_id",
    "distribution_point_id",
    "item_id",
    "quantity_shipped",
    "shipment_status",
    "planned_ship_date",
    "planned_delivery_date",
]


EXPECTED_SHIPMENT_COLUMNS = [
    "shipment_id",
    "supplier_id",
    "source_warehouse_id",
    "distribution_point_id",
    "item_id",
    "item_name",
    "item_category",
    "quantity_shipped",
    "shipment_status",
    "planned_ship_date",
    "planned_delivery_date",
    "actual_delivery_date",
    "transport_mode",
]


def load_data():
    shipments = pd.read_csv(SHIPMENTS_PATH)
    warehouses = pd.read_csv(WAREHOUSES_PATH)
    suppliers = pd.read_csv(SUPPLIERS_PATH)
    distribution_points = pd.read_csv(DISTRIBUTION_POINTS_PATH)

    return shipments, warehouses, suppliers, distribution_points


def add_issue(issues, row, issue_type, issue_detail):
    issues.append(
        {
            "shipment_id": row.get("shipment_id"),
            "issue_type": issue_type,
            "issue_detail": issue_detail,
        }
    )


def validate_schema(shipments):
    missing_columns = []

    for column in EXPECTED_SHIPMENT_COLUMNS:
        if column not in shipments.columns:
            missing_columns.append(column)

    return missing_columns


def validate_shipments(shipments, warehouses, suppliers, distribution_points):
    issues = []

    valid_warehouse_ids = set(warehouses["warehouse_id"])
    valid_supplier_ids = set(suppliers["supplier_id"])
    valid_distribution_point_ids = set(distribution_points["distribution_point_id"])

    duplicate_mask = shipments["shipment_id"].duplicated(keep=False)

    for index, row in shipments.iterrows():
        # Missing mandatory fields
        for field in MANDATORY_SHIPMENT_FIELDS:
            if pd.isna(row.get(field)) or str(row.get(field)).strip() == "":
                add_issue(
                    issues,
                    row,
                    "missing_mandatory_field",
                    f"Missing value in mandatory field: {field}",
                )

        # Duplicate shipment IDs
        if duplicate_mask.iloc[index]:
            add_issue(
                issues,
                row,
                "duplicate_shipment_id",
                "Duplicate shipment_id found in source data",
            )

        # Invalid supplier reference
        supplier_id = row.get("supplier_id")
        if pd.notna(supplier_id) and supplier_id not in valid_supplier_ids:
            add_issue(
                issues,
                row,
                "invalid_supplier_reference",
                f"Supplier ID does not exist in supplier master data: {supplier_id}",
            )

        # Invalid warehouse reference
        warehouse_id = row.get("source_warehouse_id")
        if pd.notna(warehouse_id) and warehouse_id not in valid_warehouse_ids:
            add_issue(
                issues,
                row,
                "invalid_warehouse_reference",
                f"Warehouse ID does not exist in warehouse master data: {warehouse_id}",
            )

        # Invalid distribution point reference
        distribution_point_id = row.get("distribution_point_id")
        if (
            pd.notna(distribution_point_id)
            and distribution_point_id not in valid_distribution_point_ids
        ):
            add_issue(
                issues,
                row,
                "invalid_distribution_point_reference",
                f"Distribution point ID does not exist in master data: {distribution_point_id}",
            )

        # Negative or zero quantity
        quantity = row.get("quantity_shipped")
        if pd.notna(quantity):
            try:
                quantity_value = float(quantity)
                if quantity_value <= 0:
                    add_issue(
                        issues,
                        row,
                        "invalid_quantity",
                        f"Quantity must be greater than zero. Found: {quantity}",
                    )
            except ValueError:
                add_issue(
                    issues,
                    row,
                    "invalid_quantity",
                    f"Quantity is not numeric. Found: {quantity}",
                )

        # Date validation
        planned_ship_date = pd.to_datetime(
            row.get("planned_ship_date"), errors="coerce"
        )
        planned_delivery_date = pd.to_datetime(
            row.get("planned_delivery_date"), errors="coerce"
        )
        actual_delivery_date = pd.to_datetime(
            row.get("actual_delivery_date"), errors="coerce"
        )

        if pd.isna(planned_ship_date):
            add_issue(
                issues,
                row,
                "invalid_date",
                "planned_ship_date is missing or invalid",
            )

        if pd.isna(planned_delivery_date):
            add_issue(
                issues,
                row,
                "invalid_date",
                "planned_delivery_date is missing or invalid",
            )

        if pd.notna(planned_ship_date) and pd.notna(planned_delivery_date):
            if planned_delivery_date < planned_ship_date:
                add_issue(
                    issues,
                    row,
                    "impossible_delivery_date",
                    "planned_delivery_date is before planned_ship_date",
                )

        if pd.notna(planned_ship_date) and pd.notna(actual_delivery_date):
            if actual_delivery_date < planned_ship_date:
                add_issue(
                    issues,
                    row,
                    "impossible_delivery_date",
                    "actual_delivery_date is before planned_ship_date",
                )

        # Delayed shipment business rule
        if pd.notna(actual_delivery_date) and pd.notna(planned_delivery_date):
            if actual_delivery_date > planned_delivery_date:
                delay_days = (actual_delivery_date - planned_delivery_date).days
                add_issue(
                    issues,
                    row,
                    "delayed_shipment",
                    f"Shipment delivered {delay_days} days later than planned",
                )

    return pd.DataFrame(issues)


def create_summary(shipments, issue_df, missing_columns):
    issue_type_counts = {}

    if not issue_df.empty:
        issue_type_counts = (
            issue_df["issue_type"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

    affected_shipments = 0
    if not issue_df.empty:
        affected_shipments = issue_df["shipment_id"].nunique()

    summary = {
        "validated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_layer": "bronze",
        "source_file": str(SHIPMENTS_PATH.relative_to(BASE_DIR)),
        "total_source_rows": int(len(shipments)),
        "missing_schema_columns": missing_columns,
        "total_quality_issues": int(len(issue_df)),
        "affected_unique_shipments": int(affected_shipments),
        "issue_type_counts": issue_type_counts,
    }

    return summary


def save_reports(issue_df, summary):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    issue_report_path = REPORTS_DIR / "bronze_data_quality_issues.csv"
    summary_report_path = REPORTS_DIR / "bronze_validation_summary.json"

    issue_df.to_csv(issue_report_path, index=False)

    with open(summary_report_path, "w") as f:
        json.dump(summary, f, indent=2)

    return issue_report_path, summary_report_path


def main():
    shipments, warehouses, suppliers, distribution_points = load_data()

    missing_columns = validate_schema(shipments)

    issue_df = validate_shipments(
        shipments=shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    summary = create_summary(
        shipments=shipments,
        issue_df=issue_df,
        missing_columns=missing_columns,
    )

    issue_report_path, summary_report_path = save_reports(issue_df, summary)

    print("Bronze validation completed.")
    print()
    print(f"Source shipment rows: {summary['total_source_rows']}")
    print(f"Total quality issues found: {summary['total_quality_issues']}")
    print(f"Affected unique shipments: {summary['affected_unique_shipments']}")
    print()
    print("Issue counts:")

    if summary["issue_type_counts"]:
        for issue_type, count in summary["issue_type_counts"].items():
            print(f"- {issue_type}: {count}")
    else:
        print("- No issues found")

    print()
    print("Reports created:")
    print(f"- {issue_report_path}")
    print(f"- {summary_report_path}")


if __name__ == "__main__":
    main()