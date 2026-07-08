import streamlit as st

from services.supplier_service import (
    get_suppliers,
    create_supplier,
    update_supplier,
    set_supplier_active,
)


def supplier_management_tab():

    st.subheader("🏢 Supplier Management")

    suppliers = get_suppliers()

    st.metric(
        "Συνολικοί Προμηθευτές",
        len(suppliers)
    )

    st.dataframe(
        suppliers,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================================
    # ADD SUPPLIER
    # =====================================================

    st.subheader("➕ Add Supplier")

    supplier_name = st.text_input(
        "Supplier Name",
        key="new_supplier_name"
    )

    country = st.text_input(
        "Country",
        key="new_supplier_country"
    )

    lead_time = st.number_input(
        "Lead Time (days)",
        min_value=1,
        value=60,
        step=1,
        key="new_supplier_lead_time"
    )

    if st.button("➕ Add Supplier"):

        if not supplier_name.strip():

            st.warning("Συμπλήρωσε Supplier Name.")

        elif supplier_name.strip() in suppliers["supplier_name"].values:

            st.warning("Ο προμηθευτής υπάρχει ήδη.")

        else:

            result = create_supplier(
                supplier_name=supplier_name,
                country=country,
                lead_time_days=int(lead_time)
            )

            if result["success"]:

                st.success(result["message"])
                st.rerun()

            else:

                st.error(result["message"])

    # =====================================================
    # UPDATE SUPPLIER
    # =====================================================

    if suppliers.empty:

        st.info(
            "Δεν υπάρχουν ακόμα προμηθευτές."
        )

        return

    st.divider()

    st.subheader("✏️ Update Supplier")

    supplier_id = st.selectbox(
        "Supplier",
        suppliers["supplier_id"].tolist(),
        key="edit_supplier_id"
    )

    row = suppliers[
        suppliers["supplier_id"] == supplier_id
    ].iloc[0]

    edit_name = st.text_input(
        "Supplier Name",
        value=row["supplier_name"],
        key="edit_supplier_name"
    )

    edit_country = st.text_input(
        "Country",
        value=row["country"] if row["country"] else "",
        key="edit_supplier_country"
    )

    edit_lead = st.number_input(
        "Lead Time",
        min_value=1,
        value=int(row["lead_time_days"]),
        key="edit_supplier_lead"
    )

    active = st.checkbox(
        "Active",
        value=bool(row["active"]),
        key="edit_supplier_active"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("💾 Save Supplier"):

            result = update_supplier(
                supplier_id=supplier_id,
                supplier_name=edit_name,
                country=edit_country,
                lead_time_days=int(edit_lead)
            )

            if result["success"]:

                set_supplier_active(
                    supplier_id=supplier_id,
                    active=active
                )

                st.success("Ο προμηθευτής ενημερώθηκε.")

                st.rerun()

            else:

                st.error(result["message"])