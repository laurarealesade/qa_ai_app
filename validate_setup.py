"""
Validates that all connections are working before running the pipeline.
Run this after filling in your .env file.

    python validate_setup.py
"""
import sys
import os
from pathlib import Path

# Allow running from project root
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

    # ── 1. Environment variables ──────────────────────────────────────────────
    print("1. Variables de entorno (.env)")
    required_vars = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]
    optional_vars = ["POWERBI_WORKSPACE_ID", "POWERBI_DATASET_ID"]

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print(f"  {FAIL} python-dotenv no instalado — corre: pip install -r requirements.txt")
        sys.exit(1)

    for var in required_vars:
        val = os.getenv(var, "")
        if val and val != f"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" and "your-" not in val:
            print(f"  {PASS} {var}")
        else:
            print(f"  {FAIL} {var} — no configurado en .env")
            ok = False

    for var in optional_vars:
        val = os.getenv(var, "")
        if val and "xxxx" not in val:
            print(f"  {PASS} {var} (Power BI)")
        else:
            print(f"  {WARN} {var} — no configurado (refresh automático desactivado)")

    # ── 2. Agents reference file ──────────────────────────────────────────────
    print("\n2. Archivo de referencia de agentes")
    def check_agents_file():
        import pandas as pd
        path = Path("data/agents_reference.xlsx")
        if not path.exists():
            raise FileNotFoundError("data/agents_reference.xlsx no existe")
        df = pd.read_excel(path)
        required_cols = {"Agent_ID", "Agent_Name", "Activity"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")
        return f"{len(df)} agentes, actividades: {sorted(df['Activity'].unique().tolist())}"

    ok &= check("data/agents_reference.xlsx", check_agents_file)

    # ── 3. Azure AD authentication ────────────────────────────────────────────
    print("\n3. Autenticación Azure AD (MSAL)")
    def check_msal():
        import msal
        return "módulo disponible"
    ok &= check("msal instalado", check_msal)

    def check_graph_token():
        from src.auth import get_graph_token
        token = get_graph_token()
        return f"token obtenido ({len(token)} chars)"
    ok &= check("Token de Microsoft Graph", check_graph_token)

    # ── 4. Microsoft Graph — Mailbox access ───────────────────────────────────
    print("\n4. Acceso al buzón de correo (Graph API)")
    def check_mailbox():
        import requests
        from src.auth import get_graph_token
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me/mailFolders/inbox",
            headers={"Authorization": f"Bearer {get_graph_token()}"},
        )
        if resp.status_code == 200:
            count = resp.json().get("totalItemCount", "?")
            return f"inbox accesible ({count} mensajes)"
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.json().get('error', {}).get('message', resp.text)}")
    ok &= check("Leer inbox (Mail.Read)", check_mailbox)

    # ── 5. OneDrive access ────────────────────────────────────────────────────
    print("\n5. Acceso a OneDrive (Graph API)")
    def check_onedrive():
        import requests
        from src.auth import get_graph_token
        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me/drive/root",
            headers={"Authorization": f"Bearer {get_graph_token()}"},
        )
        if resp.status_code == 200:
            name = resp.json().get("name", "OneDrive")
            quota = resp.json().get("quota", {})
            used_gb = round(quota.get("used", 0) / 1e9, 2)
            return f"'{name}' — {used_gb} GB usados"
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.json().get('error', {}).get('message', resp.text)}")
    ok &= check("OneDrive raíz (Files.ReadWrite)", check_onedrive)

    def check_onedrive_write():
        import requests
        from src.auth import get_graph_token
        test_content = b"test"
        resp = requests.put(
            "https://graph.microsoft.com/v1.0/me/drive/root:/servicenow-reports/.test:/content",
            headers={
                "Authorization": f"Bearer {get_graph_token()}",
                "Content-Type": "application/octet-stream",
            },
            data=test_content,
        )
        if resp.status_code in (200, 201):
            # Clean up test file
            item_id = resp.json()["id"]
            requests.delete(
                f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}",
                headers={"Authorization": f"Bearer {get_graph_token()}"},
            )
            return "escritura y borrado OK"
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.json().get('error', {}).get('message', resp.text)}")
    ok &= check("Escritura en OneDrive", check_onedrive_write)

    # ── 6. Power BI (optional) ────────────────────────────────────────────────
    pbi_ws = os.getenv("POWERBI_WORKSPACE_ID", "")
    pbi_ds = os.getenv("POWERBI_DATASET_ID", "")
    if pbi_ws and pbi_ds and "xxxx" not in pbi_ws:
        print("\n6. Power BI Service")
        def check_powerbi_token():
            from src.auth import get_powerbi_token
            token = get_powerbi_token()
            return f"token obtenido ({len(token)} chars)"
        ok &= check("Token de Power BI", check_powerbi_token)

        def check_powerbi_dataset():
            import requests
            from src.auth import get_powerbi_token
            resp = requests.get(
                f"https://api.powerbi.com/v1.0/myorg/groups/{pbi_ws}/datasets/{pbi_ds}",
                headers={"Authorization": f"Bearer {get_powerbi_token()}"},
            )
            if resp.status_code == 200:
                name = resp.json().get("name", "dataset")
                return f"dataset '{name}' encontrado"
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.json().get('error', {}).get('message', resp.text)}")
        ok &= check("Dataset de Power BI", check_powerbi_dataset)
    else:
        print(f"\n6. Power BI Service — {WARN} omitido (IDs no configurados)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if ok:
        print(f"{PASS} Todo listo. Puedes ejecutar: python run.py")
    else:
        print(f"{FAIL} Hay errores que resolver antes de ejecutar el pipeline.")
        print("   Revisa el README.md para instrucciones de configuración.")
    print()


if __name__ == "__main__":
    main()
