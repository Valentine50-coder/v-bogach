"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-09-4"
NOTES = [
    "Нижнє меню тепер повне: Про Валентину, Про запуск, Для кого, Програма, Що ви отримаєте, Умови і ціна, Оплатити, Меню",
    "Кожен розділ відкривається з окремою картинкою (фото Валентини, заголовок, головне коротко) і повним текстом",
    "Тексти оформлені: жирним головне, курсивом думки Валентини, моно для дат, цін і номерів тем програми",
    "Кнопка «Оплатити» внизу одразу створює рахунок WayForPay",
    "Щоб побачити нове нижнє меню, надішліть агенту /start або /menu",
]


async def send(bot):
    if db.flag_get("changelog") == VERSION:
        return
    db.flag_set("changelog", VERSION)
    text = "🔄 <b>Агента оновлено</b>\n\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(NOTES, 1))
    for a in C.ADMIN_IDS:
        try:
            await bot.send_message(a, text, parse_mode="HTML")
        except Exception as e:
            log.warning("changelog %s: %s", a, e)
