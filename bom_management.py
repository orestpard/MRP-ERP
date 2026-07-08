import streamlit as st
import pandas as pd

from sqlalchemy import text

from db import engine
from utils.audit import log_action

def bom_management_tab():
    st.subheader("🛠 BOM Management")

    # ============================================
    # MODELS
    # ============================================

    models = pd.read_sql(
        """
        SELECT DISTINCT model
        FROM stage_inputs
        ORDER BY model
        """,
        engine
    )

    selected_model = st.selectbox(
        "Model",
        models["model"],
        key="bom_model"
    )

    # ============================================
    # STAGES
    # ============================================

    stages = pd.read_sql(
        f"""
            SELECT DISTINCT stage_id
            FROM stage_inputs
            WHERE model='{selected_model}'
            ORDER BY stage_id
            """,
        engine
    )

    selected_stage = st.selectbox(
        "Stage",
        stages["stage_id"],
        key="bom_stage"
    )

    # ============================================
    # INPUTS
    # ============================================

    st.markdown("### Inputs")

    inputs = pd.read_sql(
        f"""
            SELECT
                id,
                material_code,
                quantity_per_unit,
                use_head_count
            FROM stage_inputs
            WHERE model='{selected_model}'
            AND stage_id={selected_stage}
            ORDER BY id
            """,
        engine
    )

    edited_inputs = st.data_editor(
        inputs,
        use_container_width=True,
        num_rows="fixed",
        key="bom_inputs_editor"
    )

    if st.button(
            "💾 Save Employee Changes",
            key="employee_save_changes_button"
    ):

        with engine.begin() as conn:

            for _, row in edited_employees.iterrows():
                conn.execute(
                    text("""
                         UPDATE employees
                         SET employee_name = :name,
                             active        = :active
                         WHERE employee_id = :id
                         """),
                    {
                        "id": int(row["employee_id"]),
                        "name": row["employee_name"].strip(),
                        "active": int(row["active"])
                    }
                )

                log_action(
                    "UPDATE",
                    "employees",
                    int(row["employee_id"]),
                    f"Employee={row['employee_name']}"
                )

        st.success("Employee changes saved.")

        st.rerun()

    if st.button(
            "💾 Save Employee Changes",
            key="save_employee_changes"
    ):

        with engine.begin() as conn:

            for _, row in edited_employees.iterrows():
                conn.execute(
                    text("""
                         UPDATE employees
                         SET employee_name = :name,
                             active        = :active
                         WHERE employee_id = :id
                         """),
                    {
                        "id": int(row["employee_id"]),
                        "name": row["employee_name"].strip(),
                        "active": int(row["active"])
                    }
                )

                log_action(
                    "UPDATE",
                    "employees",
                    int(row["employee_id"]),
                    f"Employee={row['employee_name']}"
                )

        st.success("Employee changes saved successfully.")

        st.rerun()

    # ============================================
    # ADD NEW INPUT
    # ============================================

    st.markdown("---")
    st.markdown("### ➕ Add Input Material")

    materials = pd.read_sql(
        """
        SELECT material_code
        FROM materials
        ORDER BY material_code
        """,
        engine
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        new_material = st.selectbox(
            "Material",
            materials["material_code"],
            key="new_bom_material"
        )

    with col2:

        new_qty = st.number_input(
            "Quantity",
            min_value=0.0001,
            value=1.0,
            step=0.1,
            key="new_bom_qty"
        )

    with col3:

        new_head = st.selectbox(
            "Use Head Count",
            [0, 1],
            key="new_bom_head"
        )
    if st.button(
            "➕ Add Input",
            key="add_input"
    ):

        exists = pd.read_sql(
            f"""
                SELECT COUNT(*) AS cnt
                FROM stage_inputs
                WHERE
                    model='{selected_model}'
                    AND stage_id={selected_stage}
                    AND material_code='{new_material}'
                """,
            engine
        )

        if exists.loc[0, "cnt"] > 0:

            st.warning(
                "Material already exists in this stage."
            )

        else:

            with engine.begin() as conn:

                conn.execute(
                    text("""
                         INSERT INTO stage_inputs
                         (stage_id,
                          model,
                          material_code,
                          quantity_per_unit,
                          use_head_count)
                         VALUES (:stage,
                                 :model,
                                 :material,
                                 :qty,
                                 :head)
                         """),
                    {
                        "stage": selected_stage,
                        "model": selected_model,
                        "material": new_material,
                        "qty": new_qty,
                        "head": new_head
                    }
                )

            log_action(
                "CREATE",
                "BOM",
                0,
                f"{selected_model} Stage {selected_stage}"
            )

            run_inventory_update()

            st.success("Input added successfully.")

            st.rerun()

    # ============================================
    # DELETE INPUT
    # ============================================

    st.markdown("---")
    st.markdown("### 🗑 Delete Input Material")

    if inputs.empty:

        st.info("Δεν υπάρχουν inputs για διαγραφή σε αυτό το stage.")

    else:

        delete_options = inputs.copy()

        delete_options["display"] = (
                delete_options["id"].astype(str)
                + " | "
                + delete_options["material_code"].astype(str)
                + " | Qty: "
                + delete_options["quantity_per_unit"].astype(str)
        )

        selected_delete = st.selectbox(
            "Select input to delete",
            delete_options["display"],
            key="delete_input_select"
        )

        selected_delete_id = int(
            selected_delete.split(" | ")[0]
        )

        confirm_delete = st.checkbox(
            "Επιβεβαιώνω ότι θέλω να διαγράψω αυτό το input.",
            key="confirm_delete_input"
        )

        if st.button(
                "🗑 Delete Input",
                key="delete_input_button"
        ):

            if not confirm_delete:

                st.warning(
                    "Πρέπει πρώτα να επιβεβαιώσεις τη διαγραφή."
                )

            else:

                row_to_delete = inputs[
                    inputs["id"] == selected_delete_id
                    ].iloc[0]

                with engine.begin() as conn:

                    conn.execute(
                        text("""
                             DELETE
                             FROM stage_inputs
                             WHERE id = :id
                             """),
                        {
                            "id": selected_delete_id
                        }
                    )

                log_action(
                    "DELETE",
                    "BOM",
                    selected_delete_id,
                    f"Deleted input {row_to_delete['material_code']} from Model={selected_model}, Stage={selected_stage}"
                )

                run_inventory_update()

                st.success(
                    "Input deleted successfully."
                )

                st.rerun()
    # ============================================
    # OUTPUTS
    # ============================================

    st.markdown("### Outputs")

    outputs = pd.read_sql(
        f"""
            SELECT
                id,
                output_material,
                output_qty
            FROM stage_outputs
            WHERE model='{selected_model}'
            AND stage_id={selected_stage}
            ORDER BY id
            """,
        engine
    )

    edited_outputs = st.data_editor(
        outputs,
        use_container_width=True,
        num_rows="fixed",
        key="bom_outputs_editor"
    )
    # ============================================
    # WHERE IS THIS MATERIAL USED
    # ============================================

    st.markdown("---")
    st.subheader("🔍 Where is this material used?")

    material_search = st.text_input(
        "Material Code",
        key="where_used_search"
    )
    if material_search:

        where_used = pd.read_sql(
            """
            SELECT model,
                   stage_id,
                   material_code,
                   quantity_per_unit,
                   use_head_count
            FROM stage_inputs
            WHERE material_code LIKE %(search)s
            ORDER BY model,
                     stage_id
            """,
            engine,
            params={
                "search": f"%{material_search}%"
            }
        )

        if where_used.empty:

            st.warning(
                "Material not found."
            )

        else:

            st.dataframe(
                where_used,
                use_container_width=True
            )

            st.success(
                f"Found {len(where_used)} usages."
            )
    # ============================================
    # SAVE BUTTON
    # ============================================

    if st.button(
            "💾 Save BOM",
            key="save_bom"
    ):

        with engine.begin() as conn:

            # -------------------------------
            # UPDATE INPUTS
            # -------------------------------

            for _, row in edited_inputs.iterrows():
                conn.execute(
                    text("""
                         UPDATE stage_inputs
                         SET material_code     = :material,
                             quantity_per_unit = :qty,
                             use_head_count    = :head
                         WHERE id = :id
                         """),
                    {
                        "id": int(row["id"]),
                        "material": str(row["material_code"]).strip(),
                        "qty": float(row["quantity_per_unit"]),
                        "head": int(row["use_head_count"])
                    }
                )

            # -------------------------------
            # UPDATE OUTPUTS
            # -------------------------------

            for _, row in edited_outputs.iterrows():
                conn.execute(
                    text("""
                         UPDATE stage_outputs
                         SET output_material = :material,
                             output_qty      = :qty
                         WHERE id = :id
                         """),
                    {
                        "id": int(row["id"]),
                        "material": str(row["output_material"]).strip(),
                        "qty": float(row["output_qty"])
                    }
                )

        log_action(
            "UPDATE",
            "BOM",
            0,
            f"Model={selected_model}, Stage={selected_stage}"
        )

        run_inventory_update()

        st.success(
            "✅ BOM updated successfully."
        )

        st.rerun()