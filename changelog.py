"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-09-3"
NOTES = [
    "Під полем вводу тепер завжди є дві кнопки: «🏠 Меню» і «Інтенсив «Здоровий кишківник»»",
    "Кнопки з'являються при першому /start і не зникають, людина завжди може повернутися в меню",
    "Тим, хто вже писав агенту, кнопки з'являться після /start або /menu",
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
