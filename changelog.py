"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-27-jan1748"
NOTES = [
    "Фразу <i>«не замінює консультації»</i> прибрано всюди: в агенті, адвенті, на сайті й в описах каруселей",
    "<b>Інтенсив «Здоровий кишківник» у січні:</b> участь <code>350 грн</code> до 30.11, <code>499 грн</code> з 1 по 31.12, з січня <code>1748 грн</code>. "
    "Без броні й доплат. Рядки «750 для перших 20» і «далі 1444» прибрано. Хто вже забронював за 350, вважається учасником без доплати. "
    "В адвенті 28 і 31.12 участь за <code>159 грн</code>",
    "Для кодового слова <b>ЦУКОР</b> (гайд про солодке): <code>https://t.me/valentina_shvets_bot?start=cukor</code>",
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
