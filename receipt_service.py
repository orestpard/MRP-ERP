from typing import Any

import pandas as pd
from sqlalchemy import text

from db import engine
from services.inventory_service import run_inventory_update
from services.inventory_service_v2 import InventoryService
from utils.audit import log_action


# =====================================================
# READ
# =====================================================

def get_receipts_history() -> pd.DataFrame:
    """
    Return receipts history.
    """

    query = """
        SELECT *
        FROM receipts
        ORDER BY id DESC
    """

    return pd.read_sql(query, engine)


# =====================================================
# CREATE
# =====================================================

def save_receipt(
    receipt_date,
    material_code: str,
    qty_in: float,
    supplier: str,
    price=None,
    reference_number=None,
) -> dict[str, Any]:
    """
    Save a receipt transaction.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO receipts
                    (
                        receipt_date,
                        material_code,
                        qty_in,
                        supplier,
                        price,
                        reference_number
                    )
                    VALUES
                    (
                        :receipt_date,
                        :material_code,
                        :qty_in,
                        :supplier,
                        :price,
                        :reference_number
                    )
                """),
                {
                    "receipt_date": receipt_date,
                    "material_code": material_code.strip(),
                    "qty_in": qty_in,
                    "supplier": supplier.strip(),
                    "price": price,
                    "reference_number": reference_number,
                },
            )

            receipt_id = conn.execute(
                text("SELECT LAST_INSERT_ID()")
            ).scalar()

            log_action(
                "CREATE",
                "receipts",
                int(receipt_id),
                f"Material={material_code}, Qty={qty_in}"
            )

        run_inventory_update()
        # -----------------------------------------
        # Update new Inventory Engine
        # -----------------------------------------

        inventory = InventoryService()

        inventory_result = inventory.receive_material(
            material_code=material_code.strip(),
            quantity=qty_in,
            reference=reference_number,
            created_by="Receipt Service"
        )

        if not inventory_result["success"]:
            raise Exception(inventory_result["message"])
        return {
            "success": True,
            "message": "Το receipt καταχωρήθηκε επιτυχώς.",
            "data": {
                "receipt_id": int(receipt_id)
            }
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None,
        }


# =====================================================
# UPDATE
# =====================================================

def update_receipt(
    receipt_id: int,
    receipt_date,
    material_code: str,
    qty_in: float,
    supplier: str,
) -> dict[str, Any]:
    """
    Update receipt.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE receipts
                    SET receipt_date = :receipt_date,
                        material_code = :material_code,
                        qty_in = :qty_in,
                        supplier = :supplier
                    WHERE id = :id
                """),
                {
                    "receipt_date": receipt_date,
                    "material_code": material_code.strip(),
                    "qty_in": qty_in,
                    "supplier": supplier.strip(),
                    "id": receipt_id,
                },
            )

            log_action(
                "UPDATE",
                "receipts",
                receipt_id,
                f"Material={material_code}, Qty={qty_in}"
            )

        run_inventory_update()

        return {
            "success": True,
            "message": "Το receipt ενημερώθηκε.",
            "data": None,
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None,
        }


# =====================================================
# DELETE
# =====================================================

def delete_receipt(
    receipt_id: int,
) -> dict[str, Any]:
    """
    Delete receipt.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE
                    FROM receipts
                    WHERE id = :id
                """),
                {
                    "id": receipt_id
                },
            )

            log_action(
                "DELETE",
                "receipts",
                receipt_id,
            )

        run_inventory_update()

        return {
            "success": True,
            "message": "Το receipt διαγράφηκε.",
            "data": None,
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None,
        }