"""27.11.2026 (Тетяна): Валентині окремим повідомленням коротко, що змінилось в адвенті, і посилання, щоб пощолкати. flag advnote2711."""
import logging

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config as C
import db

log = logging.getLogger("advnote2711")
PAGE = "https://tafijcuktetana12-coder.github.io/agents/kyshkivnyk/advent/"


async def job(ctx):
    if db.flag_get("advnote2711") == "1":
        return
    db.flag_set("advnote2711", "1")
    me = await ctx.bot.get_me()
    link = f"https://t.me/{me.username}?start=advent"
    text = ("🎄 <b>Ваш адвент-календар оновлено за вашими правками</b>\n\n"
            "<b>Що змінилось:</b>\n"
            "• заголовок <b>«ЗДОРОВІ СВЯТА без зайвих кг та проблем в ШКТ»</b>\n"
            "• ваш новий текст запрошення і <i>святкове фото з келихом</i>\n"
            "• після кнопки «Хочу в адвент» ваш текст <i>«Вітаю, ви в моєму адвенті»</i>\n"
            "• <b>6 грудня</b> після рецепту подарунок на Миколая: гайд <b>155 грн</b> замість 621, з вашим фото і кнопкою оплати\n"
            "• <b>25 грудня</b> після рецепту різдвяна консультація <b>1125 грн</b> замість 4500, з фото і кнопкою оплати\n"
            "• у календарі віконця 6, 24 і 25 тепер рожеві, з подарунком 🎁\n\n"
            f"Пощолкайте самі 👇\n<code>{link}</code>\n\n"
            "<i>Валентино, буде все добре</i> ❤")
    kb = M([[B("🎄 Відкрити адвент в агенті", url=link)], [B("📅 Подивитися календар", url=PAGE)]])
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        except Exception as e:
            log.warning("advnote2711 %s: %s", a, e)
