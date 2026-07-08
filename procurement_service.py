import pandas as pd

from services.report_service import load_report_sheet


def build_procurement_plan():

    stock = load_report_sheet("inventory_status")
    consumption = load_report_sheet("consumption_detail")

    if stock.empty or consumption.empty:
        return pd.DataFrame()


    today = consumption["production_date"].max()

    days_history = max(
        (
                today -
                consumption["production_date"].min()
        ).days,
        1
    )
    avg_consumption = (
        consumption
        .groupby("material_code")["consumption"]
        .sum()
        .reset_index()
    )

    avg_consumption[
        "avg_daily_consumption"
    ] = (
            avg_consumption["consumption"]
            / days_history
    )

    planning = stock.merge(
        avg_consumption[
            [
                "material_code",
                "avg_daily_consumption"
            ]
        ],
        on="material_code",
        how="left"
    )

    planning[
        "avg_daily_consumption"
    ] = planning[
        "avg_daily_consumption"
    ].fillna(0)

    planning["coverage_days"] = planning.apply(
        lambda row:
        (
                row["current_stock"]
                /
                row["avg_daily_consumption"]
        )
        if row["avg_daily_consumption"] > 0
        else None,
        axis=1
    )

    def get_status(days):

        if pd.isna(days):
            return "⚪ NO CONSUMPTION"

        elif days < 30:
            return "🔴 REORDER"

        elif days < 90:
            return "🟡 LOW"

        else:
            return "🟢 OK"

    planning["status"] = planning[
        "coverage_days"
    ].apply(get_status)

    planning["safety_stock"] = (
            planning["avg_daily_consumption"] * 30
    )
    planning["required_stock"] = (
                                         planning["avg_daily_consumption"]
                                         *
                                         planning["lead_time_days"]
                                 ) + planning["safety_stock"]
    planning["suggested_order_qty"] = (
            planning["required_stock"]
            -
            planning["current_stock"]
    )

    planning["suggested_order_qty"] = (
        planning["suggested_order_qty"]
        .clip(lower=0)
    )
    planning[
        "suggested_order_qty"
    ] = (
        planning[
            "suggested_order_qty"
        ]
        .round(0)
    )

    return planning