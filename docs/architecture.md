# Architecture

## Project Name

Humanitarian Supply Data Lakehouse Migration & Quality Lab

---

## Purpose

This project simulates how humanitarian supply-chain data can be migrated from raw operational files into a lakehouse-style reporting structure.

The pipeline uses Bronze, Silver, and Gold layers to separate raw data, cleaned data, and analytics-ready reporting outputs.

---

## Architecture Diagram

```text
+-----------------------------+
| Synthetic Source Systems    |
| - Shipments                 |
| - Warehouses                |
| - Suppliers                 |
| - Inventory                 |
| - Distribution Points       |
+-------------+---------------+
              |
              v
+-----------------------------+
| Bronze Layer                |
| Raw CSV and JSON files      |
| No cleaning applied         |
| Intentional quality issues  |
+-------------+---------------+
              |
              v
+-----------------------------+
| Bronze Validation           |
| - Schema checks             |
| - Mandatory field checks    |
| - Duplicate checks          |
| - Reference checks          |
| - Date checks               |
| - Quantity checks           |
+-------------+---------------+
              |
              v
+-----------------------------+
| Silver Layer                |
| Cleaned and standardized    |
| Hard validation failures    |
| rejected                    |
| Delays retained as KPIs     |
+-------------+---------------+
              |
              v
+-----------------------------+
| Gold Layer                  |
| Analytics-ready tables      |
| KPI summaries               |
| Supplier performance        |
| Warehouse inventory         |
| Distribution summaries      |
| Data-quality summary        |
+-------------+---------------+
              |
              v
+-----------------------------+
| Streamlit Dashboard         |
| Reporting and demo layer    |
+-----------------------------+
```

---

## Layer Responsibilities

## Bronze Layer

The Bronze layer stores raw source data.

Files include:

* `shipments_raw.csv`
* `shipments_raw.json`
* `warehouses_raw.csv`
* `suppliers_raw.csv`
* `inventory_raw.csv`
* `distribution_points_raw.csv`

No cleaning is applied in Bronze. This preserves the original source extract.

---

## Silver Layer

The Silver layer contains cleaned and standardized records.

Hard validation failures are rejected, including:

* Missing mandatory shipment fields
* Duplicate shipment IDs after the first accepted record
* Unknown warehouse IDs
* Unknown distribution point IDs
* Invalid or impossible dates
* Negative or zero shipment quantities

Delayed shipments are not rejected. They are kept and enriched with:

* `delay_days`
* `is_delayed`

This is because delivery delay is a business-performance signal, not necessarily a data-quality error.

---

## Gold Layer

The Gold layer contains analytics-ready reporting tables.

Gold outputs include:

* `kpi_summary.csv`
* `shipment_status_summary.csv`
* `supplier_performance.csv`
* `warehouse_inventory_summary.csv`
* `distribution_point_summary.csv`
* `data_quality_summary.csv`

These files are used by the Streamlit dashboard.

---

## Reconciliation Logic

The project uses this row-count reconciliation rule:

```text
source_rows = silver_rows + rejected_unique_shipments
```

Current sample result:

```text
126 = 120 + 6
```

This confirms that every source shipment is either accepted into Silver or rejected with a documented reason.

---

## Governance and Traceability

The project includes basic governance-style controls:

* Source row number retained in Silver
* Rejected records report
* Bronze validation summary
* Silver cleaning summary
* Gold reconciliation report
* Source-to-target mapping
* Data dictionary
* Test plan
* Automated pytest tests

---

## Future Databricks Version

This project can later be migrated into Databricks Free Edition or PySpark/Delta Lake by replacing Pandas CSV processing with Spark DataFrames and Delta tables.

| Current Component  | Future Databricks Component          |
| ------------------ | ------------------------------------ |
| CSV files          | External files or volumes            |
| Pandas scripts     | Databricks notebooks                 |
| Bronze CSV outputs | Bronze Delta tables                  |
| Silver CSV outputs | Silver Delta tables                  |
| Gold CSV outputs   | Gold Delta tables                    |
| pytest tests       | CI checks or notebook tests          |
| Streamlit app      | Databricks dashboard or external app |

---

## Honest Scope

This is a local lakehouse-style simulation.

It does not claim:

* Production Databricks deployment
* Enterprise-scale Spark processing
* Real UNICEF data
* Real beneficiary records
* Cloud production governance

The project demonstrates practical migration, validation, reconciliation, reporting, and testing logic.
