"""Page 1: Sales Overview — KPI cards + Market comparison + alerts."""

import sys
import importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import src.dashboard.styles as _styles
importlib.reload(_styles)
from src.dashboard.styles import COLORS, CHART_COLORS
from src.dashboard.loader import load_all

if "data" not in st.session_state:
    st.session_state["data"] = load_all()
regional = st.session_state["data"][0]

df_market = regional.get("market", pd.DataFrame())
df_country = regional.get("country", pd.DataFrame())

# ── Market filter ──
market_filter = st.session_state.get("filter_market", "全部市场")
if market_filter != "全部市场" and market_filter in df_market.index:
    df_market_display = df_market.copy()
    df_market_filtered = df_market.loc[[market_filter]]
else:
    df_market_display = df_market
    df_market_filtered = df_market

# Filter badge
if market_filter != "全部市场":
    st.markdown(
        f'<span class="brand-badge">筛选: {market_filter}</span>',
        unsafe_allow_html=True,
    )

# ── Page header ──
st.markdown(
    '<div class="page-header">'
    '<h1>Sales Overview</h1>'
    '<span class="subtitle">Revenue · Profit · Market Performance</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── KPI row ──
total_sales = df_market_filtered["Total_Sales"].sum() if "Total_Sales" in df_market_filtered.columns else 0
total_profit = df_market_filtered["Total_Profit"].sum() if "Total_Profit" in df_market_filtered.columns else 0
avg_rate = (total_profit / total_sales * 100) if total_sales else 0
orders = int(df_market_filtered.get("Order_Count", pd.Series([0])).sum())

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${total_sales/1e6:,.1f}<span style="font-size:0.9rem;font-weight:500;color:#94A3B8;">M</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Total Profit</div>
            <div class="kpi-value">${total_profit/1e3:,.1f}<span style="font-size:0.9rem;font-weight:500;color:#94A3B8;">K</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c3:
    rc = COLORS["success"] if avg_rate >= 15 else COLORS["danger"]
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Profit Margin</div>
            <div class="kpi-value" style="color:{rc};">{avg_rate:.1f}<span style="font-size:0.9rem;font-weight:500;">%</span></div>
        </div>""",
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{orders:,}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ──
cl, cr = st.columns(2)

with cl:
    st.markdown(
        '<div class="section-card"><div class="section-title">Revenue &amp; Profit by Market</div>',
        unsafe_allow_html=True,
    )
    if len(df_market_display) > 0:
        df_plot = df_market_display.reset_index()
        name_col = df_plot.columns[0]
        bar_colors = [
            "#EC4899" if market_filter != "全部市场" and v == market_filter else COLORS["primary"]
            for v in df_plot[name_col]
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_plot[name_col], y=df_plot["Total_Sales"] / 1e6,
            name="Revenue", marker_color=bar_colors,
            marker_line_width=0, hovertemplate="$%{y:.1f}M<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=df_plot[name_col], y=df_plot["Total_Profit"] / 1e3,
            name="Profit", yaxis="y2",
            mode="lines+markers", marker=dict(size=9, color=COLORS["primary_dark"], line=dict(width=2, color="white")),
            line=dict(width=2.5, color=COLORS["primary_dark"]),
            hovertemplate="$%{y:.1f}K<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickfont=dict(color=COLORS["ink_secondary"]), tickangle=0),
            yaxis=dict(title="Revenue (M)", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            yaxis2=dict(title="Profit (K)", overlaying="y", side="right", gridcolor="white", tickfont=dict(color=COLORS["ink_muted"])),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=COLORS["ink_secondary"], size=12)),
            margin=dict(l=0, r=40, t=0, b=0), height=360,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown(
        '<div class="section-card"><div class="section-title">Revenue Share by Market</div>',
        unsafe_allow_html=True,
    )
    if len(df_market_display) > 0:
        df_plot = df_market_display.reset_index()
        name_col = df_plot.columns[0]
        fig = px.pie(
            df_plot, values="Total_Sales", names=name_col, hole=0.55,
            color_discrete_sequence=CHART_COLORS["category"],
        )
        fig.update_traces(
            textposition="inside", textinfo="percent+label",
            textfont=dict(size=12, color="white"),
            marker=dict(line=dict(color="white", width=2)),
            hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0), height=360,
            paper_bgcolor="white", showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Low-performance alerts (Notion-style warning) ──
if "Is_LowPerformance" in df_market_display.columns:
    low = df_market_display[df_market_display["Is_LowPerformance"] == "是"]
    if len(low) > 0:
        st.markdown(
            '<div class="section-card">'
            '<div class="section-title">⚠ Low-Performance Markets</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(min(len(low), 4))
        for i, (name, row) in enumerate(low.iterrows()):
            with cols[i]:
                profit_rate = row.get("Avg_Profit_Rate", 0)
                if isinstance(profit_rate, float) and profit_rate < 1:
                    profit_rate *= 100
                st.markdown(
                    f"""<div class="alert-card">
                        <div class="title">{name}</div>
                        <div class="detail">Revenue: ${row["Total_Sales"]/1e6:.2f}M</div>
                        <div class="highlight">Margin: {profit_rate:.1f}%</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

# ── Country choropleth ──
st.markdown(
    '<div class="section-card"><div class="section-title">Revenue by Country</div>',
    unsafe_allow_html=True,
)
if len(df_country) > 0 and "Total_Sales" in df_country.columns:
    df_plot = df_country.reset_index()
    name_col = df_plot.columns[0]
    fig = px.choropleth(
        df_plot, locations=name_col, locationmode="country names",
        color="Total_Sales", hover_name=name_col,
        color_continuous_scale=CHART_COLORS["sequential_blue"],
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=400,
        paper_bgcolor="white",
        geo=dict(bgcolor=COLORS["canvas_soft"], lakecolor=COLORS["canvas_soft"]),
        coloraxis_colorbar=dict(tickfont=dict(color=COLORS["ink_secondary"], size=11)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
