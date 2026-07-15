"""Retail Lens — Design System. Inspired by Vercel + Stripe + Linear + Apple."""

# ═══════════════════════════════════════════
#  COLOR SYSTEM
# ═══════════════════════════════════════════
COLORS = {
    # Brand
    "primary": "#6366F1",
    "primary_dark": "#4F46E5",
    "primary_light": "#EEF2FF",

    # Surface ladder (Vercel-inspired)
    "canvas": "#FFFFFF",
    "canvas_soft": "#F8FAFC",
    "canvas_subtle": "#F1F5F9",

    # Text
    "ink": "#0F172A",
    "ink_secondary": "#475569",
    "ink_muted": "#94A3B8",
    "ink_inverse": "#FFFFFF",

    # Border
    "border": "#E2E8F0",
    "border_light": "#F1F5F9",

    # Semantic
    "success": "#10B981",
    "success_bg": "#ECFDF5",
    "warning": "#F59E0B",
    "warning_bg": "#FFFBEB",
    "danger": "#EF4444",
    "danger_bg": "#FEF2F2",
    "info": "#3B82F6",

    # Sidebar (Linear-inspired dark)
    "sidebar_bg": "#0A0A0B",
    "sidebar_hover": "#1A1A1C",
    "sidebar_text": "#D4D4D8",
    "sidebar_muted": "#71717A",

    # Gradient stops
    "gradient_start": "#6366F1",
    "gradient_mid": "#8B5CF6",
    "gradient_end": "#EC4899",
}

# ═══════════════════════════════════════════
#  CHART COLOR PALETTES
# ═══════════════════════════════════════════
CHART_COLORS = {
    "category": [
        "#6366F1", "#8B5CF6", "#EC4899", "#06B6D4",
        "#10B981", "#F59E0B", "#EF4444", "#3B82F6",
        "#14B8A6", "#F97316",
    ],
    "sequential_blue": [[0, "#E0E7FF"], [0.5, "#6366F1"], [1.0, "#312E81"]],
    "sequential_red": [[0, "#FEE2E2"], [0.5, "#EF4444"], [1.0, "#7F1D1D"]],
    "sequential_warm": [[0, "#FEF3C7"], [0.5, "#F59E0B"], [1.0, "#92400E"]],
    "diverging": [[0, "#EF4444"], [0.5, "#F8FAFC"], [1.0, "#10B981"]],
}

# ═══════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════
GLOBAL_CSS = """
<style>
/* ── Inter font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

/* ── Page background + subtle top gradient ── */
.main {
    background: linear-gradient(180deg, #EEF2FF 0%, #F8FAFC 160px, #FFFFFF 100%);
}

/* ── SIDEBAR: Linear-inspired dark ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09090B 0%, #18181B 100%) !important;
    border-right: 1px solid #27272A !important;
}
[data-testid="stSidebar"] * {
    color: #D4D4D8 !important;
}
[data-testid="stSidebar"] label {
    color: #71717A !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stCaption {
    color: #52525B !important;
    font-size: 0.68rem !important;
}
[data-testid="stSidebar"] hr {
    border-color: #27272A !important;
    margin: 1rem 0 !important;
}

/* ── Sidebar selectbox ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #18181B !important;
    border: 1px solid #27272A !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: #6366F1 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #71717A !important;
}

/* ── KPI CARD (Vercel-style stacked shadow) ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow:
        0px 1px 2px rgba(15,23,42,0.04),
        0px 1px 3px rgba(15,23,42,0.06);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.kpi-card:hover {
    box-shadow:
        0px 4px 6px rgba(15,23,42,0.04),
        0px 2px 4px rgba(15,23,42,0.04);
    transform: translateY(-1px);
}
.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.15;
    letter-spacing: -0.02em;
}

/* ── SECTION CARD ── */
.section-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0px 1px 2px rgba(15,23,42,0.04);
    margin-bottom: 1rem;
    height: 100%;
}
.section-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::before {
    content: '';
    width: 3px;
    height: 16px;
    background: #6366F1;
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── ALERT / LOW-PERFORMANCE CARD ── */
.alert-card {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    transition: box-shadow 0.2s;
}
.alert-card:hover {
    box-shadow: 0px 2px 4px rgba(239,68,68,0.1);
}
.alert-card .title {
    font-weight: 600;
    color: #991B1B;
    font-size: 0.875rem;
}
.alert-card .detail {
    color: #64748B;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}
.alert-card .highlight {
    color: #EF4444;
    font-size: 0.75rem;
    font-weight: 500;
}

/* ── BRAND BADGE ── */
.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #EEF2FF;
    color: #4F46E5;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.15rem 0.55rem;
    border-radius: 9999px;
}

/* ── PAGE HEADER ── */
.page-header {
    margin-bottom: 1.25rem;
}
.page-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
    letter-spacing: -0.03em;
}
.page-header .subtitle {
    font-size: 0.8rem;
    color: #94A3B8;
    font-weight: 400;
}

/* ── Plotly tweaks ── */
.js-plotly-plot .plotly .main-svg {
    border-radius: 8px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ── Block container max-width ── */
.block-container { max-width: 1400px; padding-top: 1rem; }
</style>
"""
