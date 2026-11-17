"""16.11.2026: відео Валентини «Чому бунтує кишківник» і «Відгуки моїх клієнтів».

Відео: media/buntuye.mp4 (17.11 замінено на нову версію від Валентини, стара на YouTube l-5a59E9HHk вийшла англійською; кеш vid_fid2). Вхід: ?start=bunt (кодове слово БУНТ у ManyChat),
кнопка в нижньому меню і в головному меню. Хто не оплатив інтенсив, через 2 год отримує одне нагадування (9:00-21:00 Київ).
Відгуки: images/vidguky/v1..v6.jpg одним альбомом + текст з приміткою про ліки, кнопки інтенсиву.
file_id відео і фото кешуються у kv (vid_fid, rev_fids). Нагадування: таблиця vid_fu (uid, at, sent).
"""
import json
import logging
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M, InputMediaPhoto

import config as C
import db

log = logging.getLogger("vidrev")
HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(HERE, "media", "buntuye.mp4")
REVS = [os.path.join(HERE, "images", "vidguky", f"v{i}.jpg") for i in range(1, 7)]
YOUTUBE = "https://valentine50-coder.github.io/v-bogach/#video"  # 17.11: YouTube-версія вийшла англійською, запасне посилання на сайт
FU_SEC = 2 * 3600

BTN_VIDEO = "🎥 Відео: чому бунтує кишківник"
BTN_REVS = "💬 Відгуки моїх клієнтів"
BTN_INT = "Детальніше про інтенсив"

VIDEO_CAP = ("🎥 <b>Чому бунтує кишківник</b>\n\n"
             "У цьому відео я розповідаю про основні причини збоїв у кишківнику і покроковий план, "
             "як навести лад у нашому «другому мозку».\n\n"
             "Подивіться до кінця, там я запрошую вас на інтенсив ❤")
REV_TEXT = ("💬 <b>Відгуки моїх клієнтів</b>\n\n"
            "Це справжні повідомлення людей, з якими ми відновлювали кишківник: менше здуття, регулярний стілець, "
            "чистіша шкіра, кращі аналізи.\n\n"
            "<i>Результати в кожного свої. Тут можуть бути й ваші 😉</i>")
FOLLOW = ("Ви вже подивились відео «Чому бунтує кишківник»? ❤\n\n"
          "На інтенсиві ми пройдемо цей шлях разом, крок за кроком 🎯\n\n"
          "Кількість місць обмежена ‼️")


def init():
    with db.conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS vid_fu(uid INTEGER PRIMARY KEY, at INTEGER, sent INTEGER DEFAULT 0)")


def kb_video():
    return M([[B(BTN_INT, callback_data="int")], [B(BTN_REVS, callback_data="revs")]])


def kb_revs():
    return M([[B(BTN_INT, callback_data="int")], [B("💳 Оплатити участь", callback_data="pay")]])


async def send_video(ctx, chat_id, uid=None):
    fid = db.flag_get("vid_fid2")
    try:
        if fid:
            m = await ctx.bot.send_video(chat_id, fid, caption=VIDEO_CAP, parse_mode="HTML", reply_markup=kb_video())
        else:
            with open(VIDEO, "rb") as f:
                m = await ctx.bot.send_video(chat_id, f, caption=VIDEO_CAP, parse_mode="HTML", reply_markup=kb_video(),
                                             supports_streaming=True, width=1280, height=720,
                                             read_timeout=180, write_timeout=180)
            if m and m.video:
                db.flag_set("vid_fid2", m.video.file_id)
    except Exception as e:
        log.warning("video %s: %s", chat_id, e)
        await ctx.bot.send_message(chat_id, VIDEO_CAP + f"\n\n{YOUTUBE}", parse_mode="HTML", reply_markup=kb_video())
    if uid and uid not in C.ADMIN_IDS:
        with db.conn() as c:
            c.execute("INSERT OR IGNORE INTO vid_fu(uid, at) VALUES(?,?)", (uid, int(time.time())))


async def send_reviews(ctx, chat_id):
    try:
        fids = json.loads(db.flag_get("rev_fids") or "[]")
    except ValueError:
        fids = []
    try:
        if len(fids) == len(REVS):
            await ctx.bot.send_media_group(chat_id, [InputMediaPhoto(f) for f in fids])
        else:
            files = [open(p, "rb") for p in REVS]
            try:
                ms = await ctx.bot.send_media_group(chat_id, [InputMediaPhoto(f) for f in files],
                                                    read_timeout=120, write_timeout=120)
            finally:
                for f in files:
                    f.close()
            if ms and len(ms) == len(REVS):
                db.flag_set("rev_fids", json.dumps([m.photo[-1].file_id for m in ms]))
    except Exception as e:
        log.warning("reviews %s: %s", chat_id, e)
    await ctx.bot.send_message(chat_id, REV_TEXT, parse_mode="HTML", reply_markup=kb_revs())


async def followup_job(ctx):
    h = datetime.now(ZoneInfo("Europe/Kyiv")).hour
    if not 9 <= h < 21:
        return
    now = int(time.time())
    with db.conn() as c:
        rows = c.execute("SELECT f.uid FROM vid_fu f LEFT JOIN users u ON u.id = f.uid "
                         "WHERE f.sent = 0 AND f.at <= ? AND COALESCE(u.int_paid, 0) = 0", (now - FU_SEC,)).fetchall()
        c.execute("UPDATE vid_fu SET sent = 1 WHERE sent = 0 AND at <= ?", (now - FU_SEC,))  # до відправки
    for r in rows:
        db.flag_set(f"dz_at:{r[0]}", str(now))  # 16.11: щоб дожим інтенсиву не прийшов одразу слідом (GAP 2 год)
        try:
            await ctx.bot.send_message(r[0], FOLLOW, parse_mode="HTML",
                                       reply_markup=M([[B(BTN_INT, callback_data="int")], [B(BTN_REVS, callback_data="revs")]]))
        except Exception as e:
            log.warning("video fu %s: %s", r[0], e)
