"""
Entry point. Runs the pipeline once immediately, then every POLL_INTERVAL_MINUTES.

Usage:
    python run.py          # runs forever (scheduler mode)
    python run.py --once   # runs once and exits (useful for cron / Task Scheduler)
"""
import logging
import sys
import time

import schedule

from src.config import POLL_INTERVAL_MINUTES
from src.main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    once = "--once" in sys.argv

    run_pipeline()

    if once:
        sys.exit(0)

    schedule.every(POLL_INTERVAL_MINUTES).minutes.do(run_pipeline)
    logging.getLogger(__name__).info(
        "Scheduler running — next check in %d minute(s). Press Ctrl+C to stop.",
        POLL_INTERVAL_MINUTES,
    )

    while True:
        schedule.run_pending()
        time.sleep(30)
