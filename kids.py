"""24.11.2026: кнопка старту «Курс «Здоров'я дітей»» (раніше «скоро») = курс Валентини «7 кроків до хронічного здоров'я вашої дитини»
з її старого ланцюжка SendPulse: 5 відеолекцій у закритому Telegram-каналі + 5 бонусів, 999 грн замість 2485.

show(): опис → пауза → бонуси і ціна, кнопки «Придбати за 999 грн» (kids:buy → WayForPay, kind "kids"),
«Поставити питання» (особисті Валентини), меню.
on_paid(): flag kids_paid:<uid>, людині дякуємо; якщо закритий канал підключено (flag group:kids = "chat_id|назва"),
одразу особисте посилання (member_limit=1), інакше адмінам «додайте вручну».
/dity_kanal (адмін): «перешліть мені будь-який пост із закритого каналу курсу» → агент перевіряє, що може створювати
запрошення, і запам'ятовує канал; тим, хто вже оплатив, розсилає посилання.
"""
import asyncio
import os
import html
import logging
import time

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config as C
import crm
import db

log = logging.getLogger("kids")
PRICE = 999
PAY_URL = "https://secure.wayforpay.com/payment/kursproditey"  # 24.11: пряме посилання від Тетяни
OLD = 2485
NAME = "Курс «7 кроків до хронічного здоров'я вашої дитини»"

TEXT_1 = ("<b>Найголовніше про здоров'я дітей - в одному курсі та цінні подарунки з доступом назавжди</b>❗ 📲\n\n"
          "<b>Понад 15 років я допомагаю батькам</b> ростити хронічно здорових дітей. Навчаю простим корисним навичкам, "
          "що мінімізують захворювання та економлять ваш час, кошти та нерви 🤗")
TEXT_2 = ("<b>У закритому телеграм-каналі на вас уже чекають 5 відеолекцій та 5 бонусів до курсу:</b>\n\n"
          "1️⃣ гайд \"45 найкорисніших продуктів для дітей\", з описом їхньої харчової цінності\n\n"
          "2️⃣збірник \"50 рецептів корисних страв для дітей\"\n\n"
          "3 шпаргалка найшкідливіших Е-добавок\n\n"
          "4 тест на виявлення паразитів\n\n"
          "5 конспект усіх лекцій у слайдах\n"
          "{price_line}")
TEXT_3 = "<b>Якщо у вас лишилися питання пишіть сюди</b>👇"
PAY_TEXT = (f"💳 <b>{NAME}</b>\n\n{PRICE} грн, доступ до закритого каналу назавжди.\n\n"
            "Після оплати агент сам надішле вам вхід у канал ❤")
PAID = ("✅ <b>Оплату отримано, дякую!</b> ❤\n\n"
        f"Ви в курсі «7 кроків до хронічного здоров'я вашої дитини».")
PAID_LINK = "Ось ваш вхід у закритий канал курсу 👇 Посилання особисте, на одну людину."
PAID_WAIT = "Вхід у закритий канал курсу Валентина надішле вам найближчим часом ❤"


def kb_info():  # 26.11 13:29 (Тетяна): як у гайді, кнопка веде на сторінку WayForPay курсу (там оплата і доступ)
    return M([[B("Придбати", url=PAY_URL)]])


def kb_ask():
    return M([[B("Написати", url=f"https://t.me/{C.AUTHOR_CONTACT.lstrip('@')}")], [B("💚 Мої послуги", callback_data="menu")]])


async def show(ctx, chat, uid):
    crm.log_ev(uid, "kids")
    img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "kids_kurs.jpg")  # 26.11: обкладинка курсу (від Тетяни)
    if os.path.exists(img) and len(TEXT_1) <= 1000:
        with open(img, "rb") as f:
            await ctx.bot.send_photo(chat, f, caption=TEXT_1, parse_mode="HTML")
    else:
        if os.path.exists(img):
            with open(img, "rb") as f:
                await ctx.bot.send_photo(chat, f)
        await ctx.bot.send_message(chat, TEXT_1, parse_mode="HTML")
    promo = __import__("promo")  # 27.11: до 31.12 знижка 50% (499,5 замість 999)
    line = (f"<b>До 31 грудня курс (разом із подарунками) зі знижкою 50%: {promo.fmt(PRICE / 2)} грн замість {PRICE} грн</b>❗"
            if promo.on() else f"<b>Наразі цей курс (разом із подарунками) можна придбати всього за {PRICE} грн замість {OLD} грн</b>❗")
    await ctx.bot.send_message(chat, TEXT_2.replace("{price_line}", line), parse_mode="HTML", reply_markup=kb_info())
    await ctx.bot.send_message(chat, TEXT_3, parse_mode="HTML", reply_markup=kb_ask())


def channel():
    v = db.flag_get("group:kids") or ""
    if "|" in v:
        cid, title = v.split("|", 1)
        return int(cid), title
    return None, ""


async def _invite(bot, uid):
    cid, _ = channel()
    if not cid:
        return None
    try:
        link = await bot.create_chat_invite_link(cid, member_limit=1, name=f"kids {uid}"[:32])
        db.flag_set(f"kids_sent:{uid}", "1")
        return M([[B("🔐 Увійти в канал курсу", url=link.invite_link)]])
    except Exception as e:
        log.warning("kids invite %s: %s", uid, e)
        return None


async def on_paid(ctx, uid, amount, cur, notify_admins):
    db.flag_set(f"kids_paid:{uid}", str(int(time.time())))
    crm.log_ev(uid, "paid", f"{amount}|курс для дітей")
    u = db.get_user(uid)
    name = (u["name"] if u else "") + (f" @{u['username']}" if u and u["username"] else "")
    kb = await _invite(ctx.bot, uid)
    try:
        await ctx.bot.send_message(uid, PAID + "\n\n" + (PAID_LINK if kb else PAID_WAIT), parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        log.warning("kids paid msg %s: %s", uid, e)
    await notify_admins(ctx, f"✅ Оплата: курс для дітей, {amount} {cur}. {name} (ID {uid}). "
                             + ("Посилання в канал надіслано автоматично." if kb else
                                "⚠️ Закритий канал курсу ще не підключено: додайте людину вручну або підключіть канал командою /dity_kanal."))


async def cmd(update, ctx, is_admin):
    if not is_admin(update.effective_user.id):
        return
    ctx.user_data["kids_wait"] = time.time()
    cid, title = channel()
    now = f"Зараз підключено: «{html.escape(title)}»." if cid else "Канал ще не підключено."
    await update.message.reply_text(
        f"👶 <b>Закритий канал курсу для дітей</b>\n{now}\n\n"
        "1. Додайте мене адміністратором у цей канал з правом <b>«Запрошувати користувачів»</b>.\n"
        "2. Перешліть мені сюди <b>будь-який пост</b> з цього каналу.", parse_mode="HTML")


async def on_forward(update, ctx, is_admin):
    """Пересланий пост з каналу після /dity_kanal. Повертає True, якщо оброблено."""
    msg = update.message
    if not msg or not is_admin(update.effective_user.id) or time.time() - ctx.user_data.get("kids_wait", 0) > 900:
        return False
    origin = getattr(msg, "forward_origin", None)
    chat = getattr(origin, "chat", None) or getattr(msg, "forward_from_chat", None)
    if not chat:
        return False
    ctx.user_data.pop("kids_wait", None)
    try:
        test = await ctx.bot.create_chat_invite_link(chat.id, member_limit=1, name="test")
        await ctx.bot.revoke_chat_invite_link(chat.id, test.invite_link)
    except Exception as e:
        await msg.reply_text(f"⚠️ Не можу створювати запрошення в «{chat.title}»: {e}\nПеревірте, що я адміністратор з правом «Запрошувати користувачів».")
        return True
    db.flag_set("group:kids", f"{chat.id}|{chat.title}")
    sent = 0
    for k, _ in db.kv_prefix("kids_paid:"):
        uid = int(k.split(":", 1)[1])
        if db.flag_get(f"kids_sent:{uid}"):
            continue
        kb = await _invite(ctx.bot, uid)
        if kb:
            try:
                await ctx.bot.send_message(uid, PAID_LINK, reply_markup=kb)
                sent += 1
            except Exception as e:
                log.warning("kids pending %s: %s", uid, e)
    await msg.reply_text(f"✅ Запам'ятала канал курсу «{chat.title}». Після оплати люди отримають особисте посилання."
                         + (f" Тим, хто вже оплатив, надіслано: {sent}." if sent else ""))
    return True
