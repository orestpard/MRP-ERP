import pandas as pd
from sqlalchemy import text

from db import engine

# =====================================================
# LOAD MASTER
# =====================================================

master = pd.read_excel("C:/Users/Orestis Pardalis/PycharmProjects/PythonProject/Spacesonic_1/logistics_plan/materials_master_v3.xlsx")

master["material_code"] = (
    master["material_code"]
    .astype(str)
    .str.strip()
)

master["stock_on_hand"] = pd.to_numeric(
    master["stock_on_hand"],
    errors="coerce"
).fillna(0)

print(f"Materials loaded: {len(master)}")

# =====================================================
# RESTORE STOCK
# =====================================================

updated = 0

with engine.begin() as conn:

    for _, row in master.iterrows():

        result = conn.execute(
            text("""
                UPDATE materials
                SET stock_on_hand = :stock
                WHERE material_code = :code
            """),
            {
                "stock": float(row["stock_on_hand"]),
                "code": row["material_code"],
            }
        )

        updated += result.rowcount

print(f"Updated rows: {updated}")

print("Stock restored successfully.")