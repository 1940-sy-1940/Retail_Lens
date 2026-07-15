"""Power BI Push Dataset 数据推送模块。

流程：
1. 定义数据集 schema（列名 + 数据类型映射 DataFrame dtype → Power BI dataType）
2. 创建 Push Dataset → 返回 dataset_id
3. 逐表推送数据 → POST rows
4. 支持幂等：dataset 已存在则复用（按 dataset_name 查找）
"""

import json
import logging

import numpy as np
import pandas as pd
import requests

from .auth import get_api_headers, POWER_BI_API_BASE

logger = logging.getLogger(__name__)

# DataFrame dtype → Power BI dataType 映射
DTYPE_MAP = {
    "int64": "Int64",
    "int32": "Int64",
    "float64": "Double",
    "float32": "Double",
    "bool": "bool",
    "object": "string",
    "string": "string",
    "datetime64[ns]": "DateTime",
}


def _df_to_schema(table_name: str, df: pd.DataFrame) -> dict:
    """从 DataFrame 推断 Power BI 数据集表结构。"""
    columns = []
    # index 列也需要包含
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        pbi_type = DTYPE_MAP.get(dtype_str, "string")
        columns.append({"name": col, "dataType": pbi_type})

    # 如果 index 有名称，作为第一列
    if df.index.name:
        columns.insert(0, {"name": df.index.name, "dataType": "string"})

    return {"name": table_name, "columns": columns}


def _df_to_rows(df: pd.DataFrame) -> list[dict]:
    """将 DataFrame 转为 Power BI rows 格式（list of dict）。

    index 列的值会被包含在内。
    """
    # 先 reset_index 让 index 变为普通列
    out = df.reset_index() if df.index.name else df.copy()

    # 处理 NaN / NaT：Power BI 不接受 NaN
    for col in out.columns:
        if out[col].dtype in ("float64", "float32"):
            out[col] = out[col].where(out[col].notna(), None)
        elif out[col].dtype == "object":
            out[col] = out[col].fillna("")

    # datetime 转为 ISO 字符串
    for col in out.select_dtypes(include=["datetime64"]).columns:
        out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

    return out.to_dict(orient="records")


def find_dataset(headers: dict, group_id: str, dataset_name: str) -> str | None:
    """查找已存在的 dataset，返回 dataset_id 或 None。"""
    url = f"{POWER_BI_API_BASE}/groups/{group_id}/datasets"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    datasets = resp.json().get("value", [])
    for ds in datasets:
        if ds.get("name") == dataset_name:
            logger.info("Found existing dataset: %s (%s)", dataset_name, ds["id"])
            return ds["id"]
    return None


def create_dataset(
    headers: dict, group_id: str, dataset_name: str, tables_data: list[dict],
) -> str:
    """创建 Push Dataset 并返回 dataset_id。"""
    tables_schema = [
        _df_to_schema(name, df) for name, df, _ in tables_data
    ]
    payload = {
        "name": dataset_name,
        "defaultMode": "Push",
        "tables": tables_schema,
    }
    url = f"{POWER_BI_API_BASE}/groups/{group_id}/datasets"
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code == 201:
        ds_id = resp.json()["id"]
        logger.info("Dataset created: %s (%s)", dataset_name, ds_id)
        return ds_id
    else:
        logger.error("Failed to create dataset: %s", resp.text)
        resp.raise_for_status()


def delete_dataset(headers: dict, group_id: str, dataset_id: str):
    """删除已有 dataset，为重建做准备。"""
    url = f"{POWER_BI_API_BASE}/groups/{group_id}/datasets/{dataset_id}"
    resp = requests.delete(url, headers=headers)
    if resp.status_code in (200, 204):
        logger.info("Deleted dataset %s", dataset_id)
    else:
        logger.warning("Failed to delete dataset %s: %s", dataset_id, resp.text)


def push_table(
    headers: dict, group_id: str, dataset_id: str,
    table_name: str, rows: list[dict],
):
    """向指定表推送数据行。"""
    url = (
        f"{POWER_BI_API_BASE}/groups/{group_id}"
        f"/datasets/{dataset_id}/tables/{table_name}/rows"
    )
    # 分批推送（Power BI 单次最多 10000 行，10MB）
    if len(rows) <= 10000:
        resp = requests.post(url, json={"rows": rows}, headers=headers)
        resp.raise_for_status()
        logger.info("  Pushed %d rows → %s", len(rows), table_name)
    else:
        chunk = 5000
        for i in range(0, len(rows), chunk):
            batch = rows[i : i + chunk]
            resp = requests.post(url, json={"rows": batch}, headers=headers)
            resp.raise_for_status()
        logger.info("  Pushed %d rows (batched) → %s", len(rows), table_name)


def push_all(
    results_map: dict,  # {"table_name": (DataFrame, description)}
    dataset_name: str = "Global_Retail_Analytics",
    client_id: str = "",
    client_secret: str = "",
    tenant_id: str = "common",
    workspace_id: str = "",
):
    """一键：认证 → 创建数据集 → 推送所有表。

    Args:
        results_map: {"regional_market": (df, "区域市场汇总"), ...}
        dataset_name: Power BI 数据集名称
        client_id/secret/tenant_id/workspace_id: Azure AD 凭证
    """
    from .auth import get_access_token

    logger.info("=== Power BI Push Dataset ===")

    # 1. 认证
    token = get_access_token(client_id, client_secret, tenant_id)
    headers = get_api_headers(token)

    # 2. 收集所有表数据
    tables_data = []
    for table_name, (df, _desc) in results_map.items():
        if len(df) > 0:
            tables_data.append((table_name, df, _desc))

    # 3. 检查是否存在同名 dataset，存在则先删除再重建（确保 schema 一致）
    existing_id = find_dataset(headers, workspace_id, dataset_name)
    if existing_id:
        delete_dataset(headers, workspace_id, existing_id)

    # 4. 创建 dataset
    ds_id = create_dataset(headers, workspace_id, dataset_name, tables_data)

    # 5. 推送各表数据
    for table_name, df, desc in tables_data:
        rows = _df_to_rows(df)
        push_table(headers, workspace_id, ds_id, table_name, rows)

    # 6. 保存 dataset_id 到本地，后续报表/嵌入可复用
    config_path = Path(__file__).resolve().parent.parent.parent / "pbi_config.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    config["dataset_id"] = ds_id
    config["dataset_name"] = dataset_name
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))

    logger.info("=== Push complete: dataset_id=%s ===", ds_id)
    logger.info("Open Power BI Service to create report: "
                "https://app.powerbi.com/groups/%s/datasets/%s", workspace_id, ds_id)

    return ds_id
