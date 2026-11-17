"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-17-1"
NOTES = [
    "Ціна інтенсиву 1444 грн тепер діє до 23.11 включно (останній день запису): в агенті, на картці «Умови і ціна» і на сайті (відлік до 23.11 23:59). Старт як і був, 24.11",
    "Нагадування після відео «Чому бунтує кишківник» і дожими інтенсиву більше не приходять одне за одним: між ними щонайменше 2 години",
]


async def send(bot):
    if db.flag_get("changelog") == VERSION:
        return
    db.flag_set("changelog", VERSION)
    text = "🔄 <b>Агента оновлено</b>\n\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(NOTES, 1))
    me = await bot.get_me()
    text += (f"\n\n<b>Посилання для кодових слів:</b>\nДіагностика: https://t.me/{me.username}?start=test"
             f"\nВся інформація про інтенсив: https://t.me/{me.username}?start=hochu"
             f"\nДля кнопок сайту: https://t.me/{me.username}?start=site")
    for a in C.ADMIN_IDS:
        try:
            await bot.send_message(a, text, parse_mode="HTML")
        except Exception as e:
            log.warning("changelog %s: %s", a, e)
