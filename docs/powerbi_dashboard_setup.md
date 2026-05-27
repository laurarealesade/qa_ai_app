# Guía: Configurar el Dashboard en Power BI

Esta guía cubre dos partes:
- **A)** Conectar Power BI al Excel de OneDrive
- **B)** Diseñar el dashboard con el layout requerido

---

## Prerequisitos

Antes de seguir esta guía:
- El pipeline ya debe haber corrido al menos una vez (`python run.py --once`)
- El archivo `servicenow-reports/dashboard_data.xlsx` debe existir en tu OneDrive

---

## Parte A — Conectar Power BI Desktop al Excel

### 1. Abrir Power BI Desktop

Descarga gratis desde [powerbi.microsoft.com](https://powerbi.microsoft.com/desktop) si aún no lo tienes.

### 2. Obtener la URL del archivo en OneDrive

1. Abre **OneDrive** en el navegador ([onedrive.live.com](https://onedrive.live.com) o el de tu empresa)
2. Navega a `servicenow-reports/` y busca `dashboard_data.xlsx`
3. Click derecho → **"Copy link"** (o "Compartir" → "Copiar vínculo")
4. Guarda esa URL — la necesitarás en el siguiente paso

### 3. Conectar desde Power BI Desktop

1. **Home** → **Get data** → **Web**
2. Pega la URL de OneDrive del paso anterior
3. Si pide credenciales: selecciona **Organizational account** → **Sign in** con tu cuenta Microsoft 365
4. Click **Connect**

> **Alternativa más estable:** En vez de URL, usa **Get data → OneDrive** (aparece en la lista de conectores) y navega al archivo directamente.

### 4. Seleccionar los datos

1. En el Navigator, expande `dashboard_data.xlsx`
2. Selecciona la hoja **Dashboard**
3. Verifica que aparezcan las columnas: `Agent_Name`, `Activity`, `Total_Toques`, `Total_Casos`
4. Click **Load** (no Transform, los datos ya vienen limpios)

---

## Parte B — Diseñar el Dashboard

### Estructura del modelo de datos

La tabla `Dashboard` tiene esta estructura:

| Columna | Tipo | Descripción |
|---|---|---|
| `Agent_Name` | Text | Nombre completo del agente |
| `Activity` | Text | Online / Offline / 7Eleven / Sr Analyst / Team Leader |
| `Total_Toques` | Whole Number | Cantidad de filas (toques) del agente |
| `Total_Casos` | Whole Number | Casos únicos atendidos por el agente |

---

### Visual 1 — Tabla principal por actividad

Este es el visual central del dashboard.

**Pasos:**
1. En el panel **Visualizations**, selecciona **Table** (ícono de tabla)
2. Arrastra al área de valores:
   - `Agent_Name` → Rows
   - `Activity` → Rows (después de Agent_Name)
   - `Total_Toques` → Values
   - `Total_Casos` → Values
3. En el panel **Filters**, agrega `Activity`:
   - Selecciona: `Online`, `Offline`, `7Eleven` (excluye Sr Analyst y Team Leader si los quieres separados)

**Formato recomendado:**
- **Format visual** → **Style presets** → "Alternating rows"
- **Column headers** → Background color: `#1F3864`, Font color: `White`
- **Values** → Font size: 11

---

### Visual 2 — Tarjetas de resumen (KPIs)

Agrega 3 tarjetas en la parte superior:

**Tarjeta "Total Agentes"**
1. Selecciona **Card** visual
2. Arriba en la barra de **Fields**: click en `Agent_Name` → selecciona **Count (Distinct)**
3. Título: "Total Agentes"

**Tarjeta "Total Toques"**
1. Selecciona **Card** visual
2. Campo: `Total_Toques` con agregación **Sum**
3. Título: "Total Toques"

**Tarjeta "Total Casos"**
1. Selecciona **Card** visual
2. Campo: `Total_Casos` con agregación **Sum**
3. Título: "Total Casos"

---

### Visual 3 — Gráfico de barras por Actividad

1. Selecciona **Clustered bar chart**
2. Y-axis: `Activity`
3. X-axis: `Total_Casos` (Sum)
4. Legend: vacío
5. Colores manuales recomendados:
   - Online: `#6AA84F`
   - Offline: `#E69138`
   - 7Eleven: `#3D85C8`

---

### Visual 4 — Segmentador (Slicer) de Actividad

Permite filtrar la tabla por grupo de agentes.

1. Selecciona **Slicer** visual
2. Campo: `Activity`
3. En **Format** → **Slicer settings** → **Style**: Dropdown o List
4. Posiciona en la esquina superior izquierda

---

### Layout sugerido

```
┌─────────────────────────────────────────────────────────────┐
│  [Slicer: Activity]   [Tarjeta: Agentes] [Toques] [Casos]   │
├──────────────────────────────────┬──────────────────────────┤
│                                  │                          │
│    TABLA: Agent_Name │ Activity  │  GRÁFICO: Casos x        │
│           Total_Toques│Total_Casos│           Actividad     │
│                                  │                          │
│  (filtrada por slicer)           │                          │
└──────────────────────────────────┴──────────────────────────┘
```

---

## Parte C — Publicar en Power BI Service y configurar refresh

### 1. Publicar el reporte

1. **Home** → **Publish**
2. Selecciona tu workspace (ej. `QA Dashboard`)
3. Click **Select**

### 2. Obtener los IDs para el `.env`

Una vez publicado, abre el dataset en Power BI Service:

**Workspace ID:**
- En Power BI Service, ve a tu workspace
- La URL en el navegador tiene este formato:
  `https://app.powerbi.com/groups/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/...`
- Ese UUID es tu `POWERBI_WORKSPACE_ID`

**Dataset ID:**
- Click en el dataset `dashboard_data`
- La URL del dataset tiene este formato:
  `https://app.powerbi.com/groups/{workspace_id}/datasets/YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY`
- Ese UUID es tu `POWERBI_DATASET_ID`

Pega ambos valores en tu `.env`.

### 3. Configurar refresh automático en Power BI Service (respaldo)

Además del refresh que dispara el pipeline, configura un refresh programado como respaldo:

1. En Power BI Service, ve al **Dataset** → **Settings**
2. **Scheduled refresh** → activar toggle
3. Frecuencia: **Every 1 hour**
4. En **Data source credentials** → **Edit credentials** → **OAuth2** → inicia sesión

### 4. Verificar el refresh automático del pipeline

Corre el script de validación para confirmar que el refresh funciona:

```bash
python validate_setup.py
```

Debes ver:
```
✓ Token de Power BI — token obtenido
✓ Dataset de Power BI — dataset 'dashboard_data' encontrado
```

---

## Resultado final

El dashboard se actualiza automáticamente:
- **Cuando llega un correo** de ServiceNow → el pipeline lo detecta en la próxima ejecución horaria
- **Cada hora** → el pipeline revisa si hay correos nuevos y actualiza el Excel en OneDrive
- **Power BI** → refresca el dataset automáticamente al detectar cambios en el Excel de OneDrive

No necesitas hacer nada manual. Solo deja `python run.py` corriendo en tu máquina o servidor.
