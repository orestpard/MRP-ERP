import pandas as pd
from sqlalchemy import text

from db import engine


def migrate_raw_items():

    print("======================================")
    print("RAW INVENTORY MIGRATION")
    print("======================================")

    # -----------------------------------
    # Load materials
    # -----------------------------------

    materials = pd.read_sql(
        """
        SELECT
            material_code,
            material_name,
            unit,
            stock_on_hand
        FROM materials
        ORDER BY material_code
        """,
        engine
    )

    print(f"Materials found : {len(materials)}")

    inserted = 0
    skipped = 0

    with engine.begin() as conn:

        for _, row in materials.iterrows():

            exists = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM items
                    WHERE material_code = :material_code
                      AND stage_code = 'RAW'
                """),
                {
                    "material_code": row["material_code"]
                }
            ).scalar()

            if exists:
                skipped += 1
                continue

            conn.execute(
                text("""
                    INSERT INTO items
                    (
                        material_code,
                        stage_code,
                        item_name,
                        unit,
                        item_type,
                        stock_on_hand
                    )
                    VALUES
                    (
                        :material_code,
                        'RAW',
                        :item_name,
                        :unit,
                        'RAW',
                        :stock
                    )
                """),
                {
                    "material_code": row["material_code"],
                    "item_name": row["material_name"],
                    "unit": row["unit"],
                    "stock": row["stock_on_hand"]
                }
            )

            inserted += 1

    print()
    print(f"Inserted : {inserted}")
    print(f"Skipped  : {skipped}")
    print()
    print("Migration completed.")


if __name__ == "__main__":

    migrate_raw_items()