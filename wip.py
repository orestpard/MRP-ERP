import streamlit as st

from config import REPORT_FILE
from services.report_service import load_report_sheet

def wip_tab():
    st.subheader(
        "🏭 Work In Progress / Internal Production"
    )

    if REPORT_FILE.exists():

        stock_df = load_report_sheet(
            "inventory_status"
        )

        outputs = load_report_sheet(
            "outputs"
        )

        output_detail = load_report_sheet(
            "output_detail"
        )

        if not stock_df.empty:

            stock_df["material_code"] = (
                stock_df["material_code"]
                .astype(str)
            )

            wip = stock_df[
                stock_df["material_code"]
                .str.contains(r"\|S", na=False)
            ]

            raw = stock_df[
                stock_df["material_code"]
                .str.contains(
                    "RAW",
                    case=False,
                    na=False
                )
            ]

            finished = stock_df[
                stock_df["material_code"]
                .str.contains(
                    "FIN",
                    case=False,
                    na=False
                )
            ]

            st.subheader("🏭 WIP Materials")

            if not wip.empty:

                st.dataframe(
                    wip,
                    use_container_width=True
                )

            else:

                st.info(
                    "Δεν βρέθηκαν WIP materials."
                )

            st.subheader("🧱 Raw Materials")

            if not raw.empty:

                st.dataframe(
                    raw,
                    use_container_width=True
                )

            else:

                st.info(
                    "Δεν βρέθηκαν RAW materials."
                )

            st.subheader(
                "📦 Finished / Final Materials"
            )

            if not finished.empty:

                st.dataframe(
                    finished,
                    use_container_width=True
                )

            else:

                st.info(
                    "Δεν βρέθηκαν FIN materials."
                )

        st.divider()

        st.subheader(
            "🔄 Internal Production Outputs"
        )

        if not outputs.empty:

            st.dataframe(
                outputs,
                use_container_width=True
            )

        else:

            st.info(
                "Δεν υπάρχουν outputs."
            )

        st.subheader("🔎 Output Detail")

        if not output_detail.empty:

            st.dataframe(
                output_detail.tail(100),
                use_container_width=True
            )

        else:

            st.info(
                "Δεν υπάρχει output_detail."
            )

    else:

        st.warning(
            "Δεν υπάρχει inventory_report_v4.xlsx ακόμα."
        )