# Known Limitations

## Project

Humanitarian Supply Data Lakehouse Migration & Quality Lab

---

## Purpose

This document explains the limitations of the project so that the scope is clear and interview-defensible.

The project is a portfolio simulation, not a production humanitarian data platform.

---

## 1. Synthetic Data Only

The project uses synthetic humanitarian supply-chain data.

It does not use:

* Real UNICEF data
* Real beneficiary records
* Real supplier contracts
* Real warehouse operations data
* Real emergency response data

This avoids privacy, security, and ethical issues.

---

## 2. Local Pandas Implementation

The current version uses Python and Pandas.

It simulates a lakehouse-style workflow using local CSV and JSON files.

It does not currently use:

* Production Databricks jobs
* Delta Lake tables
* Spark clusters
* Unity Catalog
* Cloud object storage
* Enterprise data governance tools

The project can be migrated later to Databricks Free Edition, PySpark, or Delta Lake.

---

## 3. Small Dataset Size

The dataset is intentionally small so that it can run easily on a local laptop and on Hugging Face Spaces.

This project does not test:

* Large-scale distributed processing
* Partitioning strategy
* Cluster cost optimization
* Streaming ingestion
* High-volume data lake performance

---

## 4. Basic Governance Only

The project includes simple governance-style controls:

* Source row number
* Rejected records report
* Validation summary
* Cleaning summary
* Reconciliation report
* Documentation
* Automated tests

It does not implement full enterprise governance such as:

* Role-based access control
* Data lineage tools
* Data classification policies
* Data retention policies
* Audit trails
* Approval workflows
* Master data management

---

## 5. Simplified Business Rules

The business rules are simplified for demonstration.

Examples:

* Shipments with hard data-quality errors are rejected.
* Delayed shipments are retained as KPI records.
* Duplicate shipment IDs keep the first record and reject later duplicates.
* Reference checks use small master tables.

In a real system, these rules would need agreement from business, logistics, data governance, and reporting teams.

---

## 6. Limited Error Handling

The scripts are designed for clarity and learning.

They do not include advanced production error handling such as:

* Retry logic
* Pipeline scheduling
* Logging framework
* Alerting
* Monitoring
* Data contract enforcement
* Failed job recovery

---

## 7. No Real API Integration

The current project uses local CSV and JSON files.

It does not ingest data from:

* ERP systems
* Supply-chain APIs
* Warehouse management systems
* Vendor portals
* Real-time logistics platforms

---

## 8. Streamlit Dashboard Is a Demo Layer

The Streamlit dashboard is used for demonstration and portfolio presentation.

It is not intended as a secure production reporting application.

It does not include:

* Authentication
* User roles
* Row-level security
* Secure deployment controls
* Database-backed reporting

---

## 9. Reconciliation Is Row-Based

The project includes row-count reconciliation:

```text
source_rows = silver_rows + rejected_unique_shipments
```

It also reports shipment and inventory totals.

However, a real migration would require deeper reconciliation, including:

* Financial value reconciliation
* Item-level reconciliation
* Time-period reconciliation
* Source system extracts vs target tables
* Control totals
* Exception sign-off

---

## 10. Humanitarian Context Is Simplified

The project uses a humanitarian supply-chain scenario, but it does not model the full complexity of humanitarian operations.

It simplifies:

* Beneficiary registration
* Emergency prioritization
* Cold-chain logistics
* Customs clearance
* Procurement rules
* Multi-agency coordination
* Donor reporting requirements

---

## Summary

This project is suitable for demonstrating:

* Data migration thinking
* Lakehouse-style layering
* Data-quality checks
* Reconciliation
* Reporting continuity
* Dashboarding
* Testing
* Documentation

It should not be described as a production UNICEF system or an enterprise Databricks implementation.
