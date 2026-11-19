"""19.11.2026 (Тетяна): нова стратегія Валентини.
Набір на листопадовий інтенсив закрито. Запис у групу на січень: бронь 350 грн, повна вартість 750 грн для перших 20 учасників,
далі 1444 грн. Консультація Валентини зі знижкою 50% до кінця листопада: людина платить одразу в агенті, Валентина потім сама пише.

Оплати WayForPay (kind): jb бронь 350, jf повністю (750 або 1444), jr доплата залишку після броні, cons консультація.
Стан людини kv jan:<uid> = "b750" | "b1444" (бронь, у якій сумі група) або "f" (оплачено повністю); course_paid=1 зупиняє дожими.
Консультація: kv cons:<uid> = "paid". Ціну консультації (повну) Валентина вводить сама (kv cons_price), знижка рахується тут.
setup_job: після оновлення один раз питає адмінів ціну консультації, дату старту січневої групи і коли доплата після броні;
відповіді зберігає (kv jan_q:<код>) і пересилає всім адмінам. announce: прев'ю розсилки + «✅ Розіслати» (jn:go).
"""
import asyncio
import html
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from telegram.error import Forbidden

import config as C
import db

log = logging.getLogger("jan")
TZ = ZoneInfo("Europe/Kyiv")
BOOK, EARLY, FULL, SEATS = 350, 750, C.INTENSIVE_AMOUNT, 20
CONS_UNTIL = datetime(2026, 11, 30, 23, 59, tzinfo=TZ)
_BG = set()

# ---------- тексти ----------
BTN_CONS = "📅 ЗАПИСАТИСЬ НА КОНСУЛЬТАЦІЮ"
BTN_JAN = "🧠 Група на січень"
BTN_BOOK = f"Забронювати місце: {BOOK} грн"
CLOSED = ("<b>Увага: набір учасників інтенсиву на листопад закрито</b> ❗️\n\n"
          "Наразі йде <b>запис у групу на січень</b>. Вартість бронювання <code>350 грн</code>. "
          "Повна вартість <b>для перших 20 учасників</b> <code>750 грн</code> 🔥")
CONS_LINE = ("Якщо вам уже зараз потрібна допомога, можете записатись на <b>індивідуальну консультацію Валентини "
             "з 50% знижкою</b> <i>(до кінця листопада)</i> ‼️")
ANNOUNCE = CLOSED + "\n\n" + CONS_LINE
JAN_TERMS = ("<b>ГРУПА НА СІЧЕНЬ</b>\n\n"
             "<b>НА ВАС ЧЕКАЄ:</b>\n"
             "‼️ Спеціальний <b>Telegram-канал</b> із відео, гайдами, рецептами <b>з доступом назавжди</b>\n"
             "✓ Постійно діючий чат підтримки з авторкою та тренерами\n"
             "✓ Повноцінний курс + мініконсультації + супровід\n\n"
             "Бронювання місця: <code>350 грн</code>\n"
             "Повна вартість <b>для перших 20 учасників</b>: <code>750 грн</code> 🔥 <i>(далі 1444 грн)</i>\n\n"
             "<i>Матеріали мають інформаційний характер і не замінюють індивідуальної консультації нутриціолога.</i>")
URGENT = "\n\n‼️ <b>Ціна 750 грн тільки для перших 20 учасників.</b> <i>Кількість місць обмежена</i> ❗"
PAY_CHOICE = ("<b>Як вам зручніше?</b>\n\n"
              "<b>Забронювати місце:</b> <code>350 грн</code> зараз, решту доплатите ближче до старту\n"
              "<b>Оплатити повністю:</b> <code>{full} грн</code>{note}\n\n"
              "<i>У будь-якому разі ваше місце в групі на січень закріплюється одразу після оплати.</i>")
BOOKED = ("✅ <b>Місце в групі на січень заброньовано!</b> Дякую ❤\n\n"
          "Ваша повна вартість <code>{total} грн</code>, тобто доплатити лишається <code>{rest} грн</code>. "
          "Я нагадаю ближче до старту, а можна доплатити й зараз кнопкою нижче.\n\n"
          "<i>Посилання на групу надішлю перед стартом.</i>")
PAID_FULL = ("✅ <b>Ви в групі на січень, оплату отримано!</b> Дякую ❤\n\n"
             "<i>Посилання на групу надішлю перед стартом.</i>")
CONS_INFO = ("<b>Індивідуальна консультація Валентини</b>\n\n"
             "Особисто розберемо вашу ситуацію: симптоми, аналізи, харчування, і ви отримаєте <b>чіткий план, з чого почати саме вам</b>.\n\n"
             "{price}\n\n"
             "<i>Після оплати Валентина сама напише вам в особисті, щоб узгодити зручний час.</i>")
CONS_PRICE = "Вартість: <s>{full} грн</s> <code>{half} грн</code> <b>зі знижкою 50%</b> <i>(до кінця листопада)</i> ‼️"
CONS_PRICE_FULL = "Вартість: <code>{full} грн</code>"
CONS_NOPRICE = ("Запис уже відкрито ❤ Натисніть кнопку нижче, я передам вашу заявку Валентині, і вона напише вам особисто.")
CONS_PAID = ("✅ <b>Консультацію оплачено, дякую!</b> ❤\n\n"
             "Валентина напише вам особисто найближчим часом, щоб узгодити зручний час.")

QUESTIONS = [
    ("cons", "💬 Скільки коштує ваша індивідуальна консультація <b>без знижки</b>? Напишіть тільки число в гривнях "
             "(наприклад <code>1600</code>). Агент сам покаже людям ціну зі знижкою 50% до кінця листопада і прийматиме оплату."),
    ("start", "📅 Коли старт групи на січень? Напишіть дату (наприклад <code>12 січня</code>)."),
    ("rest", "💳 Ті, хто забронював місце за 350 грн, коли доплачують решту (400 грн для перших 20)? "
             "Напишіть своїми словами, наприклад «за тиждень до старту»."),
]


def now():
    return datetime.now(TZ)


def cons_full():
    try:
        return int(db.flag_get("cons_price") or 0)
    except ValueError:
        return 0


def cons_amount():
    f = cons_full()
    if not f:
        return 0
    return (f + 1) // 2 if now() <= CONS_UNTIL else f


def cons_text():
    f = cons_full()
    if not f:
        return CONS_INFO.format(price=CONS_NOPRICE)
    p = CONS_PRICE.format(full=f, half=cons_amount()) if now() <= CONS_UNTIL else CONS_PRICE_FULL.format(full=f)
    return CONS_INFO.format(price=p)


def taken():
    return sum(1 for _, v in db.kv_prefix("jan:") if v and v[0] in "bf")


def early():
    return taken() < SEATS


def full_price():
    return EARLY if early() else FULL


def seats_line():
    left = SEATS - taken()
    return f"\n\n🔥 За ціною 750 грн лишилось місць: <b>{left}</b> з {SEATS}" if left > 0 else ""


def start_line():
    s = db.flag_get("jan_q:start")
    return f"Старт: <code>{html.escape(s)}</code>\n" if s else ""


def kb_cons_jan(extra=None):
    rows = [[B(BTN_CONS, callback_data="cons")], [B(BTN_JAN, callback_data="jan")]]
    return M(rows + (extra or []))


# ---------- показ ----------
async def show_jan(ctx, chat, kb_back):
    __import__("crm").log_ev(chat, "jan")
    await ctx.bot.send_message(chat, CLOSED + "\n\n" + start_line() + JAN_TERMS + seats_line(), parse_mode="HTML",
                               reply_markup=M([[B(BTN_BOOK, callback_data="jn:book")],
                                               [B(f"Оплатити повністю: {full_price()} грн", callback_data="jn:full")],
                                               [B(BTN_CONS, callback_data="cons")]] + kb_back))


async def show_cons(ctx, chat, kb_back):
    __import__("crm").log_ev(chat, "cons")
    amt = cons_amount()
    btn = B(f"Оплатити консультацію: {amt} грн", callback_data="jn:cons") if amt else B("📅 Записатись", callback_data="jn:conreq")
    await ctx.bot.send_message(chat, cons_text(), parse_mode="HTML", reply_markup=M([[btn]] + kb_back))


async def pay_choice(ctx, chat, kb_back):
    fp = full_price()
    note = " <i>(ціна для перших 20 учасників)</i>" if fp == EARLY else ""
    await ctx.bot.send_message(chat, PAY_CHOICE.format(full=fp, note=note) + seats_line(), parse_mode="HTML",
                               reply_markup=M([[B(BTN_BOOK, callback_data="jn:book")],
                                               [B(f"Оплатити повністю: {fp} грн", callback_data="jn:full")],
                                               [B(BTN_CONS, callback_data="cons")]] + kb_back))


# ---------- кнопки ----------
async def on_cb(ctx, u, chat, data, make_invoice, notify_admins, who):
    st = db.flag_get(f"jan:{u.id}") or ""
    if data == "jn:book":
        if st:
            await ctx.bot.send_message(chat, "Ваше місце в групі на січень уже закріплене ❤")
            return
        await make_invoice(ctx, u, chat, "jb", BOOK, "Бронювання місця в групі на січень «Здоровий кишківник»",
                           "Ось посилання на бронювання 👇 Після оплати поверніться в цей чат, протягом хвилини я все підтверджу ❤")
    elif data == "jn:full":
        if st == "f":
            await ctx.bot.send_message(chat, "Групу на січень у вас уже оплачено повністю ❤")
            return
        if st.startswith("b"):
            await _rest(ctx, u, chat, st, make_invoice)
            return
        fp = full_price()
        await make_invoice(ctx, u, chat, f"jf{fp}", fp, "Група на січень «Здоровий кишківник»",
                           "Ось посилання на оплату 👇 Після оплати поверніться в цей чат, протягом хвилини я все підтверджу ❤")
    elif data == "jn:rest":
        if st.startswith("b"):
            await _rest(ctx, u, chat, st, make_invoice)
    elif data == "jn:cons":
        amt = cons_amount()
        if not amt:
            await on_cb(ctx, u, chat, "jn:conreq", make_invoice, notify_admins, who)
            return
        await make_invoice(ctx, u, chat, "cons", amt, "Індивідуальна консультація Валентини Швець",
                           "Ось посилання на оплату консультації 👇 Після оплати поверніться в цей чат ❤")
    elif data == "jn:conreq":
        __import__("crm").log_ev(u.id, "cons_req")
        await ctx.bot.send_message(chat, "Дякую! Передала вашу заявку, Валентина напише вам особисто найближчим часом ❤")
        await notify_admins(ctx, f"📅 Заявка на консультацію (ціну ще не задано, оплати в агенті поки немає): {who(u)}")


async def _rest(ctx, u, chat, st, make_invoice):
    total = int(st[1:] or EARLY)
    rest = total - BOOK
    await make_invoice(ctx, u, chat, "jr", rest, "Доплата: група на січень «Здоровий кишківник»",
                       f"Ось посилання на доплату <code>{rest} грн</code> 👇 Після оплати поверніться в цей чат ❤")


# ---------- оплати ----------
async def on_paid(ctx, uid, kind, amount, cur, notify_admins):
    """True, якщо оплату оброблено тут."""
    u = db.get_user(uid)
    name = (u["name"] if u else "") + (f" @{u['username']}" if u and u["username"] else "")
    crm = __import__("crm")
    if kind == "jb":
        total = EARLY if early() else FULL
        db.flag_set(f"jan:{uid}", f"b{total}")  # до повідомлень
        db.set_field(uid, "course_paid", 1)
        crm.log_ev(uid, "paid", f"{amount}|бронь січень")
        await _send(ctx, uid, BOOKED.format(total=total, rest=total - BOOK),
                    M([[B(f"Доплатити {total - BOOK} грн", callback_data="jn:rest")]]))
        await notify_admins(ctx, f"✅ Бронь у групу на січень: {amount} {cur}. {name} (ID {uid}). Повна вартість для неї {total} грн, "
                                 f"доплата {total - BOOK}. Зайнято місць: {taken()} з {SEATS} за 750.")
        return True
    if kind.startswith("jf") or kind == "jr":
        db.flag_set(f"jan:{uid}", "f")
        db.set_field(uid, "course_paid", 1)
        crm.log_ev(uid, "paid", f"{amount}|{'доплата' if kind == 'jr' else 'повністю'} січень")
        await _send(ctx, uid, PAID_FULL)
        await notify_admins(ctx, f"✅ Група на січень {'доплата' if kind == 'jr' else 'повністю'}: {amount} {cur}. {name} (ID {uid}). "
                                 f"Зайнято місць: {taken()} з {SEATS} за 750.")
        return True
    if kind == "cons":
        db.flag_set(f"cons:{uid}", "paid")
        crm.log_ev(uid, "paid", f"{amount}|консультація")
        await _send(ctx, uid, CONS_PAID)
        nick = f"https://t.me/{u['username']}" if u and u["username"] else f"ID {uid} (ніка немає, напишіть через /crm або агента)"
        await notify_admins(ctx, f"✅ Оплачено консультацію: {amount} {cur}. {name}\nНапишіть їй, щоб узгодити час: {nick}")
        return True
    return False


async def _send(ctx, uid, text, kb=None):
    try:
        await ctx.bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        log.warning("jan send %s: %s", uid, e)


# ---------- питання Валентині після оновлення ----------
def _next_q():
    for code, text in QUESTIONS:
        if not db.flag_get(f"jan_q:{code}"):
            return code, text
    return None, None


async def setup_job(ctx):
    if db.flag_get("jan_setup") == "1":
        return
    db.flag_set("jan_setup", "1")
    code, text = _next_q()
    if not code:
        return
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, "🙋‍♀️ <b>Кілька питань, щоб агент правильно приймав запис</b>\n\n"
                                          "Відповідайте просто повідомленням у цей чат.\n\n" + text, parse_mode="HTML")
        except Exception as e:
            log.warning("jan setup %s: %s", a, e)
    db.flag_set("jan_wait", code)


async def on_admin_text(update, ctx, notify_admins):
    """True, якщо текст адміна був відповіддю на питання."""
    code = db.flag_get("jan_wait")
    if not code:
        return False
    txt = (update.message.text or "").strip()
    if code == "cons":
        digits = "".join(ch for ch in txt if ch.isdigit())
        if not digits:
            await update.message.reply_text("Напишіть, будь ласка, тільки число, наприклад 1600")
            return True
        db.flag_set("cons_price", digits)
        txt = digits
    db.flag_set(f"jan_q:{code}", txt)
    ans = {"cons": f"ціна консультації {txt} грн (зі знижкою {cons_amount()} грн до 30.11)", "start": f"старт січневої групи: {txt}",
           "rest": f"доплата після броні: {txt}"}[code]
    await notify_admins(ctx, f"📝 Записала відповідь: {ans}")
    nxt, text = _next_q()
    if nxt:
        db.flag_set("jan_wait", nxt)
        await update.message.reply_text(text, parse_mode="HTML")
    else:
        db.flag_set("jan_wait", "")
        await update.message.reply_text("Дякую, усе записала ❤ Агент уже приймає запис на консультацію і в групу на січень.")
    return True


async def cmd_kons(update, ctx):
    """/kons N: змінити повну ціну консультації; /kons без числа: показати, що записано."""
    if update.effective_user.id not in C.ADMIN_IDS:
        return
    if ctx.args and ctx.args[0].isdigit():
        db.flag_set("cons_price", ctx.args[0])
    q = {c: db.flag_get(f"jan_q:{c}") or "—" for c, _ in QUESTIONS}
    await update.message.reply_text(f"Консультація: {cons_full() or '—'} грн, зараз люди платять {cons_amount() or '—'} грн\n"
                                    f"Старт січневої групи: {q['start']}\nДоплата після броні: {q['rest']}\n"
                                    f"Зайнято місць за 750: {taken()} з {SEATS}\n\nЗмінити ціну консультації: /kons 1600")


# ---------- розсилка ----------
async def announce_preview_job(ctx):
    if db.flag_get("jn_prev") == "1":
        return
    db.flag_set("jn_prev", "1")
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, ANNOUNCE, parse_mode="HTML", reply_markup=kb_cons_jan())
            await ctx.bot.send_message(a, "👆 Так виглядатиме розсилка всім в агенті, хто ще не оплатив. Розсилаємо?",
                                       reply_markup=M([[B("✅ Розіслати", callback_data="jn:go")]]))
        except Exception as e:
            log.warning("jan prev %s: %s", a, e)


async def announce_go(ctx, chat, notify_admins):
    if db.flag_get("jn_sent") == "1":
        await ctx.bot.send_message(chat, "Цю розсилку вже надіслано ❤")
        return
    db.flag_set("jn_sent", "1")  # до відправки
    await ctx.bot.send_message(chat, "Розсилаю, звіт надішлю сюди 😉")
    _BG.add(asyncio.create_task(_send_all(ctx, notify_admins)))


async def _send_all(ctx, notify_admins):
    with db.conn() as c:
        users = c.execute("SELECT id FROM users WHERE int_paid=0 AND course_paid=0").fetchall()
    ok = fail = 0
    for r in users:
        uid = r["id"]
        if uid in C.ADMIN_IDS or db.flag_get(f"jns:{uid}"):
            continue
        db.flag_set(f"jns:{uid}", "1")
        try:
            await ctx.bot.send_message(uid, ANNOUNCE, parse_mode="HTML", reply_markup=kb_cons_jan())
            ok += 1
        except Forbidden:
            __import__("crm").log_ev(uid, "blocked")
            fail += 1
        except Exception as e:
            log.warning("jan bc %s: %s", uid, e)
            fail += 1
        await asyncio.sleep(0.05)
    await notify_admins(ctx, f"📬 Розсилку «січень + консультація» надіслано: {ok}, не дійшло: {fail}.")
