import streamlit as st
import pandas as pd

from sqlalchemy import text
from services.inventory_service import run_inventory_update
from db import engine
from utils.audit import log_action

def material_management_tab():
    st.subheader("🧰 Material Management")

    materials_df = pd.read_sql(
        """
        SELECT material_code,
               material_name,
               stock_on_hand,
               unit,
               supplier,
               lead_time_days
        FROM materials
        ORDER BY material_code
        """,
        engine
    )

    search_code = st.text_input(
        "Search Material Code",
        key="manage_material_search"
    )

    if search_code:

        matches = materials_df[
            materials_df["material_code"]
            .astype(str)
            .str.contains(
                search_code,
                case=False,
                na=False
            )
        ]

        if matches.empty:

            st.warning("Δεν βρέθηκε υλικό.")

        else:

            selected_code = st.selectbox(
                "Select Material",
                matches["material_code"].tolist(),
                key="manage_material_select"
            )

            selected_row = materials_df[
                materials_df["material_code"] == selected_code
                ].iloc[0]

            st.write("### Edit Material")

            edit_name = st.text_input(
                "Material Name",
                value=str(selected_row["material_name"]),
                key="manage_material_name"
            )

            edit_stock = st.number_input(
                "Stock on Hand",
                value=float(selected_row["stock_on_hand"]),
                step=1.0,
                key="manage_stock_on_hand"
            )

            edit_unit = st.text_input(
                "Unit",
                value=str(selected_row["unit"]),
                key="manage_unit"
            )

            edit_supplier = st.text_input(
                "Supplier",
                value=str(selected_row["supplier"]),
                key="manage_supplier"
            )

            edit_lead_time = st.number_input(
                "Lead Time Days",
                value=float(selected_row["lead_time_days"])
                if pd.notna(selected_row["lead_time_days"])
                else 0.0,
                step=1.0,
                key="manage_lead_time"
            )

            if st.button(
                    "💾 Save Material Changes",
                    key="save_material_changes"
            ):
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                             UPDATE materials
                             SET material_name  = :material_name,
                                 stock_on_hand  = :stock_on_hand,
                                 unit           = :unit,
                                 supplier       = :supplier,
                                 lead_time_days = :lead_time_days
                             WHERE material_code = :material_code
                             """),
                        {
                            "material_name": edit_name.strip(),
                            "stock_on_hand": float(edit_stock),
                            "unit": edit_unit.strip(),
                            "supplier": edit_supplier.strip(),
                            "lead_time_days": float(edit_lead_time),
                            "material_code": selected_code
                        }
                    )

                log_action(
                    "UPDATE",
                    "materials",
                    0,
                    f"Material={selected_code}, Stock={edit_stock}, Supplier={edit_supplier}, LeadTime={edit_lead_time}"
                )

                run_inventory_update()

                st.success(
                    "Το υλικό ενημερώθηκε και το inventory ανανεώθηκε."
                )
