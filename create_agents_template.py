"""
Run this script once to generate the agents_reference.xlsx template.
Then fill in your agents and re-save the file.

    python create_agents_template.py
"""
import pandas as pd
from pathlib import Path

sample = pd.DataFrame([
    {"Agent_ID": "AG001", "Agent_Name": "Juan Pérez",    "Activity": "Online"},
    {"Agent_ID": "AG002", "Agent_Name": "María López",   "Activity": "Offline"},
    {"Agent_ID": "AG003", "Agent_Name": "Carlos García", "Activity": "7Eleven"},
])

out = Path("data/agents_reference.xlsx")
out.parent.mkdir(exist_ok=True)
sample.to_excel(out, index=False)
print(f"Template created at {out}")
print("Edit it with your real agents and save.")
