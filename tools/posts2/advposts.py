"""27.11: 2 каруселі, що ведуть в адвент «Здорові свята» (слово АДВЕНТ): a1 у стилі адвенту (зелений/білий/рожевий),
a2 у синьому стилі збірника рецептів. Рецепти й поради тільки з її збірника (images/advent/r/)."""
import base64
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "images", "posts")


def b64(p):
    ext = "png" if p.endswith(".png") else "jpeg"
    with open(p, "rb") as f:
        return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()


VAL = b64(os.path.join(HERE, "val1_cut.png"))
CAL = b64(os.path.join(ROOT, "images", "advent", "prev", "1_kalendar.jpg"))
R14 = b64(os.path.join(ROOT, "images", "advent", "r", "r14.jpg"))
R09 = b64(os.path.join(ROOT, "images", "advent", "r", "r09.jpg"))
NAME = "Валентина Швець · нутриціолог, health-коуч"

GREEN = dict(ink="#0f3d2e", ink2="#1d6b47", acc="#e8457f", sub="#2b4a3e",
             bg="linear-gradient(160deg,#e3f3e8 0%,#ffffff 55%,#fdeef3 100%)",
             dark="linear-gradient(160deg,#145c3b,#0b2f22)", chip="#e3f3e8")
BLUE = dict(ink="#16305e", ink2="#2f5fa8", acc="#c9a24a", sub="#2a3f66",
            bg="linear-gradient(165deg,#dce9fb 0%,#ffffff 55%,#eef4fd 100%)",
            dark="linear-gradient(160deg,#2f5fa8,#152b55)", chip="#dce9fb")


def css(t):
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:Inter;color:{t['ink']};position:relative;overflow:hidden;background:{t['bg']}}}
.tag{{display:inline-block;background:{t['ink2']};color:#fff;font-weight:800;font-size:22px;letter-spacing:2px;padding:11px 24px;border-radius:30px}}
h1{{font-size:96px;font-weight:800;line-height:1.0;letter-spacing:-2.5px}}
h2{{font-size:62px;font-weight:800;line-height:1.06;letter-spacing:-1px}}
em{{font-family:Lora;font-style:italic;font-weight:600;color:{t['acc']};letter-spacing:0}}
.sub{{font-size:34px;line-height:1.4;color:{t['sub']}}}
.sub b{{color:{t['ink']}}}
.num{{position:absolute;right:60px;top:56px;font-size:24px;font-weight:700;color:#8a98a8}}
.foot{{position:absolute;left:60px;bottom:40px;font-size:22px;color:#6b7f8f;font-weight:600}}
.card{{background:#fff;border-radius:30px;box-shadow:0 14px 34px rgba(20,40,60,.12);padding:46px 44px}}
.ph{{position:absolute;border-radius:34px;overflow:hidden;box-shadow:0 22px 50px rgba(20,40,60,.22);background:#fff}}
.ph img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.quote{{font-family:Lora;font-style:italic;font-size:54px;line-height:1.25;color:{t['ink']}}}
.big{{font-size:150px;font-weight:900;color:{t['ink2']};line-height:1}}
.cta{{background:{t['dark']};color:#fff}}
.cta .sub{{color:#e8eef5}}
.cta .foot{{color:#c5d3e0}}
.word{{display:inline-block;background:#fff;color:{t['acc']};font-weight:900;font-size:84px;letter-spacing:3px;padding:16px 46px;border-radius:26px}}
.disc{{position:absolute;left:60px;right:60px;bottom:80px;font-size:20px;opacity:.7}}
.n{{display:inline-flex;width:84px;height:84px;border-radius:50%;background:{t['chip']};color:{t['ink2']};font-weight:900;font-size:42px;align-items:center;justify-content:center}}
"""


def doc(t, body, cls=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css(t)}</style></head><body class="{cls}">{body}</body></html>'


def foot(n, total):
    return f'<div class="num">{n}/{total}</div><div class="foot">{NAME}</div>'


# ---------- a1: стиль адвенту, «подарунок до свят» ----------
A1 = [
    # 1 обкладинка: текст зверху зліва, фото справа знизу
    lambda t: doc(t, f"""
<div style="position:absolute;left:60px;top:70px;width:640px">
  <span class="tag">ПОДАРУНОК ДО СВЯТ</span>
  <h1 style="margin-top:40px">Свята без <em>важкості?</em></h1>
  <div class="sub" style="margin-top:34px;width:560px">31 день здорових святкових рецептів від мене, щодня з 1 грудня</div>
</div>
<img src="{VAL}" style="position:absolute;right:-40px;bottom:0;height:900px">
<div class="foot">{NAME}</div>"""),
    # 2 знайома думка: текст по центру
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:300px">
  <span class="tag">ЗНАЙОМО?</span>
  <div class="quote" style="margin-top:46px">«Корпоративи, салати, солодке… А&nbsp;в&nbsp;січні: чому так важко і живіт як камінь?»</div>
  <div class="sub" style="margin-top:46px">Грудень у багатьох проходить однаково. <b>Я хочу, щоб цього року у вас було інакше.</b></div>
</div>{foot(2, 5)}"""),
    # 3 що всередині: текст знизу, календар зверху
    lambda t: doc(t, f"""
<div class="ph" style="left:250px;top:60px;width:580px;height:760px"><img src="{CAL}"></div>
<div style="position:absolute;left:70px;right:70px;bottom:110px">
  <h2>Щоранку о 9:00 <em>одне віконце</em></h2>
  <div class="sub" style="margin-top:22px">Сніданки, обіди й вечері <b>без цукру, глютену і лактози</b> з мого збірника, і мої підказки, як не переїсти на святах.</div>
</div>{foot(3, 5)}"""),
    # 4 заперечення + доказ рецептом: текст збоку справа
    lambda t: doc(t, f"""
<div class="ph" style="left:50px;top:150px;width:470px;height:1040px"><img src="{R14}" style="object-position:center"></div>
<div style="position:absolute;left:570px;right:60px;top:300px">
  <span class="tag">ВІКОНЦЕ №3</span>
  <h2 style="margin-top:34px">«Значить, олів'є <em>не можна?</em>»</h2>
  <div class="sub" style="margin-top:28px">Можна! Із запеченими овочами, курячою грудкою і <b>заправкою з грецького йогурту</b> замість майонезу. Смак знайомий, а важкості немає.</div>
</div>{foot(4, 5)}"""),
    # 5 одна дія
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:240px">
  <h2 style="color:#fff">Хочете такий грудень?</h2>
  <div class="sub" style="margin-top:34px">Напишіть у коментарях слово</div>
  <div style="margin-top:30px"><span class="word">АДВЕНТ</span></div>
  <div class="sub" style="margin-top:40px">і я надішлю вам свій адвент «Здорові свята» ❤<br>А на Святвечір на вас чекає <b style="color:#fff">подарунок</b> 🎁</div>
</div>
<div class="disc">Інформація має ознайомчий характер і не замінює особистої консультації.</div>
<div class="foot">{NAME}</div>""", "cta"),
]

# ---------- a2: синій стиль збірника, «як не переїсти на свята» ----------
A2 = [
    # 1 обкладинка: фото зліва, текст справа по центру
    lambda t: doc(t, f"""
<img src="{VAL}" style="position:absolute;left:-60px;bottom:0;height:880px">
<div style="position:absolute;left:430px;right:50px;top:330px">
  <span class="tag">3 МОЇ ПРАВИЛА</span>
  <h1 style="margin-top:36px;font-size:76px">Як&nbsp;не&nbsp;переїсти <em>на&nbsp;свята?</em></h1>
  <div class="sub" style="margin-top:30px">Без голоду і без «мені тільки водички»</div>
</div>
<div class="foot">{NAME}</div>"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:110px">
  <span class="n">1</span>
  <h2 style="margin-top:34px">Починайте <em>з овочів</em></h2>
  <div class="sub" style="margin-top:26px">Якщо першою стравою будуть овочі чи овочевий салат, <b>ви з'їсте менше</b> і не відчуєте важкості в шлунку.</div>
</div>
<div class="ph" style="left:250px;bottom:110px;width:580px;height:560px"><img src="{R09}" style="object-position:center 30%"></div>
{foot(2, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:420px">
  <span class="n">2</span>
  <h2 style="margin-top:34px">Не голодуйте <em>перед застіллям</em></h2>
  <div class="card" style="margin-top:40px"><div class="sub">Не пропускайте сніданок і обід, <b>а для святкового столу залиште легку пізню вечерю.</b> Так ви не накинетесь на все одразу.</div></div>
</div>{foot(3, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;bottom:130px">
  <div class="big">1-2</div>
  <h2 style="margin-top:10px">ложки кожної <em>улюбленої страви</em></h2>
  <div class="sub" style="margin-top:26px">Кладіть у тарілку все, що подобається. <b>Не відмовляйте собі, просто дотримуйтесь міри.</b></div>
</div>
<span class="n" style="position:absolute;left:70px;top:110px">3</span>
{foot(4, 5)}"""),
    lambda t: doc(t, f"""
<div style="position:absolute;left:70px;right:70px;top:230px">
  <h2 style="color:#fff">Це лише 3 з моїх підказок</h2>
  <div class="sub" style="margin-top:30px">Ще 30 рецептів і порад у моєму адвенті «Здорові свята»: щоранку одне віконце з 1 грудня.</div>
  <div class="sub" style="margin-top:44px">Напишіть у коментарях слово</div>
  <div style="margin-top:26px"><span class="word">АДВЕНТ</span></div>
  <div class="sub" style="margin-top:34px">і я надішлю його вам ❤</div>
</div>
<div class="disc">Інформація має ознайомчий характер і не замінює особистої консультації.</div>
<div class="foot">{NAME}</div>""", "cta"),
]


def build(key, slides, theme):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, f in enumerate(slides, 1):
            pg.set_content(f(theme), wait_until="load")
            pg.wait_for_timeout(250)
            path = os.path.join(OUT, f"{key}_{i}.jpg")
            pg.screenshot(path=path, type="jpeg", quality=92)
        b.close()


if __name__ == "__main__":
    build("a1", A1, GREEN)
    build("a2", A2, BLUE)
    print("ok")
