import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"


SHIPMENTS_PATH = BRONZE_DIR / "shipments" / "shipments_raw.csv"
WAREHOUSES_PATH = BRONZE_DIR / "warehouses" / "warehouses_raw.csv"
SUPPLIERS_PATH = BRONZE_DIR / "suppliers" / "suppliers_raw.csv"
DISTRIBUTION_POINTS_PATH = (
    BRONZE_DIR / "distribution_points" / "distribution_points_raw.csv"
)
INVENTORY_PATH = BRONZE_DIR / "inventory" / "inventory_raw.csv"


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


DATE_COLUMNS = [
    "planned_ship_date",
    "planned_delivery_date",
    "actual_delivery_date",
]


def load_bronze_data():
    shipments = pd.read_csv(SHIPMENTS_PATH)
    warehouses = pd.read_csv(WAREHOUSES_PATH)
    suppliers = pd.read_csv(SUPPLIERS_PATH)
    distribution_points = pd.read_csv(DISTRIBUTION_POINTS_PATH)
    inventory = pd.read_csv(INVENTORY_PATH)

    return shipments, warehouses, suppliers, distribution_points, inventory


def standardize_text_columns(df):
    df = df.copy()

    for column in df.columns:
      if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column]):
         df[column] = df[column].astype("string").str.strip()
    return df


def standardize_master_tables(warehouses, suppliers, distribution_points, inventory):
    warehouses = standardize_text_columns(warehouses)
    suppliers = standardize_text_columns(suppliers)
    distribution_points = standardize_text_columns(distribution_points)
    inventory = standardize_text_columns(inventory)

    inventory["quantity_available"] = pd.to_numeric(
        inventory["quantity_available"],
        errors="coerce",
    )

    inventory["last_stock_update"] = pd.to_datetime(
        inventory["last_stock_update"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    return warehouses, suppliers, distribution_points, inventory


def add_rejection(rejections, row, reason, detail):
    rejections.append(
        {
            "shipment_id": row.get("shipment_id"),
            "rejection_reason": reason,
            "rejection_detail": detail,
        }
    )


def clean_shipments(shipments, warehouses, suppliers, distribution_points):
    shipments = shipments.copy()
    shipments = standardize_text_columns(shipments)

    rejections = []

    valid_warehouse_ids = set(warehouses["warehouse_id"])
    valid_supplier_ids = set(suppliers["supplier_id"])
    valid_distribution_point_ids = set(distribution_points["distribution_point_id"])

    # Keep source row number for traceability.
    shipments.insert(0, "source_row_number", range(1, len(shipments) + 1))

    # Convert quantity.
    shipments["quantity_shipped"] = pd.to_numeric(
        shipments["quantity_shipped"],
        errors="coerce",
    )

    # Convert dates.
    for column in DATE_COLUMNS:
        shipments[column] = pd.to_datetime(shipments[column], errors="coerce")

    # Standardize shipment status.
    shipments["shipment_status"] = (
        shipments["shipment_status"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    duplicate_mask = shipments["shipment_id"].duplicated(keep="first")

    keep_rows = []

    for index, row in shipments.iterrows():
        row_has_hard_error = False

        # Missing mandatory fields.
        for field in MANDATORY_SHIPMENT_FIELDS:
            value = row.get(field)

            if pd.isna(value) or str(value).strip() == "":
                add_rejection(
                    rejections,
                    row,
                    "missing_mandatory_field",
                    f"Missing value in mandatory field: {field}",
                )
                row_has_hard_error = True

        # Duplicate shipment ID.
        # Rule: keep the first record, reject later duplicates.
        if duplicate_mask.iloc[index]:
            add_rejection(
                rejections,
                row,
                "duplicate_shipment_id",
                "Duplicate shipment_id found. Later duplicate record rejected.",
            )
            row_has_hard_error = True

        # Invalid supplier reference.
        supplier_id = row.get("supplier_id")
        if pd.notna(supplier_id) and supplier_id not in valid_supplier_ids:
            add_rejection(
                rejections,
                row,
                "invalid_supplier_reference",
                f"Supplier ID not found in supplier master data: {supplier_id}",
            )
            row_has_hard_error = True

        # Invalid warehouse reference.
        warehouse_id = row.get("source_warehouse_id")
        if pd.notna(warehouse_id) and warehouse_id not in valid_warehouse_ids:
            add_rejection(
                rejections,
                row,
                "invalid_warehouse_reference",
                f"Warehouse ID not found in warehouse master data: {warehouse_id}",
            )
            row_has_hard_error = True

        # Invalid distribution point reference.
        distribution_point_id = row.get("distribution_point_id")
        if (
            pd.notna(distribution_point_id)
            and distribution_point_id not in valid_distribution_point_ids
        ):
            add_rejection(
                rejections,
                row,
                "invalid_distribution_point_reference",
                f"Distribution point ID not found in master data: {distribution_point_id}",
            )
            row_has_hard_error = True

        # Quantity rule.
        quantity = row.get("quantity_shipped")
        if pd.isna(quantity) or quantity <= 0:
            add_rejection(
                rejections,
                row,
                "invalid_quantity",
                f"Quantity must be greater than zero. Found: {quantity}",
            )
            row_has_hard_error = True

        # Date rules.
        planned_ship_date = row.get("planned_ship_date")
        planned_delivery_date = row.get("planned_delivery_date")
        actual_delivery_date = row.get("actual_delivery_date")

        if pd.isna(planned_ship_date):
            add_rejection(
                rejections,
                row,
                "invalid_date",
                "planned_ship_date is missing or invalid",
            )
            row_has_hard_error = True

        if pd.isna(planned_delivery_date):
            add_rejection(
                rejections,
                row,
                "invalid_date",
                "planned_delivery_date is missing or invalid",
            )
            row_has_hard_error = True

        if pd.notna(planned_ship_date) and pd.notna(planned_delivery_date):
            if planned_delivery_date < planned_ship_date:
                add_rejection(
                    rejections,
                    row,
                    "impossible_delivery_date",
                    "planned_delivery_date is before planned_ship_date",
                )
                row_has_hard_error = True

        if pd.notna(planned_ship_date) and pd.notna(actual_delivery_date):
            if actual_delivery_date < planned_ship_date:
                add_rejection(
                    rejections,
                    row,
                    "impossible_delivery_date",
                    "actual_delivery_date is before planned_ship_date",
                )
                row_has_hard_error = True

        if not row_has_hard_error:
            keep_rows.append(index)

    silver_shipments = shipments.loc[keep_rows].copy()

    # Business KPI fields: these are not rejection rules.
    silver_shipments["delay_days"] = (
        silver_shipments["actual_delivery_date"]
        - silver_shipments["planned_delivery_date"]
    ).dt.days

    silver_shipments["delay_days"] = silver_shipments["delay_days"].fillna(0)

    silver_shipments["is_delayed"] = silver_shipments["delay_days"] > 0

    # Standardize dates back to clean string format for CSV output.
    for column in DATE_COLUMNS:
        silver_shipments[column] = silver_shipments[column].dt.strftime("%Y-%m-%d")

    silver_shipments["quantity_shipped"] = silver_shipments[
        "quantity_shipped"
    ].astype(int)

    silver_shipments["record_quality_status"] = "accepted"

    rejected_records = pd.DataFrame(rejections)

    return silver_shipments, rejected_records


def save_silver_outputs(
    silver_shipments,
    warehouses,
    suppliers,
    distribution_points,
    inventory,
    rejected_records,
):
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    silver_shipments.to_csv(SILVER_DIR / "shipments_silver.csv", index=False)
    warehouses.to_csv(SILVER_DIR / "warehouses_silver.csv", index=False)
    suppliers.to_csv(SILVER_DIR / "suppliers_silver.csv", index=False)
    distribution_points.to_csv(
        SILVER_DIR / "distribution_points_silver.csv",
        index=False,
    )
    inventory.to_csv(SILVER_DIR / "inventory_silver.csv", index=False)

    rejected_records.to_csv(
        REPORTS_DIR / "silver_rejected_records.csv",
        index=False,
    )


def create_summary(raw_shipments, silver_shipments, rejected_records):
    rejection_counts = {}

    if not rejected_records.empty:
        rejection_counts = (
            rejected_records["rejection_reason"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

    rejected_unique_shipments = 0

    if not rejected_records.empty:
        rejected_unique_shipments = rejected_records["shipment_id"].nunique()

    summary = {
        "processed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_stage": "bronze_to_silver",
        "source_rows": int(len(raw_shipments)),
        "silver_rows": int(len(silver_shipments)),
        "rejected_issue_count": int(len(rejected_records)),
        "rejected_unique_shipments": int(rejected_unique_shipments),
        "delayed_shipments_kept_in_silver": int(
            silver_shipments["is_delayed"].sum()
        ),
        "total_quantity_shipped_in_silver": int(
            silver_shipments["quantity_shipped"].sum()
        ),
        "rejection_reason_counts": rejection_counts,
        "business_rule_note": (
            "Delayed shipments are retained in Silver as business KPI records. "
            "Hard validation failures are rejected."
        ),
    }

    return summary


def save_summary(summary):
    summary_path = REPORTS_DIR / "silver_cleaning_summary.json"

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary_path


def main():
    (
        raw_shipments,
        warehouses,
        suppliers,
        distribution_points,
        inventory,
    ) = load_bronze_data()

    (
        warehouses,
        suppliers,
        distribution_points,
        inventory,
    ) = standardize_master_tables(
        warehouses,
        suppliers,
        distribution_points,
        inventory,
    )

    silver_shipments, rejected_records = clean_shipments(
        shipments=raw_shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
    )

    save_silver_outputs(
        silver_shipments=silver_shipments,
        warehouses=warehouses,
        suppliers=suppliers,
        distribution_points=distribution_points,
        inventory=inventory,
        rejected_records=rejected_records,
    )

    summary = create_summary(
        raw_shipments=raw_shipments,
        silver_shipments=silver_shipments,
        rejected_records=rejected_records,
    )

    summary_path = save_summary(summary)

    print("Silver layer created successfully.")
    print()
    print(f"Source shipment rows: {summary['source_rows']}")
    print(f"Silver shipment rows: {summary['silver_rows']}")
    print(f"Rejected issue count: {summary['rejected_issue_count']}")
    print(f"Rejected unique shipments: {summary['rejected_unique_shipments']}")
    print(
        "Delayed shipments kept in Silver: "
        f"{summary['delayed_shipments_kept_in_silver']}"
    )
    print()
    print("Rejection counts:")

    if summary["rejection_reason_counts"]:
        for reason, count in summary["rejection_reason_counts"].items():
            print(f"- {reason}: {count}")
    else:
        print("- No rejected records")

    print()
    print("Files created:")
    print(f"- {SILVER_DIR / 'shipments_silver.csv'}")
    print(f"- {SILVER_DIR / 'warehouses_silver.csv'}")
    print(f"- {SILVER_DIR / 'suppliers_silver.csv'}")
    print(f"- {SILVER_DIR / 'distribution_points_silver.csv'}")
    print(f"- {SILVER_DIR / 'inventory_silver.csv'}")
    print(f"- {REPORTS_DIR / 'silver_rejected_records.csv'}")
    print(f"- {summary_path}")


if __name__ == "__main__":
    main()