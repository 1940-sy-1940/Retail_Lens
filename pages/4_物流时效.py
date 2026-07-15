"""Page 4: Shipping Performance — mode comparison + delay analysis."""

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
logistics_data = st.session_state["data"][3]

df_ship = logistics_data.get("ship_mode", pd.DataFrame())
df_priority = logistics_data.get("order_priority", pd.DataFrame())
df_delay = logistics_data.get("delay_analysis", pd.DataFrame())

# ── Ship mode filter ──
ship_filter = st.session_state.get("filter_ship", "全部方式")

# ── Page header ──
st.markdown(
    '<div class="page-header">'
    '<h1>Shipping Performance</h1>'
    '<span class="subtitle">Delivery Speed · Delay Analysis · Mode Comparison</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── KPI row ──
avg_days = df_ship["Avg_ShippingDays"].mean() if len(df_ship) > 0 and "Avg_ShippingDays" in df_ship.columns else 0
median_days = df_ship["Median_ShippingDays"].mean() if len(df_ship) > 0 and "Median_ShippingDays" in df_ship.columns else 0
delay_count = int(df_delay["Delay_Order_Count"].sum()) if len(df_delay) > 0 and "Delay_Order_Count" in df_delay.columns else 0
total_ship_orders = int(df_ship["Order_Count"].sum()) if len(df_ship) > 0 and "Order_Count" in df_ship.columns else 1
delay_rate = (delay_count / total_ship_orders * 100) if total_ship_orders > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Avg Delivery Time</div>
            <div class="kpi-value">{avg_days:.1f}<span style="font-size:0.9rem;font-weight:500;color:#94A3B8;">d</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Median Delivery</div>
            <div class="kpi-value">{median_days:.1f}<span style="font-size:0.9rem;font-weight:500;color:#94A3B8;">d</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c3:
    dc = COLORS["danger"] if delay_rate > 5 else COLORS["warning"] if delay_rate > 2 else COLORS["success"]
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Delayed Orders</div>
            <div class="kpi-value" style="color:{dc};">{delay_count:,}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with c4:
    dcr = COLORS["danger"] if delay_rate > 5 else COLORS["warning"] if delay_rate > 2 else COLORS["success"]
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Delay Rate</div>
            <div class="kpi-value" style="color:{dcr};">{delay_rate:.1f}<span style="font-size:0.9rem;font-weight:500;">%</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ──
cl, cr = st.columns(2)

with cl:
    st.markdown(
        '<div class="section-card"><div class="section-title">Delivery Time by Ship Mode</div>',
        unsafe_allow_html=True,
    )
    if len(df_ship) > 0 and "Avg_ShippingDays" in df_ship.columns:
        # Highlight selected ship mode
        bar_colors_ship = [
            "#EC4899" if ship_filter != "全部方式" and ship_filter in str(idx) else COLORS["primary"]
            for idx in df_ship.index
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Avg Days", x=df_ship.index, y=df_ship["Avg_ShippingDays"],
            marker_color=bar_colors_ship, marker_line_width=0,
            hovertemplate="Avg: %{y:.1f}d<extra></extra>",
        ))
        if "Median_ShippingDays" in df_ship.columns:
            fig.add_trace(go.Scatter(
                name="Median", x=df_ship.index, y=df_ship["Median_ShippingDays"],
                mode="lines+markers", marker=dict(size=8, color=COLORS["primary_dark"], line=dict(width=2, color="white")),
                line=dict(width=2.5, color=COLORS["primary_dark"]),
                hovertemplate="Median: %{y:.1f}d<extra></extra>",
            ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickfont=dict(color=COLORS["ink_secondary"], size=11)),
            yaxis=dict(title="Days", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=COLORS["ink_secondary"], size=11)),
            margin=dict(l=0, r=0, t=0, b=0), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown(
        '<div class="section-card"><div class="section-title">Shipping by Order Priority</div>',
        unsafe_allow_html=True,
    )
    if len(df_priority) > 0 and "Avg_ShippingDays" in df_priority.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Avg Days", x=df_priority.index, y=df_priority["Avg_ShippingDays"],
            marker_color="#8B5CF6", marker_line_width=0,
            hovertemplate="Avg: %{y:.1f}d<extra></extra>",
        ))
        if "Median_ShippingDays" in df_priority.columns:
            fig.add_trace(go.Scatter(
                name="Median", x=df_priority.index, y=df_priority["Median_ShippingDays"],
                mode="lines+markers", marker=dict(size=8, color="#6D28D9", line=dict(width=2, color="white")),
                line=dict(width=2.5, color="#6D28D9"),
                hovertemplate="Median: %{y:.1f}d<extra></extra>",
            ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickfont=dict(color=COLORS["ink_secondary"], size=11)),
            yaxis=dict(title="Days", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=COLORS["ink_secondary"], size=11)),
            margin=dict(l=0, r=0, t=0, b=0), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Delay analysis ──
st.markdown(
    '<div class="section-card"><div class="section-title">Delay Analysis by Ship Mode</div>',
    unsafe_allow_html=True,
)
if len(df_delay) > 0:
    fig = go.Figure()
    bar_colors = []
    for idx in df_delay.index:
        bar_colors.append(COLORS["primary"] if "Same" in str(idx) or "First" in str(idx) else COLORS["danger"])
    fig.add_trace(go.Bar(
        x=df_delay.index, y=df_delay.get("Delay_Order_Count", df_delay.iloc[:, 0]),
        marker_color=bar_colors, marker_line_width=0,
        text=[f"{int(v):,}" for v in df_delay.get("Delay_Order_Count", df_delay.iloc[:, 0])],
        textposition="outside",
        textfont=dict(color=COLORS["ink_secondary"], size=12),
        hovertemplate="%{x}<br>Delayed: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickfont=dict(color=COLORS["ink_secondary"], size=11)),
        yaxis=dict(title="Delayed Orders", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
        margin=dict(l=0, r=0, t=0, b=0), height=360,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
