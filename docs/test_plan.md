# Test Plan

## Project

Humanitarian Supply Data Lakehouse Migration & Quality Lab

---

## Purpose

The purpose of this test plan is to verify that the data pipeline correctly validates, cleans, transforms, reconciles, and reports humanitarian supply-chain data.

The tests focus on data-quality logic, Silver layer transformation rules, and Gold layer KPI calculation.

---

## Test Scope

The test scope includes:

* Bronze schema validation
* Mandatory field validation
* Invalid reference detection
* Negative quantity rejection
* Duplicate shipment handling
* Delayed shipment handling
* Gold KPI calculation

The test scope does not include:

* Cloud infrastructure testing
* Real Databricks cluster testing
* Performance testing at large scale
* Real humanitarian operational data
* User authentication or access control

---

## Test Tool

The project uses:

```text
pytest
```

Tests are located in:

```text
tests/test_data_pipeline.py
```

---

## Test Cases

| Test ID | Test Name                                 | Purpose                                                          | Expected Result                                                           |
| ------- | ----------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------- |
| T001    | Schema validation detects missing columns | Verify that missing shipment fields are detected                 | Missing fields are returned by validation logic                           |
| T002    | Missing mandatory field detection         | Verify that missing required values are flagged                  | `missing_mandatory_field` issue is created                                |
| T003    | Invalid warehouse reference detection     | Verify that unknown warehouse IDs are flagged                    | `invalid_warehouse_reference` issue is created                            |
| T004    | Negative quantity rejection               | Verify that invalid shipment quantities are rejected from Silver | Record is rejected with `invalid_quantity`                                |
| T005    | Delayed shipment retained                 | Verify that delayed shipments are kept as business KPI records   | Record remains in Silver with `delay_days` and `is_delayed`               |
| T006    | Duplicate shipment rejection              | Verify that later duplicate shipment IDs are rejected            | First record is kept, later duplicate is rejected                         |
| T007    | Gold status KPI calculation               | Verify that grouped shipment KPIs are calculated correctly       | Shipment count, total quantity, delayed count, and delay rate are correct |

---

## How to Run Tests

From the project root:

```bash
python -m pytest -q
```

Expected result:

```text
7 passed
```

---

## Current Test Result

Current result:

```text
7 passed
```

---

## Manual Validation Checks

In addition to automated tests, the following manual checks are performed:

| Check                               | File                                             | Expected Result                        |
| ----------------------------------- | ------------------------------------------------ | -------------------------------------- |
| Bronze raw files exist              | `data/bronze/`                                   | Raw CSV and JSON files are available   |
| Bronze validation report exists     | `outputs/reports/bronze_data_quality_issues.csv` | Quality issues are listed              |
| Silver cleaned shipment file exists | `data/silver/shipments_silver.csv`               | Accepted records only                  |
| Silver rejected records exist       | `outputs/reports/silver_rejected_records.csv`    | Rejected records have reasons          |
| Gold KPI summary exists             | `data/gold/kpi_summary.csv`                      | Dashboard-ready KPIs are available     |
| Reconciliation report exists        | `outputs/reports/reconciliation_report.json`     | Row balance check is true              |
| Dashboard runs locally              | `app/app.py`                                     | Streamlit dashboard loads successfully |

---

## Reconciliation Test

The main reconciliation rule is:

```text
source_rows = silver_rows + rejected_unique_shipments
```

Current result:

```text
126 = 120 + 6
```

This confirms that each raw shipment is either accepted into Silver or rejected with a documented reason.

---

## Test Interpretation

The test suite confirms that the core data migration and data-quality logic works correctly for the synthetic sample dataset.

It does not prove production readiness. It is intended to demonstrate practical validation, cleaning, transformation, and reconciliation logic in a portfolio project.
