"""24.11.2026: кнопка старту «Гайд «Як приборкати...»» = гайд Валентини «Як позбутися тяги до солодкого».
27.11 (Тетяна): PDF гайду в media/gayd_solodke.pdf. До 31.12 акція 50% (310,5 грн замість 621): кнопка «Написати»
Валентині зі словом «гайд», продаж веде вона сама. З 1.01 автоматично: рахунок WayForPay на 621 грн (kind "guide"),
після оплати агент сам надсилає PDF (file_id у kv guide_fid) і пише адмінам, хто купив."""
import asyncio
import logging
import os
from urllib.parse import quote

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import crm
import db
import promo

log = logging.getLogger("guide")
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images", "guide_solodke.jpg")
PDF = os.path.join(HERE, "media", "gayd_solodke.pdf")
ME = "https://t.me/health_shvets"
PRICE = 621
NAME = "Гайд «Як приборкати тягу до солодкого»"
TEXT_1 = ("<b>Цей гайд допоможе вам раз і назавжди зійти з цукрової голки й уникнути безлічі проблем зі здоров'ям 💯\n\n"
          "У ньому - мій власний досвід колишньої солодкоїжки та прості способи звільнення від цукрової залежності.</b>")
TEXT_2 = ("<b>У гайді я розкриваю:</b>\n"
          "✅ <i>справжні причини тяги до солодкого</i>\n"
          "✅<i>наслідки цукрової залежності</i>\n"
          "✅<i>побудову здорових стосунків із цукром</i>\n"
          "✅<i>приховані цукри в продуктах</i>\n"
          "✅<i>рейтинг солодощів (від найшкідливіших до найкорисніших)</i>\n"
          "✅<i>безпечні альтернативи шкідливим смаколикам</i>")
TEXT_PROMO = ("<b>До 31 грудня гайд зі знижкою 50%: <s>621 грн</s> 310,5 грн</b> ‼️\n\n"
              "Щоб придбати, напишіть мені «гайд» 👇")
TEXT_BUY = f"<b>Придбати гайд «Як приборкати тягу до солодкого»: {PRICE} грн</b> 👇\n\n<i>Після оплати агент одразу надішле вам гайд</i> ❤"
PAY_TEXT = (f"💳 <b>{NAME}</b>\n\n{PRICE} грн. Після оплати агент одразу надішле вам гайд у PDF ❤")
PAID = "✅ <b>Оплату отримано, дякую!</b> ❤\n\nОсь ваш гайд «Як приборкати тягу до солодкого» 👇"


def kb():
    if promo.on():
        return M([[B("Написати", url=f"{ME}?text={quote('гайд')}")], [B("☰ Меню", callback_data="menu")]])
    return M([[B(f"Придбати за {PRICE} грн", callback_data="guide:buy")], [B("☰ Меню", callback_data="menu")]])


async def show(ctx, chat, uid):
    crm.log_ev(uid, "guide")
    if os.path.exists(IMG):  # 26.11: фото Валентини з фруктами і тістечком (від Тетяни)
        with open(IMG, "rb") as f:
            await ctx.bot.send_photo(chat, f, caption=TEXT_1, parse_mode="HTML")
    else:
        await ctx.bot.send_message(chat, TEXT_1, parse_mode="HTML")
    await asyncio.sleep(5)
    await ctx.bot.send_message(chat, TEXT_2, parse_mode="HTML")
    await ctx.bot.send_message(chat, TEXT_PROMO if promo.on() else TEXT_BUY, parse_mode="HTML", reply_markup=kb())


async def send_pdf(bot, uid):
    fid = db.flag_get("guide_fid")
    if fid:
        try:
            await bot.send_document(uid, fid)
            return True
        except Exception as e:
            log.warning("guide fid: %s", e)
    with open(PDF, "rb") as f:
        m = await bot.send_document(uid, f, filename="Гайд_як_приборкати_тягу_до_солодкого.pdf",
                                    read_timeout=300, write_timeout=300)
    if m and m.document:
        db.flag_set("guide_fid", m.document.file_id)
    return True


async def on_paid(ctx, uid, amount, cur, notify_admins):
    db.flag_set(f"guide_paid:{uid}", "1")
    crm.log_ev(uid, "paid", f"{amount}|гайд")
    u = db.get_user(uid)
    name = (u["name"] if u else "") + (f" @{u['username']}" if u and u["username"] else "")
    ok = False
    try:
        await ctx.bot.send_message(uid, PAID, parse_mode="HTML")
        ok = await send_pdf(ctx.bot, uid)
    except Exception as e:
        log.warning("guide send %s: %s", uid, e)
    await notify_admins(ctx, f"✅ Купили гайд про солодке: {amount} {cur}. {name} (ID {uid}). "
                             + ("Гайд надіслано автоматично." if ok else "⚠️ Гайд надіслати не вдалось, надішліть вручну."))
