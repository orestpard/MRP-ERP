import pandas as pd

from config import REPORT_FILE


def load_report_sheet(sheet_name):

    try:

        return pd.read_excel(
            REPORT_FILE,
            sheet_name=sheet_name
        )

    except Exception:

        return pd.DataFrame()