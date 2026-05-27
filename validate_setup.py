"""
Validates that the local setup is correct before running the pipeline.

    python validate_setup.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m!\033[0m"


def check(label: str, fn):
    try:
        result = fn()
        print(f"  {PASS} {label}" + (f" — {result}" if result else ""))
        return True
    except Exception as exc:
        print(f"  {FAIL} {label}")
        print(f"      → {exc}")
        return False


def main():
    print("\n=== ServiceNow → Power BI — Validación de configuración ===\n")
    ok = True

    # ── 1. .env variables ─────────────────────────────────────────────────────
    print("1. Variables de entorno (.env)")
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print(f"  {FAIL} python-dotenv no instalado — corre: pip install -r requirements.txt")
        sys.exit(1)

    for var in ["INCOMING_FOLDER", "OUTPUT_FILE"]:
        val = os.getenv(var, "")
        if val:
            print(f"  {PASS} {var} = {val}")
        else:
            print(f"  {FAIL} {var} — no configurado en .env")
            ok = False

    # ── 2. Carpetas ───────────────────────────────────────────────────────────
    print("\n2. Carpetas en OneDrive")
    def check_incoming():
        from src.config import INCOMING_FOLDER, PROCESSED_FOLDER
        INCOMING_FOLDER.mkdir(parents=True, exist_ok=True)
        PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
        xlsx_count = len(list(INCOMING_FOLDER.glob("*.xlsx")))
        return f"creada — {xlsx_count} archivo(s) Excel pendientes"
    ok &= check("Carpeta incoming", check_incoming)

    def check_output_dir():
        from src.config import OUTPUT_FILE
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        return str(OUTPUT_FILE.parent)
    ok &= check("Carpeta de salida", check_output_dir)

    # ── 3. Archivo de agentes ─────────────────────────────────────────────────
    print("\n3. Tabla de referencia de agentes")
    def check_agents():
        import pandas as pd
        from src.config import AGENTS_REFERENCE_FILE
        if not AGENTS_REFERENCE_FILE.exists():
            raise FileNotFoundError(f"{AGENTS_REFERENCE_FILE} no existe")
        df = pd.read_excel(AGENTS_REFERENCE_FILE)
        missing = {"Agent_ID", "Agent_Name", "Activity"} - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")
        counts = df.groupby("Activity")["Agent_Name"].count().to_dict()
        return f"{len(df)} agentes — {counts}"
    ok &= check("agents_reference.xlsx", check_agents)

    # ── 4. Dependencias Python ────────────────────────────────────────────────
    print("\n4. Dependencias Python")
    for lib in ["pandas", "openpyxl", "schedule"]:
        def _check(l=lib):
            __import__(l)
            import importlib.metadata
            return importlib.metadata.version(l)
        ok &= check(lib, _check)

    # ── 5. Power BI (opcional) ────────────────────────────────────────────────
    pbi_ws = os.getenv("POWERBI_WORKSPACE_ID", "")
    if pbi_ws:
        print("\n5. Power BI auto-refresh")
        def check_pbi():
            import msal
            from src.config import POWERBI_CLIENT_ID, POWERBI_CLIENT_SECRET, POWERBI_TENANT_ID
            if not all([POWERBI_CLIENT_ID, POWERBI_CLIENT_SECRET, POWERBI_TENANT_ID]):
                raise ValueError("Faltan POWERBI_CLIENT_ID, CLIENT_SECRET o TENANT_ID")
            app = msal.ConfidentialClientApplication(
                client_id=POWERBI_CLIENT_ID,
                client_credential=POWERBI_CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{POWERBI_TENANT_ID}",
            )
            result = app.acquire_token_for_client(
                scopes=["https://analysis.windows.net/powerbi/api/.default"]
            )
            if "access_token" not in result:
                raise RuntimeError(result.get("error_description"))
            return "token obtenido"
        ok &= check("Power BI token", check_pbi)
    else:
        print(f"\n5. Power BI auto-refresh — {WARN} omitido (usa el refresh programado de Power BI Service)")

    # ── Resumen ───────────────────────────────────────────────────────────────
    print()
    if ok:
        print(f"{PASS} Todo listo. Ejecuta: python run.py")
    else:
        print(f"{FAIL} Hay errores. Revisa los puntos marcados arriba.")
    print()


if __name__ == "__main__":
    main()
