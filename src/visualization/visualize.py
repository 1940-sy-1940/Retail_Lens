"""可视化模块：生成 8 张 PNG 图表。"""

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from ..config import OUTPUT_FIGURES_DIR, CHART_DPI, CHART_FIGSIZE, TOP_N_CHARTS

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

logger = logging.getLogger(__name__)


def _save(name: str) -> str:
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    p = OUTPUT_FIGURES_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(p, dpi=CHART_DPI, bbox_inches="tight")
    plt.close()
    logger.info("  → %s", p)
    return str(p)


# ── 区域销售 ──

def plot_regional_sales(market_df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=CHART_FIGSIZE)
    x = range(len(market_df))
    ax1.bar(x, market_df["Total_Sales"] / 1e6, 0.4, label="销售额(M)", color="#4E79A7")
    ax1.set_xticks(x)
    ax1.set_xticklabels(market_df.index, rotation=30)
    ax1.set_ylabel("销售额 (百万)")
    ax2 = ax1.twinx()
    ax2.plot(x, market_df["Total_Profit"] / 1e3, "o-", color="#E15759", lw=2, label="利润(K)")
    ax2.set_ylabel("利润 (千)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    plt.title("各市场销售额与利润对比")
    return _save("01_regional_sales_market")


def plot_regional_profit_rate(market_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    s = market_df.sort_values("Avg_Profit_Rate")
    colors = ["#E15759" if v else "#4E79A7" for v in s["Is_LowPerformance"]]
    ax.barh(s.index, s["Avg_Profit_Rate"] * 100, color=colors)
    ax.set_xlabel("平均利润率 (%)")
    ax.set_title("各市场利润率（红色=低效区域）")
    return _save("02_regional_profit_rate")


# ── 品类 ──

def plot_category_sales(cat_df: pd.DataFrame):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    ax1.pie(cat_df["Total_Sales"], labels=cat_df.index, autopct="%1.1f%%", startangle=90)
    ax1.set_title("品类销售额占比")
    ax2.bar(cat_df.index, cat_df["Total_Profit"] / 1e3, color="#59A14F")
    ax2.set_ylabel("利润 (千)")
    ax2.set_title("各品类总利润")
    ax2.tick_params(axis="x", rotation=30)
    return _save("03_category_sales")


def plot_subcategory_top(subcat_df: pd.DataFrame):
    top = subcat_df.head(TOP_N_CHARTS)
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    colors = ["#E15759" if v else "#4E79A7" for v in top["Is_LowSales"]]
    ax.barh(top.index[::-1], top["Total_Sales"][::-1] / 1e3, color=colors[::-1])
    ax.set_xlabel("销售额 (千)")
    ax.set_title(f"子品类销售额 Top{TOP_N_CHARTS}（红色=低销品类）")
    return _save("04_subcategory_top")


# ── 客户 ──

def plot_customer_segments(seg_df: pd.DataFrame):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    ax1.pie(seg_df["Customer_Count"], labels=seg_df.index, autopct="%1.1f%%", startangle=90)
    ax1.set_title("客户分层人数占比")
    ax2.bar(seg_df.index, seg_df["Total_Sales"] / 1e6, color="#76B7B2")
    ax2.set_ylabel("总销售额 (百万)")
    ax2.set_title("各分层客户贡献销售额")
    ax2.tick_params(axis="x", rotation=30)
    return _save("05_customer_segments")


def plot_repurchase_summary(summary_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis("off")
    tbl = ax.table(cellText=summary_df.values, colLabels=summary_df.columns,
                    cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1.2, 1.8)
    for (r, _), c in tbl.get_celld().items():
        if r == 0:
            c.set_facecolor("#4E79A7")
            c.set_text_props(color="white", fontweight="bold")
    plt.title("客户复购核心指标", fontweight="bold", pad=20)
    return _save("06_repurchase_summary")


# ── 物流 ──

def plot_shipping_days(ship_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    ax.bar(ship_df.index, ship_df["Avg_ShippingDays"], color="#B07AA1")
    ax.set_ylabel("平均物流天数")
    ax.set_title("各运输方式平均物流时效")
    ax.tick_params(axis="x", rotation=30)
    for i, (avg, med) in enumerate(
        zip(ship_df["Avg_ShippingDays"], ship_df["Median_ShippingDays"])
    ):
        ax.text(i, avg + 0.1, f"中:{med:.1f}d", ha="center", fontsize=9)
    return _save("07_shipping_days")


def plot_delay_analysis(delay_df: pd.DataFrame):
    if len(delay_df) == 0:
        return
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    ax.bar(delay_df.index, delay_df["Delay_Order_Count"], color="#E15759")
    ax.set_ylabel("延迟订单数 (>P95)")
    ax.set_title("各运输方式高延迟订单分布")
    ax.tick_params(axis="x", rotation=30)
    return _save("08_delay_analysis")


# ── 综合 ──

def generate_all_charts(
    regional: dict, category: dict, repurchase: dict, logistics: dict,
) -> list[str]:
    saved = []
    if "market" in regional:
        saved.append(plot_regional_sales(regional["market"]))
        saved.append(plot_regional_profit_rate(regional["market"]))
    if "category" in category:
        saved.append(plot_category_sales(category["category"]))
    if "sub_category" in category:
        saved.append(plot_subcategory_top(category["sub_category"]))
    if "customer_segments" in repurchase:
        saved.append(plot_customer_segments(repurchase["customer_segments"]))
    if "repurchase_summary" in repurchase:
        saved.append(plot_repurchase_summary(repurchase["repurchase_summary"]))
    if "ship_mode" in logistics:
        saved.append(plot_shipping_days(logistics["ship_mode"]))
    if "delay_analysis" in logistics:
        saved.append(plot_delay_analysis(logistics["delay_analysis"]))
    return saved
