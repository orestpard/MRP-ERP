import streamlit as st

from services.procurement_service import build_procurement_plan


def purchase_orders_tab():

    st.subheader(
        "🛒 Purchase Order Generator"
    )

    planning = build_procurement_plan()

    if planning.empty:

        st.warning(
            "Δεν υπάρχουν δεδομένα για Purchase Orders."
        )

        return

    purchase_df = planning[
        planning["suggested_order_qty"] > 0
    ].copy()

    show_cols = [
        "material_code",
        "material_name",
        "supplier",
        "current_stock",
        "suggested_order_qty"
    ]

    existing_cols = [
        col
        for col in show_cols
        if col in purchase_df.columns
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Materials To Order",
            len(purchase_df)
        )

    with col2:

        st.metric(
            "Total Suggested Qty",
            round(
                purchase_df[
                    "suggested_order_qty"
                ].sum(),
                0
            )
        )

    st.dataframe(
        purchase_df[
            existing_cols
        ].sort_values(
            "suggested_order_qty",
            ascending=False
        ),
        use_container_width=True
    )