"""26.11.2026: адвент Валентини «Здорові свята» в агенті (Тетяна: «тільки в агенті»). 31 віконце з її файлу «Здорове меню на тиждень».

- ?start=advent (кодове слово АДВЕНТ у ManyChat) або кнопка av:join: людина в адвенті (kv av:<uid>=1).
- 1-31.12 о 9:00 за Києвом job надсилає віконце дня всім, хто в адвенті (kv avs:<n>:<uid> ДО відправки, kv av_day = n).
- Хто приєднався пізніше, одразу отримує сьогоднішнє віконце, а минулі відкриває кнопкою «📖 Відкриті віконця» (av:list → av:o:<n>).
- 24.12 подарунок: PDF media/zdorove_menu_tyzhden.pdf. 28.12 і 31.12 бронь інтенсиву за спецціною 159 (кнопка jn:abook, оплата jba у jan.py).
- Розсилка-запрошення: preview_job адмінам (kv av_prev) + «✅ Розіслати» (av:go, kv av_sent ДО відправки), усім, хто не заблокував.
- Кнопка «🎄 Відкрити календар» (web_app) на сторінку APP_URL: зелено-біла сторінка з кульками, віконця по датах (tools/advent_page.py → agents/kyshkivnyk/advent).
- /advent (адмін): скільки людей в адвенті, яке віконце сьогодні.
"""
import asyncio
import logging
import os

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M, WebAppInfo
from telegram.error import Forbidden

import config as C
import db
from advent_data import W

log = logging.getLogger("advent")
_BG = set()
DIR = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(DIR, "media", "zdorove_menu_tyzhden.pdf")
HOUR = 9

INVITE = ("🎄 <b>Адвент «Здорові свята»</b>\n\n"
          "Грудень у багатьох проходить однаково: корпоративи, салати, солодке, а потім у січні <i>«чому так важко і живіт як камінь?»</i>\n\n"
          "Я хочу, щоб цього року було інакше. Тому з <b>1 по 31 грудня</b> щоранку о 9:00 я відкриватиму для вас одне віконце: "
          "сніданок, обід чи вечеря <b>без цукру, глютену і лактози</b>, мої підказки для кишківника і конструктор здорової тарілки.\n\n"
          "А на Святвечір на вас чекає <b>подарунок</b> 🎁\n\n"
          "<i>Усе безкоштовно, просто натисніть кнопку</i> 👇")
JOINED = ("Ви в адвенті ❤\n\n"
          "Ось ваш календар 👇 Кожне віконце відкривається у свій день.\n\n"
          "<b>1 грудня о 9:00</b> я надішлю вам перше віконце, і так щоранку до самого Нового року.\n\n"
          "<i>Порада: увімкніть сповіщення від цього чату, щоб не пропустити</i> 😉")
JOINED_LATE = "Ви в адвенті ❤ Ось сьогоднішнє віконце 👇 Минулі можна відкрити кнопкою «📖 Відкриті віконця»."
NOTE = "\n\n<i>Меню не замінює особистої консультації спеціаліста.</i>"
BTN_JOIN = "🎄 Хочу в адвент"
BTN_LIST = "📖 Відкриті віконця"
BTN_APP = "🎄 Відкрити календар"
APP_URL = "https://tafijcuktetana12-coder.github.io/agents/kyshkivnyk/advent/"  # 26.11: сторінка-календар (tools/advent_page.py)


def app_btn(n=0):
    return B(BTN_APP, web_app=WebAppInfo(APP_URL + (f"?d={n}" if n else "")))
BTN_BOOK = "🎄 Забронювати за 159 грн"


def _now():
    return __import__("crm").kyiv_now()


def today_n():
    """Номер віконця, яке вже відкрито сьогодні (0 до 1.12 9:00, 31 після грудня)."""
    t = _now()
    if (t.year, t.month) < (2026, 12):
        return 0
    if t.year > 2026:
        return 31
    return t.day if t.hour >= HOUR else t.day - 1


def joined(uid):
    return db.flag_get(f"av:{uid}") == "1"


def members():
    with db.conn() as c:
        return [int(r["k"].split(":")[1]) for r in c.execute("SELECT k FROM kv WHERE k LIKE 'av:%' AND v='1'")
                if r["k"].split(":")[1].isdigit()]


def kb_window(n):
    rows = [[app_btn()]]
    if len(W[n - 1]) > 3 and W[n - 1][3] == "book":
        rows.append([B(BTN_BOOK, callback_data="jn:abook")])
    if n > 1:
        rows.append([B(BTN_LIST, callback_data="av:list")])
    return M(rows)


async def send_window(bot, chat, n):
    pic, title, text = W[n - 1][:3]
    kind = W[n - 1][3] if len(W[n - 1]) > 3 else ""
    body = f"🎄 <b>Віконце {n} · {n} грудня</b>\n<b>{title}</b>\n\n{text}"
    if n == 5:
        body += NOTE
    kb = kb_window(n)
    if pic:
        path = os.path.join(DIR, "images", "advent", pic + ".jpg")
        if len(body) <= 1000:
            with open(path, "rb") as f:
                await bot.send_photo(chat, f, caption=body, parse_mode="HTML", reply_markup=kb)
        else:
            with open(path, "rb") as f:
                await bot.send_photo(chat, f)
            await bot.send_message(chat, body, parse_mode="HTML", reply_markup=kb)
    else:
        await bot.send_message(chat, body, parse_mode="HTML", reply_markup=kb)
    if kind == "gift":
        fid = db.flag_get("av_pdf")
        if fid:
            m = await bot.send_document(chat, fid, caption="🎁 Здорове меню на тиждень")
        else:
            with open(PDF, "rb") as f:
                m = await bot.send_document(chat, f, filename="Здорове_меню_на_тиждень.pdf", caption="🎁 Здорове меню на тиждень")
            try:
                db.flag_set("av_pdf", m.document.file_id)
            except Exception:
                pass


async def open_(ctx, chat, uid):
    """?start=advent: опис і кнопка, або одразу приєднання."""
    __import__("crm").log_ev(uid, "advent_open")
    if joined(uid):
        n = today_n()
        if n:
            await send_window(ctx.bot, chat, min(n, 31))
        else:
            await ctx.bot.send_message(chat, JOINED, parse_mode="HTML", reply_markup=M([[app_btn()]]))
        return
    await ctx.bot.send_message(chat, INVITE, parse_mode="HTML", reply_markup=M([[B(BTN_JOIN, callback_data="av:join")]]))


async def on_cb(ctx, u, chat, data, notify_admins):
    if data == "av:join":
        new = not joined(u.id)
        db.flag_set(f"av:{u.id}", "1")
        n = today_n()
        if new:
            __import__("crm").log_ev(u.id, "advent_join")
        if n:
            for i in range(1, min(n, 31) + 1):
                db.flag_set(f"avs:{i}:{u.id}", "1")  # минулі не дублюємо в job
            await ctx.bot.send_message(chat, JOINED_LATE)
            await send_window(ctx.bot, chat, min(n, 31))
        else:
            await ctx.bot.send_message(chat, JOINED, parse_mode="HTML", reply_markup=M([[app_btn()]]))
    elif data == "av:list":
        n = min(today_n(), 31)
        if not n:
            await ctx.bot.send_message(chat, "Перше віконце відкриється 1 грудня о 9:00 😉")
            return
        rows, row = [], []
        for i in range(1, n + 1):
            row.append(B(str(i), callback_data=f"av:o:{i}"))
            if len(row) == 6:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        await ctx.bot.send_message(chat, "Оберіть віконце 👇", reply_markup=M(rows))
    elif data.startswith("av:o:"):
        i = int(data.split(":")[2])
        if 1 <= i <= min(today_n(), 31):
            await send_window(ctx.bot, chat, i)
        else:
            await ctx.bot.send_message(chat, f"Це віконце відкриється {i} грудня о 9:00 😉")
    elif data == "av:go" and u.id in C.ADMIN_IDS:
        if db.flag_get("av_sent") == "1":
            await ctx.bot.send_message(chat, "Запрошення в адвент уже розіслано ❤")
            return
        db.flag_set("av_sent", "1")  # до відправки
        await ctx.bot.send_message(chat, "Розсилаю, звіт надішлю сюди 😉")
        _BG.add(asyncio.create_task(_invite_all(ctx, notify_admins)))


async def _invite_all(ctx, notify_admins):
    crm = __import__("crm")
    ok = fail = 0
    for uid in crm.members("all"):
        if joined(uid) or db.flag_get(f"avi:{uid}"):
            continue
        db.flag_set(f"avi:{uid}", "1")
        try:
            await ctx.bot.send_message(uid, INVITE, parse_mode="HTML", reply_markup=M([[B(BTN_JOIN, callback_data="av:join")]]))
            ok += 1
        except Forbidden:
            crm.log_ev(uid, "blocked")
            fail += 1
        except Exception as e:
            log.warning("advent invite %s: %s", uid, e)
            fail += 1
        await asyncio.sleep(0.05)
    await notify_admins(ctx, f"📬 Запрошення в адвент надіслано: {ok}, не дійшло: {fail}.")


async def preview_job(ctx):
    if db.flag_get("av_prev") == "1":
        return
    db.flag_set("av_prev", "1")
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, INVITE, parse_mode="HTML", reply_markup=M([[B(BTN_JOIN, callback_data="av:join")]]))
            await ctx.bot.send_message(
                a, "👆 Так виглядатиме запрошення в адвент «Здорові свята» (31 віконце з вашого «Здорового меню на тиждень», "
                   "24.12 сам файл у подарунок, 28.12 і 31.12 бронь інтенсиву за спецціною 159 замість 350). Посилання для Instagram: "
                   "https://t.me/valentina_shvets_bot?start=advent\n\n"
                   "Розіслати запрошення всім в агенті?",
                reply_markup=M([[B("✅ Розіслати", callback_data="av:go")]]))
        except Exception as e:
            log.warning("advent prev %s: %s", a, e)


async def job(ctx):
    """Кожні 5 хв: о 9:00 1-31.12 віконце дня всім, хто в адвенті."""
    t = _now()
    if (t.year, t.month) != (2026, 12) or t.hour < HOUR or t.hour >= 21:
        return
    n = t.day
    if db.flag_get("av_day") == str(n):
        return
    db.flag_set("av_day", str(n))
    crm = __import__("crm")
    ok = 0
    for uid in members():
        if db.flag_get(f"avs:{n}:{uid}"):
            continue
        db.flag_set(f"avs:{n}:{uid}", "1")
        try:
            await send_window(ctx.bot, uid, n)
            ok += 1
        except Forbidden:
            crm.log_ev(uid, "blocked")
        except Exception as e:
            log.warning("advent day %s %s: %s", n, uid, e)
        await asyncio.sleep(0.1)
    log.info("advent day %s sent %s", n, ok)


async def cmd(update, ctx):
    if update.effective_user.id not in C.ADMIN_IDS:
        return
    t = ctx.args[0] if ctx.args else ""
    if t.isdigit() and 1 <= int(t) <= 31:  # /advent 5: подивитись віконце
        await send_window(ctx.bot, update.effective_chat.id, int(t))
        return
    await update.message.reply_text(
        f"🎄 Адвент «Здорові свята»: в адвенті {len(members())} людей, сьогодні віконце {today_n() or 'ще не почалось'}.\n"
        "Подивитись будь-яке віконце: /advent 5")


VALYA = ("🎄 <b>Ваш адвент-календар «Здорові свята» готовий!</b>\n\n"
         "31 віконце з вашого «Здорового меню на тиждень». З <b>1 по 31 грудня</b> щоранку о 9:00 агент сам надсилатиме людям віконце дня, "
         "а ще в кожного є зелений календар з кульками, де віконця відкриваються по датах.\n\n"
         "🎁 <b>24 грудня</b> файл «Здорове меню на тиждень» у подарунок\n"
         "🎄 <b>28 і 31 грудня</b> бронь інтенсиву «Здоровий кишківник» за спецціною <code>159 грн</code> (для всіх інших 350)\n\n"
         "🔗 <b>Посилання, за яким запускається адвент</b> (для Instagram, сторіс, каналу, ManyChat):\n"
         "<code>https://t.me/valentina_shvets_bot?start=advent</code>\n\n"
         "У меню агента зверху тепер кнопка <b>«🎄 АДВЕНТ-КАЛЕНДАР «ЗДОРОВІ СВЯТА»»</b>.\n\n"
         "Подивитися будь-яке віконце: <code>/advent 8</code>, скільки людей в адвенті: /advent\n\n"
         "<i>Нижче фото, як адвент виглядає зсередини, а потім запрошення, яке можна розіслати всім кнопкою «✅ Розіслати»</i> 👇")
PREV = ["1_kalendar", "2_vikontse", "3_bron159", "4_do_startu", "5_zaproshennia", "6_vikontse_v_chati", "7_podarunok"]


async def valya_job(ctx):
    """26.11 (Тетяна): адмінам один раз пояснення, посилання і фото адвенту (kv av_valya)."""
    if db.flag_get("av_valya") == "1":
        return
    db.flag_set("av_valya", "1")
    from telegram import InputMediaPhoto
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, VALYA, parse_mode="HTML", reply_markup=M([[app_btn()]]))
            files = [open(os.path.join(DIR, "images", "advent", "prev", n + ".jpg"), "rb") for n in PREV]
            try:
                await ctx.bot.send_media_group(a, [InputMediaPhoto(f) for f in files])
            finally:
                for f in files:
                    f.close()
        except Exception as e:
            log.warning("advent valya %s: %s", a, e)
