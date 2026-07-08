import streamlit as st
import pandas as pd

from datetime import date

from db import engine
from services.receipt_service import save_receipt


def receipts_tab():

    st.subheader("📦 Καταχώρηση Αγορών / Receipts")

    receipts = pd.read_sql(
        """
        SELECT *
        FROM receipts
        ORDER BY id DESC
        """,
        engine
    )

    rec_date = st.date_input(
        "Ημερομηνία",
        value=date.today(),
        key="rec_date"
    )

    material_code = st.text_input(
        "Material Code",
        key="receipt_material_code"
    )

    qty = st.number_input(
        "Ποσότητα",
        min_value=1.0,
        step=1.0,
        key="qty"
    )

    supplier = st.text_input(
        "Supplier",
        key="supplier"
    )

    if st.button("➕ Προσθήκη Receipt"):

        if not str(material_code).strip():

            st.error("Συμπλήρωσε Material Code.")

        elif not str(supplier).strip():

            st.error("Συμπλήρωσε Supplier.")

        else:

            result = save_receipt(
                receipt_date=pd.to_datetime(rec_date),
                material_code=str(material_code).strip(),
                qty_in=float(qty),
                supplier=str(supplier).strip(),
                price=None,
                reference_number=None,
            )

            if result["success"]:

                st.success(result["message"])
                st.rerun()

            else:

                st.error(result["message"])

            st.dataframe(
                receipts,
                use_container_width=True,
                height=500
            )