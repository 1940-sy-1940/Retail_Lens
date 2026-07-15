"""全局配置：路径、分析阈值、图表样式。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── 数据路径 ──
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_EXCEL = DATA_RAW_DIR / "Global_Superstore2.xlsx"
RAW_CSV = DATA_RAW_DIR / "Global_Superstore2.csv"
CLEANED_DATA = DATA_PROCESSED_DIR / "cleaned_data.csv"

# ── 输出路径 ──
OUTPUT_DATA_DIR = PROJECT_ROOT / "outputs" / "data"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

# ── 分析参数 ──
LOW_PERFORMANCE_QUANTILE = 0.25
REPURCHASE_THRESHOLD = 2
TOP_N_CHARTS = 15

# ── 图表 ──
CHART_DPI = 150
CHART_FIGSIZE = (14, 7)
