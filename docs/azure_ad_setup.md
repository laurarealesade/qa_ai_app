# Guía: Registro de App en Azure AD

Esta guía te lleva paso a paso para registrar la aplicación en Azure Active Directory
y obtener los 3 valores que necesitas en el `.env`.

---

## Lo que vas a obtener

| Variable en `.env`     | Dónde la encuentras               |
|------------------------|-----------------------------------|
| `AZURE_TENANT_ID`      | Overview de la app → Directory ID |
| `AZURE_CLIENT_ID`      | Overview de la app → Application ID |
| `AZURE_CLIENT_SECRET`  | Certificates & secrets            |

---

## Paso 1 — Abrir Azure Portal

1. Ve a **[portal.azure.com](https://portal.azure.com)** e inicia sesión con tu cuenta Microsoft 365 corporativa (la misma con la que recibes los correos de ServiceNow).
2. En la barra de búsqueda superior escribe **"App registrations"** y selecciónalo.

---

## Paso 2 — Crear la aplicación

1. Click en **"+ New registration"**
2. Llena el formulario:
   - **Name:** `ServiceNow-PowerBI-Automation`
   - **Supported account types:** `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI:** déjalo vacío
3. Click en **Register**

Al terminar verás la página de **Overview** de tu nueva app.

---

## Paso 3 — Copiar los IDs

En la página **Overview** copia:
- **Application (client) ID** → pégalo como `AZURE_CLIENT_ID` en tu `.env`
- **Directory (tenant) ID** → pégalo como `AZURE_TENANT_ID` en tu `.env`

---

## Paso 4 — Crear el Client Secret

1. En el menú izquierdo, click en **"Certificates & secrets"**
2. Pestaña **"Client secrets"** → **"+ New client secret"**
3. Descripción: `servicenow-automation`
4. Expiry: **24 months** (o el máximo disponible)
5. Click en **Add**
6. **⚠ IMPORTANTE:** Copia el valor de la columna **"Value"** AHORA. Solo se muestra una vez.
   - Pégalo como `AZURE_CLIENT_SECRET` en tu `.env`

---

## Paso 5 — Agregar permisos de API

1. En el menú izquierdo, click en **"API permissions"**
2. Click en **"+ Add a permission"**

### Permisos de Microsoft Graph

Click en **"Microsoft Graph"** → **"Application permissions"**

Busca y agrega estos 3 permisos:

| Permiso | Para qué sirve |
|---|---|
| `Mail.Read` | Leer los correos del inbox y descargar adjuntos |
| `Files.ReadWrite` | Subir y actualizar el Excel en OneDrive |
| `MailboxSettings.Read` | Crear categorías de Outlook para marcar correos procesados |

### Permisos de Power BI (si usas refresh automático)

Click en **"+ Add a permission"** → **"Power BI Service"** → **"Application permissions"**

| Permiso | Para qué sirve |
|---|---|
| `Dataset.ReadWrite.All` | Disparar el refresh del dataset |

---

## Paso 6 — Grant Admin Consent

> ⚠ Este paso requiere que seas **administrador del tenant** o que alguien con ese rol lo apruebe.

1. Verás el botón **"Grant admin consent for [tu organización]"**
2. Click en el botón → Confirmar
3. Todos los permisos deben mostrar un ✓ verde en la columna **"Status"**

Si no tienes permisos de administrador, pídele a tu IT que apruebe los permisos de la app `ServiceNow-PowerBI-Automation`.

---

## Paso 7 — Verificar el `.env`

Tu archivo `.env` debe quedar así (con tus valores reales):

```env
AZURE_TENANT_ID=12345678-abcd-1234-abcd-123456789012
AZURE_CLIENT_ID=87654321-dcba-4321-dcba-210987654321
AZURE_CLIENT_SECRET=AbCdEfGh~123456789_secretvalue
SERVICENOW_SENDER=noreply@service-now.com
ONEDRIVE_INCOMING_FOLDER=servicenow-reports/incoming
ONEDRIVE_OUTPUT_FILE=servicenow-reports/dashboard_data.xlsx
POWERBI_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POWERBI_DATASET_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POLL_INTERVAL_MINUTES=60
```

---

## Paso 8 — Validar la configuración

```bash
python validate_setup.py
```

Deberías ver:

```
✓ AZURE_TENANT_ID
✓ AZURE_CLIENT_ID
✓ AZURE_CLIENT_SECRET
✓ data/agents_reference.xlsx — 50 agentes
✓ Token de Microsoft Graph — token obtenido
✓ Leer inbox (Mail.Read)
✓ Escritura en OneDrive
✓ Todo listo. Puedes ejecutar: python run.py
```

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `AADSTS700016: Application not found` | Client ID incorrecto | Verifica `AZURE_CLIENT_ID` en el Overview |
| `AADSTS7000215: Invalid client secret` | Secret mal copiado o expirado | Crea un nuevo secret |
| `Authorization_RequestDenied` | Falta Grant Admin Consent | Pide al admin que apruebe los permisos |
| `Insufficient privileges` | Falta el permiso específico | Revisa que todos los permisos estén en verde |
