"""24.11.2026: кнопка старту «Гайд «Як приборкати...»» (раніше «скоро») = гайд Валентини «Як позбутися тяги до солодкого»
з її ланцюжка SendPulse «цукор». Оплата прямим посиланням WayForPay (від Тетяни), агент оплату не бачить."""
import asyncio

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config as C
import crm

PAY_URL = "https://secure.wayforpay.com/payment/gaydcucor"
TEXT_1 = ("🍰 <b>Цей гайд допоможе вам раз і назавжди злізти з цукрової голки</b> й уникнути безлічі проблем зі здоров'ям 💯\n\n"
          "У ньому <i>мій власний досвід колишньої солодкоїжки</i> і прості способи звільнитися від цукрової залежності.")
TEXT_2 = ("📖 <b>Гайд «Як позбутися тяги до солодкого»</b>\n\n"
          "<b>У гайді я розкриваю:</b>\n"
          "✅ справжні причини тяги до солодкого\n"
          "✅ наслідки цукрової залежності\n"
          "✅ як побудувати здорові стосунки з цукром\n"
          "✅ приховані цукри в продуктах\n"
          "✅ рейтинг солодощів: від найшкідливіших до найкорисніших\n"
          "✅ безпечні альтернативи шкідливим смаколикам\n\n"
          "🎁 Зараз гайд можна придбати <b>зі знижкою 30%</b> 👇")


def kb():
    return M([[B("💳 Придбати гайд зі знижкою 30%", url=PAY_URL)],
              [B("💬 Поставити питання", url=f"https://t.me/{C.AUTHOR_CONTACT.lstrip('@')}")],
              [B("☰ Меню", callback_data="menu")]])


async def show(ctx, chat, uid):
    crm.log_ev(uid, "guide")
    await ctx.bot.send_message(chat, TEXT_1, parse_mode="HTML")
    await asyncio.sleep(3)
    await ctx.bot.send_message(chat, TEXT_2, parse_mode="HTML", reply_markup=kb())
