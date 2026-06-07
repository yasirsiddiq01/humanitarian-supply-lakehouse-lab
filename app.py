from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

GOLD_DIR = BASE_DIR / "data" / "gold"
SILVER_DIR = BASE_DIR / "data" / "silver"


st.set_page_config(
    page_title="Humanitarian Supply Lakehouse Lab",
    layout="wide",
)


@st.cache_data
def load_csv(path):
    return pd.read_csv(path)


def check_required_files():
    required_files = [
        GOLD_DIR / "kpi_summary.csv",
        GOLD_DIR / "shipment_status_summary.csv",
        GOLD_DIR / "supplier_performance.csv",
        GOLD_DIR / "warehouse_inventory_summary.csv",
        GOLD_DIR / "distribution_point_summary.csv",
        GOLD_DIR / "data_quality_summary.csv",
        SILVER_DIR / "shipments_silver.csv",
    ]

    return [str(path) for path in required_files if not path.exists()]


def main():
    st.title("Humanitarian Supply Data Lakehouse Migration & Quality Lab")

    st.markdown(
        """
        This demo simulates a humanitarian supply-chain data migration into a
        Bronze, Silver, and Gold lakehouse-style architecture.

        It demonstrates ingestion, validation, cleaning, rejected-record handling,
        reconciliation, Gold KPI outputs, and dashboard-ready reporting.
        """
    )

    missing_files = check_required_files()

    if missing_files:
        st.error("Required output files are missing.")
        st.write("The Space needs the sample Silver and Gold CSV outputs included in the repository.")
        st.write("Missing files:")
        for file_path in missing_files:
            st.write(f"- {file_path}")
        return

    kpi_summary = load_csv(GOLD_DIR / "kpi_summary.csv")
    shipment_status_summary = load_csv(GOLD_DIR / "shipment_status_summary.csv")
    supplier_performance = load_csv(GOLD_DIR / "supplier_performance.csv")
    warehouse_inventory_summary = load_csv(GOLD_DIR / "warehouse_inventory_summary.csv")
    distribution_point_summary = load_csv(GOLD_DIR / "distribution_point_summary.csv")
    data_quality_summary = load_csv(GOLD_DIR / "data_quality_summary.csv")
    shipments_silver = load_csv(SILVER_DIR / "shipments_silver.csv")

    kpi = kpi_summary.iloc[0]

    st.header("1. Migration and Reconciliation KPIs")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Source Rows", int(kpi["total_source_rows"]))
    col2.metric("Silver Rows", int(kpi["silver_rows"]))
    col3.metric("Rejected Shipments", int(kpi["rejected_unique_shipments"]))
    col4.metric("Gold Shipments", int(kpi["total_shipments_in_gold"]))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Quantity Shipped", int(kpi["total_quantity_shipped"]))
    col6.metric("Inventory Available", int(kpi["total_inventory_available"]))
    col7.metric("Delayed by Date", int(kpi["delayed_by_date_shipments"]))
    col8.metric("Delay Rate", f"{float(kpi['delayed_by_date_rate_percent']):.2f}%")

    st.info(
        "Reconciliation rule: source rows should equal accepted Silver rows "
        "plus rejected unique shipments."
    )

    st.code(
        f"{int(kpi['total_source_rows'])} = "
        f"{int(kpi['silver_rows'])} + "
        f"{int(kpi['rejected_unique_shipments'])}"
    )

    st.header("2. Shipment Status Overview")
    st.dataframe(shipment_status_summary, use_container_width=True)
    st.bar_chart(
        shipment_status_summary.set_index("shipment_status")["shipment_count"]
    )

    st.header("3. Delayed Shipments")
    delayed_shipments = shipments_silver[shipments_silver["is_delayed"] == True]
    st.write(f"Delayed shipment records kept in Silver: {len(delayed_shipments)}")

    delayed_columns = [
        "shipment_id",
        "supplier_id",
        "source_warehouse_id",
        "distribution_point_id",
        "item_name",
        "quantity_shipped",
        "shipment_status",
        "planned_delivery_date",
        "actual_delivery_date",
        "delay_days",
        "transport_mode",
    ]

    st.dataframe(
        delayed_shipments[delayed_columns].sort_values(
            by="delay_days",
            ascending=False,
        ),
        use_container_width=True,
    )

    st.header("4. Supplier Performance")
    st.dataframe(supplier_performance, use_container_width=True)
    st.bar_chart(
        supplier_performance.set_index("supplier_name")["delayed_rate_percent"]
    )

    st.header("5. Warehouse Inventory Summary")
    st.dataframe(warehouse_inventory_summary, use_container_width=True)
    st.bar_chart(
        warehouse_inventory_summary.set_index("warehouse_name")[
            "total_quantity_available"
        ]
    )

    st.header("6. Distribution Point Summary")
    st.dataframe(distribution_point_summary, use_container_width=True)

    st.header("7. Data Quality Issue Summary")
    st.dataframe(data_quality_summary, use_container_width=True)
    st.bar_chart(data_quality_summary.groupby("metric_name")["metric_value"].sum())

    st.header("8. Download Gold Outputs")

    for file_name in [
        "kpi_summary.csv",
        "shipment_status_summary.csv",
        "supplier_performance.csv",
        "warehouse_inventory_summary.csv",
        "distribution_point_summary.csv",
        "data_quality_summary.csv",
    ]:
        file_path = GOLD_DIR / file_name

        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download {file_name}",
                data=f,
                file_name=file_name,
                mime="text/csv",
            )

    st.caption(
        "Scope note: this is a local Pandas-based lakehouse simulation. "
        "It does not claim production Databricks implementation or real UNICEF data."
    )


if __name__ == "__main__":
    main()