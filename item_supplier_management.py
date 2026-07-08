import streamlit as st

from services.item_supplier_service import (
    get_materials,
    get_suppliers,
    get_item_suppliers,
    create_item_supplier,
)


def item_supplier_management_tab():

    st.subheader("🔗 Item Supplier Management")

    materials = get_materials()

    suppliers = get_suppliers()

    if materials.empty:

        st.warning("Δεν υπάρχουν υλικά.")

        return

    if suppliers.empty:

        st.warning("Δεν υπάρχουν προμηθευτές.")

        return

    material_display = st.selectbox(
        "Material",
        materials["material"].tolist()
    )

    material_id = int(
        materials.loc[
            materials["material"] == material_display,
            "item_id"
        ].iloc[0]
    )

    st.divider()

    st.subheader("Current Suppliers")

    current = get_item_suppliers(material_id)

    if current.empty:

        st.info("Δεν υπάρχουν προμηθευτές για αυτό το υλικό.")

    else:

        st.dataframe(
            current,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("➕ Add Supplier")

    supplier_name = st.selectbox(
        "Supplier",
        suppliers["supplier_name"].tolist()
    )

    supplier_id = int(
        suppliers.loc[
            suppliers["supplier_name"] == supplier_name,
            "supplier_id"
        ].iloc[0]
    )

    lead_time = st.number_input(
        "Lead Time (days)",
        min_value=1,
        value=60,
        step=1
    )

    preferred = st.checkbox(
        "Preferred Supplier"
    )

    if st.button("➕ Assign Supplier"):

        result = create_item_supplier(
            material_id=material_id,
            supplier_id=supplier_id,
            lead_time_days=int(lead_time),
            is_preferred=preferred
        )

        if result["success"]:

            st.success(result["message"])

            st.rerun()

        else:

            st.error(result["message"])