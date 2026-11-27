"""24.11.2026: кнопка старту «Знижки на аналізи» = ланцюжок SendPulse Валентини «Знижки» (тексти дослівно).

Перше повідомлення з трьома кнопками: Сінево (промокод і інструкція), Діла (15%, номер і QR), генетичні тести (humess, SHVETS 5%).
Картинки необов'язкові: якщо Тетяна надішле файли, покласти в images/znyzhky/ (synevo.jpg, dila_qr.jpg, dnk_pakety.jpg),
агент сам почне їх показувати. Без файлу йде лише текст.
"""
import asyncio
import os

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import crm

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "znyzhky")
SYNEVO_URL = "https://www.synevo.ua/"
DNK_URL = "https://www.humess.com/"

MENU = "<b>Аналізи можна робити дешевше, ніж ви думаєте</b>"
SYN_1 = ("Друзі, увага❗\nМаємо промокод для знижок на аналізи в Сінево❗\n\n"
         "Даю цю можливість відсьогодні не лише моїм клієнтам, а й усім підписникам🙌")
SYN_2 = ("<b>ІНСТРУКЦІЯ ЩОДО ВИКОРИСТАННЯ ПРОМОКОДУ ДЛЯ ЗНИЖОК У СІНЕВО:</b>\n\n"
         "1️⃣ Переходимо на сайт Сінево\n<b>sinevo.ua</b>\n"
         "2️⃣  Реєструємось або авторизуємось в особистому кабінеті\n"
         "3️⃣  Знаходимо необхідні аналізи і додаємо їх у кошик.\n"
         "4️⃣  Вводимо і застосовуємо промокод на сторінці кошика:\n<b><code>6658-0026-5600</code></b>\n"
         "5️⃣ Підтверджуємо оформлення замовлення та вибираємо профіль того, хто саме буде здавати аналізи\n"
         "6️⃣Обираємо спосіб оплати (онлайн чи на пункті)\n"
         " 7️⃣Отримуємо номер успішно оформленого замовлення")
DILA = ("<b>Друзі, всі, хто в мене в Україні, є хороша новина: нам з вами дали фіксовану знижку 15% на аналізи в "
        "лабораторіях \"Діла\" по свій Україні ‼️\n"
        "Для отримання знижки 15%, ви в лабораторії показуєте оцей  QR-код 👇\n"
        " Або можете вказати оцей 6-значний номер <code>924755</code></b>")
DNK_1 = "На цьому сайті - детальна інформація про різні пакети, що саме можна дослідити і що це дає 👇"
DNK_2 = "А це вартість різних пакетів 👆\n\nПроте нам із вами дали знижку 5% за промокодом <b><code>SHVETS</code> ❗</b>"


def _img(name):
    p = os.path.join(DIR, name)
    return p if os.path.exists(p) else None


def kb_menu():
    return M([[B("Промокод в СІНЕВО", callback_data="zn:syn")],
              [B("Промокод в ДІЛА", callback_data="zn:dila")],
              [B("Генетичні тести", callback_data="zn:dnk")],
              [B("💚 Мої послуги", callback_data="menu")]])


async def _send(ctx, chat, text, photo=None, kb=None):
    p = _img(photo) if photo else None
    if p:
        with open(p, "rb") as f:
            await ctx.bot.send_photo(chat, f, caption=text, parse_mode="HTML", reply_markup=kb)
    else:
        await ctx.bot.send_message(chat, text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def show(ctx, chat, uid):
    crm.log_ev(uid, "discounts")
    await ctx.bot.send_message(chat, MENU, parse_mode="HTML", reply_markup=kb_menu())


async def on_cb(ctx, chat, uid, data):
    crm.log_ev(uid, data)
    if data == "zn:syn":
        await _send(ctx, chat, SYN_1, "synevo.jpg")
        await _send(ctx, chat, SYN_2, kb=M([[B("перейти на сайт", url=SYNEVO_URL)], [B("💚 Мої послуги", callback_data="menu")]]))
        # у SendPulse далі пауза 5 с і ще щось (на скріні обрізано): допишемо, коли Тетяна надішле
    elif data == "zn:dila":
        if _img("dila_qr.jpg"):
            await ctx.bot.send_message(chat, DILA, parse_mode="HTML")
            await _send(ctx, chat, "", "dila_qr.jpg", kb_menu())
        else:
            await ctx.bot.send_message(chat, DILA, parse_mode="HTML", reply_markup=kb_menu())
    elif data == "zn:dnk":
        await ctx.bot.send_message(chat, DNK_1, parse_mode="HTML", reply_markup=M([[B("ДНК тест", url=DNK_URL)]]))
        await _send(ctx, chat, DNK_2, "dnk_pakety.jpg", kb_menu())
