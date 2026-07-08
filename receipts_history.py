import streamlit as st
import pandas as pd

from sqlalchemy import text

from db import engine
from utils.audit import log_action
from services.inventory_service import run_inventory_update

def receipts_history_tab():
    st.subheader("📦 Ιστορικό Αγορών")

    receipts_history = pd.read_sql(
        """
        SELECT *
        FROM receipts
        ORDER BY id DESC
        """,
        engine
    )

    col1, col2 = st.columns(2)

    with col1:

        material_filter = st.text_input(
            "Material Code",
            key="receipt_material_filter"
        )

    with col2:

        supplier_filter = st.text_input(
            "Supplier",
            key="receipt_supplier_filter"
        )

    filtered_receipts = receipts_history.copy()

    if material_filter:
        filtered_receipts = filtered_receipts[
            filtered_receipts["material_code"]
            .astype(str)
            .str.contains(
                material_filter,
                case=False,
                na=False
            )
        ]

    if supplier_filter:
        filtered_receipts = filtered_receipts[
            filtered_receipts["supplier"]
            .astype(str)
            .str.contains(
                supplier_filter,
                case=False,
                na=False
            )
        ]

    st.metric(
        "Συνολικά Receipts",
        len(filtered_receipts)
    )

    st.dataframe(
        filtered_receipts,
        use_container_width=True,
        height=500
    )
    st.divider()
    st.subheader("✏️ Διόρθωση / Διαγραφή Receipt")

    receipt_id = st.selectbox(
        "Επιλογή Receipt",
        receipts_history["id"].tolist(),
        key="edit_receipt_id"
    )

    selected_receipt = receipts_history[
        receipts_history["id"] == receipt_id
        ]

    row = selected_receipt.iloc[0]

    edit_receipt_date = st.date_input(
        "Ημερομηνία",
        value=pd.to_datetime(
            row["receipt_date"]
        ).date(),
        key="edit_receipt_date"
    )

    edit_material = st.text_input(
        "Material Code",
        value=str(row["material_code"]),
        key="edit_material"
    )

    edit_qty = st.number_input(
        "Ποσότητα",
        min_value=0.0,
        value=float(row["qty_in"]),
        step=1.0,
        key="edit_qty"
    )

    edit_supplier = st.text_input(
        "Supplier",
        value=str(row["supplier"]),
        key="edit_supplier"
    )

    col_update, col_delete = st.columns(2)

    with col_update:

        if st.button(
                "💾 Αποθήκευση Receipt"
        ):
            with engine.begin() as conn:
                conn.execute(
                    text("""
                         UPDATE receipts
                         SET receipt_date  = :receipt_date,
                             material_code = :material_code,
                             qty_in        = :qty_in,
                             supplier      = :supplier
                         WHERE id = :id
                         """),
                    {
                        "receipt_date": edit_receipt_date,
                        "material_code": edit_material.strip(),
                        "qty_in": float(edit_qty),
                        "supplier": edit_supplier.strip(),
                        "id": int(receipt_id)
                    }
                )

                log_action(
                    "UPDATE",
                    "receipts",
                    int(receipt_id),
                    f"Material={edit_material}, Qty={edit_qty}"
                )

        run_inventory_update()

        st.success(
            "Το receipt ενημερώθηκε."
        )

        # st.rerun()

    with col_delete:

        confirm_delete = st.checkbox(
            "Επιβεβαίωση διαγραφής",
            key="confirm_delete_receipt"
        )

        if st.button(
                "🗑 Διαγραφή Receipt"
        ):

            if not confirm_delete:

                st.warning(
                    "Τσέκαρε πρώτα την επιβεβαίωση διαγραφής."
                )

            else:

                with engine.begin() as conn:

                    conn.execute(
                        text("""
                             DELETE
                             FROM receipts
                             WHERE id = :id
                             """),
                        {
                            "id": int(receipt_id)
                        }
                    )

                log_action(
                    "DELETE",
                    "receipts",
                    int(receipt_id)
                )

                run_inventory_update()

                st.success(
                    "Το receipt διαγράφηκε."
                )