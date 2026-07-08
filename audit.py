import pandas as pd

from db import engine


def log_action(
    action_type,
    table_name,
    record_id,
    details=""
):
    audit_row = pd.DataFrame([{
        "action_type": action_type,
        "table_name": table_name,
        "record_id": record_id,
        "details": details
    }])

    audit_row.to_sql(
        "audit_log",
        engine,
        if_exists="append",
        index=False
    )