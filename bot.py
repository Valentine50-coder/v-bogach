"""Агент Валентини Швець: воронка «Старт» і воронка «ХОЧУ» (інтенсив «Здоровий кишківник»)."""
import asyncio
import logging
import os

from telegram import (BotCommand, BotCommandScopeChat, InlineKeyboardButton as B,
                      InlineKeyboardMarkup as M, Update)
from telegram.ext import (Application, CallbackQueryHandler, ChatMemberHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

import config as C
import db
import groups
import texts as T
import wfp

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")
IMG = os.path.join(os.path.dirname(__file__), "images")


def is_admin(uid): return uid in C.ADMIN_IDS


def kb_start():
    rows = [[B(T.BTN_INTENSIVE, callback_data="int")]]
    rows += [[B(text, callback_data=f"soon:{code}")] for text, code in C.START_BUTTONS]
    return M(rows)


def kb_intensive():
    return M([[B(T.BTN_PAY, callback_data="pay")],
              [B(T.BTN_INSTALL, callback_data="install")],
              [B(T.BTN_QUESTION, callback_data="ask")],
              [B(T.BTN_MENU, callback_data="menu")]])


async def send_photo(ctx, chat_id, name, caption=None):
    path = os.path.join(IMG, name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            await ctx.bot.send_photo(chat_id, f, caption=caption, parse_mode="HTML")
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
    if not await send_photo(ctx, chat_id, "start.jpg", T.START_1):
        await ctx.bot.send_message(chat_id, T.START_1)
    await ctx.bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(5)
    await ctx.bot.send_message(chat_id, T.START_2, reply_markup=kb_start(), parse_mode="HTML")


async def funnel_intensive(ctx, chat_id):
    await ctx.bot.send_message(chat_id, T.INT_1, parse_mode="HTML")
    if not await send_photo(ctx, chat_id, "intensive.jpg", T.INT_AUTHOR):
        await ctx.bot.send_message(chat_id, T.INT_AUTHOR, parse_mode="HTML")
    for part in (T.INT_FOR, T.INT_PROGRAM, T.INT_GET):
        await asyncio.sleep(2)
        await ctx.bot.send_message(chat_id, part, parse_mode="HTML")
    await asyncio.sleep(2)
    await ctx.bot.send_message(chat_id, T.INT_TERMS, reply_markup=kb_intensive(), parse_mode="HTML")


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    arg = (ctx.args[0].lower() if ctx.args else "")
    src = "hochu" if arg in ("hochu", "xochu", "intensive") else "start"
    new = db.get_user(u.id) is None
    db.upsert_user(u, src)
    if new:
        await notify_admins(ctx, f"👋 Новий підписник ({'кодове слово ХОЧУ' if src == 'hochu' else 'старт'}): {who(u)}")
    if src == "hochu":
        await funnel_intensive(ctx, update.effective_chat.id)
    else:
        await funnel_start(ctx, update.effective_chat.id)


async def cmd_menu(update: Update, ctx):
    await update.message.reply_text(T.START_2, reply_markup=kb_start(), parse_mode="HTML")


# ---------- оплата ----------
async def do_grant(ctx, uid):
    db.set_field(uid, "int_paid", 1)
    kb = await groups.invite_kb(ctx.bot, uid, "int")
    text = T.ACCESS + (T.GROUP_JOIN if kb else T.ACCESS_NO_GROUP)
    try:
        await ctx.bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        log.warning("grant send %s: %s", uid, e)


async def paid_job(ctx):
    async def on_paid(uid, kind, ref, amount, cur):
        if kind == "test":
            await notify_admins(ctx, f"✅ Тестова оплата пройшла: {amount} {cur}. Автоплатіж працює, доступ нікому не відкрито.")
            return
        await do_grant(ctx, uid)
        u = db.get_user(uid)
        name = (u["name"] if u else "") + (f" @{u['username']}" if u and u["username"] else "")
        await notify_admins(ctx, f"✅ Оплата отримана: інтенсив, {amount} {cur}. {name} (ID {uid}). Доступ відкрито автоматично.")
    try:
        await wfp.poll(on_paid)
    except Exception as e:
        log.warning("paid_job: %s", e)


# ---------- кнопки ----------
async def on_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()
    u = q.from_user
    chat = q.message.chat_id
    db.upsert_user(u)

    if data.startswith("grp:"):
        await groups.on_choose(q, ctx, data)
    elif data.startswith("grant:"):
        if is_admin(u.id):
            await do_grant(ctx, int(data.split(":")[1]))
            await q.edit_message_reply_markup(None)
            await ctx.bot.send_message(chat, "Доступ відкрито ✅")
    elif data == "menu":
        await ctx.bot.send_message(chat, T.START_2, reply_markup=kb_start(), parse_mode="HTML")
    elif data == "int":
        await funnel_intensive(ctx, chat)
    elif data.startswith("soon:"):
        await ctx.bot.send_message(chat, T.SOON, reply_markup=M([[B(T.BTN_INTENSIVE, callback_data="int")]]))
    elif data == "pay":
        db.set_field(u.id, "asked_int", 1)
        url = await wfp.create_invoice(u.id, "int", C.INTENSIVE_AMOUNT, "UAH", f"Інтенсив «{C.INTENSIVE_NAME}»")
        if url:
            await ctx.bot.send_message(chat, T.PAY_LINK, reply_markup=M([[B("Оплатити", url=url)], [B(T.BTN_MENU, callback_data="menu")]]))
            await notify_admins(ctx, f"💳 {who(u)} отримав(ла) посилання на оплату інтенсиву.")
        else:
            await ctx.bot.send_message(chat, T.PAY_MANUAL)
            await notify_admins(ctx, f"⚠️ Автооплата не спрацювала ({wfp.LAST_ERROR or 'причина невідома'}). Заявка на інтенсив: {who(u)}",
                                M([[B("Відкрити доступ", callback_data=f"grant:{u.id}")]]))
    elif data == "install":
        await ctx.bot.send_message(chat, T.INSTALL + (f"\n{C.AUTHOR_CONTACT}" if C.AUTHOR_CONTACT else ""))
        await notify_admins(ctx, f"🗓 Хоче розтермінування на 3 місяці: {who(u)}",
                            M([[B("Відкрити доступ", callback_data=f"grant:{u.id}")]]))
    elif data == "ask":
        ctx.user_data["ask"] = True
        await ctx.bot.send_message(chat, T.QUESTION)


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if ctx.user_data.pop("ask", False):
        await notify_admins(ctx, f"❓ Питання від {who(u)}:\n\n{update.message.text}")
        await update.message.reply_text(T.QUESTION_OK)
        return
    if not is_admin(u.id):
        await notify_admins(ctx, f"✉️ Повідомлення від {who(u)}:\n\n{update.message.text}")
        await update.message.reply_text("Дякую, передала ваше повідомлення ❤", reply_markup=kb_start())


# ---------- команди адміна ----------
async def cmd_stats(update: Update, ctx):
    if not is_admin(update.effective_user.id): return
    s = db.stats()
    await update.message.reply_text(f"📊 Усього людей: {s['total']}\nПрийшли за словом ХОЧУ: {s['hochu']}\n"
                                    f"Натиснули «Оплатити»: {s['asked_int']}\nОплатили інтенсив: {s['int_paid']}")


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
        "/stats звіт\n/grant ID відкрити доступ вручну\n/wfptest перевірити WayForPay\n"
        "/grupa канал інтенсиву (у самому каналі чи групі: підключити)\n\n"
        f"Звичайний старт: https://t.me/{ctx.bot.username}\n"
        f"Кодове слово ХОЧУ (для ManyChat): https://t.me/{ctx.bot.username}?start=hochu")


async def on_error(update, ctx):
    log.exception("помилка: %s", ctx.error)


async def post_init(app):
    try:
        await app.bot.set_my_commands([BotCommand("start", "Почати"), BotCommand("menu", "Меню")])
        admin_cmds = [BotCommand("start", "Почати"), BotCommand("menu", "Меню"), BotCommand("stats", "Звіт"),
                      BotCommand("wfptest", "Перевірка оплати"), BotCommand("grupa", "Канал інтенсиву"),
                      BotCommand("help", "Команди адміна")]
        for a in C.ADMIN_IDS:
            await app.bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(a))
        await app.bot.set_my_short_description(T.SHORT_DESC)
        await app.bot.set_my_description(T.DESC)
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
    app = Application.builder().token(C.BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("menu", cmd_menu, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("grant", cmd_grant))
    app.add_handler(CommandHandler("wfptest", cmd_wfptest))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("grupa", groups.cmd_grupa))
    app.add_handler(ChatMemberHandler(groups.on_my_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(on_cb))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
    app.job_queue.run_repeating(paid_job, interval=60, first=45)
    log.info("Агента запущено")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
