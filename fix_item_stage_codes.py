import pandas as pd
from sqlalchemy import text

from db import engine


def fix_stage_codes():

    print("Fixing stage codes...")

    items = pd.read_sql(
        """
        SELECT
            item_id,
            material_code
        FROM items
        """,
        engine
    )

    updated = 0

    with engine.begin() as conn:

        for _, row in items.iterrows():

            code = row["material_code"]

            if "|" not in code:
                continue

            stage = code.split("|")[1].strip()

            conn.execute(
                text("""
                    UPDATE items
                    SET stage_code = :stage
                    WHERE item_id = :item_id
                """),
                {
                    "stage": stage,
                    "item_id": row["item_id"]
                }
            )

            updated += 1

    print(f"Updated {updated} items.")


if __name__ == "__main__":

    fix_stage_codes()