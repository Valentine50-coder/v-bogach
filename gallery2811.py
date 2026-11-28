"""28.11.2026 (Тетяна): Валентині (адмінам) кнопка на сторінку з усіма запланованими каруселями грудня і січня,
щоб відкрити і подивитися всі слайди й описи. Сторінка: репозиторій agents, kyshkivnyk/posts (перезібрати, якщо змінились каруселі).
Разово flag gal2811, далі /karuseli (адмін)."""
import logging

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config as C
import db

log = logging.getLogger("gallery2811")
PAGE = "https://tafijcuktetana12-coder.github.io/agents/kyshkivnyk/posts/"
TEXT = ("📸 <b>Усі ваші каруселі на грудень і січень в одному місці</b>\n\n"
        "Натисніть кнопку, і відкриється сторінка: <b>кожна карусель з датою</b>, слайди гортаються вбік, "
        "а під каруселлю <i>«Опис до поста»</i> з кнопкою «Скопіювати».\n\n"
        "Щодня о 9:00 карусель дня, як і раніше, приходить сюди ❤\n\n"
        "<i>Відкрити ще раз: команда /karuseli</i>")


def kb():
    return M([[B("📸 Подивитися всі каруселі", url=PAGE)]])


async def job(ctx):
    if db.flag_get("gal2811") == "1":
        return
    db.flag_set("gal2811", "1")
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, TEXT, parse_mode="HTML", reply_markup=kb(), disable_web_page_preview=True)
        except Exception as e:
            log.warning("gal2811 %s: %s", a, e)


async def cmd(update, ctx):
    if update.effective_user.id not in C.ADMIN_IDS:
        return
    await update.effective_message.reply_text(TEXT, parse_mode="HTML", reply_markup=kb(), disable_web_page_preview=True)
