import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

SERVICENOW_SENDER = os.getenv("SERVICENOW_SENDER", "noreply@service-now.com")

ONEDRIVE_INCOMING_FOLDER = os.getenv("ONEDRIVE_INCOMING_FOLDER", "servicenow-reports/incoming")
ONEDRIVE_OUTPUT_FILE = os.getenv("ONEDRIVE_OUTPUT_FILE", "servicenow-reports/dashboard_data.xlsx")

POWERBI_WORKSPACE_ID = os.getenv("POWERBI_WORKSPACE_ID", "")
POWERBI_DATASET_ID = os.getenv("POWERBI_DATASET_ID", "")

POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "60"))

AGENTS_REFERENCE_FILE = BASE_DIR / "data" / "agents_reference.xlsx"

# Columns expected in the ServiceNow Excel export
SN_COLUMNS = ["Created", "Definition", "ID", "Value", "Start", "End", "Duration", "Calculation complete"]
SN_CASE_ID_COL = "ID"
SN_AGENT_ID_COL = "Value"

# Columns expected in agents_reference.xlsx
REF_AGENT_ID_COL = "Agent_ID"
REF_AGENT_NAME_COL = "Agent_Name"
REF_ACTIVITY_COL = "Activity"   # Online | Offline | 7Eleven
