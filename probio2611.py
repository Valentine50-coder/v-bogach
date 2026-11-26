"""26.11.2026 (Тетяна): Валентині анімований ролик «Пробіотики, щоб зміцнити ваш кишківник» (баночки погойдуються, кишківник
у центрі, 9:16, 6 с) файлом, щоб вона скачала. Адмінам один раз (flag probio_2611)."""
import logging
import os

import config as C
import db

log = logging.getLogger("probio2611")
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "probiotyky.mp4")
TEXT = ("🎬 <b>Ролик «Пробіотики, щоб зміцнити ваш кишківник»</b>\n\n"
        "Як ви просили: ті самі продукти, просто «кефір», а по центру кишківник. Баночки м'яко погойдуються, "
        "ролик зациклений, 9:16 для рілс і сторіс. Збережіть файл нижче ❤")


async def job(ctx):
    if db.flag_get("probio_2611") == "1":
        return
    db.flag_set("probio_2611", "1")
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, TEXT, parse_mode="HTML")
            with open(F, "rb") as f:
                await ctx.bot.send_document(a, f, filename="Probiotyky_kyshkivnyk.mp4")
        except Exception as e:
            log.warning("probio %s: %s", a, e)
