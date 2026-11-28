"""27.11 (Тетяна): каруселі за Стратегом і агентами. 28.11: e1 💥 Руйнівник міфів (ВІТАМІНИ, 7 слайдів, на слайдах без продажу),
e2 🥦 Зальотна (ДІТИ, рівно 4 слайди, ніша тільки метафорою на 3-му, продукт на 4-му). На слайдах без цін: тільки «знижка 50% до 31.12»."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan2 import page, top, img, OUT  # noqa: E402
from plan3 import word  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

N7, N4 = 7, 4

E1 = [
    page("blue", f"""<div class="full"><img src="{img('suprovid.jpg')}" style="object-position:center 30%"></div><div class="shade-b"></div>{top(1, N7, True)}
<div style="position:absolute;left:56px;right:56px;bottom:90px;color:#fff">
  <span class="pl2">МІФ</span>
  <h1 style="margin-top:30px;font-size:82px">«Вітаміни корисні всім. Гірше точно не&nbsp;буде»</h1>
  <h1 style="margin-top:26px;font-size:96px"><i class="s ac2">Серйозно?</i></h1>
</div>"""),
    page("blue", f"""{top(2, N7)}
<div style="position:absolute;left:70px;right:70px;top:120px">
  <div class="card" style="display:flex;gap:34px;align-items:center"><div class="big" style="font-size:190px">2</div>
    <div class="p" style="font-size:34px"><b>Нобелівські премії</b> мав Лайнус Полінг, один з найвідоміших учених ХХ століття</div></div>
  <div class="p" style="margin-top:46px">У 1970 році він написав книжку про вітамін С і переконав мільйони людей, що великі дози щодня захистять від застуди.</div>
  <div class="p">Людям не треба було нічого перевіряти. Якщо так каже нобелівський лауреат, хіба можна сумніватися?</div>
</div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:430px"><img src="{img('g-041.jpg')}" style="object-position:center 40%"></div>"""),
    page("blue", f"""<div class="full"><img src="{img('g-093.jpg')}" style="object-position:center"></div><div class="shade-b"></div>{top(3, N7, True)}
<div style="position:absolute;left:56px;right:56px;bottom:90px;color:#fff">
  <span class="pl">ЗДАВАЛОСЬ БИ, ВІН НЕ МІГ ПОМИЛИТИСЬ</span>
  <div class="p" style="margin-top:26px;font-size:38px;line-height:1.42">Світова слава, наукові звання, мільйони читачів. Люди пили вітамін С жменями, полиці з ним порожніли, а хто сумнівався, той сперечався з <b>двічі нобелівським лауреатом</b>.</div>
</div>"""),
    page("blue", f"""{top(4, N7, True)}
<div style="position:absolute;left:70px;right:70px;top:150px">
  <h1 style="font-size:120px"><i class="s">Але є нюанс.</i></h1>
  <div class="p" style="margin-top:50px;color:#e6ebff;font-size:38px">Великі дослідження потім показали: для більшості людей ці дози <b style="color:#fff">майже не захищають від застуди</b>. Авторитет був величезний, а організм живе за своїми правилами.</div>
</div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:380px"><img src="{img('g-016.jpg')}" style="object-position:center 45%"></div>""", "cta"),
    page("blue", f"""{top(5, N7)}
<div class="ph" style="right:56px;top:110px;width:440px;height:600px"><img src="{img('vitaminy.jpg')}" style="object-position:center 20%"></div>
<div style="position:absolute;left:70px;width:500px;top:150px"><span class="pl">У ЧОМУ СПРАВА</span>
  <h2 style="margin-top:26px;font-size:58px">Організму не потрібно <i class="s ac">«більше»</i></h2></div>
<div style="position:absolute;left:70px;right:70px;top:760px">
  <div class="p">Йому потрібно саме те, чого бракує, і у формі, яку він засвоїть. А з полиці ми часто беремо вітаміни <b>неактивних дешевих форм з купою допоміжних домішок</b>.</div>
  <div class="p">Гроші витрачені, баночка стоїть, а самопочуття те саме.</div>
</div>"""),
    page("blue", f"""<div class="full"><img src="{img('g-046.jpg')}" style="object-position:center 35%"></div><div class="shade-b"></div>{top(6, N7, True)}
<div style="position:absolute;left:56px;right:56px;bottom:90px;color:#fff">
  <span class="pl">І ЦЕ ПРО БАГАТЬОХ</span>
  <div class="p" style="margin-top:26px;font-size:37px">Від жінки, яка п'є мелатонін, бо «подрузі допомагає», до мами, що купує дитині вітаміни з мультиком на коробці. Від магнію «від стресу» до цілої шафки баночок «для енергії», які так і не допиті.</div>
</div>"""),
    page("blue", f"""<div class="full"><img src="{img('cons_valentyna.jpg')}" style="object-position:30% center"></div><div class="shade"></div>{top(7, N7, True)}
<div style="position:absolute;left:70px;right:70px;top:420px;color:#fff;text-align:center">
  <div class="quote" style="color:#fff;font-size:76px">«Корисне те, чого бракує саме вам»</div>
  <div class="p" style="margin-top:40px;opacity:.9">Валентина Швець, нутриціолог</div>
</div>"""),
]

N6 = 6
# 28.11 (Тетяна): стара версія на 4 слайди обіцяла «в кінці покажу», а давала лише назви. Тепер 6 слайдів: кожна заміна з рецептом.
E2 = [
    page("green", f"""<div class="full"><img src="{img('g-090.jpg')}" style="object-position:center"></div><div class="shade-b"></div>{top(1, N6, True)}
<div style="position:absolute;left:56px;right:56px;bottom:330px;color:#fff">
  <h1 style="font-size:100px">Миколай знову несе три кульки цукерок? 🍬</h1>
</div>"""),
    page("green", f"""{top(2, N6)}
<div style="position:absolute;left:70px;right:70px;top:120px">
  <span class="pl">ЗНАЙОМО?</span>
  <div class="p" style="font-size:35px;margin-top:30px">Дитина радіє п'ять хвилин, а потім цілий вечір скаче по стінах, вередує і не може заснути. А зранку ще й просить «ще одну цукерочку».</div>
  <div class="p" style="font-size:35px">Цього року під подушку можна покласти інше, і це <b>теж буде свято</b>: солодке, смачне і таке, що дитина з'їсть із задоволенням.</div>
  <div class="p" style="font-size:35px"><i>Ось 4 смаколики, які я раджу мамам. Зберігайте, щоб не шукати 6 грудня 👇</i></div>
</div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:470px"><img src="{img('g-101.jpg')}" style="object-position:center"></div>"""),
    page("green", f"""{top(3, N6)}
<div class="ph" style="left:70px;right:70px;top:110px;height:560px"><img src="{img('g-097.jpg')}" style="object-position:center"></div>
<div style="position:absolute;left:70px;right:70px;top:720px">
  <span class="pl">1 · ПЕЧЕНІ ЯБЛУКА З КОРИЦЕЮ</span>
  <div class="p" style="font-size:35px;margin-top:26px">Вийміть серцевину, всередину покладіть ложку кисломолочного сиру або дрібно порубаних горіхів, щіпку кориці. <b>20 хвилин у духовці</b>, і весь дім пахне святом.</div>
  <div class="p" style="font-size:35px">Солодко без цукру: яблуко віддає свій смак саме, а кориця робить його схожим на десерт.</div>
  <div class="p" style="font-size:35px">Так само можна запекти грушу. <i>Подавайте теплими, з ложкою йогурту зверху: дитина точно попросить добавки.</i></div>
</div>"""),
    page("green", f"""{top(4, N6)}
<div style="position:absolute;left:70px;right:70px;top:120px">
  <span class="pl">2 · КУЛЬКИ З ФІНІКІВ І ГОРІХІВ</span>
  <div class="p" style="font-size:35px;margin-top:26px">Фініки без кісточок, жменя горіхів і ложка какао в блендер. Скачайте кульки і обваляйте в кокосовій стружці. <b>Зберігайте в холодильнику</b>, так вони тримають форму.</div>
  <div class="p" style="font-size:35px">А ще краще ліпити їх разом з дитиною: це вже окрема святкова розвага, і з'їсть вона своє «творіння» з гордістю 😉</div>
</div>
<div class="ph" style="left:70px;right:70px;bottom:70px;height:520px"><img src="{img('g-099.jpg')}" style="object-position:center"></div>"""),
    page("green", f"""{top(5, N6)}
<div style="position:absolute;left:70px;right:70px;top:110px;display:grid;grid-template-columns:1fr 1fr;gap:22px">
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-098.jpg')}" style="width:100%;height:420px;object-fit:cover"></div>
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-096.jpg')}" style="width:100%;height:420px;object-fit:cover"></div>
</div>
<div style="position:absolute;left:70px;right:70px;top:600px">
  <span class="pl">3 · ЯГОДИ З ЙОГУРТОМ</span>
  <div class="p" style="font-size:35px;margin-top:22px">Натуральний йогурт <b>без цукру</b>, ягоди (можна заморожені) і зверху трохи гранол. Подайте в гарній склянці шарами, і це вже десерт.</div>
  <span class="pl" style="margin-top:18px;display:inline-block">4 · ТЕМНИЙ ШОКОЛАД 70-85%</span>
  <div class="p" style="font-size:35px;margin-top:22px">Два-три квадратики, і краще вдень, а не перед сном: так солодке не заважатиме дитині заснути.</div>
  <div class="p" style="font-size:35px;margin-top:26px"><i>А поруч зі смаколиками покладіть книжку чи теплі шкарпетки з оленями: свято не тільки в їжі</i> 😉</div>
</div>"""),
    page("green", f"""{top(6, N6, True)}
<div class="ph" style="right:56px;top:120px;width:400px;height:520px"><img src="{img('g-000.jpg')}" style="object-position:top"></div>
<div style="position:absolute;left:70px;width:520px;top:150px">
  <div class="quote" style="font-size:46px;color:#fff">Що кладемо під подушку, з тим дитина і прокидається</div>
</div>
<div style="position:absolute;left:70px;right:70px;top:690px">
  <div class="p" style="font-size:35px;color:#e3f3e8">З тарілкою так само, тільки щодня. Як скласти дитині тарілку <b style="color:#fff">без заборон і сліз</b>, я розповідаю в мінікурсі «7 кроків до хронічного здоров'я вашої дитини»: 5 відеолекцій, гайд «45 найкорисніших продуктів для дітей», 50 рецептів.</div>
  <div class="p" style="font-size:35px;color:#fff;margin-top:22px"><b>До 31 грудня знижка 50%.</b> Щоб дізнатися подробиці, напишіть у коментарях</div>
  <div style="margin-top:18px">{word('note', 'ДІТИ')}</div>
</div>""", "cta"),
]

SETS = {"e1": E1, "e2": E2}


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
