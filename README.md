---
title: Humanitarian Supply Lakehouse Lab
emoji: 🚚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---


# Humanitarian Supply Data Lakehouse Migration & Quality Lab

## Project Overview

This portfolio project simulates a humanitarian supply-chain data migration into a lakehouse-style architecture using Bronze, Silver, and Gold data layers.

The project is designed for a UNICEF Digital Impact Specialist / Data Engineer-style role. It demonstrates practical data engineering skills including data ingestion, validation, cleaning, reconciliation, transformation, data-quality reporting, testing, documentation, and dashboarding.

This is not an enterprise Databricks production system. It is a local, interview-defensible simulation built with Python, Pandas, pytest, and Streamlit. The design is compatible with future migration to Databricks notebooks or PySpark/Delta Lake.

---

## Business Scenario

Humanitarian supply-chain data often comes from multiple operational sources such as shipment files, warehouse records, supplier lists, inventory records, and distribution-point data.

Before this data can be trusted for reporting or decision-making, it needs to be validated, cleaned, reconciled, and transformed into analytics-ready outputs.

This project simulates that process.

---

## Architecture

```text
Synthetic Source Data
        |
        v
Bronze Layer
Raw CSV / JSON files with intentional data-quality issues
        |
        v
Bronze Validation
Schema checks, missing fields, duplicate IDs, invalid references, invalid dates
        |
        v
Silver Layer
Cleaned and standardized data
Rejected hard validation failures
Delayed shipments retained as business KPI records
        |
        v
Gold Layer
Aggregated KPI tables for reporting
        |
        v
Streamlit Dashboard
Migration KPIs, shipment status, supplier performance, warehouse inventory,
data-quality summary, and reconciliation metrics