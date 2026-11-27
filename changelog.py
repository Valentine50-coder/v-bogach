"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-27-fast"
NOTES = [
    "Усі розділи тепер приходять <b>одразу, без пауз</b> (гайд, аналізи, вітаміни, супровід, курс для дітей, старт)",
    "Гайд про солодке: більше інформації про гайд і кнопка <b>«Придбати за 310,5 грн»</b> (до 31.12), після оплати гайд приходить людині сам",
    "Кнопка «Меню» тепер називається <b>«💚 Мої послуги»</b>",
]


async def send(bot):
    if db.flag_get("changelog") == VERSION:
        return
    db.flag_set("changelog", VERSION)
    text = "🔄 <b>Агента оновлено</b>\n\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(NOTES, 1))
    me = await bot.get_me()
    text += (f"\n\n<b>Посилання для кодових слів:</b>\nДіагностика: https://t.me/{me.username}?start=test"
             f"\nВся інформація про інтенсив: https://t.me/{me.username}?start=hochu"
             f"\nДля кнопок сайту: https://t.me/{me.username}?start=site"
             f"\nКИШКІВНИК, консультація: https://t.me/{me.username}?start=cons"
             f"\nГрупа на січень: https://t.me/{me.username}?start=jan")
    for a in C.ADMIN_IDS:
        try:
            await bot.send_message(a, text, parse_mode="HTML")
        except Exception as e:
            log.warning("changelog %s: %s", a, e)
