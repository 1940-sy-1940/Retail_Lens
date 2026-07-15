"""Power BI REST API 认证模块。

支持两种凭证来源（优先级从高到低）：
1. 环境变量: PBI_CLIENT_ID / PBI_CLIENT_SECRET / PBI_TENANT_ID / PBI_WORKSPACE_ID
2. 配置文件: pbi_config.json（项目根目录）

认证方式：OAuth2 Client Credentials Flow → 获取 access_token → 调用 Power BI REST API。

前置条件（一次性配置）：
- 拥有 Power BI Pro 账号
- 在 Azure AD 注册应用，授予 Dataset.ReadWrite.All 权限
- 记录 client_id、client_secret、tenant_id、workspace_id
"""

import json
import logging
import os
import requests
from pathlib import Path

TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/token"
POWER_BI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
SCOPE = "https://analysis.windows.net/powerbi/api/.default"

logger = logging.getLogger(__name__)


def _load_config() -> dict:
    """从 pbi_config.json 加载凭证，不存在则返回空。"""
    config_path = Path(__file__).resolve().parent.parent.parent / "pbi_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def get_credentials() -> tuple[str, str, str, str]:
    """获取 Power BI 凭证 (client_id, client_secret, tenant_id, workspace_id)。

    优先环境变量，其次 pbi_config.json。
    """
    config = _load_config()
    return (
        os.getenv("PBI_CLIENT_ID") or config.get("client_id", ""),
        os.getenv("PBI_CLIENT_SECRET") or config.get("client_secret", ""),
        os.getenv("PBI_TENANT_ID") or config.get("tenant_id", "common"),
        os.getenv("PBI_WORKSPACE_ID") or config.get("workspace_id", ""),
    )


def get_access_token(client_id: str, client_secret: str, tenant_id: str = "common") -> str:
    """通过 OAuth2 Client Credentials 获取 access_token。

    tenant_id 默认为 "common"（适用于大多数场景，也可用具体 tenant ID）。
    """
    url = TOKEN_URL.format(tenant_id=tenant_id)
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": "https://analysis.windows.net/powerbi/api",
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    token = resp.json()["access_token"]
    logger.info("Access token acquired (expires in %ss)", resp.json().get("expires_in", "?"))
    return token


def get_api_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
