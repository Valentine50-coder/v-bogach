"""26.11.2026 (Тетяна): Валентині два ролики файлами, щоб вона скачала:
1) «Пробіотики, щоб зміцнити ваш кишківник» (справжні фото продуктів як у її референсі, кишківник у центрі, баночки погойдуються, 9:16, 6 с);
2) мультик «Що у вас у кишківнику, те й у вашій голові» (3 сцени, озвучка українською, слово ЖИВІТ).
Адмінам один раз (flag probio_2611b, ставиться до відправки)."""
import logging
import os

import config as C
import db

log = logging.getLogger("probio2611")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
FILES = [
    ("probiotyky.mp4", "Probiotyky_kyshkivnyk.mp4",
     "🎬 <b>Ролик «Пробіотики, щоб зміцнити ваш кишківник»</b>\n\n"
     "Як ви просили: <b>ті самі продукти на справжніх фото</b>, просто «кефір», а по центру кишківник. "
     "Баночки м'яко погойдуються, ролик зациклений, 9:16 для рілс і сторіс. <i>Збережіть файл нижче</i> ❤"),
    ("multyk_zhyvit.mp4", "Multyk_zhyvit.mp4",
     "🎬 <b>Мультик «Що у вас у кишківнику, те й у вашій голові»</b>\n\n"
     "Три сцени: хаос у животі, втомлений чоловік з «туманом» у голові і він же легкий та усміхнений. "
     "Озвучка українською, наприкінці заклик написати в коментарях <b>ЖИВІТ</b>. <i>Збережіть файл нижче</i> ❤"),
]


async def job(ctx):
    if db.flag_get("probio_2611b") == "1":
        return
    db.flag_set("probio_2611b", "1")
    for a in C.ADMIN_IDS:
        for src, name, text in FILES:
            try:
                await ctx.bot.send_message(a, text, parse_mode="HTML")
                with open(os.path.join(D, src), "rb") as f:
                    await ctx.bot.send_document(a, f, filename=name, read_timeout=180, write_timeout=180)
            except Exception as e:
                log.warning("probio %s %s: %s", a, src, e)
