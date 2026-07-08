import pandas as pd
import streamlit as st

# =========================================================
# LOCAL PROJECT
# =========================================================

from db import engine

# =========================================================
# TABS
# =========================================================

from tabs.audit_log import audit_log_tab
from tabs.analytics import analytics_tab
from tabs.bom_management import bom_management_tab
from tabs.dashboard import dashboard_tab
from tabs.employee_management import employee_management_tab
from tabs.material_management import material_management_tab
from tabs.material_search import material_search_tab
from tabs.production_history import production_history_tab
from tabs.receipts_history import receipts_history_tab
from tabs.validation import validation_tab
from tabs.wip import wip_tab
from tabs.procurement import procurement_tab
from tabs.production import production_tab
from tabs.purchase_orders import purchase_orders_tab
from tabs.receipts import receipts_tab
#from tabs.item_supplier_management import item_supplier_management_tab
from tabs.supplier_management import supplier_management_tab

# =========================================================
# PAGE
# =========================================================
st.set_page_config(layout="wide")

st.title("📦 Inventory Management System V4")


# =========================================================
# LOAD STAGES
# =========================================================
stages = pd.read_sql(
    """
    SELECT
        stage_id,
        stage_name
    FROM production_stages
    ORDER BY stage_id
    """,
    engine
)

if not stages.empty:

    stages["label"] = (
        stages["stage_id"].astype(str)
        + " - "
        + stages["stage_name"].astype(str)
    )

else:

    stages = pd.DataFrame({
        "stage_id": [1],
        "stage_name": ["Unknown"],
        "label": ["1 - Unknown"]
    })


# =========================================================
# MODELS
# =========================================================
models = [
    "all_models",
    "atrax_4",
    "atrax_5",
    "atrax_sonic",
    "atrax_3",
    "atrax_3_plus",
    "ulix_5",
    "ulix_7",
    "bellota_va1",
    "bellota_va1_pro"
]


# =========================================================
# TABS
# =========================================================
TAB_NAMES = [
    "📥 Production",
    "📦 Receipts",
    "📋 Production History",
    "📦 Receipts History",
    "📜 Audit Log",
    "🔎 Material Search",
    "🧰 Material Management",
    "👥 Employee Management",
    "🏢 Suppliers",
    #"🔗 Item Suppliers",
    "🛠 BOM Management",
    "📊 Dashboard",
    "🏭 WIP",
    "📈 Analytics",
    "⚠️ Validation",
    "📦 Procurement",
    "🛒 Purchase Orders"
]

tabs = st.tabs(TAB_NAMES)


# =========================================================
# TAB 1 — PRODUCTION
# =========================================================
with tabs[0]:

    production_tab(stages, models)

# =========================================================
# TAB 2 — RECEIPTS
# =========================================================
with tabs[1]:

    receipts_tab()

# =========================================================
# TAB 3 — PRODUCTION HISTORY
# =========================================================
with tabs[2]:
    production_history_tab()

# =========================================================
# TAB 4 — RECEIPTS HISTORY
# =========================================================
with tabs[3]:
        receipts_history_tab()

# =========================================================
# TAB 5 — AUDIT LOG
# =========================================================
with tabs[4]:

        audit_log_tab()

# =========================================================
# TAB 6 — MATERIAL SEARCH
# =========================================================
with tabs[5]:

        material_search_tab()

# =========================================================
# MATERIAL MANAGEMENT
# =========================================================
with tabs[6]:

    material_management_tab()

# =========================================================
# EMPLOYEE MANAGEMENT
# =========================================================
with tabs[7]:

    employee_management_tab()


# =========================================================
# SUPPLIER
# =========================================================
with tabs[8]:
    supplier_management_tab()

# =========================================================
# ITEM_SUPPLIER
#=========================================================
#with tabs[9]:
   # item_supplier_management_tab()

# =========================================================
# BOM MANAGEMENT
# =========================================================
with tabs[9]:

    bom_management_tab()

# =========================================================
# TAB 3 — DASHBOARD
# =========================================================
with tabs[10]:

    dashboard_tab()

 # =========================================================
 # TAB 4 — WIP / OUTPUTS
 # =========================================================
with tabs[11]:
    wip_tab()

# =========================================================
# TAB 5 — ANALYTICS
# =========================================================
with tabs[12]:
    analytics_tab()

# =========================================================
# TAB 10 — VALIDATION
# =========================================================
with tabs[13]:

    validation_tab()


# =========================================================
# PROCUREMENT PLANNING
# =========================================================

with tabs[14]:
    procurement_tab()

# =========================================================
# Purchase Orders
# =========================================================
with tabs[15]:

    purchase_orders_tab()










