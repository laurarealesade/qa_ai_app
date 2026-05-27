# Guía: Configurar la regla de Outlook

Esta regla hace que Outlook guarde automáticamente el adjunto Excel de ServiceNow
en tu carpeta de OneDrive, sin intervención manual.

---

## Paso 1 — Crear las carpetas en OneDrive

1. Abre el Explorador de Windows
2. Navega a tu carpeta de **OneDrive** (aparece en el panel izquierdo)
3. Crea estas carpetas:
   ```
   OneDrive/
   └── servicenow-reports/
       ├── incoming/      ← aquí caerán los adjuntos nuevos
       └── processed/     ← aquí los moverá el script después de procesarlos
   ```

---

## Paso 2 — Crear la regla en Outlook

### Outlook Web (outlook.office.com)

1. Click en el engranaje ⚙️ (Settings) → **View all Outlook settings**
2. **Mail** → **Rules** → **+ Add new rule**
3. Llena la regla:
   - **Name:** `Guardar adjuntos ServiceNow`
   - **Add a condition:** `From` → escribe la dirección de ServiceNow (ej. `noreply@service-now.com`)
   - **Add a condition:** `Has attachment`
   - **Add an action:** `Save attachments to OneDrive` → selecciona la carpeta `servicenow-reports/incoming`
   - **Add an action:** `Mark as read` (opcional, para mantener el inbox limpio)
4. Click **Save**

### Outlook Desktop (Windows)

1. **Home** → **Rules** → **Manage Rules & Alerts**
2. Click **New Rule...**
3. Selecciona **"Apply rule on messages I receive"** → Next
4. Condición: marca **"from people or public group"** → click en el enlace azul → escribe `noreply@service-now.com` → OK → Next
5. Acción: marca **"save attachments to a folder"** → click en **"a folder"** → navega a `OneDrive\servicenow-reports\incoming` → OK → Next
6. Excepciones: ninguna → Next
7. Nombre: `Guardar adjuntos ServiceNow` → Finish

---

## Paso 3 — Configurar el `.env`

Abre el archivo `.env` (cópialo desde `.env.example` si no existe) y escribe las rutas exactas:

```env
INCOMING_FOLDER=C:\Users\TuNombre\OneDrive\servicenow-reports\incoming
PROCESSED_FOLDER=C:\Users\TuNombre\OneDrive\servicenow-reports\processed
OUTPUT_FILE=C:\Users\TuNombre\OneDrive\servicenow-reports\dashboard_data.xlsx
POLL_INTERVAL_MINUTES=60
```

> Para saber tu ruta exacta de OneDrive: click derecho en la carpeta `incoming` en el Explorador → **Properties** → copia el campo **Location**.

---

## Paso 4 — Validar

```bash
python validate_setup.py
```

Deberías ver:
```
✓ INCOMING_FOLDER = C:\Users\...\servicenow-reports\incoming
✓ OUTPUT_FILE = C:\Users\...\servicenow-reports\dashboard_data.xlsx
✓ Carpeta incoming — creada — 0 archivo(s) Excel pendientes
✓ Carpeta de salida
✓ agents_reference.xlsx — 50 agentes
✓ pandas, openpyxl, schedule
✓ Todo listo. Ejecuta: python run.py
```

---

## Cómo funciona el flujo completo

```
Correo de ServiceNow llega a Outlook
           ↓ (regla automática)
OneDrive\servicenow-reports\incoming\reporte.xlsx
           ↓ (Python detecta el archivo — cada hora)
data_processor.py → agrupa por agente y actividad
           ↓
OneDrive\servicenow-reports\dashboard_data.xlsx
           ↓ (Power BI lee este archivo)
Dashboard actualizado
```

**No necesitas hacer nada manualmente.** Cuando llegue un correo de ServiceNow, la regla de Outlook guarda el adjunto y el script de Python lo procesa en la próxima ejecución horaria.
