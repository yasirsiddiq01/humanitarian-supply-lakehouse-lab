# Interview Explanation

## Project

Humanitarian Supply Data Lakehouse Migration & Quality Lab

---

## Short Explanation

This project simulates a humanitarian supply-chain data migration into a lakehouse-style architecture.

I created synthetic shipment, warehouse, supplier, inventory, and distribution-point data. The raw data is stored in a Bronze layer. I then validate it, clean it into a Silver layer, reject hard data-quality failures, and create Gold analytics tables for reporting.

The project also includes reconciliation reports, automated tests, documentation, and a Streamlit dashboard.

---

## Why I Built This Project

I built this project to demonstrate practical data engineering skills relevant to a Digital Impact Specialist or Data Engineer role.

The focus is not only on dashboarding. The main focus is on data migration quality:

* Can the raw data be trusted?
* What records are invalid?
* What records should be rejected?
* What records should be retained for business reporting?
* Does the row count reconcile from source to target?
* Can reporting continue after migration?

---

## Architecture Explanation

The project follows a Bronze, Silver, and Gold structure.

### Bronze

The Bronze layer contains raw CSV and JSON files.

No cleaning is applied in Bronze.

This helps preserve the original source data.

### Silver

The Silver layer contains cleaned and standardized records.

Hard validation failures are rejected.

Examples of rejected records include:

* Missing mandatory fields
* Duplicate shipment IDs
* Invalid warehouse IDs
* Invalid distribution point IDs
* Impossible delivery dates
* Negative shipment quantities

Delayed shipments are not rejected. They are kept because delay is a business performance signal, not necessarily a data-quality failure.

### Gold

The Gold layer contains analytics-ready tables.

These include:

* KPI summary
* Shipment status summary
* Supplier performance
* Warehouse inventory summary
* Distribution point summary
* Data-quality summary

The Streamlit dashboard reads from the Gold outputs.

---

## Reconciliation Explanation

The project includes a row-count reconciliation check:

```text
source_rows = silver_rows + rejected_unique_shipments
```

Current result:

```text
126 = 120 + 6
```

This means 126 raw shipment records were received. 120 were accepted into the Silver layer, and 6 unique shipments were rejected with documented reasons.

There are 7 rejection issues because one rejected shipment has two date-related issues.

---

## Data-Quality Explanation

The pipeline checks for:

* Missing mandatory fields
* Duplicate shipment IDs
* Invalid supplier references
* Invalid warehouse references
* Invalid distribution point references
* Invalid or impossible dates
* Negative shipment quantities
* Delayed shipments

The important distinction is that not every issue means rejection.

For example, delayed shipments are kept in the dataset because they are useful for reporting supplier and delivery performance.

---

## Testing Explanation

I added automated tests using pytest.

The tests verify:

* Schema validation
* Mandatory field detection
* Invalid reference detection
* Negative quantity rejection
* Duplicate shipment handling
* Delayed shipment retention
* Gold KPI calculation

Current result:

```text
7 passed
```

---

## Dashboard Explanation

The Streamlit dashboard shows:

* Source rows
* Silver rows
* Rejected shipments
* Gold shipments
* Shipment status summary
* Delayed shipments
* Supplier performance
* Warehouse inventory summary
* Distribution point summary
* Data-quality issue summary
* Downloadable Gold outputs

The dashboard is a demonstration layer. The main engineering value is in the pipeline, reconciliation, and validation logic behind it.

---

## Tools Used

The project uses:

* Python
* Pandas
* pytest
* Streamlit
* CSV and JSON
* Git-ready project structure

---

## How I Would Extend This Project

The next version could include:

* Databricks Free Edition notebooks
* PySpark transformations
* Delta Lake tables
* Data quality rules as reusable configuration
* Pipeline logging
* GitHub Actions for automated tests
* Docker deployment
* More detailed reconciliation by item, supplier, and warehouse
* More realistic source-to-target mapping
* Role-based dashboard views

---

## Honest Scope

I would not describe this as a production Databricks implementation.

The honest description is:

This is a local lakehouse-style migration and data-quality simulation using Python, Pandas, pytest, and Streamlit. It demonstrates the core thinking behind data migration, validation, reconciliation, and reporting continuity.

---

## Possible Interview Answer

If asked to explain the project, I would say:

“I built a humanitarian supply-chain lakehouse simulation to practice data migration and quality controls. I generated synthetic shipment, warehouse, supplier, inventory, and distribution-point data. The raw files are stored in a Bronze layer, then validated and cleaned into Silver. Hard data-quality failures are rejected with documented reasons, while delayed shipments are retained as business KPI records. The Gold layer creates reporting tables for shipment status, supplier performance, warehouse inventory, distribution points, and data-quality summaries. I also added reconciliation reporting, pytest tests, documentation, and a Streamlit dashboard. The project is not a production Databricks system, but it demonstrates the practical migration and reporting logic that could later be implemented in Databricks or PySpark.”
