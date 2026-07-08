import streamlit as st
import pandas as pd

from db import engine
def audit_log_tab():
    st.subheader("📜 Audit Log")

    audit_df = pd.read_sql(
        """
        SELECT id,
               action_time,
               action_type,
               table_name,
               record_id,
               details
        FROM audit_log
        ORDER BY id DESC
        """,
        engine
    )

    col1, col2 = st.columns(2)

    with col1:

        action_filter = st.selectbox(
            "Action",
            ["Όλα", "CREATE", "UPDATE", "DELETE"],
            key="audit_action"
        )

    with col2:

        table_filter = st.selectbox(
            "Table",
            ["Όλα", "production_log", "receipts"],
            key="audit_table"
        )

    filtered_audit = audit_df.copy()

    if action_filter != "Όλα":
        filtered_audit = filtered_audit[
            filtered_audit["action_type"] == action_filter
            ]

    if table_filter != "Όλα":
        filtered_audit = filtered_audit[
            filtered_audit["table_name"] == table_filter
            ]

    st.metric(
        "Συνολικές Καταγραφές",
        len(filtered_audit)
    )

    st.dataframe(
        filtered_audit,
        use_container_width=True,
        height=600
    )