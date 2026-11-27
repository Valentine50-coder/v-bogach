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

E2 = [
    page("green", f"""<div class="full"><img src="{img('g-090.jpg')}" style="object-position:center"></div><div class="shade-b"></div>{top(1, N4, True)}
<div style="position:absolute;left:56px;right:56px;bottom:330px;color:#fff">
  <h1 style="font-size:100px">Миколай знову несе три кульки цукерок? 🍬</h1>
</div>"""),
    page("green", f"""{top(2, N4)}
<div style="position:absolute;left:70px;right:70px;top:110px">
  <div class="p" style="font-size:33px"><i>Дочитайте: в кінці покажу, що покласти замість цукерок.</i></div>
  <div class="p" style="margin-top:22px">У багатьох щороку однаково: дитина радіє п'ять хвилин, а потім цілий вечір скаче по стінах і не може заснути. Цього року під подушку можна покласти інше, і це теж буде свято:</div>
</div>
<div style="position:absolute;left:70px;right:70px;top:560px;display:grid;grid-template-columns:1fr 1fr;gap:20px">
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-097.jpg')}" style="width:100%;height:230px;object-fit:cover"><div class="p" style="padding:18px 24px;font-size:28px"><b>Печені яблука</b> з корицею</div></div>
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-100.jpg')}" style="width:100%;height:230px;object-fit:cover"><div class="p" style="padding:18px 24px;font-size:28px"><b>Ягоди</b> з йогуртом</div></div>
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-099.jpg')}" style="width:100%;height:230px;object-fit:cover"><div class="p" style="padding:18px 24px;font-size:28px"><b>Кульки</b> з фініків і горіхів</div></div>
  <div class="card" style="padding:0;overflow:hidden"><img src="{img('g-096.jpg')}" style="width:100%;height:230px;object-fit:cover;object-position:center"><div class="p" style="padding:18px 24px;font-size:28px"><b>Темний шоколад</b> 70-85%</div></div>
</div>"""),
    page("green", f"""<div class="full"><img src="{img('g-101.jpg')}" style="object-position:center"></div><div class="shade"></div>{top(3, N4, True)}
<div style="position:absolute;left:70px;right:70px;top:300px" class="card">
  <div class="quote" style="font-size:50px">Що кладемо під подушку, з тим дитина і прокидається</div>
  <div class="p" style="margin-top:26px">З тарілкою так само, тільки щодня. Що лежить у ній сьогодні, з тим здоров'ям дитина і виростає. Одна цукерка на Миколая нічого не зламає. Але <b>365 днів «ну хоч щось поїла»</b> складаються в імунітет, сон, шкіру й настрій.</div>
</div>"""),
    page("green", f"""{top(4, N4, True)}
<div class="ph" style="right:56px;top:120px;width:400px;height:560px"><img src="{img('g-000.jpg')}" style="object-position:top"></div>
<div style="position:absolute;left:70px;width:520px;top:150px">
  <h2 style="font-size:56px;color:#fff">Як скласти дитині тарілку <i class="s">без заборон і сліз?</i></h2>
</div>
<div style="position:absolute;left:70px;right:70px;top:730px">
  <div class="p" style="color:#e3f3e8">Усе це в моєму мінікурсі <b style="color:#fff">«7 кроків до хронічного здоров'я вашої дитини»</b>: 5 відеолекцій, гайд «45 найкорисніших продуктів для дітей», 50 рецептів і шпаргалка найшкідливіших Е-добавок.</div>
  <div class="p" style="color:#fff;margin-top:26px"><b>До 31 грудня знижка 50%.</b> Щоб забрати, напишіть у коментарях</div>
  <div style="margin-top:22px">{word('note', 'ДІТИ')}</div>
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
