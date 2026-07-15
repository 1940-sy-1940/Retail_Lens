"""Page 2: Category Analysis — Treemap + scatter + low-sales alerts."""

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
category_data = st.session_state["data"][1]

df_cat = category_data.get("category", pd.DataFrame())
df_sub = category_data.get("sub_category", pd.DataFrame())

# ── Category filter ──
cat_filter = st.session_state.get("filter_category", "全部品类")
if cat_filter != "全部品类" and cat_filter in df_cat.index:
    df_cat_display = df_cat.loc[[cat_filter]]
    # Filter sub-categories that contain the category name in index
    df_sub_display = df_sub[df_sub.index.str.contains(cat_filter, case=False)] if len(df_sub) > 0 else df_sub
else:
    df_cat_display = df_cat
    df_sub_display = df_sub

# Filter badge
if cat_filter != "全部品类":
    st.markdown(
        f'<span class="brand-badge">筛选: {cat_filter}</span>',
        unsafe_allow_html=True,
    )

# ── Page header ──
st.markdown(
    '<div class="page-header">'
    '<h1>Category Analysis</h1>'
    '<span class="subtitle">Product Mix · Profitability · Growth Signals</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Treemap ──
st.markdown(
    '<div class="section-card"><div class="section-title">Category Revenue Treemap</div>',
    unsafe_allow_html=True,
)
if len(df_sub_display) > 0 and "Total_Sales" in df_sub_display.columns:
    df_plot = df_sub_display.reset_index()
    name_col = df_plot.columns[0]
    fig = px.treemap(
        df_plot, path=[name_col], values="Total_Sales",
        color="Avg_Profit_Rate" if "Avg_Profit_Rate" in df_plot.columns else "Total_Sales",
        color_continuous_scale=CHART_COLORS["sequential_blue"],
        hover_data={"Total_Sales": ":$,.0f", "Avg_Profit_Rate": ":.1%"} if "Avg_Profit_Rate" in df_plot.columns else {"Total_Sales": ":$,.0f"},
    )
    fig.update_traces(
        textinfo="label+value",
        textfont=dict(size=13, color="white", family="Inter"),
        marker=dict(cornerradius=4),
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=420, paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# ── Scatter: Sales vs Profit ──
cl, cr = st.columns(2)

with cl:
    st.markdown(
        '<div class="section-card"><div class="section-title">Sales vs Profit Scatter</div>',
        unsafe_allow_html=True,
    )
    if len(df_sub_display) > 0 and "Total_Sales" in df_sub_display.columns:
        df_plot = df_sub_display.reset_index()
        name_col = df_plot.columns[0]
        low_mask = df_plot.get("Is_LowSales", pd.Series(["否"] * len(df_plot))) == "是"
        fig = px.scatter(
            df_plot, x="Total_Sales", y="Total_Profit",
            size="Total_Quantity" if "Total_Quantity" in df_plot.columns else None,
            hover_name=name_col,
            color_discrete_sequence=[COLORS["primary"]],
        )
        if low_mask.any():
            fig.add_scatter(
                x=df_plot.loc[low_mask, "Total_Sales"],
                y=df_plot.loc[low_mask, "Total_Profit"],
                mode="markers", name="Low Sales",
                marker=dict(color=COLORS["danger"], size=12, symbol="x", line=dict(width=2)),
                hovertext=df_plot.loc[low_mask, name_col],
            )
        fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="white")))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Total Sales", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            yaxis=dict(title="Total Profit", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"])),
            legend=dict(orientation="h", y=1.12, font=dict(color=COLORS["ink_secondary"], size=11)),
            margin=dict(l=0, r=0, t=0, b=0), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown(
        '<div class="section-card"><div class="section-title">Category Profit Margin</div>',
        unsafe_allow_html=True,
    )
    if len(df_cat_display) > 0 and "Avg_Profit_Rate" in df_cat_display.columns:
        df_plot = df_cat_display.reset_index()
        name_col = df_plot.columns[0]
        profit_rates = df_plot["Avg_Profit_Rate"]
        if profit_rates.max() < 1:
            profit_rates = profit_rates * 100
        colors_bar = [COLORS["success"] if v >= 12 else COLORS["warning"] if v >= 8 else COLORS["danger"] for v in profit_rates]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df_plot[name_col], x=profit_rates,
            orientation="h", marker_color=colors_bar,
            marker_line_width=0,
            text=[f"{v:.1f}%" for v in profit_rates],
            textposition="outside", textfont=dict(color=COLORS["ink_secondary"], size=12),
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Profit Margin (%)", gridcolor="#F1F5F9", tickfont=dict(color=COLORS["ink_muted"]), range=[0, max(profit_rates) * 1.25]),
            yaxis=dict(tickfont=dict(color=COLORS["ink_secondary"])),
            margin=dict(l=0, r=40, t=0, b=0), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ── Category summary table ──
st.markdown(
    '<div class="section-card"><div class="section-title">Category Overview</div>',
    unsafe_allow_html=True,
)
if len(df_cat_display) > 0:
    display_cols = [c for c in ["Total_Sales", "Total_Profit", "Avg_Profit_Rate", "Order_Count", "Sales_Share"] if c in df_cat_display.columns]
    df_display = df_cat_display[display_cols].copy()
    for c in df_display.columns:
        if "Rate" in c or "Share" in c:
            df_display[c] = df_display[c].apply(lambda x: f"{x*100:.1f}%" if isinstance(x, (int, float)) and abs(x) < 10 else f"{x:.1f}%")
        elif "Sales" in c or "Profit" in c:
            df_display[c] = df_display[c].apply(lambda x: f"${x:,.0f}")
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={c: st.column_config.TextColumn(label=c.replace("_", " ").title()) for c in df_display.columns},
    )
st.markdown("</div>", unsafe_allow_html=True)
