from typing import Any

import pandas as pd
from sqlalchemy import text

from db import engine
from services.inventory_service import run_inventory_update
from utils.audit import log_action
from services.inventory_service_v2 import InventoryService

inventory = InventoryService()

# =====================================================
# READ
# =====================================================

def get_production_history() -> pd.DataFrame:
    """
    Return production history.
    """

    query = """
        SELECT
            p.id,
            p.production_date,
            p.stage_id,
            p.model,
            p.quantity,
            p.head_count,
            e.employee_name
        FROM production_log p
        LEFT JOIN employees e
            ON p.employee_id = e.employee_id
        ORDER BY p.id DESC
    """

    return pd.read_sql(query, engine)


# =====================================================
# CREATE
# =====================================================

def save_production(
    production_date,
    stage_id: int,
    model: str,
    quantity: float,
    head_count: int,
    employee_id: int,
) -> dict[str, Any]:
    """
    Create a new production transaction.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO production_log
                    (
                        production_date,
                        stage_id,
                        model,
                        quantity,
                        head_count,
                        employee_id
                    )
                    VALUES
                    (
                        :production_date,
                        :stage_id,
                        :model,
                        :quantity,
                        :head_count,
                        :employee_id
                    )
                """),
                {
                    "production_date": production_date,
                    "stage_id": stage_id,
                    "model": model,
                    "quantity": quantity,
                    "head_count": head_count,
                    "employee_id": employee_id,
                },
            )

            production_id = conn.execute(
                text("SELECT LAST_INSERT_ID()")
            ).scalar()


            log_action(
                "CREATE",
                "production_log",
                int(production_id),
                f"Employee={employee_id}, Model={model}, Qty={quantity}"
            )

        result = inventory.execute_stage_production(
            stage_id=stage_id,
            model=model,
            quantity=quantity,
            work_order_id=production_id,
            created_by="Production Service"
        )

        print("Inventory Result:", result)

        if not result["success"]:
            return result

        #run_inventory_update()

        return {
            "success": True,
            "message": "Η παραγωγή καταχωρήθηκε επιτυχώς.",
            "data": {
                "production_id": int(production_id)
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

def update_production(
    production_id: int,
    production_date,
    stage_id: int,
    model: str,
    quantity: float,
    head_count: int,
) -> dict[str, Any]:
    """
    Update an existing production transaction.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE production_log
                    SET production_date = :production_date,
                        stage_id = :stage_id,
                        model = :model,
                        quantity = :quantity,
                        head_count = :head_count
                    WHERE id = :id
                """),
                {
                    "production_date": production_date,
                    "stage_id": stage_id,
                    "model": model,
                    "quantity": quantity,
                    "head_count": head_count,
                    "id": production_id,
                },
            )

            log_action(
                "UPDATE",
                "production_log",
                production_id,
                f"Model={model}, Qty={quantity}"
            )

        run_inventory_update()

        return {
            "success": True,
            "message": "Η παραγωγή ενημερώθηκε.",
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

def delete_production(
    production_id: int,
) -> dict[str, Any]:
    """
    Delete a production transaction.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE
                    FROM production_log
                    WHERE id = :id
                """),
                {
                    "id": production_id,
                },
            )

            log_action(
                "DELETE",
                "production_log",
                production_id,
            )

        run_inventory_update()

        return {
            "success": True,
            "message": "Η εγγραφή διαγράφηκε.",
            "data": None,
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None,
        }


