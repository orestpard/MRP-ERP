import streamlit as st
import pandas as pd

from datetime import date
from db import engine
from services.production_service import save_production

def production_tab(stages, models):
    st.subheader("Καταχώρηση Παραγωγής")

    daily = pd.read_sql(
        """
        SELECT production_date,
               stage_id,
               model,
               quantity,
               head_count
        FROM production_log
        ORDER BY id DESC
        """,
        engine
    )

    if "date" in daily.columns:
        daily["date"] = pd.to_datetime(
            daily["date"],
            errors="coerce"
        )

    # =====================================================
    # INPUTS
    # =====================================================
    prod_date = st.date_input(
        "Ημερομηνία",
        value=date.today()
    )

    # =====================================================
    # EMPLOYEE
    # =====================================================

    employees = pd.read_sql(
        """
        SELECT employee_id,
               employee_name
        FROM employees
        WHERE active = 1
        ORDER BY employee_name
        """,
        engine
    )

    selected_employee = st.selectbox(
        "👤 Employee",
        employees["employee_name"]
    )

    employee_id = int(
        employees.loc[
            employees["employee_name"] == selected_employee,
            "employee_id"
        ].iloc[0]
    )

    # =====================================================
    # STAGE SELECTBOX
    # =====================================================
    selected_stage = st.selectbox(
        "Stage",
        stages["label"]
    )

    stage_id = int(
        selected_stage.split(" - ")[0]
    )

    # =====================================================
    # MODEL SELECTBOX
    # =====================================================
    model = st.selectbox(
        "Model",
        models
    )

    quantity = st.number_input(
        "Ποσότητα",
        min_value=1,
        step=1
    )

    # =====================================================
    # HEAD COUNT
    # =====================================================
    head_count = 1

    if stage_id == 7:
        head_count = st.number_input(
            "Αριθμός Κεφαλών",
            min_value=1,
            max_value=6,
            value=1,
            step=1
        )

    # =====================================================
    # SAVE
    # =====================================================

    if st.button("➕ Προσθήκη Παραγωγής"):

        result = save_production(
            production_date=pd.to_datetime(prod_date),
            stage_id=int(stage_id),
            model=model,
            quantity=int(quantity),
            head_count=int(head_count),
            employee_id=employee_id
        )

        if result["success"]:

            st.success(result["message"])

            st.rerun()

        else:

            st.error(result["message"])

            st.write(result)

    st.dataframe(
        daily.tail(20),
        use_container_width=True
    )