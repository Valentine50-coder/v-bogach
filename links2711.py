"""27.11.2026 (Тетяна): окремим повідомленням Валентині посилання для кодових слів Instagram (ManyChat), flag links2711."""
import logging

import config as C
import db

log = logging.getLogger("links2711")

WORDS = [("КОНСУЛЬТАЦІЯ", "konsultatsiya"), ("АНАЛІЗИ", "analizy"), ("ВІТАМІНИ", "vitaminy"), ("ДІТИ", "dity"),
         ("АДВЕНТ", "advent")]


async def job(ctx):
    if db.flag_get("links2711") == "1":
        return
    db.flag_set("links2711", "1")
    me = await ctx.bot.get_me()
    lines = "\n".join(f"<b>{w}</b>\n<code>https://t.me/{me.username}?start={s}</code>\n" for w, s in WORDS)
    text = ("🔗 <b>Посилання для кодових слів в Instagram</b>\n\n"
            "Вставте кожне в ManyChat на своє слово. Людина натискає і одразу потрапляє на потрібний продукт ❤\n\n"
            + lines +
            "\n<b>ЩИТОВИДКА</b> і <b>МЕТЕЛИК</b>: посилання додамо, щойно в агенті з'явиться курс «Ввімкни свою щитовидку».\n"
            f"<i>Для гайду про солодке, якщо захочете окреме слово:</i> <code>https://t.me/{me.username}?start=gayd</code>")
    for a in C.ADMIN_IDS:
        try:
            await ctx.bot.send_message(a, text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            log.warning("links2711 %s: %s", a, e)
