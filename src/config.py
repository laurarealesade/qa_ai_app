import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

# Local OneDrive-synced folder paths (Windows example shown in .env.example)
INCOMING_FOLDER = Path(os.environ["INCOMING_FOLDER"])
PROCESSED_FOLDER = Path(os.getenv("PROCESSED_FOLDER", str(INCOMING_FOLDER.parent / "processed")))
OUTPUT_FILE = Path(os.environ["OUTPUT_FILE"])

AGENTS_REFERENCE_FILE = BASE_DIR / "data" / "agents_reference.xlsx"

# Columns in the ServiceNow Excel export
SN_CASE_ID_COL = "ID"
SN_AGENT_ID_COL = "Value"

# Columns in agents_reference.xlsx
REF_AGENT_ID_COL = "Agent_ID"
REF_AGENT_NAME_COL = "Agent_Name"
REF_ACTIVITY_COL = "Activity"

# Power BI optional auto-refresh via REST API
# Leave blank to skip — Power BI Service will refresh on its own schedule
POWERBI_WORKSPACE_ID = os.getenv("POWERBI_WORKSPACE_ID", "")
POWERBI_DATASET_ID = os.getenv("POWERBI_DATASET_ID", "")
POWERBI_CLIENT_ID = os.getenv("POWERBI_CLIENT_ID", "")
POWERBI_CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET", "")
POWERBI_TENANT_ID = os.getenv("POWERBI_TENANT_ID", "")

POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "60"))
