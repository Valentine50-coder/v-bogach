"""14.11.2026: готові каруселі для Instagram Валентини (images/posts/k1..k5_1..5.jpg + опис).

Щодня о 9:00 за Києвом агент надсилає адмінам одну карусель: слайди альбомом і опис окремим повідомленням,
щоб Валентина скачала і виклала сама. Кодові слова пишуть У КОМЕНТАРЯХ: ЖИВІТ (тест), КИШКІВНИК (інтенсив).
intro_job: одразу пояснення і перша карусель (kv ip_intro), далі job кожні 5 хв, вікно 9:00-15:00 (kv ip:<key>).
Слайди збирає Claude (scratchpad val/build.py), тут тільки готові картинки.
"""
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import InputMediaPhoto

import config as C
import db

log = logging.getLogger("instaposts")
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "posts")
TZ = ZoneInfo("Europe/Kyiv")

POSTS = [
    ("k1", None, "«Їх називають шкідливими, а кишківник їх любить» (слово КИШКІВНИК)",
     "Квашена капуста, квасоля, картопля, рис і навіть шоколад: їх часто прибирають з раціону, а кишківнику вони потрібні ❤ "
     "Гортайте, щоб дізнатися, як їсти їх правильно.\n\n"
     "Протокол харчування і меню розбираємо на моєму інтенсиві «Здоровий кишківник», старт 24 листопада.\n\n"
     "Напишіть у коментарях КИШКІВНИК, і я надішлю вам усе про інтенсив."),
    ("k2", "2026-11-15 09:00", "«Живіт здувається до вечора?» (слово ЖИВІТ)",
     "Здуття не завжди пов'язане з тим, що ви з'їли. Іноді причина в тому, як ви їсте, у стресі чи в мікробіомі. "
     "Збережіть собі ці 5 причин 😉\n\n"
     "А щоб зрозуміти, що саме з вашим кишківником, пройдіть мою діагностику з 10 питань.\n\n"
     "Напишіть у коментарях ЖИВІТ, і я надішлю тест."),
    ("k3", "2026-11-16 09:00", "«Міфи про кишківник, у які ви досі вірите» (слово КИШКІВНИК)",
     "Пробіотики для всіх, виключення цілих груп продуктів, «корисна їжа діє одразу». Через ці міфи можна роками ходити по колу ❤\n\n"
     "Як обрати пре- і пробіотики саме для себе, розповім на інтенсиві «Здоровий кишківник».\n\n"
     "Напишіть у коментарях КИШКІВНИК."),
    ("k4", "2026-11-17 09:00", "«Кишківник говорить через шкіру» (слово ЖИВІТ)",
     "Висипання, тьмяний колір обличчя, втома навіть після сну. Іноді шкіра підказує, що варто звернути увагу на кишківник. "
     "Один сигнал ще не діагноз, але кілька разом варто перевірити 😉\n\n"
     "Напишіть у коментарях ЖИВІТ, і я надішлю вам тест."),
    ("k5", "2026-11-18 09:00", "«Закрепи: що їсти, а що обмежити» (слово КИШКІВНИК)",
     "Вода, клітковина, ківі та чорнослив, рух щодня. Прості кроки, з яких я раджу почати ❤\n\n"
     "А 10 основних причин закрепів і що з ними робити розбираємо в окремій темі інтенсиву «Здоровий кишківник».\n\n"
     "Напишіть у коментарях КИШКІВНИК, і я надішлю подробиці."),
]

INTRO = ("📸 <b>Готові каруселі для Instagram</b>\n\n"
         "Щодня о <b>9:00</b> сюди приходитиме одна готова карусель: 5 слайдів і опис.\n"
         "Кодові слова люди пишуть <b>у коментарях під постом</b>:\n"
         "• <b>ЖИВІТ</b>: діагностика (тест);\n"
         "• <b>КИШКІВНИК</b>: інформація про інтенсив.\n\n"
         "Що робити: збережіть слайди (натисніть на фото, «Зберегти»), скопіюйте опис і викладіть каруселлю 😉\n\n"
         "Перша карусель уже нижче 👇")


async def send_post(bot, chat_id, key, title, caption):
    files = [os.path.join(DIR, f"{key}_{i}.jpg") for i in range(1, 6)]
    files = [f for f in files if os.path.exists(f)]
    if not files:
        return
    hs = [open(f, "rb") for f in files]
    try:
        await bot.send_media_group(chat_id, [InputMediaPhoto(h) for h in hs])
    finally:
        for h in hs:
            h.close()
    await bot.send_message(chat_id, f"📌 Карусель на сьогодні: {title}\n\nОпис 👇 (натисніть і скопіюйте)")
    await bot.send_message(chat_id, caption)


async def _to_admins(bot, key, title, caption):
    for a in C.ADMIN_IDS:
        try:
            await send_post(bot, a, key, title, caption)
        except Exception as e:
            log.warning("instapost %s %s: %s", key, a, e)


async def intro_job(context):
    if db.flag_get("ip_intro") == "1":
        return
    db.flag_set("ip_intro", "1")
    key, _, title, cap = POSTS[0]
    db.flag_set(f"ip:{key}", "1")
    for a in C.ADMIN_IDS:
        try:
            await context.bot.send_message(a, INTRO, parse_mode="HTML")
        except Exception as e:
            log.warning("instapost intro %s: %s", a, e)
    await _to_admins(context.bot, key, title, cap)


async def job(context):
    if db.flag_get("ip_intro") != "1":
        return
    now = datetime.now(TZ)
    for key, at, title, cap in POSTS:
        if not at:
            continue
        t = datetime.strptime(at, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        if t <= now < t + timedelta(hours=6) and db.flag_get(f"ip:{key}") != "1":
            db.flag_set(f"ip:{key}", "1")
            await _to_admins(context.bot, key, title, cap)
