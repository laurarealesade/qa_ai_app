"""
Orchestrator: watches the incoming OneDrive folder for new ServiceNow Excel files,
processes each one, and writes the aggregated dashboard Excel to the output path.
"""
import logging

from src.config import OUTPUT_FILE
from src.data_processor import dataframe_to_excel_bytes, process_servicenow_excel
from src.file_monitor import fetch_new_attachments
from src.powerbi_client import trigger_dataset_refresh

log = logging.getLogger(__name__)


def run_pipeline() -> None:
    log.info("=== Pipeline started ===")
    processed_count = 0

    for filename, file_bytes in fetch_new_attachments():
        log.info("Processing: %s", filename)
        try:
            dashboard_df = process_servicenow_excel(file_bytes)
        except Exception as exc:
            log.error("Failed to process %s: %s", filename, exc)
            continue

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(dataframe_to_excel_bytes(dashboard_df))
        processed_count += 1
        log.info("Dashboard updated → %s (%d agents)", OUTPUT_FILE, len(dashboard_df))

    if processed_count:
        trigger_dataset_refresh()
        log.info("Pipeline complete — processed %d file(s)", processed_count)
    else:
        log.info("No new files to process")

    log.info("=== Pipeline finished ===")
