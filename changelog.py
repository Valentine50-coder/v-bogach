"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-26-advent3"
NOTES = [
    "У меню зверху кнопка «🎄 АДВЕНТ-КАЛЕНДАР «ЗДОРОВІ СВЯТА»»",
    "Адвент тепер має свій зелено-білий календар з кульками (кнопка «🎄 Відкрити календар»), віконця відкриваються по датах",
    "Адвент «Здорові свята»: 31 віконце з вашого «Здорового меню на тиждень», з 1 по 31 грудня щоранку о 9:00",
    "Посилання для Instagram: t.me/valentina_shvets_bot?start=advent (кодове слово в ManyChat на ваш вибір, напр. АДВЕНТ)",
    "24 грудня файл «Здорове меню на тиждень» у подарунок, 28 і 31 грудня бронь інтенсиву за спецціною 159 грн (для інших лишається 350)",
    "Запрошення в адвент усім в агенті піде тільки після вашої кнопки «✅ Розіслати». /advent показує, скільки людей в адвенті, /advent 5 показує віконце",
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
