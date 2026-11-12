"""Діагностика «Що не так з вашим кишківником?» (кодове слово, ?start=test).

10 питань кнопками А/Б/В (12.11: за новою програмою з 14 тем). Кожна відповідь дає бал у зону або «ок».
Результат = зона з найбільшою кількістю балів. Рівні бали = показуємо обидві.
Тексти тут, міняти можна вільно. Це самоперевірка, не діагноз.
"""
import logging
import os

from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config as C
import db

log = logging.getLogger("quiz")
IMG = os.path.join(os.path.dirname(__file__), "images")

INTRO = ("<b>Що не так з вашим кишківником?</b>\n\n"
         "Пройдіть коротку діагностику: <code>10 питань</code>, <code>3 хвилини</code>, відповіді кнопками.\n\n"
         "<i>Наприкінці я покажу, на що ваш кишківник найбільше «скаржиться» і з чого почати.</i>\n\n"
         "<i>Це самоперевірка, а не медичний діагноз.</i>")
BTN_GO = "Почати діагностику"
BTN_MENU = "Пройти діагностику кишківника"

# (питання, [(текст відповіді, зона)]) ; зони: zakrep, meteo, skin, nerv, ok
QUESTIONS = [
    ("Як ви зазвичай почуваєтесь <b>після їжі</b>?",
     [("Легко і комфортно", "ok"), ("Здуття, гази, «надутий живіт»", "meteo"), ("Важкість, ніби камінь", "zakrep")]),
    ("Який у вас <b>стілець</b>?",
     [("Щодня, без проблем", "ok"), ("Рідше ніж раз на день або із зусиллям", "zakrep"),
      ("Часто рідкий або нестабільний", "nerv")]),
    ("Яким стає <b>живіт до вечора</b>?",
     [("Таким самим, як зранку", "ok"), ("Помітно більшим, «надутим»", "meteo"), ("Іноді болить або спазмує", "nerv")]),
    ("Як живіт реагує на <b>стрес</b>?",
     [("Ніяк не реагує", "ok"), ("При хвилюванні одразу «крутить»", "nerv"), ("Від стресу стає закреп", "zakrep")]),
    ("Що зі <b>шкірою</b>?",
     [("Чиста, все добре", "ok"), ("Висипання, тьмяність", "skin"), ("Алергії, свербіж", "skin")]),
    ("Як з <b>імунітетом</b>?",
     [("Хворію рідко", "ok"), ("Часто застуди, запальні процеси", "skin"), ("Є аутоімунне захворювання або підозра на нього", "skin")]),
    ("Як з <b>енергією і вагою</b>?",
     [("Енергії вистачає, вага стабільна", "ok"), ("Втома навіть після сну", "skin"), ("Вага не йде, тягне на солодке", "meteo")]),
    ("Чи були за останній рік <b>антибіотики</b> або кишкові інфекції?",
     [("Ні", "ok"), ("Так, антибіотики", "meteo"), ("Так, інфекції або паразити", "meteo")]),
    ("Що з <b>аналізами й обстеженнями</b>?",
     [("Усе зрозуміло або не було потреби", "ok"), ("Є купа аналізів, але немає єдиної картини", "skin"),
      ("Лікар казав про дивертикули, коліт чи опущення органів", "zakrep")]),
    ("Що ви вже <b>пробували</b>?",
     [("Нічого, бо все добре", "ok"), ("Пробіотики й добавки, але без результату", "meteo"), ("Дієти, а проблема повертається", "nerv")]),
]
LETTERS = "АБВ"

RES = {
    "zakrep": ("card_res_zakrep.jpg",
               "<b>Ваш результат: кишківнику бракує руху</b>\n\n"
               "Важкість після їжі, нерегулярний стілець, відчуття «каменя» часто означають, що <b>перистальтика працює повільніше</b>, ніж треба.\n\n"
               "<i>Це не вирок і не «така в мене особливість». Причин закрепів кілька, і кожну можна знайти.</i>\n\n"
               "На інтенсиві цьому присвячена <code>тема 06</code> <b>Подолання закрепів</b>: 10 основних причин порушень випорожнень, а ще <code>тема 13</code> про вправи й масажі для кишківника."),
    "meteo": ("card_res_meteo.jpg",
              "<b>Ваш результат: здуття і баланс мікробіому</b>\n\n"
              "«Надутий» до вечора живіт, гази, тяга до солодкого часто пов'язані з <b>балансом мікрофлори</b>.\n\n"
              "<i>Здуття не потрібно просто терпіти: його причину можна знайти й прибрати.</i>\n\n"
              "На інтенсиві це <code>тема 08</code> <b>Що робити при метеоризмі</b>, <code>тема 09</code> <b>Мікробіом під контролем</b> і <code>тема 14</code> <b>«Аптечка» для ШКТ</b>."),
    "skin": ("card_res_skin.jpg",
             "<b>Ваш результат: кишківник говорить через шкіру й енергію</b>\n\n"
             "Висипання, тьмяна шкіра, втома навіть після сну дуже часто починаються <b>не зі шкіри, а з кишківника</b>.\n\n"
             "<i>Коли кишківник відновлюється, шкіра й енергія підтягуються слідом.</i>\n\n"
             "На інтенсиві це <code>тема 01</code> <b>Зв'язок усього організму з кишківником</b>, <code>тема 02</code> <b>Справжня діагностика ШКТ</b> і <code>тема 10</code> <b>Схема відновлення слизової</b>, а ще ми разом розберемо ваші аналізи."),
    "nerv": ("card_res_nerv.jpg",
             "<b>Ваш результат: живіт реагує на стрес</b>\n\n"
             "Коли хвилювання одразу відгукується спазмами чи нестабільним стільцем, працює <b>зв'язок нервової системи й кишківника</b>.\n\n"
             "<i>Це не «просто нерви», з цим можна працювати м'яко і системно.</i>\n\n"
             "На інтенсиві це <code>тема 05</code> <b>Коли ламається вісь «мозок-кишківник»</b>: як розпізнати й усунути СРК, плюс антистрес-підтримка і <code>тема 04</code> про харчові тригери."),
    "ok": ("card_res_ok.jpg",
           "<b>Ваш результат: кишківник у хорошій формі</b> ❤\n\n"
           "Чудово! Серйозних сигналів за вашими відповідями немає.\n\n"
           "<i>Тепер головне зберегти цей стан і не пропустити перші дзвіночки.</i>\n\n"
           "Інтенсив саме для тих, хто хоче <b>завжди мати здоровий кишківник і профілактувати проблеми</b>."),
}
OFFER = ("<b>Що робити далі?</b>\n\n"
         f"Запрошую вас на інтенсив <b>«{C.INTENSIVE_NAME}»</b>: старт <code>{C.INTENSIVE_START}</code>, "
         f"<b>{C.INTENSIVE_LENGTH}</b> у Telegram-каналі з чатом підтримки.\n"
         f"Вартість <code>{C.INTENSIVE_AMOUNT} грн</code> <i>({C.INTENSIVE_PRICE_NOTE})</i>, можна розтермінувати.\n\n"
         "<i>Ви отримаєте чіткий план відновлення саме для вашої ситуації.</i>")
DISCLAIMER = "<i>Діагностика має інформаційний характер і не замінює консультації лікаря чи нутриціолога.</i>"
ZONE_NAMES = {"zakrep": "закрепи", "meteo": "здуття/мікробіом", "skin": "шкіра/енергія", "nerv": "стрес/СРК", "ok": "все добре"}


def kb_q(i):
    return M([[B(f"{LETTERS[j]}. {t}", callback_data=f"qz:{i}:{j}")] for j, (t, _) in enumerate(QUESTIONS[i][1])])


def q_text(i):
    return f"<code>Питання {i + 1} з {len(QUESTIONS)}</code>\n\n<b>{QUESTIONS[i][0].replace('<b>', '').replace('</b>', '')}</b>"  # 12.11: питання повністю жирним


def result(ans):
    score = {}
    for i, j in enumerate(ans):
        z = QUESTIONS[i][1][j][1]
        if z != "ok":
            score[z] = score.get(z, 0) + 1
    if not score:
        return ["ok"]
    top = max(score.values())
    return [z for z, s in score.items() if s == top][:2]


async def send_photo(bot, chat_id, name, caption=None, kb=None):
    path = os.path.join(IMG, name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            await bot.send_photo(chat_id, f, caption=caption, parse_mode="HTML", reply_markup=kb)
        return True
    return False


async def start(bot, chat_id):
    kb = M([[B(BTN_GO, callback_data="qz:go")]])
    if not await send_photo(bot, chat_id, "card_quiz.jpg", INTRO, kb):
        await bot.send_message(chat_id, INTRO, reply_markup=kb, parse_mode="HTML")


async def on_cb(q, ctx, data, notify_admins, kb_offer, bottom_fn=None):
    """data: qz:go або qz:<питання>:<відповідь>."""
    chat = q.message.chat_id
    if data == "qz:go":
        ctx.user_data["qz"] = []
        __import__("crm").log_ev(q.from_user.id, "quiz_go")
        await ctx.bot.send_message(chat, q_text(0), reply_markup=kb_q(0), parse_mode="HTML")
        return
    _, i, j = data.split(":")
    i, j = int(i), int(j)
    ans = ctx.user_data.setdefault("qz", [])
    if i != len(ans):  # стара кнопка або повторне натискання
        return
    ans.append(j)
    __import__("crm").log_ev(q.from_user.id, f"quiz_q{i}")
    try:
        await q.edit_message_text(f"{q_text(i)}\n\n✓ <i>{QUESTIONS[i][1][j][0]}</i>", parse_mode="HTML")
    except Exception:
        pass
    if len(ans) < len(QUESTIONS):
        await ctx.bot.send_message(chat, q_text(len(ans)), reply_markup=kb_q(len(ans)), parse_mode="HTML")
        return
    zones = result(ans)
    db.flag_set(f"quiz:{q.from_user.id}", ",".join(zones))
    __import__("crm").log_ev(q.from_user.id, "quiz_done", ",".join(zones))
    for n, z in enumerate(zones):
        img, text = RES[z]
        await send_photo(ctx.bot, chat, img)
        await ctx.bot.send_message(chat, text, parse_mode="HTML",          # з першим результатом повертаємо меню
                                   reply_markup=bottom_fn() if (n == 0 and bottom_fn) else None)
    import texts as T
    await ctx.bot.send_message(chat, OFFER + T.URGENT + "\n\n" + DISCLAIMER, reply_markup=kb_offer(), parse_mode="HTML")
    u = q.from_user
    lines = [f"{k + 1}. {QUESTIONS[k][1][a][0]}" for k, a in enumerate(ans)]
    hot = " 🔥" if "ok" not in zones else ""
    await notify_admins(ctx, f"📝 Діагностику пройшов(ла){hot}: {u.full_name}" + (f" @{u.username}" if u.username else "")
                        + f" (ID {u.id})\nРезультат: {', '.join(ZONE_NAMES[z] for z in zones)}\n\n" + "\n".join(lines))
    ctx.user_data.pop("qz", None)
