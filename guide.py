"""24.11.2026: кнопка старту «Гайд «Як приборкати...»» (раніше «скоро») = гайд Валентини «Як позбутися тяги до солодкого»
з її ланцюжка SendPulse «цукор». Оплата прямим посиланням WayForPay (від Тетяни), агент оплату не бачить."""
import asyncio
import os

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import crm

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "guide_solodke.jpg")
PAY_URL = "https://secure.wayforpay.com/payment/gaydcucor"
TEXT_1 = ("<b>Цей гайд допоможе вам раз і назавжди зійти з цукрової голки й уникнути безлічі проблем зі здоров'ям 💯\n\n"
          "У ньому - мій власний досвід колишньої солодкоїжки та прості способи звільнення від цукрової залежності.</b>")
TEXT_2 = ("<b>У гайді я розкриваю:</b>\n"
          "✅ <i>справжні причини тяги до солодкого</i>\n"
          "✅<i>наслідки цукрової залежності</i>\n"
          "✅<i>побудову здорових стосунків із цукром</i>\n"
          "✅<i>приховані цукри в продуктах</i>\n"
          "✅<i>рейтинг солодощів (від найшкідливіших до найкорисніших)</i>\n"
          "✅<i>безпечні альтернативи шкідливим смаколикам</i>")
TEXT_3 = "<b>Придбати гайд \"Як позбутися тяги до солодкого\" з 30% знижкою</b> 👇"


def kb():
    return M([[B("Придбати", url=PAY_URL)], [B("☰ Меню", callback_data="menu")]])


async def show(ctx, chat, uid):
    crm.log_ev(uid, "guide")
    if os.path.exists(IMG):  # 26.11: фото Валентини з фруктами і тістечком (від Тетяни)
        with open(IMG, "rb") as f:
            await ctx.bot.send_photo(chat, f, caption=TEXT_1, parse_mode="HTML")
    else:
        await ctx.bot.send_message(chat, TEXT_1, parse_mode="HTML")
    await asyncio.sleep(5)
    await ctx.bot.send_message(chat, TEXT_2, parse_mode="HTML")
    await ctx.bot.send_message(chat, TEXT_3, parse_mode="HTML", reply_markup=kb())
