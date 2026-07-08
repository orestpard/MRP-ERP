from typing import Any

import pandas as pd
from sqlalchemy import text

from db import engine
from utils.audit import log_action


# =====================================================
# READ
# =====================================================

def get_materials() -> pd.DataFrame:
    """
    Return all materials.
    """

    query = """
        SELECT
            material_id,
            CONCAT(material_code, ' - ', material_name) AS material
        FROM materials
        ORDER BY material_code
    """

    return pd.read_sql(query, engine)

def get_suppliers() -> pd.DataFrame:
    """
    Return active suppliers.
    """

    query = """
        SELECT
            supplier_id,
            supplier_name
        FROM suppliers
        WHERE active = 1
        ORDER BY supplier_name
    """

    return pd.read_sql(query, engine)

def create_item_supplier(
    material_id: int,
    supplier_id: int,
    lead_time_days: int,
    is_preferred: bool,
) -> dict[str, Any]:

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO item_suppliers
                    (
                        material_id,
                        supplier_id,
                        lead_time_days,
                        is_preferred
                    )
                    VALUES
                    (
                        :material_id,
                        :supplier_id,
                        :lead_time_days,
                        :is_preferred
                    )
                """),
                {
                    "material_id": material_id,
                    "supplier_id": supplier_id,
                    "lead_time_days": lead_time_days,
                    "is_preferred": int(is_preferred),
                }
            )

            new_id = conn.execute(
                text("SELECT LAST_INSERT_ID()")
            ).scalar()

            log_action(
                "CREATE",
                "item_suppliers",
                int(new_id),
                f"Material={material_id}, Supplier={supplier_id}"
            )

        return {
            "success": True,
            "message": "Supplier assigned successfully.",
            "data": {
                "item_supplier_id": int(new_id)
            }
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None
        }


def get_item_suppliers():
    return None