"""Page 3: Customer Loyalty — KPI cards + donut chart + segment table."""

import sys
import importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import src.dashboard.styles as _styles
importlib.reload(_styles)
from src.dashboard.styles import COLORS, CHART_COLORS
from src.dashboard.loader import load_all

if "data" not in st.session_state:
    st.session_state["data"] = load_all()
repurchase = st.session_state["data"][2]

df_seg = repurchase.get("customer_segments", pd.DataFrame())
df_sum = repurchase.get("repurchase_summary", pd.DataFrame())

# ── Page header ──
st.markdown(
    '<div class="page-header">'
    '<h1>Customer Loyalty</h1>'
    '<span class="subtitle">Repurchase · Segmentation · Lifetime Value</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── KPI row ──
total_customers = 0
repurchase_customers = 0
repurchase_rate = 0.0
avg_life = 0.0

if len(df_sum) > 0:
    summary = df_sum.set_index("指标")["数值"].to_dict() if "指标" in df_sum.columns else {}
    total_customers = int(summary.get("总客户数", 0))
    repurchase_customers = int(summary.get("复购客户数", 0))
    repurchase_rate = (repurchase_customers / total_customers * 100) if total_customers > 0 else 0

if len(df_seg) > 0 and "Avg_Life_Days" in df_seg.columns:
    high_freq = df_seg[df_seg.index.str.contains("高频")]
    if len(high_freq) > 0:
        avg_life = high_freq["Avg_Life_Days"].iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-value">{total_customers:,}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Repeat Buyers</div>
            <div class="kpi-value">{repurchase_customers:,}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c3:
    rc = COLORS["success"] if repurchase_rate >= 70 else COLORS["warning"] if repurchase_rate >= 50 else COLORS["danger"]
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Repurchase Rate</div>
            <div class="kpi-value" style="color:{rc};">{repurchase_rate:.1f}<span style="font-size:0.9rem;font-weight:500;">%</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Avg Lifetime (High)</div>
            <div class="kpi-value">{avg_life:,.0f}<span style="font-size:0.9rem;font-weight:500;color:#94A3B8;">d</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ──
cl, cr = st.columns(2)

with cl:
    st.markdown(
        '<div class="section-card"><div class="section-title">Customer Segment Distribution</div>',
        unsafe_allow_html=True,
    )
    if len(df_seg) > 0 and "Customer_Count" in df_seg.columns:
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=df_seg.index, values=df_seg["Customer_Count"],
            hole=0.55,
            marker=dict(
                colors=[COLORS["primary"], "#8B5CF6", "#EC4899", "#F59E0B", "#94A3B8"][:len(df_seg)],
                line=dict(color="white", width=2),
            ),
            textinfo="percent+label",
            textfont=dict(size=12, color=COLORS["ink"]),
            hovertemplate="%{label}<br>%{value:,} customers<br>%{percent}<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=380,
            paper_bgcolor="white", showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown(
        '<div class="section-card"><div class="section-title">Avg Orders by Segment</div>',
        unsafe_allow_html=True,
    )
    if len(df_seg) > 0 and "Avg_Orders" in df_seg.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_seg.index, y=df_seg["Avg_Orders"],
            marker_color=[COLORS["primary"], "#8B5CF6", "#EC4899", "#F59E0B", "#94A3B8"][:len(df_seg)],
            marker_line_width=0,
            text=[f"{v:.1f}" for v in df_seg["Avg_Orders"]],
            textposition="outside",
            textfont=dict(color=COLORS["ink_secondary"], size=12),
            hovertemplate="%{x}<br>Avg Orders: %{y:.1f}<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickfont=dict(color=COLORS["ink_secondary"], size=11)),
            yaxis=dict(title="Avg Orders", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            margin=dict(l=0, r=0, t=0, b=0), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Segment detail table ──
st.markdown(
    '<div class="section-card"><div class="section-title">Segment Detail</div>',
    unsafe_allow_html=True,
)
if len(df_seg) > 0:
    df_display = df_seg.copy()
    for c in df_display.columns:
        if "Sales" in c:
            df_display[c] = df_display[c].apply(lambda x: f"${x:,.0f}")
        elif "Orders" in c or "Life" in c:
            df_display[c] = df_display[c].apply(lambda x: f"{x:,.1f}")
    st.dataframe(df_display, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
