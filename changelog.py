"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-24-about"
NOTES = [
    "Кнопка «Гайд «Як приборкати...»» тепер показує гайд «Як позбутися тяги до солодкого» з кнопкою оплати зі знижкою 30%",
    "Кнопка «Курс «Здоров'я дітей»» тепер показує курс «7 кроків до хронічного здоров'я вашої дитини»: 5 відеолекцій, 5 бонусів, кнопка оплати 999 грн веде на ваше посилання WayForPay",
    "«Знайомство з Валентиною» оновлено: хто ви, що в каналі, подарунок за підписку; під ним кнопки «Записатись на консультацію», «Написати Валентині особисто» і «Мій канал»",
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
