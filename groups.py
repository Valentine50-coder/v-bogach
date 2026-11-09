"""Групи інтенсиву й курсу: агент адмін у групі, після оплати видає особисте одноразове посилання.

Як підключити групу: додати агента в групу адміністратором з правом «Запрошувати користувачів».
Агент сам напише адмінам і спитає кнопками, це група інтенсиву чи курсу.
Якщо агента додали раніше (до оновлення), адмін пише в самій групі /grupa.
"""
import logging

from telegram import ChatMember, InlineKeyboardButton as B, InlineKeyboardMarkup as M, Update

import config as C
import db

log = logging.getLogger("groups")
NAMES = {"int": "інтенсиву", "course": "курсу"}


def group_of(kind):
    v = db.flag_get(f"group:{kind}")
    if not v:
        return None, ""
    cid, _, title = v.partition("|")
    return int(cid), title


def kb_choose(chat_id):
    return M([[B("Група інтенсиву", callback_data=f"grp:int:{chat_id}")],
              [B("Група курсу", callback_data=f"grp:course:{chat_id}")],
              [B("Це не наша група", callback_data=f"grp:no:{chat_id}")]])


async def _ask_admins(bot, chat, can_invite):
    title = chat.title or str(chat.id)
    if can_invite:
        text = (f"👋 Мене зробили адміністратором у групі «{title}».\n"
                "Це група інтенсиву чи курсу? Після оплати я видаватиму людям особисте посилання саме в цю групу.")
        kb = kb_choose(chat.id)
    else:
        text = (f"⚠️ Мене додали в групу «{title}», але я не можу запрошувати людей.\n"
                "Зробіть мене адміністратором з правом «Запрошувати користувачів» (Invite users), і я одразу напишу знову.")
        kb = None
    for a in C.ADMIN_IDS:
        try:
            await bot.send_message(a, text, reply_markup=kb)
        except Exception as e:
            log.warning("ask admin %s: %s", a, e)


async def on_my_member(update: Update, ctx):
    """Агента додали в групу, зробили адміном або забрали права."""
    m = update.my_chat_member
    if not m or m.chat.type not in ("group", "supergroup", "channel"):
        return
    new = m.new_chat_member
    if new.status == ChatMember.ADMINISTRATOR:
        await _ask_admins(ctx.bot, m.chat, bool(getattr(new, "can_invite_users", False)))
    elif new.status == ChatMember.MEMBER:
        await _ask_admins(ctx.bot, m.chat, False)
    elif new.status in (ChatMember.LEFT, ChatMember.BANNED):
        for kind in NAMES:
            cid, title = group_of(kind)
            if cid == m.chat.id:
                db.flag_set(f"group:{kind}", "")
                for a in C.ADMIN_IDS:
                    try:
                        await ctx.bot.send_message(a, f"⚠️ Мене видалили з групи {NAMES[kind]} «{title}». Посилання в неї більше не видаю.")
                    except Exception:
                        pass


async def cmd_grupa(update: Update, ctx):
    """/grupa у самій групі: адмін підключає групу, куди агента додали раніше."""
    u, chat = update.effective_user, update.effective_chat
    if not u or u.id not in C.ADMIN_IDS:
        return
    if chat.type == "private":
        lines = []
        for kind in NAMES:
            cid, title = group_of(kind)
            lines.append(f"Група {NAMES[kind]}: " + (f"«{title}» ✅" if cid else "не підключена"))
        await update.message.reply_text("\n".join(lines) + "\n\nЩоб підключити групу: додайте мене туди адміністратором "
                                        "з правом «Запрошувати користувачів» і напишіть у групі /grupa")
        return
    try:
        me = await ctx.bot.get_chat_member(chat.id, ctx.bot.id)
        can = me.status == ChatMember.ADMINISTRATOR and bool(getattr(me, "can_invite_users", False))
    except Exception:
        can = False
    await _ask_admins(ctx.bot, chat, can)


async def on_choose(q, ctx, data):
    """Кнопка адміна: grp:int|course|no:<chat_id>."""
    if q.from_user.id not in C.ADMIN_IDS:
        return
    _, kind, cid = data.split(":", 2)
    if kind == "no":
        await q.edit_message_text("Добре, цю групу не використовую.")
        return
    cid = int(cid)
    try:
        chat = await ctx.bot.get_chat(cid)
        title = chat.title or str(cid)
    except Exception:
        title = str(cid)
    db.flag_set(f"group:{kind}", f"{cid}|{title}")
    await q.edit_message_text(f"✅ Запам'ятала: «{title}» це група {NAMES[kind]}. Після оплати люди отримають особисте посилання сюди.")
    sent = await send_pending(ctx.bot, kind)
    if sent:
        await ctx.bot.send_message(q.from_user.id, f"Тим, хто вже оплатив, надіслала вхід у групу: {sent}.")


async def invite_kb(bot, uid, kind):
    """Кнопка з особистим одноразовим посиланням або None (тоді адміни отримують попередження)."""
    cid, title = group_of(kind)
    if not cid:
        return None
    try:
        link = await bot.create_chat_invite_link(cid, member_limit=1, name=f"id{uid}"[:32])
        db.flag_set(f"grpsent:{kind}:{uid}")
        return M([[B("Увійти в групу", url=link.invite_link)]])
    except Exception as e:
        log.warning("invite %s %s: %s", kind, uid, e)
        for a in C.ADMIN_IDS:
            try:
                await bot.send_message(a, f"⚠️ Не змогла створити посилання в групу {NAMES[kind]} «{title}» для ID {uid}: {e}\n"
                                          "Перевірте, що я адміністратор з правом «Запрошувати користувачів».")
            except Exception:
                pass
        return None


async def send_pending(bot, kind):
    """Після підключення групи: вхід тим, хто оплатив раніше і ще не отримав посилання."""
    n = 0
    for uid in db.paid_users(kind):
        if db.flag_get(f"grpsent:{kind}:{uid}"):
            continue
        kb = await invite_kb(bot, uid, kind)
        if not kb:
            break
        try:
            await bot.send_message(uid, f"🔗 Ось ваш вхід у групу {NAMES[kind]} 👇 Посилання особисте, на одну людину.", reply_markup=kb)
            n += 1
        except Exception as e:
            log.warning("pending %s: %s", uid, e)
    return n
