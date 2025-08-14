import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Tuple, List, Dict

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---- Basic Config ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Constants ----
RIO_COORDS = (-22.9068, -43.1729)  # Rio de Janeiro
PHRASES = {
    "Comida": [
        ["¿Tienen menú en portugués?", "Vocês têm cardápio em português?"],
        ["Sin picante, por favor.", "Sem pimenta, por favor."],
        ["La cuenta, por favor.", "A conta, por favor."],
        ["¿Puedo pagar con tarjeta?", "Posso pagar com cartão?"],
    ],
    "Transporte": [
        ["¿Cuánto cuesta hasta Copacabana?", "Quanto custa até Copacabana?"],
        ["Lléveme a esta dirección.", "Leve-me a este endereço."],
        ["¿Este bus va a Ipanema?", "Esse ônibus vai para Ipanema?"],
        ["¿Dónde tomo un taxi seguro?", "Onde pego um táxi seguro?"],
    ],
    "Playas": [
        ["¿Hay bandera roja hoy?", "Tem bandeira vermelha hoje?"],
        ["¿Dónde hay sombra/parasol?", "Onde tem sombra/guarda-sol?"],
        ["¿Dónde puedo dejar mis cosas?", "Onde posso deixar minhas coisas?"],
        ["¿Dónde alquilo una silla?", "Onde alugo uma cadeira?"],
    ],
    "Emergencias": [
        ["Ayuda, por favor.", "Ajuda, por favor."],
        ["Llame a la policía.", "Chame a polícia."],
        ["Necesito un médico.", "Preciso de um médico."],
        ["He perdido mi billetera.", "Perdi minha carteira."],
    ],
}

MAP_LINKS = {"Hospedaje (Av Atlântica 2826, Copacabana)": "https://maps.app.goo.gl/oy5CZsm1XLDCSFqP8", "Cristo Redentor": "https://maps.app.goo.gl/VXQnBEwXyQJpGg5N8", "Pão de Açúcar": "https://maps.app.goo.gl/2C3sA6MWkK6kzV6s9", "Escalera de Selarón": "https://maps.app.goo.gl/LG6RQ7Rt8vwX3KmP9", "Shopping Rio Sul": "https://maps.app.goo.gl/nB3mX7q4QwGZ3wuc8", "Shopping Leblon": "https://maps.app.goo.gl/FHYHtQfXjHVE4Pdp9", "Shopping Botafogo Praia": "https://maps.app.goo.gl/EtL8vHvq34R8PBsv9", "Playa Copacabana": "https://maps.app.goo.gl/6YjH2t1eZ2S3B1cJ6", "Playa Ipanema": "https://maps.app.goo.gl/eYg9nJpK2b7rRk2D8", "Arcos da Lapa (bares)": "https://maps.app.goo.gl/5wHm1sHc7oRvt8Wk8"}

def human_day(dt: datetime) -> str:
    return dt.strftime("%a %d/%m")

def get_open_meteo_forecast(lat: float, lon: float) -> str:
    # No API key required
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,weathercode"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&forecast_days=3&timezone=auto"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    daily = data.get("daily", {})
    days = list(range(len(daily.get("time", []))))

    def code_to_emoji(code: int) -> str:
        # Simplified WMO code mapping
        if code == 0: return "☀️"
        if code in [1, 2, 3]: return "⛅"
        if code in [45, 48]: return "🌫️"
        if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
        if code in [71, 73, 75, 85, 86]: return "❄️"
        if code in [95, 96, 99]: return "⛈️"
        return "🌤️"

    lines = ["Previsión para Río de Janeiro:"]
    for i in days:
        date_str = daily["time"][i]
        dt = datetime.fromisoformat(date_str)
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        p = daily["precipitation_sum"][i]
        code = daily["weathercode"][i]
        lines.append(f"{human_day(dt)} {code_to_emoji(code)}  Máx {tmax:.0f}°C / Mín {tmin:.0f}°C · Lluvia {p:.1f}mm")
    return "\n".join(lines)

def libre_translate(text: str, source: str, target: str) -> str:
    # Public instance of LibreTranslate (may be rate-limited)
    try:
        r = requests.post(
            "https://libretranslate.com/translate",
            timeout=10,
            headers={"Content-Type": "application/json"},
            json={"q": text, "source": source, "target": target, "format": "text"}
        )
        r.raise_for_status()
        return r.json().get("translatedText", "")
    except Exception as e:
        return f"No pude traducir ahora. Intenta de nuevo. (Detalle: {e})"

def build_phrase_keyboard() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton("Frases: Comida"), KeyboardButton("Frases: Transporte")],
        [KeyboardButton("Frases: Playas"), KeyboardButton("Frases: Emergencias")],
        [KeyboardButton("Clima en Río"), KeyboardButton("Mapas útiles")],
        [KeyboardButton("Ayuda")],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def start(update: Update, context: CallbackContext):
    user_first = update.effective_user.first_name
    msg = (
        f"¡Hola {user_first or ''}! Soy tu asistente de viaje para Río 🇧🇷.\n\n"
        "Lo que puedo hacer:\n"
        "• **Clima**: /clima\n"
        "• **Traducir** ES↔PT: /tr texto\n"
        "• **Frases útiles**: /frases o usa los botones\n"
        "• **Mapas** con lugares clave: /mapas\n"
        "• **Ayuda**: /ayuda\n\n"
        "Tip: usá los botones para ir más rápido."
    )
    update.message.reply_text(msg, reply_markup=build_phrase_keyboard(), parse_mode="Markdown")

def clima(update: Update, context: CallbackContext):
    try:
        forecast = get_open_meteo_forecast(*RIO_COORDS)
        update.message.reply_text(forecast)
    except Exception as e:
        update.message.reply_text(f"No pude obtener el clima ahora. Intenta más tarde. ({e})")

def translate_cmd(update: Update, context: CallbackContext):
    text = " ".join(context.args).strip()
    if not text:
        update.message.reply_text("Usá: /tr texto a traducir\nEj: /tr ¿Dónde puedo tomar un taxi seguro?")
        return
    # Detect simple heuristic: if has typical Portuguese chars/words, go PT->ES, else ES->PT
    sample = text.lower()
    pt_hint = any(w in sample for w in ["você","vocês","ônibus","cartão","pode","onde","tem","praia","obrigado","obrigada"])
    if pt_hint:
        translated = libre_translate(text, "pt", "es")
    else:
        translated = libre_translate(text, "es", "pt")
    update.message.reply_text(translated)

def frases(update: Update, context: CallbackContext):
    lines = ["Frases útiles (ES → PT):\n"]
    for cat, pairs in PHRASES.items():
        lines.append(f"— {cat} —")
        for es, pt in pairs:
            lines.append(f"• {es}\n  → {pt}")
        lines.append("")
    update.message.reply_text("\n".join(lines))

def mapas(update: Update, context: CallbackContext):
    lines = ["Lugares útiles en Río (abre en Google Maps):"]
    for name, link in MAP_LINKS.items():
        lines.append(f"• {name}: {link}")
    update.message.reply_text("\n".join(lines))

def ayuda(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Comandos disponibles:\n"
        "/clima — Pronóstico 3 días para Río\n"
        "/tr texto — Traducción ES↔PT\n"
        "/frases — Frases útiles por tema\n"
        "/mapas — Links de lugares clave\n"
        "/ayuda — Esta ayuda",
    )

def on_text(update: Update, context: CallbackContext):
    txt = (update.message.text or "").strip().lower()
    if "clima" in txt:
        return clima(update, context)
    if "mapa" in txt:
        return mapas(update, context)
    if "frases" in txt:
        # Show category buttons
        kb = ReplyKeyboardMarkup(
            [["Comida", "Transporte"], ["Playas", "Emergencias"], ["Clima en Río", "Mapas útiles"], ["Ayuda"]],
            resize_keyboard=True
        )
        return update.message.reply_text("Elegí una categoría:", reply_markup=kb)
    if txt in ["comida","transporte","playas","emergencias"]:
        cat = txt.capitalize()
        pairs = PHRASES.get(cat, [])
        if not pairs:
            return update.message.reply_text("Sin frases en esa categoría.")
        lines = [f"{cat} (ES → PT):"]
        for es, pt in pairs:
            lines.append(f"• {es}\n  → {pt}")
        return update.message.reply_text("\n".join(lines), reply_markup=build_phrase_keyboard())
    if "ayuda" in txt:
        return ayuda(update, context)
    # Fallback: attempt auto-translate
    sample = txt
    pt_hint = any(w in sample for w in ["você","vocês","ônibus","cartão","pode","onde","tem","praia","obrigado","obrigada"])
    translated = libre_translate(update.message.text, "pt" if pt_hint else "es", "es" if pt_hint else "pt")
    update.message.reply_text(translated)

def main():
    if not TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN env var")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("clima", clima))
    dp.add_handler(CommandHandler("tr", translate_cmd))
    dp.add_handler(CommandHandler("frases", frases))
    dp.add_handler(CommandHandler("mapas", mapas))
    dp.add_handler(CommandHandler("ayuda", ayuda))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, on_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
