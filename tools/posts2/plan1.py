"""27.11: перші каруселі контент-плану Валентини (знижка 50% до 31.12, слово 44), 3 дизайни:
p1 насичений синій (макет як зелений), p2 «як в Ольги Ейдель» у кольорах Валентини, p3 зелений.
Факти тільки з її гайду, збірника і списку послуг."""
import base64
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "images", "posts")
NAME = "Валентина Швець · нутриціолог, health-коуч"


def b64(name):
    p = name if os.path.isabs(name) else os.path.join(ROOT, "images", name)
    ext = "png" if p.endswith(".png") else "jpeg"
    with open(p, "rb") as f:
        return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()


PH = {k: b64(k + ".jpg") for k in ("cons_valentyna", "guide_solodke", "vitaminy", "analizy", "intensive", "suprovid")}
VAL_CUT = b64(os.path.join(HERE, "val1_cut.png"))

GREEN = dict(ink="#0f3d2e", ink2="#1d6b47", acc="#e8457f", sub="#2b4a3e", chip="#e3f3e8",
             bg="linear-gradient(160deg,#e3f3e8 0%,#ffffff 55%,#fdeef3 100%)", dark="linear-gradient(160deg,#145c3b,#0b2f22)")
PLUM = dict(ink="#1b2370", ink2="#3346c8", acc="#e8457f", sub="#2b336b", chip="#e3e7fb",
            bg="linear-gradient(160deg,#dfe4fb 0%,#ffffff 55%,#f6e9f5 100%)", dark="linear-gradient(160deg,#3346c8,#151b55)")


def css(t):
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:Inter;color:{t['ink']};position:relative;overflow:hidden;background:{t['bg']}}}
.tag{{display:inline-block;background:{t['ink2']};color:#fff;font-weight:800;font-size:22px;letter-spacing:2px;padding:11px 24px;border-radius:30px}}
h1{{font-size:92px;font-weight:800;line-height:1.0;letter-spacing:-2.5px}}
h2{{font-size:60px;font-weight:800;line-height:1.06;letter-spacing:-1px}}
em{{font-family:Lora;font-style:italic;font-weight:600;color:{t['acc']};letter-spacing:0}}
.sub{{font-size:33px;line-height:1.42;color:{t['sub']}}}
.sub b{{color:{t['ink']}}}
.num{{position:absolute;right:60px;top:56px;font-size:24px;font-weight:700;color:#8a98a8}}
.foot{{position:absolute;left:60px;bottom:40px;font-size:22px;color:#6b7f8f;font-weight:600}}
.card{{background:#fff;border-radius:30px;box-shadow:0 14px 34px rgba(20,30,80,.12);padding:34px 40px}}
.row{{display:flex;justify-content:space-between;align-items:center;gap:24px;padding:20px 0;border-bottom:2px solid {t['chip']}}}
.row:last-child{{border-bottom:0}}
.rt{{font-size:31px;font-weight:700;line-height:1.25}}
.rp{{text-align:right;white-space:nowrap}}
.rp s{{display:block;font-size:24px;color:#9aa3b5}}
.rp b{{font-size:36px;color:{t['acc']}}}
.ph{{position:absolute;border-radius:34px;overflow:hidden;box-shadow:0 22px 50px rgba(20,30,80,.22)}}
.ph img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.quote{{font-family:Lora;font-style:italic;font-size:56px;line-height:1.25;color:{t['ink']}}}
.cta{{background:{t['dark']};color:#fff}}
.cta .sub{{color:#e8eef5}} .cta .sub b{{color:#fff}} .cta .foot{{color:#c5d3e0}}
.word{{display:inline-block;background:#fff;color:{t['acc']};font-weight:900;font-size:110px;letter-spacing:4px;padding:10px 56px;border-radius:26px}}
.disc{{position:absolute;left:60px;right:60px;bottom:80px;font-size:20px;opacity:.7}}
.big{{font-size:140px;font-weight:900;color:{t['ink2']};line-height:1}}
"""


def doc(t, body, cls=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css(t)}</style></head><body class="{cls}">{body}</body></html>'


def foot(n, total):
    return f'<div class="num">{n}/{total}</div><div class="foot">{NAME}</div>'


def rows(items):
    return "".join(f'<div class="row"><div class="rt">{a}</div><div class="rp"><s>{b} грн</s><b>{c} грн</b></div></div>'
                   for a, b, c in items)


DISC = ''

# ---------- p1: ⚡ продаючий, насичений синій ----------
P1 = [
    lambda t: doc(t, f"""
<div class="ph" style="right:50px;bottom:100px;width:440px;height:640px"><img src="{PH['suprovid']}"></div>
<div style="position:absolute;left:60px;top:80px;width:600px">
  <span class="tag">МОЄ СВЯТО · ДО 31 ГРУДНЯ</span>
  <h1 style="margin-top:40px">Що можна взяти <em>за&nbsp;пів&nbsp;ціни?</em></h1>
  <div class="sub" style="margin-top:30px;width:470px">Усі мої послуги зі знижкою 50%. Розповідаю, щоРозповідаю, що для чогоnbsp;дляРозповідаю, що для чогоnbsp;чого</div>
</div><div class="foot">{NAME}</div>"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:60px;right:60px;top:120px">
  <h2>Коли потрібен <em>план і людина поруч</em></h2>
  <div class="card" style="margin-top:36px">{rows([
        ("Повноцінна консультація: розбір аналізів, причини проблем, персональна програма відновлення", "4500", "2250"),
        ("Супровід: раціон на місяць під ваші цілі (вага, ШКТ, запальні й аутоімунні процеси)", "4000", "2000"),
        ("Детальний розбір аналізів за оптимальними, а не лабораторними нормами", "1980", "990"),
        ("Мініконсультація з підбору добавок під ваші дефіцити", "1500", "750")])}</div>
</div>{foot(2, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:60px;right:60px;bottom:140px">
  <h2>Коли хочете <em>розібратись самі</em></h2>
  <div class="card" style="margin-top:36px">{rows([
        ("Гайд «Як приборкати тягу до солодкого»", "621", "310,5"),
        ("Мінікурс «7 кроків до хронічного здоров'я вашої дитини»", "999", "499,5")])}
    <div class="row"><div class="rt">Курс «Ввімкни свою щитовидку», окремі лекції і гайди</div><div class="rp"><b>−50%</b></div></div></div>
</div>{foot(3, 5)}"""),
    lambda t: doc(t, f"""
<div class="ph" style="left:60px;top:110px;width:420px;height:560px"><img src="{PH['cons_valentyna']}" style="object-position:30% center"></div>
<div style="position:absolute;left:540px;right:60px;top:150px">
  <div class="quote">«Займусь собою після свят»</div>
</div>
<div style="position:absolute;left:60px;right:60px;top:760px">
  <div class="sub">Так кажемо ми всі. А потім січень, і ціна вже повна, і здуття та втома нікуди не ділись.
  <b>Знижка 50% діє до 31 грудня</b>, тож почати можна зараз, а план буде готовий ще до Нового року.</div>
</div>{foot(4, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:250px">
  <h2 style="color:#fff">Не знаєте, що обрати?</h2>
  <div class="sub" style="margin-top:30px">Напишіть у коментарях</div>
  <div style="margin-top:26px"><span class="word">44</span></div>
  <div class="sub" style="margin-top:36px">і я підкажу, що підійде саме вам ❤</div>
</div><div class="foot">{NAME}</div>""", "cta"),
]

# ---------- p2: 📌 для зберігання, стиль «Ольга Ейдель» у кольорах Валентини ----------
BLUE_DEEP, PINK, CREAM = "#1f2f9e", "#ff8fb4", "#f3f5ff"


def css2():
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:Inter;position:relative;overflow:hidden;background:{CREAM};color:#141a3a}}
.bgph{{position:absolute;inset:0}} .bgph img{{width:100%;height:100%;object-fit:cover}}
.shade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,14,45,.55) 0%,rgba(10,14,45,.15) 40%,rgba(10,14,45,.75) 100%)}}
.top{{position:absolute;left:60px;right:60px;top:44px;display:flex;justify-content:space-between;font-size:24px;letter-spacing:1px;opacity:.75}}
.ph-t{{color:#fff}}
h1{{font-size:84px;font-weight:700;line-height:1.05;letter-spacing:-1.5px}}
h2{{font-size:66px;font-weight:700;line-height:1.08;letter-spacing:-1px}}
i.a{{font-family:Lora;font-style:italic;font-weight:500}}
.hl{{background:linear-gradient(transparent 55%,{PINK} 55%);padding:0 4px}}
.pl{{display:inline-block;background:{BLUE_DEEP};color:#fff;font-weight:800;font-size:26px;letter-spacing:1.5px;padding:8px 18px;border-radius:10px}}
.tx{{font-size:34px;line-height:1.45}}
.tx b{{font-weight:800}}
.box{{background:#fff;border-radius:24px;padding:30px 34px;box-shadow:0 12px 30px rgba(20,30,80,.12)}}
.li{{display:flex;gap:18px;align-items:flex-start;font-size:31px;line-height:1.35;padding:12px 0}}
.dot{{min-width:40px;height:40px;border-radius:50%;background:{BLUE_DEEP};color:#fff;font-size:24px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:2px}}
.btn{{display:inline-block;background:{BLUE_DEEP};color:#fff;font-weight:800;font-size:34px;padding:16px 34px;border-radius:40px}}
.disc{{position:absolute;left:60px;right:60px;bottom:34px;font-size:19px;opacity:.75}}
"""


def doc2(body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css2()}</style></head><body>{body}</body></html>'


def top(n, dark=False):
    return f'<div class="top {"ph-t" if dark else ""}"><span>[ {n} ]</span><span>Валентина Швець</span></div>'


P2 = [
    lambda t: doc2(f"""
<div class="bgph"><img src="{PH['guide_solodke']}" style="object-position:center 30%"></div><div class="shade"></div>
{top('гайд', True)}
<div style="position:absolute;left:60px;right:60px;bottom:150px;color:#fff">
  <h1>Чому на свята так <i class="a" style="color:{PINK}">тягне на&nbsp;солодке?</i></h1>
  <div class="tx" style="margin-top:28px;opacity:.95">4 причини з мого гайду. Збережіть, знадобиться вже на першому застіллі</div>
</div>"""),
    lambda t: doc2(f"""
{top('01')}
<div style="position:absolute;left:60px;right:60px;top:300px">
  <span class="pl">ПРИЧИНА 1</span>
  <h2 style="margin-top:28px">«Дешевий» <span class="hl">дофамін</span></h2>
  <div class="tx" style="margin-top:30px">З дитинства нас заохочували: <i class="a">«Ти молодець, ось цукерка!»</i>
  Тому втомились, засмутились, і рука сама тягнеться до солодкого. <b>Цукор швидко підіймає дофамін, але ненадовго.</b></div>
  <div class="tx" style="margin-top:26px">Шукайте «дорожчі» радощі: прогулянку, музику, спорт, розмову з близькими.</div>
</div>"""),
    lambda t: doc2(f"""
<div class="bgph"><img src="{PH['cons_valentyna']}" style="object-position:35% center"></div><div class="shade"></div>
{top('02', True)}
<div style="position:absolute;left:60px;right:60px;bottom:110px;color:#fff">
  <span class="pl">ПРИЧИНА 2</span>
  <h2 style="margin-top:26px">Мало <i class="a" style="color:{PINK}">білка</i></h2>
  <div class="tx" style="margin-top:24px">Каша з бананом на сніданок, і за 1-2 години знову голод і бажання цукерки.
  <b>Білок дає довгу ситість, а без нього тіло просить швидке паливо.</b><br>Норма білка в біохімії крові: 75-85 г/л.</div>
</div>"""),
    lambda t: doc2(f"""
{top('03')}
<div style="position:absolute;left:60px;right:60px;top:150px">
  <div class="box">
    <span class="pl">ПРИЧИНА 3</span>
    <div style="font-size:48px;font-weight:700;margin:20px 0 10px">Недосип і стрес</div>
    <div class="tx">Слабшає самоконтроль, а бажання швидкого задоволення через солодке <b>посилюється</b>. Грудень з корпоративами саме про це.</div>
  </div>
  <div class="box" style="margin-top:34px">
    <span class="pl">ПРИЧИНА 4</span>
    <div style="font-size:48px;font-weight:700;margin:20px 0 10px">Просто <i class="a">звичка</i></div>
    <div class="tx">Після <span class="hl"><b>3 днів без цукру</b></span> рецептори починають очищатися, і тяга помітно слабшає.</div>
  </div>
</div>"""),
    lambda t: doc2(f"""
<div class="bgph"><img src="{PH['vitaminy']}" style="object-position:center 20%"></div><div class="shade"></div>
{top('гайд', True)}
<div style="position:absolute;left:60px;right:60px;bottom:140px;color:#fff">
  <h2>А ще 3 причини і <i class="a" style="color:{PINK}">як подолати тягу</i></h2>
  <div class="tx" style="margin-top:24px">у моєму гайді «Як приборкати тягу до солодкого». <b>До 31 грудня 310,5 грн замість 621.</b></div>
  <div style="margin-top:34px"><span class="btn">Напишіть у коментарях 44</span></div>
</div>
"""),
]

# ---------- p3: 💥 руйнівник міфів, зелений ----------
P3 = [
    lambda t: doc(t, f"""
<div class="ph" style="left:60px;top:90px;width:470px;height:800px"><img src="{PH['vitaminy']}" style="object-position:center 25%"></div>
<div style="position:absolute;left:580px;right:50px;top:330px">
  <span class="tag">МІФ</span>
  <h1 style="margin-top:34px;font-size:80px">«Аналізи в нормі, <em>отже, я&nbsp;здорова»</em></h1>
</div>
<div style="position:absolute;left:60px;right:60px;bottom:110px" class="sub">А втома, здуття і висипання при цьому нікуди не діваються. Знайомо?</div>
<div class="foot">{NAME}</div>"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:340px">
  <div class="quote">«Лікар подивився: усе в межах норми»</div>
  <div class="sub" style="margin-top:44px">Я дивлюсь на аналізи <b>за оптимальними, а не лабораторними нормами</b>. І часто саме там видно, чому вам погано, хоча на бланку все «в нормі».</div>
</div>{foot(2, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:60px;right:60px;top:110px">
  <h2>Два показники, <em>на які я дивлюсь</em></h2>
</div>
<div style="position:absolute;left:60px;right:60px;top:330px;display:flex;flex-direction:column;gap:34px">
  <div class="card"><div class="big">≤ 5,2%</div><div class="sub" style="margin-top:14px"><b>Глікований гемоглобін</b>, середній рівень глюкози за 3 місяці. Вище, і варто дивитись на чутливість до інсуліну.</div></div>
  <div class="card"><div class="big">75-85</div><div class="sub" style="margin-top:14px"><b>Загальний білок, г/л.</b> Нижче, і можуть з'являтися тяга до солодкого, втома, ламкість волосся.</div></div>
</div>{foot(3, 5)}"""),
    lambda t: doc(t, f"""
<div class="ph" style="right:60px;top:110px;width:430px;height:640px"><img src="{PH['intensive']}" style="object-position:center 20%"></div>
<div style="position:absolute;left:60px;width:520px;top:150px"><h2>Що я роблю <em>на&nbsp;розборі</em></h2></div>
<div style="position:absolute;left:60px;right:60px;bottom:120px" class="card">
  <div class="sub">✔ розшифровую ваші аналізи за оптимальними нормами<br>✔ пояснюю причинно-наслідкові зв'язки: що з чим пов'язано<br>✔ даю рекомендації, як скоригувати стан і нормалізувати показники</div>
</div>{foot(4, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:230px">
  <h2 style="color:#fff">Покажіть мені свої аналізи</h2>
  <div class="sub" style="margin-top:26px">Детальний розбір <b>до 31 грудня за 990 грн</b> замість 1980.</div>
  <div class="sub" style="margin-top:40px">Напишіть у коментарях</div>
  <div style="margin-top:24px"><span class="word">44</span></div>
  <div class="sub" style="margin-top:34px">і я розповім, як записатися ❤</div>
</div><div class="foot">{NAME}</div>""", "cta"),
]


def build(key, slides, theme):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, f in enumerate(slides, 1):
            pg.set_content(f(theme), wait_until="load")
            pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(OUT, f"{key}_{i}.jpg"), type="jpeg", quality=92)
        b.close()


if __name__ == "__main__":
    build("p1", P1, PLUM)
    build("p2", P2, None)
    build("p3", P3, GREEN)
    print("ok")
