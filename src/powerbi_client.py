"""
Optionally triggers a Power BI dataset refresh via REST API.
Only runs when all 5 Power BI variables are set in .env.
If not configured, Power BI Service uses its own scheduled refresh.
"""
import logging

from src.config import (
    POWERBI_CLIENT_ID,
    POWERBI_CLIENT_SECRET,
    POWERBI_DATASET_ID,
    POWERBI_TENANT_ID,
    POWERBI_WORKSPACE_ID,
)

log = logging.getLogger(__name__)

PBI_BASE = "https://api.powerbi.com/v1.0/myorg"


def trigger_dataset_refresh() -> None:
    if not all([POWERBI_WORKSPACE_ID, POWERBI_DATASET_ID, POWERBI_CLIENT_ID,
                POWERBI_CLIENT_SECRET, POWERBI_TENANT_ID]):
        log.info("Power BI auto-refresh not configured — skipping")
        return

    try:
        import msal
        import requests

        app = msal.ConfidentialClientApplication(
            client_id=POWERBI_CLIENT_ID,
            client_credential=POWERBI_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{POWERBI_TENANT_ID}",
        )
        result = app.acquire_token_for_client(
            scopes=["https://analysis.windows.net/powerbi/api/.default"]
        )
        if "access_token" not in result:
            log.warning("Power BI token failed: %s", result.get("error_description"))
            return

        url = f"{PBI_BASE}/groups/{POWERBI_WORKSPACE_ID}/datasets/{POWERBI_DATASET_ID}/refreshes"
        resp = requests.post(url, headers={"Authorization": f"Bearer {result['access_token']}"})
        if resp.status_code == 202:
            log.info("Power BI refresh triggered successfully")
        else:
            log.warning("Power BI refresh returned %d: %s", resp.status_code, resp.text)
    except Exception as exc:
        log.warning("Power BI refresh error (non-fatal): %s", exc)
