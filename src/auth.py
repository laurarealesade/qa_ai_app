import msal
from src.config import AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

_GRAPH_SCOPES = ["https://graph.microsoft.com/.default"]
_POWERBI_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]

_token_cache: dict = {}


def _get_app():
    return msal.ConfidentialClientApplication(
        client_id=AZURE_CLIENT_ID,
        client_credential=AZURE_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}",
    )


def get_graph_token() -> str:
    result = _get_app().acquire_token_for_client(scopes=_GRAPH_SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"Graph auth failed: {result.get('error_description')}")
    return result["access_token"]


def get_powerbi_token() -> str:
    result = _get_app().acquire_token_for_client(scopes=_POWERBI_SCOPES)
    if "access_token" not in result:
        raise RuntimeError(f"Power BI auth failed: {result.get('error_description')}")
    return result["access_token"]
