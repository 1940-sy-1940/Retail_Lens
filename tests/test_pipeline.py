"""测试：验证数据加载、清洗、四维分析链路。"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.config import RAW_EXCEL, RAW_CSV
from src.data.make_dataset import load_raw, preprocess, make_dataset
from src.analysis.dimensions import (
    analyze_regional_sales, analyze_category_sales,
    analyze_customer_repurchase, analyze_logistics,
)


def test_data_exists():
    assert RAW_EXCEL.exists() or RAW_CSV.exists()


def test_load_raw():
    df = load_raw()
    assert len(df) > 50000          # 是大型数据集
    assert "Sales" in df.columns
    assert "Profit" in df.columns


def test_preprocess():
    df = load_raw()
    clean = preprocess(df)
    assert "ShippingDays" in clean.columns
    assert "ProfitRate" in clean.columns
    assert "Order_YM" in clean.columns
    assert clean["ShippingDays"].notna().sum() > 0


def test_make_dataset():
    df = make_dataset()
    assert len(df) > 50000
    assert "ShippingDays" in df.columns


def test_regional_analysis():
    df = make_dataset()
    result = analyze_regional_sales(df)
    assert "market" in result
    assert len(result["market"]) > 0


def test_category_analysis():
    df = make_dataset()
    result = analyze_category_sales(df)
    assert "category" in result
    assert len(result["category"]) > 0
    assert "sub_category" in result


def test_repurchase_analysis():
    df = make_dataset()
    result = analyze_customer_repurchase(df)
    assert "customer_segments" in result
    assert "repurchase_summary" in result


def test_logistics_analysis():
    df = make_dataset()
    result = analyze_logistics(df)
    assert "ship_mode" in result
    assert "delay_analysis" in result
