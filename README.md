# Rio Travel Assistant (Telegram Bot)

Un bot simple para ayudarte en tu viaje a Río de Janeiro:
- /clima: pronóstico 3 días (Open-Meteo, sin API key)
- /tr <texto>: traducción ES↔PT (LibreTranslate público)
- /frases: frases útiles por categoría (ES→PT)
- /mapas: links directos a lugares clave (Google Maps)
- Botones rápidos para uso desde el teléfono

## Deploy rápido (Replit)

1) Crea tu bot en Telegram
   - Abre Telegram y habla con @BotFather
   - Usa `/newbot`, define nombre y usuario (termina en `bot`)
   - Copia el `TOKEN` que te entrega (formato: 123456:ABC-...)

2) Sube este proyecto a Replit
   - Ve a replit.com → Create Repl → Import from GitHub (o sube los archivos .zip)
   - Una vez dentro, crea un "Secret":
     - Key: TELEGRAM_BOT_TOKEN
     - Value: <tu token del paso anterior>

3) Instala dependencias y ejecuta
   - En la consola de Replit:
     ```
     pip install -r requirements.txt
     python bot.py
     ```
   - Verás `Polling` en la consola. ¡Listo!

4) Prueba tu bot
   - En Telegram, abre tu bot y escribe `/start`

## Alternativa local (tu notebook o compu)
- Instala Python 3.10+
- `pip install -r requirements.txt`
- Exporta la variable de entorno y ejecuta:
  - macOS/Linux:
    ```bash
    export TELEGRAM_BOT_TOKEN="TU_TOKEN"
    python bot.py
    ```
  - Windows (PowerShell):
    ```powershell
    setx TELEGRAM_BOT_TOKEN "TU_TOKEN"
    python bot.py
    ```

### Notas
- La traducción usa un servicio público (LibreTranslate). Si llega a estar lento, intenta de nuevo.
- Para clima, se usa Open-Meteo (gratis, sin API key).
- Los links de mapas abren Google Maps.
