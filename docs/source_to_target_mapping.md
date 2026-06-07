# Source-to-Target Mapping

## Purpose

This document explains how raw Bronze source fields are mapped into cleaned Silver tables and analytics-ready Gold outputs.

The goal is to show migration traceability from source files to reporting tables.

---

## Layer Flow

```text
Bronze raw files
    ↓
Silver cleaned tables
    ↓
Gold reporting tables
```

---

## Bronze to Silver: Shipments

| Bronze Field                                | Silver Field          | Transformation / Rule                                          |
| ------------------------------------------- | --------------------- | -------------------------------------------------------------- |
| source row position                         | source_row_number     | Added during Silver processing for traceability                |
| shipment_id                                 | shipment_id           | Trimmed and retained if valid                                  |
| supplier_id                                 | supplier_id           | Must exist in supplier master table                            |
| source_warehouse_id                         | source_warehouse_id   | Must exist in warehouse master table                           |
| distribution_point_id                       | distribution_point_id | Must exist in distribution point master table                  |
| item_id                                     | item_id               | Trimmed and retained                                           |
| item_name                                   | item_name             | Trimmed and standardized as text                               |
| item_category                               | item_category         | Trimmed and standardized as text                               |
| quantity_shipped                            | quantity_shipped      | Converted to numeric integer; must be greater than zero        |
| shipment_status                             | shipment_status       | Trimmed and converted to title case                            |
| planned_ship_date                           | planned_ship_date     | Converted to date format YYYY-MM-DD                            |
| planned_delivery_date                       | planned_delivery_date | Converted to date format YYYY-MM-DD                            |
| actual_delivery_date                        | actual_delivery_date  | Converted to date format YYYY-MM-DD when present               |
| transport_mode                              | transport_mode        | Trimmed and retained                                           |
| planned_delivery_date, actual_delivery_date | delay_days            | Calculated as actual_delivery_date minus planned_delivery_date |
| delay_days                                  | is_delayed            | True when delay_days is greater than zero                      |
| validation result                           | record_quality_status | Set to accepted for valid Silver records                       |

---

## Silver Rejection Rules

Records are rejected from Silver when they contain hard validation failures.

| Rule                                              | Rejection Reason                     |
| ------------------------------------------------- | ------------------------------------ |
| Missing mandatory shipment field                  | missing_mandatory_field              |
| Duplicate shipment ID after first accepted record | duplicate_shipment_id                |
| Supplier ID not found in supplier master data     | invalid_supplier_reference           |
| Warehouse ID not found in warehouse master data   | invalid_warehouse_reference          |
| Distribution point ID not found in master data    | invalid_distribution_point_reference |
| Quantity is zero, negative, or not numeric        | invalid_quantity                     |
| Planned ship date or delivery date is invalid     | invalid_date                         |
| Planned delivery date is before planned ship date | impossible_delivery_date             |
| Actual delivery date is before planned ship date  | impossible_delivery_date             |

---

## Important Business Rule

Delayed shipments are not rejected.

They are kept in Silver and Gold because delay is a business performance signal, not necessarily a data-quality error.

Fields added:

| Field      | Meaning                                            |
| ---------- | -------------------------------------------------- |
| delay_days | Number of days between planned and actual delivery |
| is_delayed | Boolean flag showing whether a shipment was late   |

---

## Silver to Gold Mapping

### kpi_summary.csv

| Gold Field                   | Source                    | Logic                                                |
| ---------------------------- | ------------------------- | ---------------------------------------------------- |
| total_source_rows            | Bronze validation summary | Count of raw shipment rows                           |
| silver_rows                  | Silver cleaning summary   | Count of accepted Silver shipment rows               |
| rejected_unique_shipments    | Silver rejection report   | Count of unique rejected shipment IDs                |
| rejected_issue_count         | Silver rejection report   | Count of rejection issues                            |
| total_shipments_in_gold      | shipments_silver.csv      | Count of Silver shipment records                     |
| delivered_shipments          | shipments_silver.csv      | Count where shipment_status = Delivered              |
| in_transit_shipments         | shipments_silver.csv      | Count where shipment_status = In Transit             |
| cancelled_shipments          | shipments_silver.csv      | Count where shipment_status = Cancelled              |
| delayed_status_shipments     | shipments_silver.csv      | Count where shipment_status = Delayed                |
| delayed_by_date_shipments    | shipments_silver.csv      | Count where is_delayed = True                        |
| delayed_by_date_rate_percent | shipments_silver.csv      | delayed_by_date_shipments divided by total shipments |
| total_quantity_shipped       | shipments_silver.csv      | Sum of quantity_shipped                              |
| total_inventory_available    | inventory_silver.csv      | Sum of quantity_available                            |
| average_delay_days           | shipments_silver.csv      | Average delay_days                                   |

---

### shipment_status_summary.csv

| Gold Field             | Source               | Logic                                       |
| ---------------------- | -------------------- | ------------------------------------------- |
| shipment_status        | shipments_silver.csv | Group by shipment_status                    |
| shipment_count         | shipments_silver.csv | Count shipments                             |
| total_quantity_shipped | shipments_silver.csv | Sum quantity_shipped                        |
| delayed_shipments      | shipments_silver.csv | Sum is_delayed                              |
| average_delay_days     | shipments_silver.csv | Average delay_days                          |
| delayed_rate_percent   | shipments_silver.csv | delayed_shipments divided by shipment_count |

---

### supplier_performance.csv

| Gold Field             | Source               | Logic                                       |
| ---------------------- | -------------------- | ------------------------------------------- |
| supplier_id            | shipments_silver.csv | Joined with suppliers_silver.csv            |
| supplier_name          | suppliers_silver.csv | Supplier master field                       |
| supplier_category      | suppliers_silver.csv | Supplier master field                       |
| country                | suppliers_silver.csv | Supplier country                            |
| shipment_count         | shipments_silver.csv | Count shipments per supplier                |
| total_quantity_shipped | shipments_silver.csv | Sum quantity_shipped                        |
| delayed_shipments      | shipments_silver.csv | Sum is_delayed                              |
| average_delay_days     | shipments_silver.csv | Average delay_days                          |
| delayed_rate_percent   | shipments_silver.csv | delayed_shipments divided by shipment_count |

---

### warehouse_inventory_summary.csv

| Gold Field               | Source                | Logic                             |
| ------------------------ | --------------------- | --------------------------------- |
| warehouse_id             | inventory_silver.csv  | Joined with warehouses_silver.csv |
| warehouse_name           | warehouses_silver.csv | Warehouse master field            |
| country                  | warehouses_silver.csv | Warehouse country                 |
| city                     | warehouses_silver.csv | Warehouse city                    |
| warehouse_type           | warehouses_silver.csv | Warehouse type                    |
| item_count               | inventory_silver.csv  | Count unique item IDs             |
| total_quantity_available | inventory_silver.csv  | Sum quantity_available            |

---

### distribution_point_summary.csv

| Gold Field              | Source                         | Logic                                       |
| ----------------------- | ------------------------------ | ------------------------------------------- |
| distribution_point_id   | shipments_silver.csv           | Joined with distribution_points_silver.csv  |
| distribution_point_name | distribution_points_silver.csv | Distribution point master field             |
| country                 | distribution_points_silver.csv | Country                                     |
| city                    | distribution_points_silver.csv | City                                        |
| beneficiary_group       | distribution_points_silver.csv | Beneficiary group                           |
| shipment_count          | shipments_silver.csv           | Count shipments                             |
| total_quantity_received | shipments_silver.csv           | Sum quantity_shipped                        |
| delayed_shipments       | shipments_silver.csv           | Sum is_delayed                              |
| average_delay_days      | shipments_silver.csv           | Average delay_days                          |
| delayed_rate_percent    | shipments_silver.csv           | delayed_shipments divided by shipment_count |

---

## Reconciliation Rule

The project uses this row-count reconciliation:

```text
source_rows = silver_rows + rejected_unique_shipments
```

Current sample result:

```text
126 = 120 + 6
```

This confirms that every source shipment is either accepted into Silver or rejected with a documented reason.
