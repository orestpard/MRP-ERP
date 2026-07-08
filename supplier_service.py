from typing import Any

import pandas as pd
from sqlalchemy import text

from db import engine
from utils.audit import log_action


# =====================================================
# READ
# =====================================================

def get_suppliers() -> pd.DataFrame:
    """
    Return all suppliers.
    """

    query = """
        SELECT
            supplier_id,
            supplier_name,
            country,
            lead_time_days,
            active
        FROM suppliers
        ORDER BY supplier_name
    """

    return pd.read_sql(query, engine)


def get_active_suppliers() -> pd.DataFrame:
    """
    Return active suppliers.
    """

    query = """
        SELECT
            supplier_id,
            supplier_name,
            country,
            lead_time_days
        FROM suppliers
        WHERE active = 1
        ORDER BY supplier_name
    """

    return pd.read_sql(query, engine)


# =====================================================
# CREATE
# =====================================================

def create_supplier(
    supplier_name: str,
    country: str,
    lead_time_days: int,
) -> dict[str, Any]:
    """
    Create supplier.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO suppliers
                    (
                        supplier_name,
                        country,
                        lead_time_days,
                        active
                    )
                    VALUES
                    (
                        :supplier_name,
                        :country,
                        :lead_time_days,
                        1
                    )
                """),
                {
                    "supplier_name": supplier_name.strip(),
                    "country": country.strip(),
                    "lead_time_days": int(lead_time_days),
                },
            )

            supplier_id = conn.execute(
                text("SELECT LAST_INSERT_ID()")
            ).scalar()

            log_action(
                "CREATE",
                "suppliers",
                int(supplier_id),
                supplier_name
            )

        return {
            "success": True,
            "message": "Ο προμηθευτής δημιουργήθηκε.",
            "data": {
                "supplier_id": int(supplier_id)
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

def update_supplier(
    supplier_id: int,
    supplier_name: str,
    country: str,
    lead_time_days: int,
) -> dict[str, Any]:
    """
    Update supplier.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE suppliers
                    SET supplier_name = :supplier_name,
                        country = :country,
                        lead_time_days = :lead_time_days
                    WHERE supplier_id = :supplier_id
                """),
                {
                    "supplier_name": supplier_name.strip(),
                    "country": country.strip(),
                    "lead_time_days": int(lead_time_days),
                    "supplier_id": supplier_id,
                },
            )

            log_action(
                "UPDATE",
                "suppliers",
                supplier_id,
                supplier_name
            )

        return {
            "success": True,
            "message": "Ο προμηθευτής ενημερώθηκε.",
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
# STATUS
# =====================================================

def set_supplier_active(
    supplier_id: int,
    active: bool,
) -> dict[str, Any]:
    """
    Activate / Deactivate supplier.
    """

    try:

        with engine.begin() as conn:

            conn.execute(
                text("""
                    UPDATE suppliers
                    SET active = :active
                    WHERE supplier_id = :supplier_id
                """),
                {
                    "active": int(active),
                    "supplier_id": supplier_id,
                },
            )

            log_action(
                "UPDATE",
                "suppliers",
                supplier_id,
                f"Active={active}"
            )

        return {
            "success": True,
            "message": "Η κατάσταση ενημερώθηκε.",
            "data": None,
        }

    except Exception as e:

        print(e)

        return {
            "success": False,
            "message": str(e),
            "data": None,
        }