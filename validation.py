import streamlit as st
import pandas as pd

from db import engine

def validation_tab():
    st.subheader("⚠️ Validation")

    materials = pd.read_sql(
        "SELECT * FROM materials",
        engine
    )

    production = pd.read_sql(
        "SELECT * FROM production_log",
        engine
    )

    receipts = pd.read_sql(
        "SELECT * FROM receipts",
        engine
    )

    stages = pd.read_sql(
        "SELECT * FROM production_stages",
        engine
    )
    invalid_production_qty = production[
        production["quantity"] <= 0
        ]

    st.write("### Production Quantity Errors")

    if invalid_production_qty.empty:

        st.success("No production quantity errors")

    else:

        st.dataframe(
            invalid_production_qty,
            use_container_width=True
        )
        invalid_receipts_qty = receipts[
            receipts["qty_in"] <= 0
            ]

        st.write("### Receipt Quantity Errors")

        if invalid_receipts_qty.empty:

            st.success("No receipt quantity errors")

        else:

            st.dataframe(
                invalid_receipts_qty,
                use_container_width=True
            )
            invalid_receipt_materials = receipts[
                ~receipts["material_code"].isin(
                    materials["material_code"]
                )
            ]

            st.write("### Unknown Material Codes")

            if invalid_receipt_materials.empty:

                st.success("All material codes valid")

            else:

                st.dataframe(
                    invalid_receipt_materials,
                    use_container_width=True
                )
                invalid_stages = production[
                    ~production["stage_id"].isin(
                        stages["stage_id"]
                    )
                ]

                st.write("### Invalid Stage IDs")

                if invalid_stages.empty:

                    st.success("All stage IDs valid")

                else:

                    st.dataframe(
                        invalid_stages,
                        use_container_width=True
                    )
                    duplicate_materials = materials[
                        materials.duplicated(
                            subset=["material_code"],
                            keep=False
                        )
                    ]

                    st.write("### Duplicate Materials")

                    if duplicate_materials.empty:

                        st.success("No duplicate materials")

                    else:

                        st.dataframe(
                            duplicate_materials,
                            use_container_width=True
                        )