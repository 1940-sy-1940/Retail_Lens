"""数据加载与清洗：优先 Excel → 字段规范化 → 缺失值填充 → IQR 截断 → 衍生字段。

清洗后写入 data/processed/cleaned_data.csv，后续加载跳过清洗（闭环缓存）。
"""

import logging
import pandas as pd

from ..config import RAW_EXCEL, RAW_CSV, CLEANED_DATA, DATA_PROCESSED_DIR

logger = logging.getLogger(__name__)


def load_raw() -> pd.DataFrame:
    """优先加载 Excel，回退到 CSV。"""
    path = RAW_EXCEL if RAW_EXCEL.exists() else RAW_CSV
    logger.info("Loading raw data from %s", path.name)
    if path.suffix == ".xlsx":
        return pd.read_excel(str(path))
    return pd.read_csv(str(path))


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """清洗并构造衍生字段。"""
    # 列名规范化
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # 日期解析
    for col in ["Order_Date", "Ship_Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    # 衍生字段：物流天数
    if "Order_Date" in df.columns and "Ship_Date" in df.columns:
        df["ShippingDays"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

    # 衍生字段：利润率
    if "Sales" in df.columns and "Profit" in df.columns:
        df["ProfitRate"] = df["Profit"] / df["Sales"].replace(0, pd.NA)

    # 衍生字段：订单年月
    if "Order_Date" in df.columns:
        df["Order_YM"] = df["Order_Date"].dt.to_period("M").astype(str)

    # 缺失值填充
    for col in df.columns:
        if df[col].dtype in ("object", "string"):
            df[col] = df[col].fillna("Unknown")
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())

    # IQR 异常值截断
    skip = ["Row_ID", "Postal_Code", "ShippingDays", "Order_YM"]
    num_cols = [c for c in df.select_dtypes("number").columns if c not in skip]
    for col in num_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        df[col] = df[col].clip(lower=q1 - 1.5 * (q3 - q1), upper=q3 + 1.5 * (q3 - q1))

    logger.info("Cleaned: %d rows × %d cols", len(df), len(df.columns))
    return df


def make_dataset() -> pd.DataFrame:
    """完整清洗流程，结果缓存到 data/processed/。"""
    if CLEANED_DATA.exists():
        logger.info("Loading cached cleaned data → %s", CLEANED_DATA)
        return pd.read_csv(CLEANED_DATA, parse_dates=["Order_Date", "Ship_Date"])

    df = load_raw()
    df = preprocess(df)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED_DATA, index=False)
    logger.info("Saved cleaned data → %s", CLEANED_DATA)
    return df
