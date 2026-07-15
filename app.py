"""Retail Lens — 全球零售运营数据分析看板。"""

import sys
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd

# Force fresh import to bust Streamlit module cache
import src.dashboard.styles as _styles
importlib.reload(_styles)
from src.dashboard.styles import COLORS, GLOBAL_CSS

from src.dashboard.loader import load_all, needs_analyze

st.set_page_config(
    page_title="Retail Lens",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if needs_analyze():
    st.error("### No analysis data found")
    st.info("Run the following command first:")
    st.code("python main.py analyze", language="bash")
    st.stop()

regional, category, repurchase, logistics = load_all()

# Store in session before navigation
st.session_state["data"] = (regional, category, repurchase, logistics)

# ── Sidebar: brand + filters ──
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.5rem 0 0.5rem 0;">
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.25rem;">
                <div style="width:34px;height:34px;background:linear-gradient(135deg,#6366F1,#8B5CF6);border-radius:8px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <span style="color:#FFF;font-weight:700;font-size:0.95rem;">R</span>
                </div>
                <span style="color:#F4F4F5;font-size:1.1rem;font-weight:700;letter-spacing:-0.02em;">Retail Lens</span>
            </div>
            <span style="color:#71717A;font-size:0.68rem;letter-spacing:0.04em;">零售运营分析平台</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border-color:#27272A;margin:1rem 0;">', unsafe_allow_html=True)

    st.markdown(
        '<span style="color:#52525B;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">数据筛选</span>',
        unsafe_allow_html=True,
    )

    markets = list(regional.get("market", pd.DataFrame()).index)
    selected_market = (
        st.selectbox("市场", ["全部市场"] + markets, label_visibility="collapsed")
        if markets
        else "全部市场"
    )

    cats = list(category.get("category", pd.DataFrame()).index)
    selected_category = (
        st.selectbox("品类", ["全部品类"] + cats, label_visibility="collapsed")
        if cats
        else "全部品类"
    )

    ships = list(logistics.get("ship_mode", pd.DataFrame()).index)
    selected_ship = (
        st.selectbox("运输方式", ["全部方式"] + ships, label_visibility="collapsed")
        if ships
        else "全部方式"
    )

    st.markdown('<hr style="border-color:#27272A;margin:1.5rem 0 1rem 0;">', unsafe_allow_html=True)

    mem_mb = (
        sum(
            df.memory_usage(deep=True).sum()
            for d in [regional, category, repurchase, logistics]
            for df in d.values()
        )
        / 1e6
    )
    st.caption(f"数据缓存 · {mem_mb:.1f} MB")

st.session_state["filter_market"] = selected_market
st.session_state["filter_category"] = selected_category
st.session_state["filter_ship"] = selected_ship

# ── Navigation: explicit Chinese page names ──
pg = st.navigation(
    {
        "零售分析": [
            st.Page("pages/1_销售总览.py", title="销售总览"),
            st.Page("pages/2_品类分析.py", title="品类分析"),
            st.Page("pages/3_客户复购.py", title="客户复购"),
            st.Page("pages/4_物流时效.py", title="物流时效"),
        ],
    }
)
pg.run()
