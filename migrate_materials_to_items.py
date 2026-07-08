import pandas as pd

from db import engine


# =====================================================
# LOAD MATERIALS
# =====================================================

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

print(f"Materials found: {len(materials)}")


# =====================================================
# CHECK EXISTING ITEMS
# =====================================================

existing = pd.read_sql(
    """
    SELECT material_code
    FROM items
    """,
    engine
)

existing_codes = set(existing["material_code"])


# =====================================================
# PREPARE NEW ITEMS
# =====================================================

new_items = materials[
    ~materials["material_code"].isin(existing_codes)
].copy()

new_items["stage_code"] = "RAW"
new_items["item_type"] = "MATERIAL"

new_items = new_items[
    [
        "material_code",
        "stage_code",
        "material_name",
        "unit",
        "item_type",
        "stock_on_hand",
    ]
]

new_items = new_items.rename(
    columns={
        "material_name": "item_name"
    }
)

print(f"New items to insert: {len(new_items)}")


# =====================================================
# INSERT
# =====================================================

if len(new_items):

    new_items.to_sql(
        "items",
        engine,
        if_exists="append",
        index=False
    )

    print("Items inserted successfully.")

else:

    print("Nothing to insert.")