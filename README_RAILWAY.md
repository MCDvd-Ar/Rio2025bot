# Deploy en Railway — Rio Travel Assistant

Este proyecto ya está listo para desplegarse en Railway como **Worker** (proc `worker` en Procfile).

## Pasos rápidos

1) **Sube el código a GitHub**
   - Crea un repo nuevo y sube estos archivos (o sube el ZIP tal cual).

2) **Crea el proyecto en Railway**
   - https://railway.app → New Project → **Deploy from GitHub** → selecciona tu repo.

3) **Variables de entorno**
   - En la pestaña "Variables", agrega:
     - `TELEGRAM_BOT_TOKEN` = tu token de @BotFather

4) **Tipo de servicio**
   - Railway detectará el `Procfile` y creará un **Worker**.
   - No necesita puerto web ni dominios.

5) **Deploy y logs**
   - Railway construirá la imagen (detecta `requirements.txt`).
   - Una vez desplegado, ve a **Logs**: deberías ver que el bot inicia el polling.
   - Abre Telegram y envía `/start` a tu bot.

## Notas
- El bot funciona por polling, así que no requiere webhook/dominio.
- Si cambias el código, haz **Deploy** de nuevo para que tome la nueva versión.
- Guarda tu token como **Variable de entorno**; no lo subas al repo.
