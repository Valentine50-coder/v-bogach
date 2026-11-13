"""13.11.2026: дожими інтенсиву для всіх, хто ще не оплатив (тексти в dozhim_texts.py).

Графік від моменту, коли людина зайшла (для тих, хто був в агенті раніше, від запуску дожимів, kv dz_launch):
день 1: +1 год, +4 год, 19:00; день 2: 11:00, 18:00; день 3: 13:00; далі раз на 2 дні о 12:00 (тексти MID по черзі);
останній день запису (день перед стартом): 10:00, 15:00, 20:00. Те, що випадає на останній день чи пізніше, пропускаємо.
Тільки 9:00-21:00 за Києвом, не адмінам, не тим, хто заблокував агента, зупиняються після оплати (кнопки «Не цікаво» немає).
Між дожимами щонайменше 2 години; що не встигло, йде по черзі; в останній день одразу актуальне. Прогрес: kv dz:<uid> (до відправки).
"""
import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from telegram.error import Forbidden

import config as C
import db
import dozhim_texts as D

log = logging.getLogger("dozhim")
TZ = ZoneInfo(getattr(C, "TZ", "Europe/Kyiv"))
GAP = 2 * 3600


def _at(d, h):
    return datetime(d.year, d.month, d.day, h, 0, tzinfo=TZ)


def plan(start_ts):
    """[(час, ключ тексту)] для людини, яка зайшла в start_ts."""
    s = datetime.fromtimestamp(start_ts, TZ)
    d0 = s.date()
    last = D.START - timedelta(days=1)
    steps = [(s + timedelta(hours=1), "d1a"), (s + timedelta(hours=4), "d1b"), (_at(d0, 19), "d1c"),
             (_at(d0 + timedelta(days=1), 11), "d2a"), (_at(d0 + timedelta(days=1), 18), "d2b"),
             (_at(d0 + timedelta(days=2), 13), "d3a")]
    d, k = d0 + timedelta(days=4), 0
    while d < last and D.MID:
        steps.append((_at(d, 12), f"mid{k % len(D.MID)}"))
        d += timedelta(days=2)
        k += 1
    steps = sorted([x for x in steps if x[0].date() < last and x[0] >= s], key=lambda x: x[0])
    steps += [x for x in ((_at(last, 10), "l1"), (_at(last, 15), "l2"), (_at(last, 20), "l3")) if x[0] >= s]
    return steps


def text_of(key):
    if key.startswith("mid"):
        return D.MID[int(key[3:])]
    return D.TEXTS[key]


def _blocked():
    try:
        with db.conn() as c:
            rows = c.execute("SELECT uid, ev FROM events WHERE ev IN ('blocked','unblocked') ORDER BY at").fetchall()
    except Exception:
        return set()
    st = {}
    for r in rows:
        st[r["uid"]] = r["ev"] == "blocked"
    return {u for u, b in st.items() if b}


def _kb():
    return M([[B(D.BTN_MORE, callback_data="int")], [B(D.BTN_ASK, callback_data="ask")]])


async def job(ctx):
    now = datetime.now(TZ)
    if not (9 <= now.hour < 21) or now.date() >= D.START:
        return
    launch = int(db.flag_get("dz_launch") or 0)
    if not launch:
        launch = int(time.time())
        db.flag_set("dz_launch", str(launch))
    blocked = _blocked()
    with db.conn() as c:
        users = c.execute("SELECT id, joined, int_paid, course_paid FROM users").fetchall()
    for u in users:
        uid = u["id"]
        if u["int_paid"] or u["course_paid"] or uid in C.ADMIN_IDS or uid in blocked:
            continue
        start = max(int(u["joined"] or 0), launch)
        steps = plan(start)
        done = int(db.flag_get(f"dz:{uid}") or 0)
        due = [i for i, (t, _) in enumerate(steps) if t <= now and i >= done]
        if not due:
            continue
        if time.time() - int(db.flag_get(f"dz_at:{uid}") or 0) < GAP:
            continue  # між дожимами щонайменше 2 години (наприклад, після нічної тиші)
        last_day = [i for i in due if steps[i][1].startswith("l")]
        i = last_day[-1] if last_day else due[0]  # в останній день одразу актуальне, інакше по черзі
        db.flag_set(f"dz:{uid}", str(i + 1))  # до відправки
        db.flag_set(f"dz_at:{uid}", str(int(time.time())))
        try:
            await ctx.bot.send_message(uid, text_of(steps[i][1]), parse_mode="HTML", reply_markup=_kb(),
                                       disable_web_page_preview=True)
            try:
                import crm
                crm.log_ev(uid, "dozhim", steps[i][1])
            except Exception:
                pass
        except Forbidden:
            try:
                import crm
                crm.log_ev(uid, "blocked")
            except Exception:
                pass
        except Exception as e:
            log.warning("dozhim %s: %s", uid, e)
