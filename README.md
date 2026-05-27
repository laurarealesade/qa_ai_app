# ServiceNow → OneDrive → Power BI Automation

Cada hora (o cuando llega un correo de ServiceNow con adjunto Excel), este script:
1. Lee los correos no procesados desde Outlook via Microsoft Graph API
2. Descarga el archivo Excel adjunto
3. Cruza los IDs de agente con la tabla de referencia local (`data/agents_reference.xlsx`)
4. Genera la tabla agregada del dashboard (Agent_Name, Activity, Total_Toques, Total_Casos)
5. Sube el resultado a OneDrive (`servicenow-reports/dashboard_data.xlsx`)
6. Dispara el refresh del dataset en Power BI Service

---

## Configuración en 5 pasos

### 1. Registro de app en Azure AD

1. Ve a [portal.azure.com](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Nombre: `ServiceNow-PowerBI-Automation`
3. Tipo de cuenta: **Accounts in this organizational directory only**
4. Redirect URI: vacío (no se necesita)
5. Click en **Register**

Una vez creada la app:
- Copia el **Application (client) ID** → `AZURE_CLIENT_ID`
- Copia el **Directory (tenant) ID** → `AZURE_TENANT_ID`
- Ve a **Certificates & secrets** → **New client secret** → copia el valor → `AZURE_CLIENT_SECRET`

**Permisos necesarios (API permissions → Add a permission → Microsoft Graph → Application permissions):**
| Permiso | Propósito |
|---|---|
| `Mail.Read` | Leer correos del inbox |
| `Files.ReadWrite` | Subir archivos a OneDrive |
| `MailboxSettings.Read` | Leer categorías de Outlook |

Después de agregar los permisos: **Grant admin consent**.

Para Power BI también necesitas:
- **Power BI Service** → Application permissions → `Dataset.ReadWrite.All`

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Crear el archivo `.env`

```bash
cp .env.example .env
```

Llena los valores en `.env` con tus IDs reales.

### 4. Tabla de referencia de agentes

El archivo `data/agents_reference.xlsx` ya contiene los 50 agentes del equipo (24 Online, 10 Offline, 13 7Eleven, 2 Sr Analyst, 1 Team Leader).

Para agregar o modificar agentes, edita directamente ese archivo. El `Agent_ID` (columna A) debe coincidir exactamente con el valor que llega en la columna `Value` del Excel de ServiceNow.

> **Nota:** Team Leader y Sr Analyst aparecerán en el dashboard con esas etiquetas. Si solo quieres ver Online / Offline / 7Eleven, filtra la columna `Activity` en Power BI al diseñar el visual.

### 5. Conectar Power BI al Excel de OneDrive

1. Abre **Power BI Desktop**
2. **Get Data** → **OneDrive for Business**
3. Navega a `servicenow-reports/dashboard_data.xlsx`
4. Selecciona la hoja `Dashboard`
5. Diseña el visual: tabla con Agent_Name, Activity, Total_Toques, Total_Casos
6. Publica el reporte en **Power BI Service**
7. En Power BI Service: ve al dataset → **Settings** → **Scheduled refresh** → activa y configura cada hora como respaldo

---

## Ejecutar la automatización

**Modo continuo (recomendado — deja corriendo en tu máquina o servidor):**
```bash
python run.py
```

**Modo una sola vez (para cron o Task Scheduler de Windows):**
```bash
python run.py --once
```

**Programar en Windows Task Scheduler:**
- Acción: `python C:\ruta\del\proyecto\run.py --once`
- Trigger: repetir cada 1 hora

**Programar en Linux/Mac (cron):**
```
0 * * * * cd /ruta/del/proyecto && python run.py --once >> logs/cron.log 2>&1
```

---

## Estructura del proyecto

```
qa_ai_app/
├── src/
│   ├── config.py           # Variables de configuración
│   ├── auth.py             # Autenticación con Azure AD (MSAL)
│   ├── email_monitor.py    # Lectura de correos via Graph API
│   ├── data_processor.py   # Transformación y agregación del Excel
│   ├── onedrive_client.py  # Subida de archivos a OneDrive
│   ├── powerbi_client.py   # Trigger de refresh en Power BI
│   └── main.py             # Orquestador del pipeline
├── data/
│   └── agents_reference.xlsx   # Tabla Agent_ID → Nombre, Actividad
├── run.py                  # Entry point con scheduler
├── create_agents_template.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Dashboard — Columnas de salida

| Columna | Descripción |
|---|---|
| `Agent_Name` | Nombre del agente |
| `Activity` | Online / Offline / 7Eleven |
| `Total_Toques` | COUNT de filas (cada fila = un toque) |
| `Total_Casos` | DISTINCT COUNT del campo `ID` (casos únicos) |
