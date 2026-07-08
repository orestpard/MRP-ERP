import streamlit as st
import pandas as pd

from services.production_service import (
    get_production_history,
    update_production,
    delete_production,
)


def production_history_tab():

    st.subheader("📋 Ιστορικό Παραγωγής")

    # =====================================================
    # LOAD DATA
    # =====================================================

    production_history = get_production_history()

    # =====================================================
    # FILTERS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        date_filter = st.date_input(
            "Από Ημερομηνία",
            value=None,
            key="hist_date"
        )

    with col2:

        model_filter = st.selectbox(
            "Model",
            ["Όλα"] + sorted(
                production_history["model"]
                .dropna()
                .unique()
                .tolist()
            ),
            key="hist_model"
        )

    filtered = production_history.copy()

    if date_filter:

        filtered = filtered[
            pd.to_datetime(
                filtered["production_date"]
            ).dt.date >= date_filter
        ]

    if model_filter != "Όλα":

        filtered = filtered[
            filtered["model"] == model_filter
        ]

    # =====================================================
    # TABLE
    # =====================================================

    st.metric(
        "Συνολικές Καταχωρήσεις",
        len(filtered)
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        height=600
    )

    # =====================================================
    # EDIT
    # =====================================================

    st.divider()

    st.subheader("✏️ Διόρθωση / Διαγραφή Παραγωγής")

    edit_id = st.selectbox(
        "Επιλογή εγγραφής",
        production_history["id"].tolist(),
        key="edit_production_id"
    )

    selected_row = production_history[
        production_history["id"] == edit_id
    ]

    row = selected_row.iloc[0]

    edit_date = st.date_input(
        "Ημερομηνία",
        value=pd.to_datetime(
            row["production_date"]
        ).date(),
        key="edit_production_date"
    )

    edit_stage_id = st.number_input(
        "Stage ID",
        min_value=1,
        value=int(row["stage_id"]),
        step=1,
        key="edit_stage_id"
    )

    edit_model = st.text_input(
        "Model",
        value=str(row["model"]),
        key="edit_model"
    )

    edit_quantity = st.number_input(
        "Ποσότητα",
        min_value=0.0,
        value=float(row["quantity"]),
        step=1.0,
        key="edit_quantity"
    )

    edit_head_count = st.number_input(
        "Head Count",
        min_value=1,
        value=int(row["head_count"])
        if pd.notna(row["head_count"])
        else 1,
        step=1,
        key="edit_head_count"
    )

    # =====================================================
    # BUTTONS
    # =====================================================

    col_update, col_delete = st.columns(2)

    with col_update:

        if st.button("💾 Αποθήκευση Αλλαγών"):

            result = update_production(
                production_id=int(edit_id),
                production_date=edit_date,
                stage_id=int(edit_stage_id),
                model=edit_model.lower().strip(),
                quantity=float(edit_quantity),
                head_count=int(edit_head_count),
            )

            if result["success"]:

                st.success(result["message"])
                st.rerun()

            else:

                st.error(result["message"])

    with col_delete:

        confirm_delete = st.checkbox(
            "Επιβεβαίωση διαγραφής",
            key="confirm_delete_production"
        )

        if st.button("🗑 Διαγραφή Εγγραφής"):

            if not confirm_delete:

                st.warning(
                    "Τσέκαρε πρώτα την επιβεβαίωση διαγραφής."
                )

            else:

                result = delete_production(
                    production_id=int(edit_id)
                )

                if result["success"]:

                    st.success(result["message"])
                    st.rerun()

                else:

                    st.error(result["message"])