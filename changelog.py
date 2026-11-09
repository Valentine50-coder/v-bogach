"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-09-7"
NOTES = [
    "Головне меню тепер по порядку: Знайомство з Валентиною, Інтенсив «Здоровий кишківник», Діагностика кишківника, далі інші продукти і «Запитати у Валентини»",
    "Нова воронка для сайту (?start=site): коротке вітання, коротка пропозиція, «Перейти до оплати» (все одразу або частинами), після оплати доступ і кнопка «Запитати у Валентини»",
    "Кнопка «Запитати у Валентини» є в меню, у розділах, після діагностики і в повідомленні з доступом",
    "Кнопки «Долучитися» на сайті ведуть в агента на воронку для сайту",
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
