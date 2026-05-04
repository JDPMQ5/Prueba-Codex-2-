# MVP Comercial Sell-Out 2026 (Clientes sin compra en abril)

MVP simple en **Python + Streamlit** para detectar clientes que compraron antes de abril 2026, pero **no compraron en abril 2026**, priorizarlos y generar alertas tipo Telegram.

## 1) Instalación rápida

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 2) Estructura del proyecto

- `app.py`
- `requirements.txt`
- `README.md`
- `.env.example`
- `src/`
  - `data_loader.py`
  - `analysis.py`
  - `telegram_alerts.py`
  - `utils.py`
- `data/dummy_sellout_2026.csv` (opcional para pruebas)

## 3) Lógica del MVP

1. Carga archivo CSV/Excel.
2. Limpia nombres de columnas y valida columnas mínimas.
3. Convierte `FechaFacturacion` a fecha.
4. Filtra solo:
   - `tipo_de_cliente_real = Regular`
   - `agrupador = Venta`
5. Detecta clientes que compraron antes del **01/04/2026** y no compraron entre **01/04/2026 y 30/04/2026**.
6. Calcula métricas históricas por cliente y asigna prioridad.
7. Muestra KPIs, tabla priorizada y alerta Telegram agrupada por BK.

## 4) Reglas de prioridad implementadas

- **Alta**: última compra en marzo 2026 **y** `nr_canje_historico` en cuartil alto (>= P75).
- **Media**: última compra en febrero o marzo 2026.
- **Baja**: última compra anterior a febrero 2026.

## 5) Telegram: configuración

### Paso A: crear bot con BotFather

1. En Telegram busca `@BotFather`.
2. Envía `/start`.
3. Envía `/newbot`.
4. Define nombre y username del bot (debe terminar en `bot`).
5. Copia el token entregado por BotFather.

### Paso B: obtener TELEGRAM_CHAT_ID

Opción simple (chat personal):

1. Busca tu bot en Telegram y envíale cualquier mensaje (ej. "hola").
2. En navegador abre:
   - `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates`
3. Busca en la respuesta JSON el campo `chat` -> `id`.
4. Ese valor es tu `TELEGRAM_CHAT_ID`.

### Paso C: variables de entorno

1. Copia `.env.example` a `.env`.
2. Completa:

```env
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```

> Si no configuras credenciales, la app **no se rompe**: muestra el texto de alerta para copiar.

## 6) Datos de prueba

Puedes usar `data/dummy_sellout_2026.csv` para probar rápidamente la app.

## 7) Notas

- No usa base de datos aún.
- No usa login.
- Solo integra API de Telegram de forma opcional.
- El objetivo es velocidad de despliegue y accionabilidad comercial.
