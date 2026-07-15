"""Streamlit 看板数据加载器：从 outputs/data/ CSV 加载，带缓存。

模块入口使用 @st.cache_data 确保数据只加载一次。
"""

import streamlit as st
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "data"


def _path(prefix: str, name: str) -> Path:
    return OUTPUT_DIR / f"{prefix}_{name}.csv"


@st.cache_data(ttl=3600, show_spinner="正在加载数据...")
def load_all():
    """加载全部四维度分析数据。返回 (regional, category, repurchase, logistics)。"""

    def _load(prefix, name):
        p = _path(prefix, name)
        return pd.read_csv(p, index_col=0) if p.exists() else pd.DataFrame()

    regional = {
        "market": _load("regional", "market"),
        "region": _load("regional", "region"),
        "country": _load("regional", "country"),
    }

    category = {
        "category": _load("category", "category"),
        "sub_category": _load("category", "sub_category"),
    }

    repurchase = {
        "customer_segments": _load("repurchase", "customer_segments"),
        "repurchase_summary": _load("repurchase", "repurchase_summary"),
    }

    logistics = {
        "ship_mode": _load("logistics", "ship_mode"),
        "order_priority": _load("logistics", "order_priority"),
        "delay_analysis": _load("logistics", "delay_analysis"),
    }

    # 过滤空表
    regional = {k: v for k, v in regional.items() if len(v) > 0}
    category = {k: v for k, v in category.items() if len(v) > 0}
    repurchase = {k: v for k, v in repurchase.items() if len(v) > 0}
    logistics = {k: v for k, v in logistics.items() if len(v) > 0}

    return regional, category, repurchase, logistics


def needs_analyze() -> bool:
    """检查是否需要先运行 analyze。"""
    return not OUTPUT_DIR.exists() or not any(OUTPUT_DIR.iterdir())
