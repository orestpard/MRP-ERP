import streamlit as st

from services.inventory_service import run_inventory_update
from config import REPORT_FILE
from services.report_service import load_report_sheet

def dashboard_tab():
    st.subheader("Dashboard")

    if st.button("🔄 Run Inventory Update"):

        if run_inventory_update():
            st.success("Inventory updated successfully.")
        else:
            st.error("Inventory update failed.")



    if REPORT_FILE.exists():

        stock_df = load_report_sheet(
            "inventory_status"
        )

        if not stock_df.empty:

            if "inventory_status" not in stock_df.columns:
                stock_df["inventory_status"] = "OK"

            if "current_stock" not in stock_df.columns:
                stock_df["current_stock"] = 0

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Σύνολο Υλικών",
                len(stock_df)
            )

            col2.metric(
                "Out of Stock",
                int(
                    (
                            stock_df["inventory_status"]
                            == "OUT_OF_STOCK"
                    ).sum()
                )
            )

            col3.metric(
                "Low Stock",
                int(
                    (
                            stock_df["inventory_status"]
                            == "LOW_STOCK"
                    ).sum()
                )
            )

            col4.metric(
                "Total Current Stock",
                round(
                    stock_df["current_stock"].sum(),
                    2
                )
            )

            st.subheader("Απόθεμα")

            st.dataframe(
                stock_df,
                use_container_width=True
            )

            st.subheader("Alerts")

            alerts = stock_df[
                (stock_df["inventory_status"] != "OK")
                &
                (
                        stock_df["material_code"].astype(str).str.contains(r"\|RAW$", regex=True, na=False)
                        |
                        ~stock_df["material_code"].astype(str).str.contains(r"\|S", regex=True, na=False)
                )
                ]

            if not alerts.empty:

                st.dataframe(
                    alerts,
                    use_container_width=True
                )

            else:

                st.success(
                    "Δεν υπάρχουν alerts"
                )

        else:

            st.warning(
                "Το inventory_status είναι κενό ή δεν βρέθηκε."
            )

    else:

        st.warning(
            "Δεν υπάρχει inventory_report_v4.xlsx ακόμα."
        )