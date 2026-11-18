"""Звіт адмінам після кожного оновлення агента.

Як користуватися: при кожній зміні міняйте VERSION і пишіть пункти в NOTES простими словами.
Після перезапуску агент один раз надішле адмінам «Агента оновлено» з цими пунктами.
"""
import logging

import config as C
import db

log = logging.getLogger("changelog")

VERSION = "2026-11-18-3"
NOTES = [
    "Каруселі на 19-29 листопада перезібрано за «Стратегом»: у кожній новий слайд «Ви думаєте» з сумнівом читачки її словами і спокійною відповіддю, з фото Валентини",
    "Фото Валентини в каруселях тепер вирізані з фону і стоять повністю, без обрізаної рамки",
    "Карусель про висипання приходить сьогодні (18.11), решта за розкладом о 9:00",
    "В описах до каруселей додано абзац з цим сумнівом і відповіддю, далі одна дія: слово в коментарях",
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
