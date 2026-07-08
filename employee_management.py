import streamlit as st
import pandas as pd

from sqlalchemy import text
from db import engine
from utils.audit import log_action
from services.employee_service import create_employee

def employee_management_tab():
    st.subheader("👥 Employee Management")

    # =========================================================
    # PRODUCTION PERIOD
    # =========================================================

    period = st.radio(
        "📊 Production Statistics",
        [
            "Today",
            "This Month",
            "Total"
        ],
        horizontal=True
    )

    if period == "Today":

        where_clause = """
                AND p.production_date = CURDATE()
            """

    elif period == "This Month":

        where_clause = """
                AND MONTH(p.production_date)=MONTH(CURDATE())
                AND YEAR(p.production_date)=YEAR(CURDATE())
            """

    else:

        where_clause = ""

    employees_df = pd.read_sql(

        f"""
            SELECT

                e.employee_id,
                e.employee_name,
                e.active,

                COALESCE(SUM(p.quantity),0) AS total_production

            FROM employees e

            LEFT JOIN production_log p

                ON e.employee_id = p.employee_id

                {where_clause}

            GROUP BY

                e.employee_id,
                e.employee_name,
                e.active

            ORDER BY

                total_production DESC,
                e.employee_name
            """,

        engine

    )

    # =========================================================
    # CURRENT EMPLOYEES
    # =========================================================

    st.subheader("📋 Current Employees")

    total_qty = employees_df["total_production"].sum()

    active_people = len(
        employees_df[
            employees_df["active"] == 1
            ]
    )

    working_today = len(
        employees_df[
            employees_df["total_production"] > 0
            ]
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "👥 Active Employees",
        active_people
    )

    c2.metric(
        "🏭 Working",
        working_today
    )

    c3.metric(
        "📦 Production",
        int(total_qty)
    )

    edited_employees = st.data_editor(

        employees_df,

        use_container_width=True,

        hide_index=True,

        disabled=[
            "employee_id",
            "total_production"
        ],

        column_config={

            "employee_id": st.column_config.NumberColumn(
                "ID"
            ),

            "employee_name": st.column_config.TextColumn(
                "Employee"
            ),

            "active": st.column_config.CheckboxColumn(
                "Active"
            ),

            "total_production": st.column_config.NumberColumn(
                "Total Production",
                format="%d"
            )

        },

        key="employee_editor"

    )

    # =========================================================
    # ADD EMPLOYEE
    # =========================================================

    st.divider()

    st.subheader("➕ Add Employee")

    new_employee_name = st.text_input(
        "Employee Name",
        key="new_employee_name"
    )

    if st.button(
            "➕ Add Employee",
            key="add_employee_button"
    ):

        if not new_employee_name.strip():

            st.warning("Συμπλήρωσε όνομα εργαζομένου.")

        elif new_employee_name.strip() in employees_df["employee_name"].values:

            st.warning("Ο εργαζόμενος υπάρχει ήδη.")

        else:

            result = create_employee(
                new_employee_name.strip()
            )

            if result["success"]:

                st.success(result["message"])
                st.rerun()

            else:

                st.error(result["message"])

            log_action(
                "CREATE",
                "employees",
                0,
                f"Employee={new_employee_name.strip()}"
            )

            st.success("Ο εργαζόμενος προστέθηκε.")

            st.rerun()