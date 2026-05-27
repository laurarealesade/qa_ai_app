"""
Uploads/downloads files to OneDrive via Microsoft Graph API.
All paths are relative to the authenticated user's OneDrive root.
"""
import logging

import requests

from src.auth import get_graph_token

log = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _headers(extra: dict | None = None) -> dict:
    h = {"Authorization": f"Bearer {get_graph_token()}"}
    if extra:
        h.update(extra)
    return h


def upload_file(onedrive_path: str, file_bytes: bytes) -> str:
    """
    Uploads file_bytes to onedrive_path (e.g. 'folder/file.xlsx').
    Creates intermediate folders automatically.
    Returns the OneDrive item ID.
    """
    encoded_path = onedrive_path.replace(" ", "%20")
    url = f"{GRAPH_BASE}/me/drive/root:/{encoded_path}:/content"

    resp = requests.put(
        url,
        headers=_headers({"Content-Type": "application/octet-stream"}),
        data=file_bytes,
    )
    resp.raise_for_status()
    item_id = resp.json()["id"]
    log.info("Uploaded to OneDrive: %s (item %s)", onedrive_path, item_id)
    return item_id


def download_file(onedrive_path: str) -> bytes:
    encoded_path = onedrive_path.replace(" ", "%20")
    url = f"{GRAPH_BASE}/me/drive/root:/{encoded_path}:/content"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    return resp.content
