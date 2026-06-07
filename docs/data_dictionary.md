# Data Dictionary

## Purpose

This document defines the main data fields used in the Humanitarian Supply Data Lakehouse Migration & Quality Lab.

The project uses synthetic data only. No real beneficiary, UNICEF, or operational humanitarian data is used.

---

# Bronze Layer

The Bronze layer stores raw source files with no cleaning applied.

## shipments_raw.csv / shipments_raw.json

| Field                 | Type        | Description                                                          |
| --------------------- | ----------- | -------------------------------------------------------------------- |
| shipment_id           | string      | Unique shipment identifier in the source system                      |
| supplier_id           | string      | Supplier identifier                                                  |
| source_warehouse_id   | string      | Warehouse where the shipment starts                                  |
| distribution_point_id | string      | Destination distribution point                                       |
| item_id               | string      | Item identifier                                                      |
| item_name             | string      | Human-readable item name                                             |
| item_category         | string      | Category such as Medical, Nutrition, WASH, Shelter, or Education     |
| quantity_shipped      | integer     | Number of units shipped                                              |
| shipment_status       | string      | Shipment status such as Delivered, In Transit, Delayed, or Cancelled |
| planned_ship_date     | date string | Planned date when shipment leaves the warehouse                      |
| planned_delivery_date | date string | Planned delivery date                                                |
| actual_delivery_date  | date string | Actual delivery date, if available                                   |
| transport_mode        | string      | Transport method such as Air, Road, or Sea                           |

---

## warehouses_raw.csv

| Field          | Type   | Description                                                       |
| -------------- | ------ | ----------------------------------------------------------------- |
| warehouse_id   | string | Unique warehouse identifier                                       |
| warehouse_name | string | Warehouse name                                                    |
| country        | string | Country where the warehouse is located                            |
| city           | string | City where the warehouse is located                               |
| warehouse_type | string | Warehouse category such as Central, Regional, Emergency, or Field |

---

## suppliers_raw.csv

| Field             | Type   | Description                                                           |
| ----------------- | ------ | --------------------------------------------------------------------- |
| supplier_id       | string | Unique supplier identifier                                            |
| supplier_name     | string | Supplier organization name                                            |
| supplier_category | string | Supplier type such as Medical, Nutrition, Shelter, WASH, or Education |
| country           | string | Supplier country                                                      |

---

## inventory_raw.csv

| Field              | Type        | Description                         |
| ------------------ | ----------- | ----------------------------------- |
| inventory_id       | string      | Unique inventory record identifier  |
| warehouse_id       | string      | Warehouse where inventory is stored |
| item_id            | string      | Item identifier                     |
| item_name          | string      | Item name                           |
| item_category      | string      | Item category                       |
| quantity_available | integer     | Current available quantity          |
| last_stock_update  | date string | Last stock update date              |

---

## distribution_points_raw.csv

| Field                   | Type   | Description                                         |
| ----------------------- | ------ | --------------------------------------------------- |
| distribution_point_id   | string | Unique distribution point identifier                |
| distribution_point_name | string | Distribution point or service location name         |
| country                 | string | Country                                             |
| city                    | string | City                                                |
| beneficiary_group       | string | High-level beneficiary group served by the location |

---

# Silver Layer

The Silver layer contains cleaned, standardized, and accepted records.

## shipments_silver.csv

| Field                 | Type        | Description                                                       |
| --------------------- | ----------- | ----------------------------------------------------------------- |
| source_row_number     | integer     | Original row number from the Bronze shipment file                 |
| shipment_id           | string      | Shipment identifier                                               |
| supplier_id           | string      | Valid supplier identifier                                         |
| source_warehouse_id   | string      | Valid warehouse identifier                                        |
| distribution_point_id | string      | Valid distribution point identifier                               |
| item_id               | string      | Item identifier                                                   |
| item_name             | string      | Standardized item name                                            |
| item_category         | string      | Standardized item category                                        |
| quantity_shipped      | integer     | Valid positive shipment quantity                                  |
| shipment_status       | string      | Standardized shipment status                                      |
| planned_ship_date     | date string | Standardized planned ship date                                    |
| planned_delivery_date | date string | Standardized planned delivery date                                |
| actual_delivery_date  | date string | Standardized actual delivery date, where available                |
| transport_mode        | string      | Standardized transport mode                                       |
| delay_days            | numeric     | Difference between actual delivery date and planned delivery date |
| is_delayed            | boolean     | True when delay_days is greater than zero                         |
| record_quality_status | string      | Accepted record status                                            |

---

## silver_rejected_records.csv

| Field            | Type   | Description                                 |
| ---------------- | ------ | ------------------------------------------- |
| shipment_id      | string | Shipment identifier rejected from Silver    |
| rejection_reason | string | Short rejection category                    |
| rejection_detail | string | Human-readable explanation of the rejection |

---

# Gold Layer

The Gold layer contains analytics-ready reporting tables.

## kpi_summary.csv

| Field                        | Type      | Description                                                              |
| ---------------------------- | --------- | ------------------------------------------------------------------------ |
| generated_at                 | timestamp | Time when the KPI table was generated                                    |
| total_source_rows            | integer   | Number of raw shipment rows in Bronze                                    |
| silver_rows                  | integer   | Number of accepted shipment rows in Silver                               |
| rejected_unique_shipments    | integer   | Number of unique shipments rejected                                      |
| rejected_issue_count         | integer   | Total number of rejection issues                                         |
| total_shipments_in_gold      | integer   | Number of shipment records used in Gold reporting                        |
| delivered_shipments          | integer   | Count of delivered shipments                                             |
| in_transit_shipments         | integer   | Count of in-transit shipments                                            |
| cancelled_shipments          | integer   | Count of cancelled shipments                                             |
| delayed_status_shipments     | integer   | Count of shipments with status Delayed                                   |
| delayed_by_date_shipments    | integer   | Count of shipments where actual delivery date is later than planned date |
| delayed_by_date_rate_percent | numeric   | Percentage of shipments delayed by date                                  |
| total_quantity_shipped       | integer   | Sum of all accepted shipment quantities                                  |
| total_inventory_available    | integer   | Sum of all available inventory                                           |
| average_delay_days           | numeric   | Average delay days across accepted shipments                             |

---

## shipment_status_summary.csv

| Field                  | Type    | Description                                    |
| ---------------------- | ------- | ---------------------------------------------- |
| shipment_status        | string  | Shipment status category                       |
| shipment_count         | integer | Number of shipments in that status             |
| total_quantity_shipped | integer | Total quantity shipped for that status         |
| delayed_shipments      | integer | Number of delayed shipments in that status     |
| average_delay_days     | numeric | Average delay days for that status             |
| delayed_rate_percent   | numeric | Percentage of delayed shipments in that status |

---

## supplier_performance.csv

| Field                  | Type    | Description                               |
| ---------------------- | ------- | ----------------------------------------- |
| supplier_id            | string  | Supplier identifier                       |
| supplier_name          | string  | Supplier name                             |
| supplier_category      | string  | Supplier category                         |
| country                | string  | Supplier country                          |
| shipment_count         | integer | Number of shipments handled by supplier   |
| total_quantity_shipped | integer | Total quantity shipped by supplier        |
| delayed_shipments      | integer | Number of delayed shipments from supplier |
| average_delay_days     | numeric | Average delay days for supplier shipments |
| delayed_rate_percent   | numeric | Supplier delay rate                       |

---

## warehouse_inventory_summary.csv

| Field                    | Type    | Description                        |
| ------------------------ | ------- | ---------------------------------- |
| warehouse_id             | string  | Warehouse identifier               |
| warehouse_name           | string  | Warehouse name                     |
| country                  | string  | Warehouse country                  |
| city                     | string  | Warehouse city                     |
| warehouse_type           | string  | Warehouse type                     |
| item_count               | integer | Number of unique item types stored |
| total_quantity_available | integer | Total inventory quantity available |

---

## distribution_point_summary.csv

| Field                   | Type    | Description                     |
| ----------------------- | ------- | ------------------------------- |
| distribution_point_id   | string  | Distribution point identifier   |
| distribution_point_name | string  | Distribution point name         |
| country                 | string  | Country                         |
| city                    | string  | City                            |
| beneficiary_group       | string  | Beneficiary group               |
| shipment_count          | integer | Number of shipments received    |
| total_quantity_received | integer | Total quantity received         |
| delayed_shipments       | integer | Number of delayed shipments     |
| average_delay_days      | numeric | Average delay days              |
| delayed_rate_percent    | numeric | Percentage of delayed shipments |

---

## data_quality_summary.csv

| Field        | Type    | Description                             |
| ------------ | ------- | --------------------------------------- |
| stage        | string  | Pipeline stage where issue was detected |
| metric_name  | string  | Quality issue or rejection metric       |
| metric_value | integer | Count of the issue or metric            |
