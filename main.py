import pandas as pd

# Load files
daily = pd.read_excel("C:/Users/Orestis Pardalis/PycharmProjects/PythonProject/Spacesonic_1/logistics_plan/daily_production.xlsx")
materials_stage = pd.read_excel("C:/Users/Orestis Pardalis/PycharmProjects/PythonProject/Spacesonic_1/logistics_plan/materials_stage.xlsx", sheet_name="all_stages")
materials_master = pd.read_excel("C:/Users/Orestis Pardalis/PycharmProjects/PythonProject/Spacesonic_1/logistics_plan/materials_master_v2.xlsx", sheet_name="ATRAX_CONTROL_UNIT")

# --- STEP 1: Join production with materials ---
df = daily.merge(materials_stage, on="stage_id", how="left")

# --- STEP 2: Calculate consumption ---
df["consumption"] = df["quantity"] * df["quantity_per_unit"]

# --- STEP 3: Aggregate per material ---
consumption_per_material = (
    df.groupby("material_code")["consumption"]
    .sum()
    .reset_index()
)

# --- STEP 4: Merge with stock ---
stock = materials_master[["material_code", "stock_on_hand"]]

inventory = stock.merge(consumption_per_material, on="material_code", how="left")
inventory["consumption"] = inventory["consumption"].fillna(0)

# --- STEP 5: Calculate new stock ---
inventory["new_stock"] = inventory["stock_on_hand"] - inventory["consumption"]

# --- STEP 6: Alerts ---
inventory["alert"] = inventory["new_stock"] < 1000  # threshold

print(inventory)
