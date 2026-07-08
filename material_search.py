import streamlit as st
import pandas as pd

from db import engine
from config import REPORT_FILE

def material_search_tab():
    st.subheader("🔎 Material Search")

    stock = pd.read_excel(
        "inventory_report_v4.xlsx",
        sheet_name="inventory_status"
    )

    material_code = st.text_input(
        "Material Code"
    )

    if material_code:

        result = stock[
            stock["material_code"]
            .astype(str)
            .str.contains(
                material_code,
                case=False,
                na=False
            )
        ]

        if result.empty:

            st.warning(
                "Δεν βρέθηκε υλικό."
            )

        else:

            row = result.iloc[0]

            receipts_df = pd.read_sql(
                """
                SELECT *
                FROM receipts
                WHERE material_code = %s
                ORDER BY receipt_date DESC LIMIT 10
                """,
                engine,
                params=(row["material_code"],)
            )

            consumption_detail = pd.read_excel(
                REPORT_FILE,
                sheet_name="consumption_detail"
            )

            material_consumption = consumption_detail[
                consumption_detail["material_code"].astype(str)
                == str(row["material_code"])
                ].copy()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Current Stock",
                    round(
                        row["current_stock"],
                        2
                    )
                )
            current_stock = float(row["current_stock"])

            if current_stock < 0:

                st.error("🔴 NEGATIVE STOCK")

            elif current_stock < 100:

                st.warning("🟡 LOW STOCK")

            else:

                st.success("🟢 STOCK OK")

            with col2:
                st.metric(
                    "Supplier",
                    str(row["supplier"])
                )

            with col3:
                st.metric(
                    "Lead Time",
                    row["lead_time_days"]
                )

            st.write("### Material Details")

            st.write(
                {
                    "Material Code":
                        row["material_code"],
                    "Material Name":
                        row["material_name"],
                    "Unit":
                        row["unit"],
                    "Inventory Status":
                        row["inventory_status"]
                }
            )

            st.write("### Inventory Summary")

            summary = {
                "Current Stock":
                    row["current_stock"],
                "Consumption":
                    row["consumption"],
                "Qty In":
                    row["qty_in"],
                "Qty Out":
                    row["qty_out"],
                "Inventory Status":
                    row["inventory_status"]
            }

            st.write(summary)

            st.metric(
                "Συνολική Κατανάλωση",
                round(
                    row["consumption"],
                    2
                )
            )

            st.write("### Full Record")

            st.dataframe(
                result,
                use_container_width=True
            )

            st.write("### 📦 Τελευταίες Αγορές")

            if receipts_df.empty:

                st.info(
                    "Δεν υπάρχουν receipts για το υλικό."
                )

            else:

                st.dataframe(
                    receipts_df[
                        [
                            "receipt_date",
                            "qty_in",
                            "supplier"
                        ]
                    ],
                    use_container_width=True
                )

                st.write("### 🏭 Κατανάλωση Υλικού")

                if material_consumption.empty:

                    st.info("Δεν υπάρχει κατανάλωση για το υλικό.")

                else:

                    st.metric(
                        "Συνολική Κατανάλωση",
                        round(
                            material_consumption["consumption"].sum(),
                            2
                        )
                    )

                    show_cols = [
                        "production_date",
                        "stage_id",
                        "model",
                        "quantity",
                        "quantity_per_unit",
                        "consumption"
                    ]

                    existing_cols = [
                        col for col in show_cols
                        if col in material_consumption.columns
                    ]

                    st.dataframe(
                        material_consumption[existing_cols]
                        .tail(20)
                        .sort_index(ascending=False),
                        use_container_width=True
                    )

                st.metric(
                    "Συνολικές Αγορές",
                    round(
                        receipts_df["qty_in"].sum(),
                        2
                    )
                )
                st.metric(
                    "Αριθμός Receipts",
                    len(receipts_df)
                )
                if not receipts_df.empty:
                    last_receipt = receipts_df[
                        "receipt_date"
                    ].max()

                    if not receipts_df.empty:
                        last_receipt = receipts_df[
                            "receipt_date"
                        ].max()

                        st.metric(
                            "Τελευταία Αγορά",
                            pd.to_datetime(
                                last_receipt
                            ).strftime("%d/%m/%Y")
                        )
