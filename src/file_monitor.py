"""
Scans the incoming OneDrive-synced folder for unprocessed Excel files
and moves them to the processed folder after reading.
"""
import logging
import shutil
from pathlib import Path
from typing import Iterator

from src.config import INCOMING_FOLDER, PROCESSED_FOLDER

log = logging.getLogger(__name__)


def fetch_new_attachments() -> Iterator[tuple[str, bytes]]:
    """
    Yields (filename, file_bytes) for every Excel file found in INCOMING_FOLDER,
    then moves each file to PROCESSED_FOLDER so it won't be read again.
    """
    INCOMING_FOLDER.mkdir(parents=True, exist_ok=True)
    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

    files = list(INCOMING_FOLDER.glob("*.xlsx")) + list(INCOMING_FOLDER.glob("*.xls"))

    if not files:
        log.info("No new files in %s", INCOMING_FOLDER)
        return

    log.info("Found %d new file(s) in %s", len(files), INCOMING_FOLDER)

    for path in files:
        try:
            file_bytes = path.read_bytes()
            log.info("Reading: %s (%d bytes)", path.name, len(file_bytes))
            yield path.name, file_bytes

            dest = PROCESSED_FOLDER / path.name
            # Avoid overwriting if a file with the same name was processed before
            if dest.exists():
                dest = PROCESSED_FOLDER / f"{path.stem}_{path.stat().st_mtime_ns}{path.suffix}"
            shutil.move(str(path), str(dest))
            log.info("Moved to processed: %s", dest.name)

        except Exception as exc:
            log.error("Error reading %s: %s", path.name, exc)
