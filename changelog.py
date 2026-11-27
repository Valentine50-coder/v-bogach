"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-27-advent-v"
NOTES = [
    "Адвент: нове запрошення з вашим святковим фото і ваш текст «ЗДОРОВІ СВЯТА без зайвих кг та проблем в ШКТ»",
    "Після кнопки «Хочу в адвент» тепер ваш текст «Вітаю, ви в моєму адвенті»",
    "6 грудня після рецепту: подарунок на Миколая, гайд про солодке 155 грн замість 621 (кнопка оплати, гайд приходить сам)",
    "25 грудня після рецепту: різдвяна консультація 1125 грн замість 4500 (кнопка оплати)",
    "Сторінка-календар: новий заголовок, віконця 6, 24 і 25 з подарунками",
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
