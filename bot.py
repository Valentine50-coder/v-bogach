"""Агент Валентини Швець: воронка «Старт» і воронка «ХОЧУ» (інтенсив «Здоровий кишківник»)."""
import asyncio
import time
import logging
import os

from telegram import (BotCommand, BotCommandScopeChat, InlineKeyboardButton as B,
                      InlineKeyboardMarkup as M, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
from telegram.ext import (Application, CallbackQueryHandler, ChatMemberHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

import config as C
import changelog
import db
import groups
import quiz
import crm
import texts as T
import wfp

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")
IMG = os.path.join(os.path.dirname(__file__), "images")


def is_admin(uid): return uid in C.ADMIN_IDS


def kb_start(adm=False):
    rows = [[B(T.BTN_ABOUT, callback_data="sec:author")],
            [B(T.BTN_INTENSIVE, callback_data="int")],
            [B(quiz.BTN_MENU, callback_data="qz:start")]]
    rows += [[B(text, callback_data=f"soon:{code}")] for text, code in C.START_BUTTONS]
    rows.append([B(T.BTN_CHANNEL, url=C.CHANNEL_URL)])
    rows.append([kb_ask()])
    if adm:
        rows.append([B(crm.BTN, callback_data="crm:menu")])
    return M(rows)


def kb_ask():
    """Кнопка «Запитати у Валентини»: напряму в Telegram, якщо задано контакт, інакше через агента."""
    if C.AUTHOR_CONTACT:
        return B(T.BTN_ASK_V, url=f"https://t.me/{C.AUTHOR_CONTACT.lstrip('@')}")
    return B(T.BTN_ASK_V, callback_data="ask")


def kb_bottom(adm=False):
    """Меню під полем вводу (10.11 як в агенті Тетяни): широка назва, далі два стовпчики; можна згорнути значком клавіатури."""
    rows = [[KeyboardButton(t) for t, _ in row] for row in T.BTN_BOTTOM]
    if adm:
        rows.append([KeyboardButton(crm.BTN)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=False)


HIDE = ReplyKeyboardRemove()


async def ensure_bottom(ctx, uid, chat):
    """10.11: хто має старе меню (до оновлення), отримує нове при першій дії, без розсилки."""
    if not ctx.user_data.get("hid") and db.flag_get(f"bm2:{uid}") != "1":
        await show_bottom(ctx, chat)


def hide(ctx):
    """Сховати нижнє меню, поки людина проходить діагностику чи пише питання."""
    ctx.user_data["hid"] = True
    return HIDE


def bottom(ctx, uid):
    ctx.user_data.pop("hid", None)
    db.flag_set(f"bm2:{uid}", "1")
    return kb_bottom(is_admin(uid))


async def show_bottom(ctx, chat_id, text=None):
    ctx.user_data.pop("hid", None)
    db.flag_set(f"bm2:{chat_id}", "1")
    await ctx.bot.send_message(chat_id, text or T.MENU_BACK, reply_markup=kb_bottom(is_admin(chat_id)), parse_mode="HTML")


BOTTOM = {t: code for row in T.BTN_BOTTOM for t, code in row}
BOTTOM.update({"Про Валентину": "author", "Про запуск": "launch", "🎯 Для кого": "for", "Програма": "program",  # 12.11: старі назви
               "🎁 Що ви отримаєте": "get", "Умови і ціна": "terms", "💳 Оплатити": "pay", "🏠 Меню": "home"})


def kb_intensive():
    return M([[B(T.BTN_PAY, callback_data="pay")],
              [B(T.BTN_INSTALL, callback_data="install")],
              [B(T.BTN_QUESTION, callback_data="ask")],
              [B(T.BTN_MENU, callback_data="menu")]])


SECTIONS = {  # код: (назва кнопки, текст, картинка)
    "launch": ("ПРО ЗАПУСК", "INT_1", "card_launch.jpg"),
    "author": ("ПРО АВТОРКУ", "INT_AUTHOR", "card_author.jpg"),
    "for": ("🎯 ДЛЯ КОГО", "INT_FOR", "card_for.jpg"),
    "program": ("ПРОГРАМА", "INT_PROGRAM", "card_program.jpg"),
    "get": ("🎁 ЩО ВИ ОТРИМАЄТЕ", "INT_GET", "card_get.jpg"),
    "terms": ("УМОВИ І ЦІНА", "INT_TERMS", "card_terms.jpg"),
}


async def show_section(ctx, chat_id, code):
    _, attr, img = SECTIONS[code]
    await send_photo(ctx, chat_id, img)
    await ctx.bot.send_message(chat_id, getattr(T, attr) + T.URGENT, reply_markup=kb_section(), parse_mode="HTML")


def kb_int_menu():
    s = [[B(v[0], callback_data=f"sec:{code}")] for code, v in SECTIONS.items() if code != "launch"]
    return M(s + [[B(T.BTN_PAY, callback_data="pay")], [B(T.BTN_MENU, callback_data="menu")]])


def kb_offer():
    return M([[B(T.BTN_PAY, callback_data="pay")],
              [B("Детальніше про інтенсив", callback_data="int")],
              [kb_ask()],
              [B(T.BTN_MENU, callback_data="menu")]])


def kb_section():
    return M([[B(T.BTN_PAY, callback_data="pay")],
              [kb_ask()],
              [B(T.BTN_BACK_INT, callback_data="int")],
              [B(T.BTN_MENU, callback_data="menu")]])


async def send_photo(ctx, chat_id, name, caption=None, kb=None):
    path = os.path.join(IMG, name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            await ctx.bot.send_photo(chat_id, f, caption=caption, parse_mode="HTML", reply_markup=kb)
        return True
    return False


async def notify_admins(ctx, text, kb=None):
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, text, reply_markup=kb)
        except Exception as e:
            log.warning("admin %s: %s", a, e)


def who(u):
    return f"{u.full_name}" + (f" @{u.username}" if u.username else "") + f" (ID {u.id})"


# ---------- воронки ----------
async def funnel_start(ctx, chat_id):
    if not await send_photo(ctx, chat_id, "start.jpg", T.START_1, bottom(ctx, chat_id)):
        await ctx.bot.send_message(chat_id, T.START_1, reply_markup=bottom(ctx, chat_id))
    await ctx.bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(5)
    await ctx.bot.send_message(chat_id, T.START_2, reply_markup=kb_start(is_admin(chat_id)), parse_mode="HTML")


async def funnel_intensive(ctx, chat_id):
    await ctx.bot.send_message(chat_id, T.INT_1, parse_mode="HTML", reply_markup=bottom(ctx, chat_id))
    if not await send_photo(ctx, chat_id, "intensive.jpg", T.INT_AUTHOR):
        await ctx.bot.send_message(chat_id, T.INT_AUTHOR, parse_mode="HTML")
    for part in (T.INT_FOR, T.INT_PROGRAM, T.INT_GET):
        await asyncio.sleep(2)
        await ctx.bot.send_message(chat_id, part, parse_mode="HTML")
    await asyncio.sleep(2)
    await ctx.bot.send_message(chat_id, T.INT_TERMS + T.URGENT, reply_markup=kb_intensive(), parse_mode="HTML")


async def intensive_card(ctx, chat_id):
    """Картка інтенсиву як в Ані: фото, коротко, розділи кнопками."""
    await send_photo(ctx, chat_id, "card_launch.jpg")
    await ctx.bot.send_message(chat_id, T.INT_1, parse_mode="HTML", reply_markup=bottom(ctx, chat_id))
    await ctx.bot.send_message(chat_id, T.INT_MENU + T.URGENT, reply_markup=kb_int_menu(), parse_mode="HTML")


async def funnel_site(ctx, chat_id):
    """З сайту: людина вже все прочитала, тут коротко, оплата і питання до Валентини."""
    if not await send_photo(ctx, chat_id, "card_launch.jpg", T.SITE_HELLO, bottom(ctx, chat_id)):
        await ctx.bot.send_message(chat_id, T.SITE_HELLO, parse_mode="HTML", reply_markup=bottom(ctx, chat_id))
    await ctx.bot.send_message(chat_id, T.SITE_OFFER + T.URGENT, parse_mode="HTML", reply_markup=M([
        [B(T.BTN_GO_PAY, callback_data="pay")],
        [kb_ask()],
        [B("Ще раз про інтенсив", callback_data="int")]]))


# ---------- 11.11: обов'язкова підписка на канал ----------
def kb_gate():
    return M([[B(T.GATE_BTN_SUB, url=C.CHANNEL_URL)], [B(T.GATE_BTN_CHECK, callback_data="chg:check")]])


async def is_member(bot, uid):
    """True / False, або None, якщо агент не може перевірити (не адмін каналу)."""
    try:
        m = await bot.get_chat_member(C.CHANNEL_USERNAME, uid)
        return m.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        log.warning("перевірка підписки: %s", e)
        return None


async def gate(ctx, uid, chat_id, src=None):
    """True, якщо людину зупинили: вона не підписана, їй показано кнопки. src запам'ятовуємо, щоб потім відкрити."""
    if not C.CHANNEL_USERNAME or is_admin(uid):
        return False
    member = await is_member(ctx.bot, uid)
    if member is None:
        last = db.flag_get("gate_alert")
        if not last or time.time() - float(last) > 86400:
            db.flag_set("gate_alert", str(time.time()))
            await notify_admins(ctx, T.GATE_ADMIN_ALERT)
        return False
    if member is False:
        if src:
            db.flag_set(f"gate_src:{uid}", src)
        crm.log_ev(uid, "gate")
        await ctx.bot.send_message(chat_id, T.GATE_WELCOME, reply_markup=kb_gate(), parse_mode="HTML")
        return True
    return False


async def gate_job(ctx):
    """Один раз пише адмінам, коли агент став адміном каналу і перевірка запрацювала."""
    if not C.CHANNEL_USERNAME or db.flag_get("gate_connected") == "1":
        return
    try:
        me = await ctx.bot.get_chat_member(C.CHANNEL_USERNAME, ctx.bot.id)
    except Exception as e:
        log.info("gate_job: %s", e)
        return
    if me.status in ("administrator", "creator"):
        db.flag_set("gate_connected", "1")
        await notify_admins(ctx, T.GATE_CONNECTED)


async def go_src(ctx, update_or_none, chat_id, uid, src):
    if src == "hochu":
        await funnel_intensive(ctx, chat_id)
    elif src == "site":
        await funnel_site(ctx, chat_id)
    elif src == "test":
        await ctx.bot.send_message(chat_id, "Вітаю! ❤", reply_markup=bottom(ctx, uid))
        await quiz.start(ctx.bot, chat_id)
    else:
        await funnel_start(ctx, chat_id)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    arg = (ctx.args[0].lower() if ctx.args else "")
    src = ("hochu" if arg in ("hochu", "xochu", "intensive") else "test" if arg in ("test", "diagnostyka", "diag")
           else "site" if arg == "site" else "start")
    new = db.get_user(u.id) is None
    db.upsert_user(u, src)
    crm.log_ev(u.id, "start" if new else "restart", src)
    crm.log_ev(u.id, {"hochu": "int_full", "site": "site", "test": "quiz_open"}.get(src, "hello"))
    if new:
        await notify_admins(ctx, f"👋 Новий підписник ({ {'hochu': 'кодове слово ХОЧУ', 'test': 'діагностика', 'site': 'з сайту'}.get(src, 'старт') }): {who(u)}")
    if await gate(ctx, u.id, update.effective_chat.id, src):
        return
    await go_src(ctx, update, update.effective_chat.id, u.id, src)


async def cmd_menu(update: Update, ctx):
    await update.message.reply_text("Меню завжди тут, під полем вводу 👇", reply_markup=bottom(ctx, update.effective_user.id))
    await update.message.reply_text(T.START_2, reply_markup=kb_start(is_admin(update.effective_user.id)), parse_mode="HTML")


# ---------- оплата ----------
async def do_grant(ctx, uid):
    db.set_field(uid, "int_paid", 1)
    kb = await groups.invite_kb(ctx.bot, uid, "int")
    text = T.ACCESS + (T.GROUP_JOIN if kb else T.ACCESS_NO_GROUP) + T.ACCESS_ASK
    kb = M([list(r) for r in (kb.inline_keyboard if kb else [])] + [[kb_ask()]])
    try:
        await ctx.bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        log.warning("grant send %s: %s", uid, e)


async def paid_job(ctx):
    async def on_paid(uid, kind, ref, amount, cur):
        if kind == "test":
            await notify_admins(ctx, f"✅ Тестова оплата пройшла: {amount} {cur}. Автоплатіж працює, доступ нікому не відкрито.")
            return
        u = db.get_user(uid)
        name = (u["name"] if u else "") + (f" @{u['username']}" if u and u["username"] else "")
        total = len(C.INSTALL_PARTS)
        if kind.startswith("int") and kind[3:].isdigit():
            n = int(kind[3:])
            crm.log_ev(uid, "paid", f"{amount}|частина {n}/{total}")
            if n == 1:
                await do_grant(ctx, uid)
            if n < total:
                due = int(time.time()) + C.INSTALL_DAYS * 86400
                db.flag_set(f"inst:{uid}", f"{n + 1}|{due}|0")
                try:
                    await ctx.bot.send_message(uid, T.PART_PAID.format(n=n, amount=C.INSTALL_PARTS[n], days=C.INSTALL_DAYS), parse_mode="HTML")
                except Exception as e:
                    log.warning("part paid %s: %s", uid, e)
            else:
                db.flag_set(f"inst:{uid}", "done")
                try:
                    await ctx.bot.send_message(uid, T.PART_ALL_PAID)
                except Exception as e:
                    log.warning("part done %s: %s", uid, e)
            await notify_admins(ctx, f"✅ Платіж {n}/{total} розтермінування: {amount} {cur}. {name} (ID {uid})."
                                     + (" Доступ відкрито автоматично." if n == 1 else ""))
            return
        crm.log_ev(uid, "paid", f"{amount}|повністю")
        await do_grant(ctx, uid)
        await notify_admins(ctx, f"✅ Оплата отримана: інтенсив повністю, {amount} {cur}. {name} (ID {uid}). Доступ відкрито автоматично.")
    try:
        await wfp.poll(on_paid)
    except Exception as e:
        log.warning("paid_job: %s", e)


async def start_pay(ctx, u, chat):
    """Вибір: оплатити все або розтермінування."""
    db.set_field(u.id, "asked_int", 1)
    crm.log_ev(u.id, "pay_choice")
    await ctx.bot.send_message(chat, T.PAY_CHOICE + T.URGENT, parse_mode="HTML", reply_markup=M([
        [B(T.BTN_PAY_FULL, callback_data="payfull")],
        [B(T.BTN_PAY_PARTS, callback_data="paypart:1")],
        [B(T.BTN_MENU, callback_data="menu")]]))


async def make_invoice(ctx, u, chat, kind, amount, name, text):
    url = await wfp.create_invoice(u.id, kind, amount, "UAH", name)
    if url:
        crm.log_ev(u.id, "invoice", f"{kind}|{amount}")
        await ctx.bot.send_message(chat, text, parse_mode="HTML",
                                   reply_markup=M([[B("Оплатити", url=url)], [B(T.BTN_MENU, callback_data="menu")]]))
        await notify_admins(ctx, f"💳 {who(u)} отримав(ла) посилання на оплату: {name}, {amount} грн.")
    else:
        await ctx.bot.send_message(chat, T.PAY_MANUAL)
        await notify_admins(ctx, f"⚠️ Автооплата не спрацювала ({wfp.LAST_ERROR or 'причина невідома'}). Заявка: {name}, {who(u)}",
                            M([[B("Відкрити доступ", callback_data=f"grant:{u.id}")]]))


async def pay_full(ctx, u, chat):
    await make_invoice(ctx, u, chat, "int", C.INTENSIVE_AMOUNT, f"Інтенсив «{C.INTENSIVE_NAME}»", T.PAY_LINK)


async def pay_part(ctx, u, chat, n):
    if not 1 <= n <= len(C.INSTALL_PARTS):
        return
    amount = C.INSTALL_PARTS[n - 1]
    await make_invoice(ctx, u, chat, f"int{n}", amount, f"Інтенсив «{C.INTENSIVE_NAME}», платіж {n}/{len(C.INSTALL_PARTS)}",
                       T.PART_LINK.format(n=n, amount=amount))


async def install_job(ctx):
    """Нагадування про наступні платежі розтермінування."""
    now = int(time.time())
    for k, v in db.kv_prefix("inst:"):
        if not v or v == "done":
            continue
        n, due, sent = (v.split("|") + ["0"])[:3]
        if int(due) > now or sent == "1":
            continue
        uid = int(k.split(":")[1])
        n = int(n)
        try:
            await ctx.bot.send_message(uid, T.PART_REMIND.format(n=n, amount=C.INSTALL_PARTS[n - 1]), parse_mode="HTML",
                                       reply_markup=M([[B(f"Оплатити {C.INSTALL_PARTS[n - 1]} грн", callback_data=f"paypart:{n}")]]))
            db.flag_set(k, f"{n}|{due}|1")
            await notify_admins(ctx, f"⏰ Нагадала про {n}-й платіж розтермінування: ID {uid}")
        except Exception as e:
            log.warning("install remind %s: %s", uid, e)


# ---------- кнопки ----------
async def on_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()
    u = q.from_user
    chat = q.message.chat_id
    db.upsert_user(u)
    if data == "chg:check":
        member = await is_member(ctx.bot, u.id)
        if member is False and not is_admin(u.id):
            await ctx.bot.send_message(chat, T.GATE_NOT_YET, reply_markup=kb_gate(), parse_mode="HTML")
            return
        crm.log_ev(u.id, "gate_ok")
        await ctx.bot.send_message(chat, T.GATE_OK, parse_mode="HTML")
        src = db.flag_get(f"gate_src:{u.id}") or "start"
        await go_src(ctx, None, chat, u.id, src)
        return
    if not data.startswith(("grp:", "grant:", "crm:")) and await gate(ctx, u.id, chat):
        return
    if not data.startswith(("qz:", "grp:", "grant:")):
        await ensure_bottom(ctx, u.id, chat)
    if data.startswith("crm:"):
        if is_admin(u.id):
            await crm.on_cb(q, ctx, data)
        return
    if data in ("menu", "int", "ask") or data.startswith(("sec:", "soon:")):
        crm.log_ev(u.id, data)
    if data in ("menu", "int") and ctx.user_data.get("hid"):   # людина вийшла з тесту чи питання кнопкою: повертаємо меню
        await show_bottom(ctx, chat)

    if data == "qz:go":
        await ctx.bot.send_message(chat, T.QUIZ_HIDE, parse_mode="HTML", reply_markup=hide(ctx))
    if data == "qz:start":
        await quiz.start(ctx.bot, chat)
    elif data.startswith("qz:"):
        await quiz.on_cb(q, ctx, data, notify_admins, kb_offer, lambda: bottom(ctx, u.id))
    elif data.startswith("grp:"):
        await groups.on_choose(q, ctx, data)
    elif data.startswith("grant:"):
        if is_admin(u.id):
            await do_grant(ctx, int(data.split(":")[1]))
            await q.edit_message_reply_markup(None)
            await ctx.bot.send_message(chat, "Доступ відкрито ✅")
    elif data == "menu":
        await ctx.bot.send_message(chat, T.START_2, reply_markup=kb_start(is_admin(u.id)), parse_mode="HTML")
    elif data == "int":
        await intensive_card(ctx, chat)
    elif data.startswith("sec:"):
        code = data.split(":", 1)[1]
        if code in SECTIONS:
            await show_section(ctx, chat, code)
    elif data.startswith("soon:"):
        await ctx.bot.send_message(chat, T.SOON, reply_markup=M([[B(T.BTN_INTENSIVE, callback_data="int")]]))
    elif data == "pay":
        await start_pay(ctx, u, chat)
    elif data == "install":
        await start_pay(ctx, u, chat)
    elif data == "payfull":
        await pay_full(ctx, u, chat)
    elif data.startswith("paypart:"):
        await pay_part(ctx, u, chat, int(data.split(":")[1]))
    elif data == "ask":
        ctx.user_data["ask"] = True
        await ctx.bot.send_message(chat, T.QUESTION, reply_markup=hide(ctx))


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    txt = update.message.text
    if await gate(ctx, u.id, update.effective_chat.id):
        return
    if txt in BOTTOM:                 # кнопка меню важливіша за очікування тексту
        for k in ("ask", "crm_wait"):
            ctx.user_data.pop(k, None)
        code = BOTTOM[txt]
        chat = update.effective_chat.id
        if code != "pay":
            crm.log_ev(u.id, "menu" if code == "home" else f"sec:{code}")
        if code == "home":
            await update.message.reply_text(T.START_2, reply_markup=kb_start(is_admin(u.id)), parse_mode="HTML")
            if ctx.user_data.get("hid"):
                await show_bottom(ctx, chat)
        elif code == "pay":
            await start_pay(ctx, u, chat)
        else:
            await show_section(ctx, chat, code)
        return
    if is_admin(u.id) and await crm.on_admin_text(update, ctx):
        return
    if ctx.user_data.pop("ask", False):
        crm.log_ev(u.id, "question", txt[:200])
        await notify_admins(ctx, f"❓ Питання від {who(u)}:\n\n{update.message.text}")
        await update.message.reply_text(T.QUESTION_OK, reply_markup=bottom(ctx, u.id))
        return
    if not is_admin(u.id):
        crm.log_ev(u.id, "msg", txt[:200])
        await notify_admins(ctx, f"✉️ Повідомлення від {who(u)}:\n\n{update.message.text}")
        await update.message.reply_text("Дякую, передала ваше повідомлення ❤", reply_markup=kb_start())
        if ctx.user_data.get("hid"):
            await show_bottom(ctx, update.effective_chat.id)


# ---------- команди адміна ----------
async def cmd_stats(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    s = db.stats()
    await update.message.reply_text(f"📊 Усього людей: {s['total']}\nПрийшли за словом ХОЧУ: {s['hochu']}\n"
                                    f"Пройшли діагностику: {len(db.kv_prefix('quiz:'))}\nНатиснули «Оплатити»: {s['asked_int']}\nОплатили інтенсив: {s['int_paid']}")


async def cmd_grant(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    if len(ctx.args) != 1 or not ctx.args[0].isdigit():
        await update.message.reply_text("Формат: /grant ID"); return
    await do_grant(ctx, int(ctx.args[0]))
    await update.message.reply_text("Доступ відкрито ✅")


async def cmd_wfptest(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    try:
        url = await wfp.create_invoice(update.effective_user.id, "test", C.INTENSIVE_AMOUNT, "UAH", "Тест рахунку")
    except Exception as e:
        url = None
        wfp.LAST_ERROR = f"{type(e).__name__}: {str(e)[:200]}"
    ok = "✅ Рахунок створився, зв'язок з WayForPay працює." if url else f"❌ Рахунок не створився.\nПричина: {wfp.LAST_ERROR}"
    await update.message.reply_text(f"{wfp.env_report()}\n\n{ok}")


async def cmd_help(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text(
        "/crm люди, групи, розсилка, звіти\n/stats звіт\n/grant ID відкрити доступ вручну\n/wfptest перевірити WayForPay\n"
        "/grupa канал інтенсиву (у самому каналі чи групі: підключити)\n\n"
        f"Звичайний старт: https://t.me/{ctx.bot.username}\n"
        f"Кодове слово ХОЧУ, вся інформація (для ManyChat): https://t.me/{ctx.bot.username}?start=hochu\n"
        f"Діагностика кишківника (для ManyChat): https://t.me/{ctx.bot.username}?start=test")


async def cmd_crm(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    await crm.show_menu(ctx.bot, update.effective_chat.id)


async def on_error(update, ctx):
    log.exception("помилка: %s", ctx.error)


async def post_init(app):
    try:
        await app.bot.set_my_commands([BotCommand("start", "Почати"), BotCommand("menu", "Меню")])
        admin_cmds = [BotCommand("start", "Почати"), BotCommand("menu", "Меню"), BotCommand("crm", "CRM і звіти"), BotCommand("stats", "Звіт"),
                      BotCommand("wfptest", "Перевірка оплати"), BotCommand("grupa", "Канал інтенсиву"),
                      BotCommand("help", "Команди адміна")]
        for a in C.ADMIN_IDS:
            await app.bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(a))
        await app.bot.set_my_short_description(T.SHORT_DESC)
        await app.bot.set_my_description(T.DESC)
        await changelog.send(app.bot)
        if not db.flag_get("hello_sent"):
            db.flag_set("hello_sent")
            for a in C.ADMIN_IDS:
                await app.bot.send_message(a, "✅ Агента запущено.\n"
                                              f"Звичайний старт: https://t.me/{app.bot.username}\n"
                                              f"Кодове слово ХОЧУ: https://t.me/{app.bot.username}?start=hochu\n"
                                              "Команди: /help")
    except Exception as e:
        log.warning("post_init: %s", e)


def main():
    if not C.BOT_TOKEN:
        raise SystemExit("Не задано BOT_TOKEN")
    db.init()
    wfp.init_table()
    crm.init()
    crm.setup(
        admins=C.ADMIN_IDS,
        src={"hochu": "кодове слово ХОЧУ", "test": "діагностика", "site": "сайт", "start": "напряму"},
        labels={"start": "Старт", "restart": "Повторний старт", "hello": "Привітання", "int_full": "Вся інформація (ХОЧУ)",
                "site": "Прийшли з сайту", "menu": "Головне меню", "int": "Картка інтенсиву",
                "sec:author": "Про Валентину", "sec:launch": "Про запуск", "sec:for": "Для кого", "sec:program": "Програма",
                "sec:get": "Що ви отримаєте", "sec:terms": "Умови і ціна", "sec:": "Розділ інтенсиву",
                "soon:": "Кнопка «скоро»", "ask": "Натиснули «Запитати»", "question": "Поставили питання",
                "msg": "Написали в чат", "pay_choice": "Вибір оплати (бачили ціну)", "invoice": "Взяли посилання на оплату",
                "paid": "Оплатили", "quiz_open": "Відкрили діагностику", "quiz_go": "Почали діагностику",
                "quiz_q*": "Діагностика, на середині", "quiz_done": "Завершили діагностику",
                "blocked": "Заблокували агента", "unblocked": "Розблокували агента"},
        funnel=[("прийшли", ["start", "restart"]),
                ("дивились інтенсив", ["int", "int_full", "site", "sec:"]),
                ("бачили ціну", ["pay_choice", "sec:terms", "int_full", "site", "quiz_done"]),
                ("взяли посилання", ["invoice"]),
                ("оплатили", ["paid"])],
        quiz_zones=quiz.ZONE_NAMES,
        paid_fn=lambda uid: bool((db.get_user(uid) or {"int_paid": 0})["int_paid"]),
        parts_fn=lambda uid: (db.flag_get(f"inst:{uid}") or "done") != "done")
    app = Application.builder().token(C.BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("menu", cmd_menu, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("grant", cmd_grant))
    app.add_handler(CommandHandler("wfptest", cmd_wfptest))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("crm", cmd_crm))
    app.add_handler(CommandHandler("grupa", groups.cmd_grupa))
    app.add_handler(ChatMemberHandler(groups.on_my_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(crm.on_private_member, ChatMemberHandler.MY_CHAT_MEMBER), group=1)
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
    app.job_queue.run_repeating(paid_job, interval=60, first=45)
    app.job_queue.run_repeating(gate_job, interval=600, first=60)  # 11.11: «канал підключено» адмінам
    app.job_queue.run_repeating(install_job, interval=3600, first=120)
    app.job_queue.run_repeating(__import__("dozhim").job, interval=300, first=180)  # 13.11: дожими інтенсиву (dozhim.py)
    app.job_queue.run_repeating(crm.daily_job, interval=300, first=90)  # 10.11: звіт адмінам щоранку о 9:00
    log.info("Агента запущено")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
