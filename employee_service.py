from typing import Any

import pandas as pd
from sqlalchemy import text

from db import engine
from utils.audit import log_action


# =====================================================
# READ
# =====================================================

def get_employees() -> pd.DataFrame:
    """
    Return all employees.
    """

    query = """
        SELECT
            employee_id,
            employee_name,
            active
        FROM employees
        ORDER BY employee_name
    """

    return pd.read_sql(query, engine)


def get_active_employees() -> pd.DataFrame:
    """
    Return active employees only.
    """

    query = """
        SELECT
            employee_id,
            employee_name
        FROM employees
        WHERE active = 1
        ORDER BY employee_name
    """

    return pd.read_sql(query, engine)


# =====================================================
# CREATE
# =====================================================

def create_employee(
    employee_name: str,
) -> dict[str, Any]:
    """
    Create employee.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO employees
                    (
                        employee_name,
                        active
                    )
                    VALUES
                    (
                        :employee_name,
                        1
                    )
                """),
                {
                    "employee_name": employee_name.strip(),
                },
            )

            employee_id = conn.execute(
                text("SELECT LAST_INSERT_ID()")
            ).scalar()

            log_action(
                "CREATE",
                "employees",
                int(employee_id),
                employee_name
            )

        return {
            "success": True,
            "message": "Ο υπάλληλος δημιουργήθηκε.",
            "data": {
                "employee_id": int(employee_id)
            }
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None
        }


# =====================================================
# UPDATE
# =====================================================

def update_employee(
    employee_id: int,
    employee_name: str,
) -> dict[str, Any]:
    """
    Update employee.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE employees
                    SET employee_name = :employee_name
                    WHERE employee_id = :employee_id
                """),
                {
                    "employee_name": employee_name.strip(),
                    "employee_id": employee_id,
                },
            )

            log_action(
                "UPDATE",
                "employees",
                employee_id,
                employee_name
            )

        return {
            "success": True,
            "message": "Ο υπάλληλος ενημερώθηκε.",
            "data": None
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None
        }


# =====================================================
# STATUS
# =====================================================

def set_employee_active(
    employee_id: int,
    active: bool,
) -> dict[str, Any]:
    """
    Activate / Deactivate employee.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE employees
                    SET active = :active
                    WHERE employee_id = :employee_id
                """),
                {
                    "active": int(active),
                    "employee_id": employee_id,
                },
            )

            log_action(
                "UPDATE",
                "employees",
                employee_id,
                f"Active={active}"
            )

        return {
            "success": True,
            "message": "Η κατάσταση ενημερώθηκε.",
            "data": None
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None
        }


# =====================================================
# DELETE
# =====================================================

def delete_employee(
    employee_id: int,
) -> dict[str, Any]:
    """
    Delete employee.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    DELETE
                    FROM employees
                    WHERE employee_id = :employee_id
                """),
                {
                    "employee_id": employee_id,
                },
            )

            log_action(
                "DELETE",
                "employees",
                employee_id,
            )

        return {
            "success": True,
            "message": "Ο υπάλληλος διαγράφηκε.",
            "data": None
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None
        }