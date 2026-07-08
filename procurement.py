import streamlit as st

from services.procurement_service import build_procurement_plan



def procurement_tab():

    st.subheader("📦 Procurement Planning")

    planning = build_procurement_plan()

    if planning.empty:
        st.warning("Δεν υπάρχουν δεδομένα για Procurement.")
        return

    show_cols = [
        "material_code",
        "material_name",
        "current_stock",
        "avg_daily_consumption",
        "lead_time_days",
        "coverage_days",
        "required_stock",
        "suggested_order_qty",
        "status"
    ]

    st.dataframe(
        planning[show_cols]
        .sort_values("coverage_days"),
        use_container_width=True,
        height=700
    )

    st.write("### 🔴 Materials Requiring Order")

    reorder_df = planning[
        planning["suggested_order_qty"] > 0
    ]

    st.dataframe(
        reorder_df[show_cols]
        .sort_values(
            "suggested_order_qty",
            ascending=False
        ),
        use_container_width=True
    )