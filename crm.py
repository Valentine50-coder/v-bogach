"""Статистика і CRM для адмінів (10.11.2026).

1. log(uid, ev, extra) записує кожен крок людини в таблицю events.
2. daily_job щоранку о 9:00 за Києвом шле адмінам звіт за вчора: хто прийшов, звідки, воронка, де зупинились,
   діагностика, оплати, «гарячі» (взяли посилання на оплату, але не оплатили).
3. Кнопка «👥 CRM» (тільки адмінам): групи людей зі списками, розсилка групі, пошук людини, цифри за 7 днів і за сьогодні.

Налаштування під конкретного агента: setup(...) у bot.py (назви кроків, джерел, воронка).
"""
import html
import logging
import time
from datetime import datetime, timedelta, timezone

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from telegram.error import Forbidden

import db

log = logging.getLogger("crm")
BTN = "👥 CRM"

CFG = {
    "admins": [],
    "src": {},        # код джерела -> назва
    "labels": {},     # подія або префікс події -> зрозуміла назва кроку
    "funnel": [],     # [(назва, [події або префікси])]
    "quiz_zones": {},  # зона діагностики -> назва
    "paid_fn": None,  # uid -> True, якщо оплатив (для груп)
    "parts_fn": None,  # uid -> True, якщо платить частинами і ще не все
}


def setup(**kw):
    CFG.update(kw)


def init():
    with db.conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, ev TEXT, "
                  "extra TEXT, at INTEGER)")
        c.execute("CREATE INDEX IF NOT EXISTS events_at ON events(at)")
        c.execute("CREATE INDEX IF NOT EXISTS events_uid ON events(uid)")


def log_ev(uid, ev, extra=""):
    try:
        if uid in CFG["admins"]:
            return
        with db.conn() as c:
            c.execute("INSERT INTO events(uid, ev, extra, at) VALUES(?,?,?,?)", (uid, ev, str(extra or "")[:300], int(time.time())))
    except Exception as e:
        log.warning("crm log %s %s: %s", uid, ev, e)


# ---------- час за Києвом ----------
def _tz():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("Europe/Kyiv")
    except Exception:
        return timezone(timedelta(hours=2))


def kyiv_now():
    return datetime.now(_tz())


def day_bounds(days_ago=1):
    d = kyiv_now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)
    return int(d.timestamp()), int((d + timedelta(days=1)).timestamp()), d


# ---------- дані ----------
def label(ev):
    lb = CFG["labels"]
    if ev in lb:
        return lb[ev]
    for k, v in lb.items():
        if (k.endswith(":") and ev.startswith(k)) or (k.endswith("*") and ev.startswith(k[:-1])):
            return v
    return ev


def _match(ev, keys):
    return any(ev == k or (k.endswith(":") and ev.startswith(k)) for k in keys)


def _events(t0, t1):
    with db.conn() as c:
        return c.execute("SELECT uid, ev, extra, at FROM events WHERE at>=? AND at<? ORDER BY at", (t0, t1)).fetchall()


def _user(uid):
    try:
        return db.get_user(uid)
    except Exception:
        return None


def name(uid, link=True):
    u = _user(uid)
    n = html.escape((u["name"] if u and u["name"] else "") or f"ID {uid}")
    nick = f" @{u['username']}" if u and u["username"] else ""
    return (f'<a href="tg://user?id={uid}">{n}</a>' if link else n) + html.escape(nick)


def source(uid):
    with db.conn() as c:
        r = c.execute("SELECT extra FROM events WHERE uid=? AND ev='start' ORDER BY at LIMIT 1", (uid,)).fetchone()
    s = r["extra"] if r else ""
    if not s:
        u = _user(uid)
        try:
            s = (u["src"] if u and "src" in u.keys() else "") or ""
        except Exception:
            s = ""
    return s or "start"


def src_name(s):
    return CFG["src"].get(s, s or "напряму")


def report(t0, t1, title):
    ev = _events(t0, t1)
    with db.conn() as c:
        new = [r["id"] for r in c.execute("SELECT id FROM users WHERE joined>=? AND joined<?", (t0, t1))
               if r["id"] not in CFG["admins"]]
        total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    L = [f"📊 <b>{title}</b>", "", f"Нових людей: <b>{len(new)}</b> (усього в агенті {total})"]
    if new:
        srcs = {}
        for uid in new:
            s = source(uid)
            srcs[s] = srcs.get(s, 0) + 1
        L.append("<b>Звідки:</b> " + ", ".join(f"{src_name(s)} {n}" for s, n in sorted(srcs.items(), key=lambda x: -x[1])))
    active = sorted({e["uid"] for e in ev})
    L.append(f"Активних за цей час: <b>{len(active)}</b>")

    if CFG["funnel"]:
        steps = []
        for title_s, keys in CFG["funnel"]:
            steps.append(f"{title_s} {len({e['uid'] for e in ev if _match(e['ev'], keys)})}")
        L += ["", "<b>Воронка:</b>", " → ".join(steps)]

    paid_ev = [e for e in ev if e["ev"] == "paid"]
    paid_uids = {e["uid"] for e in paid_ev}
    last = {}
    for e in ev:
        if e["ev"] not in ("paid", "blocked", "unblocked", "msg"):
            last[e["uid"]] = e["ev"]
    stops = {}
    for uid, e in last.items():
        if uid not in paid_uids:
            lb = label(e)
            stops[lb] = stops.get(lb, 0) + 1
    if stops:
        L += ["", "<b>Де зупинились</b> (останній крок тих, хто не оплатив):"]
        L += [f"• {lb}: {n}" for lb, n in sorted(stops.items(), key=lambda x: -x[1])[:8]]

    qgo = {e["uid"] for e in ev if e["ev"] == "quiz_go"}
    qdone = [e for e in ev if e["ev"] == "quiz_done"]
    if qgo or qdone:
        zones = {}
        for e in qdone:
            for z in (e["extra"] or "").split(","):
                if z:
                    zones[z] = zones.get(z, 0) + 1
        L += ["", f"<b>Діагностика:</b> почали {len(qgo)}, завершили {len({e['uid'] for e in qdone})}"]
        if zones:
            L.append("Результати: " + ", ".join(f"{CFG['quiz_zones'].get(z, z)} {n}" for z, n in sorted(zones.items(), key=lambda x: -x[1])))
        qlast = {}
        for e in ev:
            if e["ev"].startswith("quiz_q"):
                qlast[e["uid"]] = e["ev"]
        drop = {}
        for uid in qgo - {e["uid"] for e in qdone}:
            k = qlast.get(uid, "")  # quiz_q<i>: відповіла на питання i (з 0), тож кинула на i+2
            n = int(k[6:]) + 2 if k[6:].isdigit() else 1
            drop[n] = drop.get(n, 0) + 1
        if drop:
            L.append("Кинули на питанні: " + ", ".join(f"№{n}: {c}" for n, c in sorted(drop.items())))

    total_sum = 0
    lines = []
    for e in paid_ev:
        amount, kind = ((e["extra"] or "0|").split("|") + [""])[:2]
        try:
            total_sum += float(amount)
        except ValueError:
            pass
        lines.append(f"• {name(e['uid'])}: {amount} грн{(' · ' + kind) if kind else ''}")
    L += ["", f"💳 <b>Оплати:</b> {len(paid_ev)} на {total_sum:g} грн"] + lines

    hot = sorted({e["uid"] for e in ev if e["ev"] == "invoice"} - _ever_paid())
    if hot:
        L += ["", "🔥 <b>Гарячі:</b> взяли посилання на оплату, але не оплатили"] + [f"• {name(u)}" for u in hot[:20]]
    asks = len([e for e in ev if e["ev"] in ("question", "msg")])
    blocked = len({e["uid"] for e in ev if e["ev"] == "blocked"})
    L += ["", f"Питань і повідомлень: {asks} · Заблокували агента: {blocked}"]
    return "\n".join(L)


def _ever_paid():
    with db.conn() as c:
        return {r[0] for r in c.execute("SELECT DISTINCT uid FROM events WHERE ev='paid'")} | (
            {r[0] for r in c.execute("SELECT DISTINCT uid FROM payments WHERE status='Approved'")} if _has("payments") else set())


def _has(table):
    with db.conn() as c:
        return bool(c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone())


async def _send_admins(bot, text, kb=None):
    for a in CFG["admins"]:
        try:
            await bot.send_message(a, text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        except Exception as e:
            log.warning("crm admin %s: %s", a, e)


async def daily_job(ctx):
    now = kyiv_now()
    if now.hour < 9:
        return
    key = now.strftime("%Y-%m-%d")
    if db.flag_get("crm_daily") == key:
        return
    db.flag_set("crm_daily", key)
    t0, t1, d = day_bounds(1)
    try:
        await _send_admins(ctx.bot, report(t0, t1, f"Звіт за {d.strftime('%d.%m')}"), M([[B(BTN, callback_data="crm:menu")]]))
    except Exception as e:
        log.exception("crm daily: %s", e)


# ---------- групи CRM ----------
GROUPS = [
    ("new7", "🆕 Прийшли за 7 днів"),
    ("quiz", "🧪 Пройшли діагностику"),
    ("price", "👀 Дійшли до оплати, не купили"),
    ("hot", "🔥 Взяли посилання на оплату, не оплатили"),
    ("parts", "🧾 Платять частинами"),
    ("paid", "💎 Оплатили"),
    ("asked", "❓ Ставили питання"),
    ("nopay", "😴 Усі, хто ще не купив"),
    ("blocked", "🚫 Заблокували агента"),
    ("all", "👥 Усі"),
]
GNAMES = dict(GROUPS)


def _blocked():
    with db.conn() as c:
        rows = c.execute("SELECT uid, ev FROM events WHERE ev IN ('blocked','unblocked') ORDER BY at").fetchall()
    st = {}
    for r in rows:
        st[r["uid"]] = r["ev"] == "blocked"
    return {u for u, b in st.items() if b}


def _with(evs):
    with db.conn() as c:
        q = " OR ".join("ev=?" if not k.endswith(":") else "ev LIKE ?" for k in evs)
        args = [k if not k.endswith(":") else k + "%" for k in evs]
        return {r[0] for r in c.execute(f"SELECT DISTINCT uid FROM events WHERE {q}", args)}


def members(g):
    with db.conn() as c:
        allu = [r["id"] for r in c.execute("SELECT id FROM users ORDER BY joined DESC") if r["id"] not in CFG["admins"]]
        week = int(time.time()) - 7 * 86400
        new7 = {r["id"] for r in c.execute("SELECT id FROM users WHERE joined>=?", (week,))}
    paid = _ever_paid() | {u for u in allu if CFG["paid_fn"] and CFG["paid_fn"](u)}
    blocked = _blocked()
    if g == "all":
        s = set(allu)
    elif g == "new7":
        s = new7
    elif g == "quiz":
        s = _with(["quiz_done"])
    elif g == "price":
        s = _with(["pay_choice", "invoice", "price"]) - paid
    elif g == "hot":
        s = _with(["invoice"]) - paid
    elif g == "parts":
        s = {u for u in allu if CFG["parts_fn"] and CFG["parts_fn"](u)}
    elif g == "paid":
        s = paid
    elif g == "asked":
        s = _with(["question", "msg"])
    elif g == "nopay":
        s = set(allu) - paid
    elif g == "blocked":
        return [u for u in allu if u in blocked]
    else:
        s = set()
    return [u for u in allu if u in s and u not in blocked]


def kb_menu():
    rows = [[B(f"{t} ({len(members(g))})", callback_data=f"crm:g:{g}")] for g, t in GROUPS]
    rows += [[B("🔎 Знайти людину", callback_data="crm:find")],
             [B("📅 Сьогодні", callback_data="crm:today"), B("📊 7 днів", callback_data="crm:week")]]
    return M(rows)


async def show_menu(bot, chat):
    with db.conn() as c:
        total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    await bot.send_message(chat, f"👥 <b>CRM</b>\n\nУсього людей в агенті: <b>{total}</b>\n"
                                 "Натисніть групу, щоб побачити людей і написати їм 👇", parse_mode="HTML", reply_markup=kb_menu())


def card(uid):
    u = _user(uid)
    if not u:
        return "Не знайшла цю людину в агенті."
    joined = datetime.fromtimestamp(u["joined"] or 0, _tz()).strftime("%d.%m.%Y %H:%M") if u["joined"] else "-"
    L = [f"👤 {name(uid)} (ID {uid})", f"Дата приходу: {joined}, звідки: {src_name(source(uid))}"]
    if uid in _ever_paid() or (CFG["paid_fn"] and CFG["paid_fn"](uid)):
        L.append("💎 Оплатили")
    if uid in _blocked():
        L.append("🚫 Заблокували агента")
    with db.conn() as c:
        rows = c.execute("SELECT ev, extra, at FROM events WHERE uid=? ORDER BY at DESC LIMIT 20", (uid,)).fetchall()
    if rows:
        L += ["", "<b>Останні кроки:</b>"]
        for r in reversed(rows):
            t = datetime.fromtimestamp(r["at"], _tz()).strftime("%d.%m %H:%M")
            ex = f" ({html.escape(r['extra'][:60])})" if r["extra"] and r["ev"] not in ("start",) else ""
            L.append(f"{t} {html.escape(label(r['ev']))}{ex}")
    return "\n".join(L)


def find(q):
    q = q.strip().lstrip("@")
    with db.conn() as c:
        if q.isdigit():
            r = c.execute("SELECT id FROM users WHERE id=?", (int(q),)).fetchone()
        else:
            r = c.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (q,)).fetchone()
            r = r or c.execute("SELECT id FROM users WHERE lower(name) LIKE lower(?)", (f"%{q}%",)).fetchone()
    return r[0] if r else None


async def on_cb(q, ctx, data):
    """data: crm:menu | crm:g:<група> | crm:send:<група> | crm:go | crm:cancel | crm:find | crm:today | crm:week"""
    chat = q.message.chat_id
    parts = data.split(":")
    if data == "crm:menu":
        await show_menu(ctx.bot, chat)
    elif parts[1] == "g":
        g = parts[2]
        ppl = members(g)
        L = [f"<b>{GNAMES.get(g, g)}</b>: {len(ppl)}", ""] + [f"{i}. {name(u)}" for i, u in enumerate(ppl[:40], 1)]
        if len(ppl) > 40:
            L.append(f"і ще {len(ppl) - 40}")
        kb = [[B("✉️ Написати цій групі", callback_data=f"crm:send:{g}")]] if ppl and g != "blocked" else []
        await ctx.bot.send_message(chat, "\n".join(L), parse_mode="HTML",
                                   reply_markup=M(kb + [[B("↩️ CRM", callback_data="crm:menu")]]))
    elif parts[1] == "send":
        ctx.user_data["crm_wait"] = ("send", parts[2])
        await ctx.bot.send_message(chat, f"Напишіть повідомлення для групи «{GNAMES.get(parts[2], parts[2])}». "
                                         "Я спершу покажу, як воно виглядатиме, і спитаю підтвердження.")
    elif data == "crm:go":
        g, text = ctx.user_data.pop("crm_send", (None, None))
        if not text:
            await ctx.bot.send_message(chat, "Немає тексту для розсилки, почніть знову з CRM.")
            return
        ok = bad = 0
        for u in members(g):
            try:
                await ctx.bot.send_message(u, text)
                ok += 1
            except Forbidden:
                log_ev(u, "blocked")
                bad += 1
            except Exception as e:
                log.warning("crm send %s: %s", u, e)
                bad += 1
            await __import__("asyncio").sleep(0.05)
        await ctx.bot.send_message(chat, f"✅ Надіслано: {ok}. Не дійшло: {bad}.")
    elif data == "crm:cancel":
        ctx.user_data.pop("crm_send", None)
        await ctx.bot.send_message(chat, "Скасовано.", reply_markup=M([[B("↩️ CRM", callback_data="crm:menu")]]))
    elif data == "crm:find":
        ctx.user_data["crm_wait"] = ("find", "")
        await ctx.bot.send_message(chat, "Напишіть нік (@nick), ID або ім'я людини.")
    elif data in ("crm:today", "crm:week"):
        if data == "crm:today":
            t0, t1, _ = day_bounds(0)
            title = "Сьогодні до " + kyiv_now().strftime("%H:%M")
        else:
            t0, t1 = day_bounds(6)[0], day_bounds(0)[1]
            title = "Останні 7 днів"
        await ctx.bot.send_message(chat, report(t0, t1, title), parse_mode="HTML", disable_web_page_preview=True,
                                   reply_markup=M([[B("↩️ CRM", callback_data="crm:menu")]]))


async def on_admin_text(update, ctx):
    """True, якщо текст адміна оброблено тут (розсилка або пошук)."""
    w = ctx.user_data.pop("crm_wait", None)
    txt = update.message.text or ""
    if txt == BTN:
        await show_menu(ctx.bot, update.effective_chat.id)
        return True
    if not w:
        return False
    if w[0] == "find":
        uid = find(txt)
        await update.message.reply_text(card(uid) if uid else "Не знайшла. Спробуйте нік без помилок або ID.",
                                        parse_mode="HTML", reply_markup=M([[B("↩️ CRM", callback_data="crm:menu")]]))
        return True
    g = w[1]
    n = len(members(g))
    ctx.user_data["crm_send"] = (g, txt)
    await update.message.reply_text("Так побачать люди 👇")
    await update.message.reply_text(txt)
    await update.message.reply_text(f"Надіслати групі «{GNAMES.get(g, g)}»? Людей у групі: {n}", reply_markup=M([
        [B(f"✅ Надіслати {n}", callback_data="crm:go")], [B("Скасувати", callback_data="crm:cancel")]]))
    return True


async def on_private_member(update, ctx):
    """Людина заблокувала або розблокувала агента."""
    m = update.my_chat_member
    if not m or m.chat.type != "private":
        return
    st = m.new_chat_member.status
    if st in ("kicked", "banned"):
        log_ev(m.from_user.id, "blocked")
    elif st == "member" and m.old_chat_member.status in ("kicked", "banned"):
        log_ev(m.from_user.id, "unblocked")
