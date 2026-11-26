"""26.11.2026: розділи Валентини з її ланцюжків SendPulse (тексти дослівно, від Тетяни скріни і посилання):
- «💊 ПІДБІР ВІТАМІНІВ»: мініконсультація-підбір 1500 грн, супровід 1000 грн/міс, запис кнопкою в особисті Валентини зі словом «вітаміни».
- «ЗНИЖКИ НА ВІТАМІНИ»: Healthfit 10% (valshvets10), Coral Club 20% (реєстрація за посиланням), 100500dobavok 5% (shvets), iHerb (NHU0793).
Фото: images/vitaminy.jpg."""
import asyncio
import os
from urllib.parse import quote

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import crm

ME = "https://t.me/health_shvets"
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "vitaminy.jpg")

PICK_1 = ("<b>Купуючи дієтичні добавки самотужки, ви дуже часто потрапляєте на недобросовісних виробників та неякісну продукцію, "
          "вітаміни неактивних дешевих форм, з купою допоміжних шкідливих домішок.</b>")
PICK_2 = ("<b>Завдяки такій моїй мініконсультації,</b> ви не потратите свої кошти на непотріб та не нашкодите своєму здоров’ю, "
          "а отримаєте рекомендації засобів, які справді принесуть вам бажані результати.")
PICK_3 = ("<b>Що ви отримаєте, скориставшись цією послугою:</b>\n\n"
          "1️⃣ Професійний підбір необхідних вам засобів, під ваш стан здоров’я, потреби, аналізи\n"
          "2️⃣ Вибір максимально якісної та безпечної продукції перевірених виробників\n"
          "3️⃣ Посилання на вказані добавки з різних сайтів, з різною вартістю, щоб ви мали вибір\n"
          "4️⃣ Схема прийому усіх засобів з відповідним дозуванням та усіма нюансами вживання\n"
          "5️⃣ Супровід у процесі вживання засобів, при потребі <i>(доплата - 1000 грн за місяць постійного супроводу)</i>\n\n"
          "<b>Вартість підбору - 1500 грн</b>\n"
          "Для замовлення послуги, пишіть сюди 👇")

DISC_1 = ("<b>Сучасне харчування не завжди забезпечує організм усіма необхідними вітамінами та мінералами.</b>\n\n"
          "Через обробку продуктів, стрес, швидкий ритм життя та виснаження ґрунтів ми часто недоотримуємо важливі поживні речовини з їжі.\n\n"
          "<i>Саме тому вітаміни можуть стати хорошим доповненням для підтримки енергії, імунітету та загального здоров’я.</i>")
DISC_2 = ("Маю великий досвід підбору вітамінів під різні запити та потреби організму…\n\n"
          "За роки роботи допомогла багатьом людям підібрати саме те, що дійсно працює ❤\n\n"
          "<b>І зараз підготувала для вас вигідні знижки на улюблені комплекси та вітаміни</b> 👇")
SHOPS = [
    ("<b>Healthfit</b> тут маємо знижку 10%. Для цього при оформленні замовлення необхідно ввести промокод <code>valshvets10</code>",
     "http://healthfit.ua"),
    ("<b>Coral-club</b> <i>25 років створює комплексні рішення для здоров'я та краси!</i>\n"
     "На цьому сайті маємо знижку 20%! Для цього спершу потрібно зареєструватись на сайті за цим посиланням, "
     "авторизуватись та оформити замовлення вже зі свого власного кабінету 👇", "https://coral.club/4410253.html"),
    ("<b>100500dobavok</b> на цьому сайті діє знижка 5%. Для цього потрібно авторизуватись на сайті та при замовленні ввести промокод <code>shvets</code>",
     "https://100500dobavok.ua/"),
    ("<b>Знижки на IHERB</b>\n\nДля отримання знижки на сайті iHerb при замовленні вказуємо цей промокод <code>NHU0793</code>",
     "https://iherb.co/pJghSkeZ?rcode=NHU0793"),
]


def kb_pick():
    return M([[B("Замовити", url=f"{ME}?text={quote('вітаміни')}")],
              [B("Знижки на вітаміни", callback_data="vit:disc")],
              [B("☰ Меню", callback_data="menu")]])


async def show_pick(ctx, chat, uid):
    crm.log_ev(uid, "vit_pick")
    if os.path.exists(IMG):
        with open(IMG, "rb") as f:
            await ctx.bot.send_photo(chat, f, caption=PICK_1, parse_mode="HTML")
    else:
        await ctx.bot.send_message(chat, PICK_1, parse_mode="HTML")
    await asyncio.sleep(3)
    await ctx.bot.send_message(chat, PICK_2, parse_mode="HTML")
    await asyncio.sleep(3)
    await ctx.bot.send_message(chat, PICK_3, parse_mode="HTML", reply_markup=kb_pick())


async def show_disc(ctx, chat, uid):
    crm.log_ev(uid, "vit_disc")
    await ctx.bot.send_message(chat, DISC_1, parse_mode="HTML")
    await asyncio.sleep(4)
    await ctx.bot.send_message(chat, DISC_2, parse_mode="HTML")
    for i, (text, url) in enumerate(SHOPS):
        await asyncio.sleep(2)
        rows = [[B("Перейти", url=url)]]
        if i == len(SHOPS) - 1:
            rows += [[B("💊 Підбір вітамінів", callback_data="vit:pick")], [B("☰ Меню", callback_data="menu")]]
        await ctx.bot.send_message(chat, text, parse_mode="HTML", reply_markup=M(rows), disable_web_page_preview=True)


async def on_cb(ctx, u, chat, data):
    if data == "vit:disc":
        await show_disc(ctx, chat, u.id)
    elif data == "vit:pick":
        await show_pick(ctx, chat, u.id)
