"""全球零售运营数据分析 — CLI 入口。

用法:
    python main.py analyze   # 全量分析 (数据清洗 → 四维分析 → 图表 → 报告)
    python main.py report    # 仅生成报告和图表（复用 outputs/data/ 缓存）
    python main.py push      # 推送分析结果到 Power BI Service（需先 analyze）
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import OUTPUT_DATA_DIR, OUTPUT_REPORTS_DIR, OUTPUT_FIGURES_DIR


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)-25s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _run_analysis():
    """执行四维分析并返回结果，同时写 CSV/图表/报告。"""
    from src.data.make_dataset import make_dataset
    from src.analysis.dimensions import (
        analyze_regional_sales, analyze_category_sales,
        analyze_customer_repurchase, analyze_logistics,
        identify_business_issues, save_analysis_results,
    )
    from src.visualization.visualize import generate_all_charts

    log = logging.getLogger("analyze")

    log.info("=== Step 1/6: Data loading & cleaning ===")
    df = make_dataset()

    log.info("=== Step 2/6: Regional sales analysis ===")
    regional = analyze_regional_sales(df)

    log.info("=== Step 3/6: Category sales analysis ===")
    category = analyze_category_sales(df)

    log.info("=== Step 4/6: Customer repurchase analysis ===")
    repurchase = analyze_customer_repurchase(df)

    log.info("=== Step 5/6: Logistics analysis ===")
    logistics = analyze_logistics(df)

    log.info("=== Step 6/6: Charts & report ===")
    save_analysis_results(regional, category, repurchase, logistics)
    charts = generate_all_charts(regional, category, repurchase, logistics)
    log.info("  %d charts → %s", len(charts), OUTPUT_FIGURES_DIR)

    issues = identify_business_issues(regional, category, logistics)

    # 报告
    report = [
        "# 全球零售运营数据分析报告",
        f"\n数据规模：{len(df):,} 条订单",
        "\n## 核心业务问题",
    ]
    for i, issue in enumerate(issues, 1):
        report.append(f"{i}. {issue}")
    if not issues:
        report.append("（未检测到显著低效区域/品类/物流问题）")

    report += [
        "\n## 维度摘要",
        f"- 区域分析：{', '.join(regional.keys())}",
        f"- 品类分析：{', '.join(category.keys())}",
        f"- 客户分析：{', '.join(repurchase.keys())}",
        f"- 物流分析：{', '.join(logistics.keys())}",
        "\n## 输出文件",
        f"- CSV：{OUTPUT_DATA_DIR}",
        f"- 图表：{OUTPUT_FIGURES_DIR}",
    ]
    rpt_path = OUTPUT_REPORTS_DIR / "analysis_report.md"
    rpt_path.parent.mkdir(parents=True, exist_ok=True)
    rpt_path.write_text("\n".join(report), encoding="utf-8")

    log.info("=== Done ===")
    for issue in issues:
        log.warning("  ! %s", issue)

    return regional, category, repurchase, logistics


def cmd_analyze():
    _run_analysis()


def cmd_report():
    """复用已有 outputs/data/ 缓存的结果生成报告和图表。"""
    import pandas as pd
    from src.visualization.visualize import generate_all_charts
    from src.analysis.dimensions import identify_business_issues

    log = logging.getLogger("report")

    def _load(prefix, name):
        path = OUTPUT_DATA_DIR / f"{prefix}_{name}.csv"
        return pd.read_csv(path, index_col=0) if path.exists() else pd.DataFrame()

    regional = {}
    for k in ["market", "region", "country"]:
        df = _load("regional", k)
        if len(df) > 0:
            regional[k] = df

    category = {}
    for k in ["category", "sub_category"]:
        df = _load("category", k)
        if len(df) > 0:
            category[k] = df

    repurchase = {}
    for k in ["customer_segments", "repurchase_summary"]:
        df = _load("repurchase", k)
        if len(df) > 0:
            repurchase[k] = df

    logistics = {}
    for k in ["ship_mode", "order_priority", "delay_analysis"]:
        df = _load("logistics", k)
        if len(df) > 0:
            logistics[k] = df

    log.info("Loaded data from %s", OUTPUT_DATA_DIR)
    charts = generate_all_charts(regional, category, repurchase, logistics)
    log.info("%d charts → %s", len(charts), OUTPUT_FIGURES_DIR)

    issues = identify_business_issues(regional, category, logistics)
    for issue in issues:
        log.warning("  ! %s", issue)


def cmd_push():
    """推送 analysis 结果到 Power BI Service。

    前置条件：
    1. 已运行 python main.py analyze
    2. 已配置凭证（pbi_config.json 或环境变量 PBI_CLIENT_ID 等）
    3. Power BI Pro 许可 + Azure AD 应用注册（Dataset.ReadWrite.All）

    运行后可在 Power BI Service 中基于推送的数据集创建报表。
    """
    import pandas as pd
    from src.powerbi.auth import get_credentials
    from src.powerbi.push_data import push_all

    log = logging.getLogger("push")

    # 加载分析结果
    def _load(prefix, name):
        path = OUTPUT_DATA_DIR / f"{prefix}_{name}.csv"
        return pd.read_csv(path, index_col=0) if path.exists() else pd.DataFrame()

    tables = {
        "regional_market": (_load("regional", "market"), "区域×市场汇总"),
        "regional_region": (_load("regional", "region"), "区域×大区汇总"),
        "regional_country": (_load("regional", "country"), "区域×国家汇总"),
        "category_category": (_load("category", "category"), "品类汇总"),
        "category_sub_category": (_load("category", "sub_category"), "子品类汇总"),
        "repurchase_customer_segments": (
            _load("repurchase", "customer_segments"), "客户分层"),
        "repurchase_summary": (
            _load("repurchase", "repurchase_summary"), "复购指标"),
        "logistics_ship_mode": (
            _load("logistics", "ship_mode"), "物流×运输方式"),
        "logistics_order_priority": (
            _load("logistics", "order_priority"), "物流×优先级"),
        "logistics_delay_analysis": (
            _load("logistics", "delay_analysis"), "物流×延迟分析"),
    }

    # 过滤空表
    tables = {k: v for k, v in tables.items() if len(v[0]) > 0}
    log.info("Loaded %d tables from %s", len(tables), OUTPUT_DATA_DIR)

    # 获取凭证
    client_id, client_secret, tenant_id, workspace_id = get_credentials()
    if not client_id or not client_secret:
        log.error(
            "Missing credentials. Set PBI_CLIENT_ID/PBI_CLIENT_SECRET env vars\n"
            "or create pbi_config.json (copy from pbi_config.example.json).\n"
            "See docs/power_bi_guide.md for setup instructions."
        )
        return

    if not workspace_id:
        log.error("Missing workspace_id. Set PBI_WORKSPACE_ID or add to pbi_config.json.")
        return

    push_all(
        results_map=tables,
        dataset_name="Global_Retail_Analytics",
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
    )


def main():
    _setup_logging()
    p = argparse.ArgumentParser(description="全球零售运营数据分析")
    s = p.add_subparsers(dest="command", required=True)
    s.add_parser("analyze", help="全量分析（清洗→四维分析→图表→报告）")
    s.add_parser("report", help="仅生成报告/图表（复用 outputs/data/ 缓存）")
    s.add_parser("push", help="推送分析结果到 Power BI Service（需先 analyze）")
    args = p.parse_args()
    {"analyze": cmd_analyze, "report": cmd_report, "push": cmd_push}[args.command]()


if __name__ == "__main__":
    main()
