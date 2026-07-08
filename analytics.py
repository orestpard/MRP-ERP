import streamlit as st
import pandas as pd

from config import REPORT_FILE
from services.report_service import load_report_sheet

def analytics_tab():
    st.subheader("📈 Analytics")

    if REPORT_FILE.exists():

        consumption_detail = load_report_sheet(
            "consumption_detail"
        )

        stock_df = load_report_sheet(
            "inventory_status"
        )

        outputs = load_report_sheet(
            "outputs"
        )

        if not consumption_detail.empty:

            if "date" in consumption_detail.columns:
                consumption_detail["date"] = (
                    pd.to_datetime(
                        consumption_detail["date"],
                        errors="coerce"
                    )
                )

            st.subheader(
                "🔝 Top 10 Consumed Materials"
            )

            top_materials = (
                consumption_detail
                .groupby("material_code")["consumption"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.bar_chart(top_materials)

            st.subheader("📅 Daily Consumption")

            if "date" in consumption_detail.columns:
                daily_consumption = (
                    consumption_detail
                    .groupby("date")["consumption"]
                    .sum()
                    .sort_index()
                )

                st.line_chart(daily_consumption)

        else:

            st.info(
                "Δεν υπάρχει consumption_detail."
            )

    else:

        st.warning(
            "Δεν υπάρχει inventory_report_v4.xlsx ακόμα."
        )