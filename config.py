"""Налаштування агента Валентини. Ключі й токени тільки в Railway → Variables."""
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_ID", "").replace(" ", "").split(",") if x.isdigit()]
DB_PATH = os.environ.get("DB_PATH", "bot.db")

# Інтенсив «Здоровий кишківник»
INTENSIVE_NAME = "Здоровий кишківник"
INTENSIVE_AMOUNT = 1444          # сума для автоматичної оплати, грн
INTENSIVE_PRICE_NOTE = "до 14.11"  # підпис біля ціни
INTENSIVE_START = "24.11"
INTENSIVE_LENGTH = "тиждень"
INTENSIVE_FORMAT = "Telegram-канал та чат підтримки"

# Нік Валентини для питань (наприклад "@valentina"); порожньо = питання йдуть адмінам через агента
AUTHOR_CONTACT = ""

# Кнопки стартового меню: (текст, код). Поки що всі відповідають «скоро».
START_BUTTONS = [
    ("Гайд «Як приборкати...»", "guide"),
    ("Курс «Здоров'я дітей»", "kids"),
    ("Консультації", "consult"),
    ("Супровід з харчування", "support"),
    ("Розбір аналізів", "analyses"),
]
