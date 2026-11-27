"""27.11 (Тетяна «збирай, відправляй»): каруселі 28.11 18:00 - 1.12 9:00 за Стратегом і агентами.
e3 ❤ Жива (АДВЕНТ), e4 💰 Гроші/бренд (ЦУКОР), e5 📌 Класична (АНАЛІЗИ), e6 💥 Міф (КОНСУЛЬТАЦІЯ),
e7 🥦 Зальотна 4 слайди (АДВЕНТ), e8 📌 Класична правила (АДВЕНТ). На слайдах без цін. Текст не на обличчі."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan2 import page, top, img, OUT  # noqa: E402
from plan3 import word, text, photo, split  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def cov(th, pic, tag, h, sub="", pos="center", where="bottom:90px", n=7, shade="shade-b", size=88):
    return page(th, f"""<div class="full"><img src="{img(pic)}" style="object-position:{pos}"></div><div class="{shade}"></div>{top(1, n, True)}
<div style="position:absolute;left:56px;right:56px;{where};color:#fff"><span class="pl2">{tag}</span>
<h1 style="margin-top:26px;font-size:{size}px">{h}</h1>{f'<div class="p" style="margin-top:20px">{sub}</div>' if sub else ''}</div>""")


def dark(th, k, n, h, paras, pic=None, pos="center"):
    ph = f'<div class="ph" style="left:70px;right:70px;bottom:70px;height:400px"><img src="{img(pic)}" style="object-position:{pos}"></div>' if pic else ""
    ps = "".join(f'<div class="p" style="color:#e6ebff;font-size:38px">{p}</div>' for p in paras)
    return page(th, f"""{top(k, n, True)}<div style="position:absolute;left:70px;right:70px;top:150px">
<h1 style="font-size:104px;color:#fff">{h}</h1><div style="margin-top:44px">{ps}</div></div>{ph}""", "cta")


def ctap(th, k, n, h, paras, w, style, after, pic=None, pos="top"):
    ph = f'<div class="ph" style="right:56px;top:110px;width:380px;height:500px"><img src="{img(pic)}" style="object-position:{pos}"></div>' if pic else ""
    wid = "width:560px" if pic else "right:70px"
    ps = "".join(f'<div class="p" style="color:#e6ebff">{p}</div>' for p in paras)
    return page(th, f"""{top(k, n, True)}{ph}
<div style="position:absolute;left:70px;{wid};top:150px"><h2 style="color:#fff;font-size:58px">{h}</h2></div>
<div style="position:absolute;left:70px;right:70px;top:{660 if pic else 420}px">{ps}
<div class="p" style="margin-top:34px;color:#fff">Напишіть у коментарях</div><div style="margin-top:20px">{word(style, w)}</div>
<div class="p" style="margin-top:24px;color:#e6ebff">{after}</div></div>""", "cta")


def lst(th, k, n, h, items, pic=None, pos="center"):
    rows = "".join(f'<div class="card" style="padding:24px 32px;display:flex;gap:22px;align-items:flex-start"><div style="font-size:40px">{a}</div>'
                   f'<div class="p" style="font-size:31px">{b}</div></div>' for a, b in items)
    ph = f'<div class="ph" style="left:70px;right:70px;bottom:70px;height:300px"><img src="{img(pic)}" style="object-position:{pos}"></div>' if pic else ""
    return page(th, f"""{top(k, n)}<div style="position:absolute;left:70px;right:70px;top:120px"><h2 style="font-size:58px">{h}</h2>
<div style="margin-top:30px;display:flex;flex-direction:column;gap:18px">{rows}</div></div>{ph}""")


def rule(th, k, n, num, h, paras, pic, pos="center", where="bottom"):
    ps = "".join(f'<div class="p" style="font-size:41px;line-height:1.45">{p}</div>' for p in paras)
    ph_top = where == "bottom"
    ph = f'<div class="ph" style="left:70px;right:70px;{"top:110px" if ph_top else "bottom:70px"};height:{540 if ph_top else 600}px"><img src="{img(pic)}" style="object-position:{pos}"></div>'
    box = "top:700px" if ph_top else "top:130px"
    return page(th, f"""{top(k, n)}{ph}<div style="position:absolute;left:70px;right:70px;{box}">
<div style="display:flex;gap:26px;align-items:center"><div class="big" style="font-size:130px">{num}</div><h2 style="font-size:52px">{h}</h2></div>
<div style="margin-top:22px;font-size:39px">{ps}</div></div>""")


def txtb(th, k, n, quote, paras, pic, pos="center"):
    ps = "".join(f'<div class="p">{p}</div>' for p in paras)
    return page(th, f"""{top(k, n)}<div class="ph" style="left:70px;right:70px;top:110px;height:520px"><img src="{img(pic)}" style="object-position:{pos}"></div>
<div style="position:absolute;left:70px;right:70px;top:690px"><div class="quote" style="font-size:52px">{quote}</div><div style="margin-top:30px">{ps}</div></div>""")


# ===== e3 · 28.11 18:00 · ❤ Жива · АДВЕНТ =====
N = 7
E3 = [
    cov("green", "advent/invite.jpg", "ЗІЗНАННЯ", "Я все б віддала за шматочок тортика",
        "Так було. І саме тому цього грудня я роблю для вас адвент", "center 25%", n=N),
    text("green", 2, "«Я просто дуже люблю солодке»",
         ["Колись я була справжньою ласункою і щиро так думала. Свято для мене означало ще шматочок торта, ще цукерку, ще десерт до чаю, "
          "і мені здавалось, що це просто смак, а не звичка, без якої я вже не можу.",
          "Тільки після свят приходили важкість, втома і відчуття, що тіло <b>просить відпочинку від самої себе</b>."],
         "g-002.jpg", "center 40%", total=N),
    photo("green", 3, "g-089.jpg", "ЩО Я ЗРОЗУМІЛА",
          ["Справа була не в силі волі. Солодке дає <b>викид дофаміну</b>, мозок запам'ятовує цей кайф і просить ще.",
           "А надлишок цукру ще й ламає роботу <b>лептину</b>, гормону, який контролює голод. Тому один шматочок ніколи не буває одним."],
          "center", total=N),
    split("green", 4, "g-035.jpg", "СЬОГОДНІ", 'Вдома в мене <i class="s ac">немає цукру</i>',
          ["Глюкоза в нормі, а біологічний вік <b>майже удвічі менший за паспортний</b>. І я не сиджу на дієтах та не відмовляюсь від свят. "
           "Я просто навчилась готувати їх інакше, так, щоб було смачно і легко водночас."], "right", "center 20%", total=N),
    txtb("green", 5, N, "«Без олів'є і торта це не свято»",
         ["Я теж так думала. Але олів'є можна зробити <b>на грецькому йогурті замість майонезу</b>, і смак той самий.",
          "А торт може бути <b>без борошна і без цукру</b>, як мої шоколадні тістечка «Новий рік без снігу», які готуються в мікрохвильовці за кілька хвилин."],
         "g-094.jpg", "center"),
    lst("green", 6, N, "Що чекає на вас у моєму адвенті",
        [("🎄", "<b>31 віконце</b>: з 1 грудня щоранку о 9:00 корисний святковий рецепт з мого збірника"),
         ("🥗", "<b>Поради</b>, як відсвяткувати без наслідків для здоров'я та фігури"),
         ("🎁", "<b>Подарунки</b> на Миколая, Святвечір і Різдво")], "g-097.jpg"),
    ctap("green", 7, N, "Хочете цього грудня інакше?",
         ["Я зібрала для вас свій адвент <b>«ЗДОРОВІ СВЯТА без зайвих кг та проблем в ШКТ»</b>. Усе безкоштовно, просто приєднуйтесь до 1 грудня."],
         "АДВЕНТ", "glow", "і я надішлю вам календар ❤", "g-000.jpg", "top"),
]

# ===== e4 · 29.11 9:00 · 💰 Гроші/бренд · ЦУКОР =====
N = 7
E4 = [
    cov("blue", "g-004.jpg", "ІСТОРІЯ БРЕНДУ", 'Санта з реклами Coca-Cola <i class="s ac2">досі продає нам цукор?</i>',
        "", "center", "top:150px", n=N, shade="shade-t"),
    text("blue", 2, "1931 рік",
         ["Coca-Cola замовила художнику <b>Геддону Сандблому</b> різдвяну рекламу. Він намалював Санту добрим, круглолицим, у червоному костюмі "
          "і з пляшкою в руці.",
          "І малював його для бренду <b>понад 30 років</b>, щозими новий образ. Компанія хотіла, щоб її напій купували не тільки влітку, а й у холодні місяці."],
         "g-089.jpg", "center", total=N),
    photo("blue", 3, "g-090.jpg", "ЩО ЦЕ ЗРОБИЛО",
          ["Рекламу щороку бачили мільйони людей. Санта з пляшкою став таким самим символом свята, як ялинка і гірлянди.",
           "І в голові закріпилась проста звичка: <b>свято означає солодке</b>."], "center", total=N),
    dark("blue", 4, N, 'Вирішив <i class="s">не смак</i>',
         ["Бренд прив'язав солодкий напій до відчуття <b style=\"color:#fff\">свята, тепла і дитинства</b>. І мозок досі шукає це відчуття в солодкому, "
          "щойно на вулиці з'являються гірлянди, а в магазинах святкові коробки цукерок."], "g-011.jpg"),
    split("blue", 5, "g-091.jpg", "ЩО ВСЕРЕДИНІ", 'Одна банка коли: <i class="s ac">7 ложок цукру</i>',
          ["У банці 0,33 л класичної коли близько <b>35 г цукру</b>. Солодке дає викид дофаміну, мозок запам'ятовує кайф і просить ще, "
           "а надлишок цукру ламає роботу лептину, гормону ситості. Так «трохи на свято» тягнеться до самого січня."], "left", "center", total=N),
    txtb("blue", 6, N, "«Я просто люблю солодке, це ж не залежність»",
         ["Мені часто пишуть саме так. Я відповідаю чесно: я теж так думала, поки була ласункою.",
          "Сьогодні вдома в мене немає цукру, і це сталося <b>без жорстких заборон і зривів</b>. Просто коли розумієш, як працює тяга, з нею стає набагато легше домовитись."],
         "g-001.jpg", "center 30%"),
    ctap("blue", 7, N, "Як розірвати зв'язок «свято = цукор»?",
         ["Свій шлях і прості способи звільнитися від цукрової залежності я розписала в гайді <b>«Як приборкати тягу до солодкого»</b>: "
          "справжні причини тяги, приховані цукри, рейтинг солодощів і безпечні альтернативи.",
          "<b style=\"color:#fff\">До 31 грудня знижка 50%.</b> Щоб дізнатися подробиці,"],
         "ЦУКОР", "quote", "і я надішлю вам усе ❤"),
]

# ===== e5 · 29.11 18:00 · 📌 Класична · АНАЛІЗИ =====
N = 7
E5 = [
    cov("green", "g-016.jpg", "ЗБЕРЕЖІТЬ", "5 помилок з аналізами, через які гроші летять на вітер",
        "", "center 30%", "bottom:100px", n=N),
    rule("green", 2, N, "1", "Здавати все підряд «за компанію»",
         ["Популярні аналізи часто <b>мало інформативні</b> саме для вас. Потрібні ті, що відповідають вашому стану і симптомам, а не весь прайс лабораторії."],
         "g-029.jpg", "center 40%"),
    rule("green", 3, N, "2", "Дивитися тільки на лабораторні норми",
         ["Показник може бути «в нормі» на бланку, але далеким від оптимального. Тому я розбираю аналізи <b>за оптимальними нормами</b>, а не лише лабораторними."],
         "g-001.jpg", "center 30%", "top"),
    rule("green", 4, N, "3", "Розшифровувати через ШІ",
         ["ШІ не знає ваших симптомів, історії і того, як показники пов'язані між собою. Людина ще більше заплутується і робить <b>хибні висновки</b>."],
         "g-026.jpg", "center 30%"),
    rule("green", 5, N, "4", "Дивитися на кожен показник окремо",
         ["Організм працює як система. Важливі <b>причинно-наслідкові зв'язки</b>: що з чим пов'язано і звідки насправді береться втома, здуття чи погана шкіра."],
         "g-045.jpg", "center 40%", "top"),
    txtb("green", 6, N, "«Я боюсь здавати, бо не знаю, які»",
         ["Що я відповідаю, коли мені так кажуть: помилка 5 саме в цьому, <b>роками відкладати</b>.",
          "Почати можна зі списку тільки потрібних вам аналізів. А в лабораторіях, які я раджу, є <b>промокоди на знижку до 15%</b>."],
         "g-049.jpg", "center 25%"),
    ctap("green", 7, N, "Хочете нарешті зрозуміти свої цифри?",
         ["Я розберу ваші аналізи доступною мовою, у голосових, які можна переслуховувати, і дам <b>чіткий план дій</b>.",
          "<b style=\"color:#fff\">До 31 грудня знижка 50%.</b> Щоб дізнатися подробиці,"],
         "АНАЛІЗИ", "note", "і я надішлю все ❤"),
]

# ===== e6 · 30.11 9:00 · 💥 Руйнівник міфів · (КОНСУЛЬТАЦІЯ в описі) =====
N = 7
E6 = [
    page("blue", f"""<div class="full"><img src="{img('g-040.jpg')}" style="object-position:center"></div><div class="shade-t"></div>{top(1, N, True)}
<div style="position:absolute;left:56px;right:56px;top:150px;color:#fff"><span class="pl2">МІФ</span>
<h1 style="margin-top:28px;font-size:80px">«Жир головний ворог фігури. Беріть усе знежирене»</h1>
<h1 style="margin-top:24px;font-size:96px"><i class="s ac2">Серйозно?</i></h1></div>"""),
    text("blue", 2, "1967 рік",
         ["У <b>New England Journal of Medicine</b>, одному з найавторитетніших медичних журналів, вийшов огляд науковців з Гарварду.",
          "Висновок звучав переконливо: у хворобах серця винні жири, а роль цукру <b>несуттєва</b>. Лікарі, журнали і виробники почали боротися з жиром."],
         "g-094.jpg", "center", total=N),
    photo("blue", 3, "g-091.jpg", "А ХТО ЗАПЛАТИВ",
          ["Майже через 50 років, у 2016-му, дослідники знайшли листування: огляд замовила і оплатила <b>асоціація цукрової промисловості</b>.",
           "Але світ уже встиг повірити, а полиці заповнились знежиреним."], "center", total=N),
    dark("blue", 4, N, '<i class="s">Але є нюанс.</i>',
         ["Коли з продукту прибирають жир, пропадає смак. І щоб знежирений йогурт чи десерт усе одно хотілося купити, туди часто додають "
          "<b style=\"color:#fff\">цукор, крохмаль і загусники</b>."], "g-098.jpg"),
    split("blue", 5, "g-040.jpg", "ЯК НАСПРАВДІ", 'Жир <i class="s ac">жиру не рівний</i>',
          ["Організму потрібні корисні жири: <b>риба, горіхи, авокадо, яйця, оливкова олія</b>. Без них гірше засвоюються вітаміни A, D, E і K, "
           "страждають гормони, шкіра і відчуття ситості."], "right", "center", total=N),
    photo("blue", 6, "g-049.jpg", "І ЦЕ ПРО БАГАТЬОХ",
          ["Від жінки, яка роками їсть знежирений сир і не розуміє, чому постійно голодна, до тієї, що боїться авокадо, бо «там же жир», "
           "а ввечері з'їдає пачку печива."], "center 20%", total=N),
    page("blue", f"""<div class="full"><img src="{img('advent/xmas_cons.jpg')}" style="object-position:center 25%"></div><div class="shade-b"></div>{top(7, N, True)}
<div style="position:absolute;left:70px;right:70px;bottom:120px;color:#fff;text-align:center">
<div class="quote" style="color:#fff;font-size:74px">«Бійтеся не жиру, а&nbsp;прихованого цукру»</div>
<div class="p" style="margin-top:30px;opacity:.9">Валентина Швець, нутриціолог</div></div>"""),
]

# ===== e7 · 30.11 18:00 · 🥦 Зальотна · рівно 4 слайди · АДВЕНТ =====
N = 4
E7 = [
    page("green", f"""{top(1, N)}<div class="ph" style="left:200px;right:200px;top:120px;height:600px;transform:rotate(-3deg)"><img src="{img('g-r14.jpg')}" style="object-position:center"></div>
<div style="position:absolute;left:70px;right:70px;top:790px"><span class="pl">31 ГРУДНЯ</span>
<h1 style="margin-top:28px;font-size:110px">Ви теж ріжете олів'є <i class="s ac">тазиком?</i></h1></div>"""),
    page("green", f"""{top(2, N)}
<div style="position:absolute;left:70px;right:70px;top:120px">
<div class="p" style="font-size:33px"><i>Дочитайте до кінця, там те, що змінить ваш святковий стіл.</i></div>
<div class="p" style="margin-top:24px">31 грудня, третя година дня. На кухні гора мисок, на плиті ще одна каструля картоплі, а в холодильнику вже немає місця.</div>
<div class="p">Ми готуємо так, ніби в гості прийде пів під'їзду, а потім ще три дні доїдаємо салати, бо <b>«не викидати ж»</b>.</div></div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:420px"><img src="{img('g-r16.jpg')}" style="object-position:center"></div>"""),
    page("green", f"""<div class="full"><img src="{img('g-r09.jpg')}" style="object-position:center"></div><div class="shade"></div>{top(3, N, True)}
<div class="card" style="position:absolute;left:70px;right:70px;top:250px">
<div class="quote" style="font-size:52px">Святковий стіл як валіза у відпустку</div>
<div class="p" style="margin-top:24px">Пакуємо «про всяк випадок» удвічі більше, ніж треба, а потім тягаємо цю вагу за собою. З тарілкою так само: на свята варто брати
<b>1-2 ложки всього, що подобається</b>, а не повну миску кожного салату.</div></div>"""),
    ctap("green", 4, N, "А якщо святкувати смачно і легко?",
         ["Завтра, <b style=\"color:#fff\">1 грудня о 9:00</b>, я відкриваю перше віконце свого адвенту «Здорові свята»: щоранку святковий рецепт "
          "з мого збірника і поради, як відсвяткувати без наслідків. Усе безкоштовно."],
         "АДВЕНТ", "flag", "і я надішлю вам календар ❤", "advent/invite.jpg", "center 20%"),
]

# ===== e8 · 1.12 9:00 · 📌 Класична (правила) · АДВЕНТ =====
N = 6
E8 = [
    cov("blue", "g-098.jpg", "МОЇ ПРАВИЛА", 'Як пережити грудень <i class="s ac2">без важкості?</i>',
        "5 правил, які я сама виконую на всіх святах", "center", "top:150px", n=N, shade="shade-t"),
    rule("blue", 2, N, "1", "Починайте з овочів",
         ["Якщо першою стравою будуть <b>овочі чи овочевий салат</b>, це допоможе не переїсти, зменшить голод і вбереже від важкості в шлунку."],
         "m-008c.jpg", "center 30%"),
    rule("blue", 3, N, "2", "Білок обов'язковий",
         ["Обирайте <b>прості страви з риби чи м'яса</b>. Білкова частина має бути на тарілці, але без надміру сиру, майонезу і соусів."],
         "m-006c.jpg", "center 25%", "top"),
    page("blue", f"""{top(4, N)}
<div style="position:absolute;left:70px;right:70px;top:120px;display:flex;flex-direction:column;gap:26px">
<div class="card"><div style="display:flex;gap:24px;align-items:center"><div class="big" style="font-size:110px">3</div><h2 style="font-size:48px">Не голодуйте до застілля</h2></div>
<div class="p" style="margin-top:14px">Не пропускайте сніданок і обід, а для свята залиште <b>легку пізню вечерю</b>. Так ви не накинетесь на все одразу.</div></div>
<div class="card"><div style="display:flex;gap:24px;align-items:center"><div class="big" style="font-size:110px">4</div><h2 style="font-size:48px">По 1-2 ложки улюбленого</h2></div>
<div class="p" style="margin-top:14px">Не відмовляйте собі в улюблених стравах, просто <b>дотримуйтесь міри</b>.</div></div></div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:330px"><img src="{img('g-097.jpg')}" style="object-position:center 60%"></div>"""),
    rule("blue", 5, N, "5", "Алкоголь за 4 години до сну",
         ["І на кожну порцію алкоголю <b>додаткова склянка води</b>. «А як же свято?» Свято лишається, просто без важкого ранку наступного дня."],
         "g-041.jpg", "center"),
    ctap("blue", 6, N, "Сьогодні відкрилось перше віконце",
         ["Мій адвент <b>«ЗДОРОВІ СВЯТА без зайвих кг та проблем в ШКТ»</b> уже стартував: щоранку о 9:00 рецепт і порада. "
          "Приєднуйтесь, навіть якщо пропустили початок, минулі віконця теж відкриються."],
         "АДВЕНТ", "outline", "і я надішлю вам календар ❤", "g-049.jpg", "center 20%"),
]

SETS = {"e3": E3, "e4": E4, "e5": E5, "e6": E6, "e7": E7, "e8": E8}


def build(keys):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for key in keys:
            for i, html in enumerate(SETS[key], 1):
                pg.set_content(html, wait_until="load")
                pg.wait_for_timeout(200)
                pg.screenshot(path=os.path.join(OUT, f"{key}_{i}.jpg"), type="jpeg", quality=90)
        b.close()


if __name__ == "__main__":
    build(sys.argv[1:] or list(SETS))
    print("ok")
