"""
Monitors the inbox via Microsoft Graph API and downloads Excel attachments
from ServiceNow report emails that have not been processed yet.
"""
import logging
from datetime import datetime, timezone
from typing import Iterator

import requests

from src.auth import get_graph_token
from src.config import SERVICENOW_SENDER

log = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
_PROCESSED_LABEL = "SN_Processed"  # category we apply after processing


def _headers() -> dict:
    return {"Authorization": f"Bearer {get_graph_token()}"}


def _ensure_category_exists() -> None:
    """Creates the Outlook category used to mark processed emails if missing."""
    url = f"{GRAPH_BASE}/me/outlook/masterCategories"
    existing = requests.get(url, headers=_headers()).json().get("value", [])
    if not any(c["displayName"] == _PROCESSED_LABEL for c in existing):
        requests.post(url, headers=_headers(), json={"displayName": _PROCESSED_LABEL, "color": "preset9"})


def _mark_processed(message_id: str) -> None:
    url = f"{GRAPH_BASE}/me/messages/{message_id}"
    requests.patch(url, headers=_headers(), json={"categories": [_PROCESSED_LABEL]})


def fetch_unprocessed_attachments() -> Iterator[tuple[str, bytes]]:
    """
    Yields (filename, file_bytes) for every Excel attachment from ServiceNow
    emails that haven't been marked as processed yet.
    """
    _ensure_category_exists()

    filter_query = (
        f"from/emailAddress/address eq '{SERVICENOW_SENDER}'"
        f" and not categories/any(c:c eq '{_PROCESSED_LABEL}')"
        f" and hasAttachments eq true"
    )
    url = (
        f"{GRAPH_BASE}/me/messages"
        f"?$filter={filter_query}"
        f"&$select=id,subject,receivedDateTime,hasAttachments"
        f"&$orderby=receivedDateTime desc"
        f"&$top=10"
    )

    messages = requests.get(url, headers=_headers()).json().get("value", [])
    log.info("Found %d unprocessed ServiceNow emails", len(messages))

    for msg in messages:
        msg_id = msg["id"]
        att_url = f"{GRAPH_BASE}/me/messages/{msg_id}/attachments"
        attachments = requests.get(att_url, headers=_headers()).json().get("value", [])

        for att in attachments:
            name: str = att.get("name", "")
            if not name.lower().endswith((".xlsx", ".xls")):
                continue
            content_bytes = requests.get(
                f"{GRAPH_BASE}/me/messages/{msg_id}/attachments/{att['id']}/$value",
                headers=_headers(),
            ).content
            log.info("Downloaded attachment: %s (%d bytes)", name, len(content_bytes))
            yield name, content_bytes

        _mark_processed(msg_id)
