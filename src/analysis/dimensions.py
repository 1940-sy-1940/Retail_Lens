"""四维分析模块：区域销售 / 品类销量 / 客户复购 / 物流时效 + 问题自动定位。

所有函数遵循 `analyze_xxx(df) -> dict[str, DataFrame]` 接口。
"""

import logging
import pandas as pd
import numpy as np

from ..config import LOW_PERFORMANCE_QUANTILE, REPURCHASE_THRESHOLD, OUTPUT_DATA_DIR

logger = logging.getLogger(__name__)


# ──────────────── 维度1：区域销售 ────────────────

def analyze_regional_sales(df: pd.DataFrame) -> dict:
    """Market / Region / Country 三层粒度。

    Returns: {"market": df, "region": df, "country": df}
    """
    results = {}
    for dim in ["Market", "Region", "Country"]:
        if dim not in df.columns:
            continue
        g = df.groupby(dim, observed=False).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Avg_Profit_Rate=("ProfitRate", "mean"),
            Order_Count=("Order_ID", "nunique"),
            Customer_Count=("Customer_ID", "nunique"),
        ).sort_values("Total_Sales", ascending=False)

        g["Sales_Share"] = (g["Total_Sales"] / g["Total_Sales"].sum()).round(4)
        g["Is_LowPerformance"] = (
            (g["Total_Profit"] <= g["Total_Profit"].quantile(LOW_PERFORMANCE_QUANTILE))
            & (g["Total_Sales"] < g["Total_Sales"].median())
        )
        results[dim.lower()] = g
        logger.info("  %s: %d entities", dim, len(g))
    return results


# ──────────────── 维度2：品类销量 ────────────────

def analyze_category_sales(df: pd.DataFrame) -> dict:
    """Category / Sub-Category 二层粒度。

    Returns: {"category": df, "sub_category": df}
    """
    results = {}
    for dim in ["Category", "Sub-Category"]:
        if dim not in df.columns:
            continue
        g = df.groupby(dim, observed=False).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Avg_Discount=("Discount", "mean"),
            Avg_Profit_Rate=("ProfitRate", "mean"),
            Order_Count=("Order_ID", "nunique"),
        ).sort_values("Total_Sales", ascending=False)

        g["Sales_Share"] = (g["Total_Sales"] / g["Total_Sales"].sum()).round(4)
        g["Quantity_Share"] = (g["Total_Quantity"] / g["Total_Quantity"].sum()).round(4)
        low = g["Total_Sales"].quantile(LOW_PERFORMANCE_QUANTILE)
        g["Is_LowSales"] = g["Total_Sales"] <= low

        results[dim.lower().replace("-", "_")] = g
        logger.info("  %s: %d entities", dim, len(g))
    return results


# ──────────────── 维度3：客户复购 ────────────────

def analyze_customer_repurchase(df: pd.DataFrame) -> dict:
    """客户购买频次分层 + 复购率统计。

    Returns: {"customer_segments": df, "repurchase_summary": df}
    """
    if "Customer_ID" not in df.columns:
        return {}

    cust = df.groupby("Customer_ID", observed=False).agg(
        Order_Count=("Order_ID", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        First_Order=("Order_Date", "min"),
        Last_Order=("Order_Date", "max"),
    )
    cust["Is_Repurchase"] = cust["Order_Count"] >= REPURCHASE_THRESHOLD
    cust["Customer_Life_Days"] = (cust["Last_Order"] - cust["First_Order"]).dt.days

    def classify(cnt):
        if cnt == 1:
            return "一次性客户"
        elif cnt <= 3:
            return "低频客户(2-3次)"
        elif cnt <= 6:
            return "中频客户(4-6次)"
        return "高频客户(7次+)"

    cust["Segment"] = cust["Order_Count"].apply(classify)

    segments = cust.groupby("Segment", observed=False).agg(
        Customer_Count=("Order_Count", "count"),
        Avg_Orders=("Order_Count", "mean"),
        Total_Sales=("Total_Sales", "sum"),
        Avg_Life_Days=("Customer_Life_Days", "mean"),
    ).reindex(["高频客户(7次+)", "中频客户(4-6次)", "低频客户(2-3次)", "一次性客户"])

    total = len(cust)
    rep_cnt = cust["Is_Repurchase"].sum()
    summary = pd.DataFrame({
        "指标": ["总客户数", "复购客户数", "复购率", "一次性客户数", "一次性占比"],
        "数值": [
            total, rep_cnt, round(rep_cnt / total, 4) if total else 0,
            total - rep_cnt, round(1 - rep_cnt / total, 4) if total else 0,
        ],
    })

    logger.info("  Customers: %d | Repurchase rate: %.2f%%", total, rep_cnt / total * 100)
    return {"customer_segments": segments, "repurchase_summary": summary}


# ──────────────── 维度4：物流时效 ────────────────

def analyze_logistics(df: pd.DataFrame) -> dict:
    """Ship Mode / Order Priority 物流天数 + 延迟订单分析。

    Returns: {"ship_mode": df, "order_priority": df, "delay_analysis": df}
    """
    results = {}
    if "ShippingDays" not in df.columns:
        return results

    for dim in ["Ship_Mode", "Order_Priority"]:
        if dim not in df.columns:
            continue
        g = df.groupby(dim, observed=False).agg(
            Avg_ShippingDays=("ShippingDays", "mean"),
            Median_ShippingDays=("ShippingDays", "median"),
            Max_ShippingDays=("ShippingDays", "max"),
            Order_Count=("Order_ID", "nunique"),
        ).sort_values("Avg_ShippingDays", ascending=True)
        results[dim.lower()] = g

    # 高延迟订单（>95分位）
    threshold = df["ShippingDays"].quantile(0.95)
    delay = df[df["ShippingDays"] >= threshold]
    if "Ship_Mode" in df.columns:
        results["delay_analysis"] = (
            delay.groupby("Ship_Mode", observed=False)
            .agg(Delay_Order_Count=("Order_ID", "nunique"), Avg_Delay_Days=("ShippingDays", "mean"))
            .sort_values("Delay_Order_Count", ascending=False)
        )

    logger.info("  Shipping threshold (p95): %.1f days", threshold)
    return results


# ──────────────── 问题定位 ────────────────

def identify_business_issues(
    regional: dict, category: dict, logistics: dict,
) -> list[str]:
    """分析结果综合定位核心业务问题。"""
    issues = []

    if "market" in regional:
        low = regional["market"][regional["market"]["Is_LowPerformance"]]
        if len(low):
            issues.append(f"低效区域：{', '.join(low.index.tolist())} — 利润/销售额双低")

    if "sub_category" in category:
        low = category["sub_category"][category["sub_category"]["Is_LowSales"]]
        if len(low):
            issues.append(f"低销子品类：{', '.join(low.index.tolist())} — 销售额末位25%")

    if "delay_analysis" in logistics and len(logistics["delay_analysis"]) > 0:
        worst = logistics["delay_analysis"].index[0]
        issues.append(f"高物流延迟：{worst} — 延迟订单最多，建议优化渠道效率")

    return issues


# ──────────────── 落盘 ────────────────

def save_analysis_results(
    regional: dict, category: dict, repurchase: dict, logistics: dict,
):
    """所有分析结果写 CSV 到 outputs/data/，兼容 Power BI 直接导入。

    导出的 DataFrame index 列会变为有意义的维度列名：
    - regional_market.csv  → index = Market 名称
    - category_sub_category.csv → index = Sub-Category 名称
    布尔列 Is_LowPerformance / Is_LowSales 转为可读中文标签。
    """
    import shutil

    # 每次覆盖，确保 Power BI 刷新时读取最新数据
    if OUTPUT_DATA_DIR.exists():
        shutil.rmtree(OUTPUT_DATA_DIR)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for prefix, results in [
        ("regional", regional), ("category", category),
        ("repurchase", repurchase), ("logistics", logistics),
    ]:
        for name, data in results.items():
            if not isinstance(data, pd.DataFrame) or len(data) == 0:
                continue

            out = data.copy()

            # 布尔列转为中文标签，Power BI 中可直接用作切片器
            for col in out.columns:
                if out[col].dtype == bool:
                    out[col] = out[col].map({True: "是", False: "否"})

            # 小数四舍五入，提高可读性
            float_cols = out.select_dtypes(include=["float"]).columns
            out[float_cols] = out[float_cols].round(4)

            filepath = OUTPUT_DATA_DIR / f"{prefix}_{name}.csv"
            out.to_csv(filepath, encoding="utf-8-sig", index_label=name)
            logger.info("  → %s (%d rows × %d cols)", filepath.name, len(out), len(out.columns))

    logger.info("All results saved to %s", OUTPUT_DATA_DIR)
