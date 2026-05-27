"""
Orchestrator: checks for new ServiceNow emails, processes attachments,
uploads aggregated data to OneDrive, and triggers a Power BI refresh.
"""
import logging

from src.config import ONEDRIVE_INCOMING_FOLDER, ONEDRIVE_OUTPUT_FILE
from src.data_processor import dataframe_to_excel_bytes, process_servicenow_excel
from src.email_monitor import fetch_unprocessed_attachments
from src.onedrive_client import upload_file
from src.powerbi_client import trigger_dataset_refresh

log = logging.getLogger(__name__)


def run_pipeline() -> None:
    log.info("=== Pipeline started ===")
    processed_count = 0

    for filename, file_bytes in fetch_unprocessed_attachments():
        log.info("Processing: %s", filename)
        try:
            dashboard_df = process_servicenow_excel(file_bytes)
        except Exception as exc:
            log.error("Failed to process %s: %s", filename, exc)
            continue

        # Archive the raw file on OneDrive
        upload_file(f"{ONEDRIVE_INCOMING_FOLDER}/{filename}", file_bytes)

        # Overwrite the master dashboard Excel with the latest aggregated data
        dashboard_bytes = dataframe_to_excel_bytes(dashboard_df)
        upload_file(ONEDRIVE_OUTPUT_FILE, dashboard_bytes)

        processed_count += 1
        log.info("Dashboard updated — %d agents", len(dashboard_df))

    if processed_count:
        trigger_dataset_refresh()
        log.info("Pipeline complete — processed %d file(s)", processed_count)
    else:
        log.info("No new ServiceNow emails found")

    log.info("=== Pipeline finished ===")
