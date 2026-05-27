"""
Triggers a Power BI dataset refresh via the REST API.
Only runs if POWERBI_WORKSPACE_ID and POWERBI_DATASET_ID are configured.
"""
import logging

import requests

from src.auth import get_powerbi_token
from src.config import POWERBI_DATASET_ID, POWERBI_WORKSPACE_ID

log = logging.getLogger(__name__)

PBI_BASE = "https://api.powerbi.com/v1.0/myorg"


def trigger_dataset_refresh() -> None:
    if not POWERBI_WORKSPACE_ID or not POWERBI_DATASET_ID:
        log.info("Power BI IDs not configured — skipping refresh trigger")
        return

    url = f"{PBI_BASE}/groups/{POWERBI_WORKSPACE_ID}/datasets/{POWERBI_DATASET_ID}/refreshes"
    token = get_powerbi_token()
    resp = requests.post(url, headers={"Authorization": f"Bearer {token}"})

    if resp.status_code == 202:
        log.info("Power BI refresh triggered successfully")
    else:
        log.warning("Power BI refresh returned %d: %s", resp.status_code, resp.text)
