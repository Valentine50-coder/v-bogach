"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-09-5"
NOTES = [
    "Кнопка «Оплатити» тепер дає вибір: оплатити все одразу 1444 грн або розтермінування",
    "Розтермінування: 3 платежі (482 + 481 + 481 грн), кожен через 30 днів",
    "Доступ до інтенсиву відкривається одразу після першого платежу",
    "Через 30 днів агент сам нагадує людині про наступний платіж і дає кнопку оплати, а вам пише, що нагадав",
    "Про кожен платіж ви отримуєте повідомлення: який номер платежу і від кого",
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
