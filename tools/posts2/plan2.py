"""27.11 (Тетяна: «щільно, вірусно, не тільки Валентина»): каруселі грудня, 2 на день.
Фото: Валентина (images/*.jpg, stock/g-000..g-074 з її гайду), стокові з її гайду й меню (stock/), сторінки збірника.
Факти тільки з її гайду «Як приборкати тягу до солодкого», збірника рецептів і списку послуг."""
import base64
import os
import sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "images", "posts")
NICK = "@health_shvets"


def img(path):
    p = path if os.path.isabs(path) else (os.path.join(HERE, "stock", path) if path[:2] in ("g-", "m-")
                                          else os.path.join(ROOT, "images", path))
    ext = "png" if p.endswith(".png") else "jpeg"
    with open(p, "rb") as f:
        return f"data:image/{ext};base64," + base64.b64encode(f.read()).decode()


THEMES = {
    # синій Валентини (стиль «як в Ольги»: фото на весь слайд, курсив, плашки)
    "blue": dict(bg="#f4f6ff", ink="#121a3d", acc="#2338c4", acc2="#8fb0ff", soft="#e4e8fb", dark="#141c5c"),
    # зелений адвенту
    "green": dict(bg="#f2f8f3", ink="#0f3d2e", acc="#1d6b47", acc2="#8fdcb0", soft="#e3f3e8", dark="#0f3d2e"),
}


def css(t):
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:1350px;font-family:Inter;color:{t['ink']};background:{t['bg']};position:relative;overflow:hidden}}
.full{{position:absolute;inset:0}} .full img{{width:100%;height:100%;object-fit:cover}}
.shade-b{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,12,40,.05) 30%,rgba(8,12,40,.82) 100%)}}
.shade-t{{position:absolute;inset:0;background:linear-gradient(0deg,rgba(8,12,40,.05) 35%,rgba(8,12,40,.8) 100%)}}
.shade{{position:absolute;inset:0;background:rgba(8,12,40,.45)}}
.top{{position:absolute;left:56px;right:56px;top:40px;display:flex;justify-content:space-between;font-size:23px;letter-spacing:1px;opacity:.7;z-index:5}}
.w{{color:#fff}}
h1{{font-size:88px;font-weight:800;line-height:1.02;letter-spacing:-2px}}
h2{{font-size:64px;font-weight:800;line-height:1.06;letter-spacing:-1.2px}}
i.s{{font-family:Lora;font-style:italic;font-weight:500;letter-spacing:0}}
.ac{{color:{t['acc']}}} .ac2{{color:{t['acc2']}}}
.hl{{background:linear-gradient(transparent 58%,{t['acc']}33 58%);padding:0 4px}}
.pl{{display:inline-block;background:{t['acc']};color:#fff;font-weight:800;font-size:24px;letter-spacing:1.5px;padding:9px 18px;border-radius:10px}}
.pl2{{display:inline-block;background:rgba(255,255,255,.92);color:{t['acc']};font-weight:800;font-size:24px;letter-spacing:1px;padding:8px 16px;border-radius:8px}}
.p{{font-size:35px;line-height:1.48}}
.p b{{font-weight:800}}
.p+.p{{margin-top:22px}}
.card{{background:#fff;border-radius:26px;padding:38px 42px;box-shadow:0 14px 36px rgba(15,20,60,.12)}}
.quote{{font-family:Lora;font-style:italic;font-size:58px;line-height:1.22}}
.ph{{position:absolute;border-radius:30px;overflow:hidden;box-shadow:0 20px 50px rgba(15,20,60,.25)}}
.ph img{{width:100%;height:100%;object-fit:cover}}
.cta{{background:{t['dark']};color:#fff}}
.wq{{font-family:Lora;font-style:italic;font-weight:600;font-size:92px;line-height:1}}
.wq u{{text-decoration:none;border-bottom:4px solid {t['acc2']};padding-bottom:6px}}
.wf{{display:inline-block;position:relative;background:{t['acc2']};color:{t['dark']};font-weight:900;font-size:56px;letter-spacing:4px;
  padding:14px 64px 14px 36px;clip-path:polygon(0 0,100% 0,88% 50%,100% 100%,0 100%)}}
.wg{{font-weight:900;font-size:70px;letter-spacing:3px;text-shadow:0 0 28px {t['acc2']},0 0 10px {t['acc2']}}}
.ws{{position:absolute;right:46px;top:50%;transform:translateY(-50%) rotate(90deg);transform-origin:center;font-weight:900;font-size:60px;letter-spacing:10px;color:{t['acc2']}}}
.disc{{position:absolute;left:56px;right:56px;bottom:30px;font-size:19px;opacity:.7}}
.big{{font-size:170px;font-weight:900;line-height:.9;color:{t['acc']}}}
"""


def page(t, body, cls=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css(THEMES[t])}</style></head><body class="{cls}">{body}</body></html>'


def top(n, total, white=False):
    return f'<div class="top {"w" if white else ""}"><span>[ {n:02d}/{total:02d} ]</span><span>{NICK}</span></div>'


DISC = "Інформація має ознайомчий характер і не замінює особистої консультації."

# ===================== 28.11 A · 💥 Руйнівник міфів · «Цукор: найсильніший легальний наркотик?» =====================
T = 6
S1 = [
    page("blue", f"""<div class="full"><img src="{img('g-011.jpg')}" style="object-position:center 30%"></div><div class="shade-t"></div>{top(1, T, True)}
<div style="position:absolute;left:56px;right:56px;top:150px;color:#fff">
  <span class="pl2">МІФ ЧИ ПРАВДА?</span>
  <h1 style="margin-top:30px">Цукор: найсильніший <i class="s ac2">легальний наркотик?</i></h1>
</div>
<div style="position:absolute;left:56px;right:56px;bottom:70px;color:#fff" class="p">Гортайте, і ви по-іншому подивитесь на «лише одну цукерочку» 👉</div>"""),
    page("blue", f"""{top(2, T)}
<div style="position:absolute;left:70px;right:70px;top:170px">
  <div class="quote">«Я просто люблю солодке, це ж не залежність»</div>
  <div class="p" style="margin-top:46px">Так думала і я. А тепер подивіться, що відбувається всередині. Солодощі викликають <b>викид дофаміну</b>, гормону радості й винагороди. Мозок запам'ятовує: цукерка дорівнює задоволенню.</div>
  <div class="p">І просить повторити. Так запускається <span class="hl"><b>гедоністичне коло</b></span>, з якого силою волі вийти майже неможливо. Справа не у вашому характері.</div>
</div>"""),
    page("blue", f"""<div class="full"><img src="{img('g-004.jpg')}" style="object-position:center 40%"></div><div class="shade-b"></div>{top(3, T, True)}
<div style="position:absolute;left:56px;right:56px;bottom:90px;color:#fff">
  <span class="pl">ЩО КАЖУТЬ ДОСЛІДЖЕННЯ</span>
  <div class="p" style="margin-top:26px;font-size:40px;line-height:1.38">Механізми залежності від цукру <b>біохімічно схожі</b> на залежність від наркотичних речовин. Тому її нині ставлять в один ряд із залежністю від алкоголю.</div>
</div>"""),
    page("blue", f"""{top(4, T)}
<div class="ph" style="right:56px;top:120px;width:420px;height:420px"><img src="{img('g-089.jpg')}"></div>
<div style="position:absolute;left:70px;width:500px;top:150px">
  <span class="pl">«АЛЕ Ж Я ТРОХИ»</span>
  <h2 style="margin-top:26px">Чому одна <i class="s ac">не&nbsp;зупиняє?</i></h2>
</div>
<div style="position:absolute;left:70px;right:70px;top:600px">
  <div class="p">Надлишок цукру порушує роботу <b>лептину</b>, гормону, який контролює голод. Тому після «шматочка» хочеться ще, а вага повзе вгору.</div>
  <div class="p">А далі те, що ми помічаємо не одразу: висипання на шкірі, <span class="hl">інсулінорезистентність</span>, кандидоз, руйнування колагену і швидше старіння.</div>
</div>"""),
    page("blue", f"""<div class="full"><img src="{img('g-002.jpg')}" style="object-position:center 25%"></div><div class="shade-b"></div>{top(5, T, True)}
<div style="position:absolute;left:56px;right:56px;bottom:80px;color:#fff">
  <h2>Я сама була <i class="s ac2">ще тією ласункою</i></h2>
  <div class="p" style="margin-top:22px">Усе б віддала за шматочок тортика чи круасана. Сьогодні вдома в мене немає цукру, глюкоза в нормі, а мій <b>біологічний вік майже удвічі менший</b> за паспортний.</div>
</div>"""),
    page("blue", f"""{top(6, T, True)}
<div style="position:absolute;left:70px;right:70px;top:180px">
  <h2>Як вийти з цього кола <i class="s">без&nbsp;зриву?</i></h2>
  <div class="p" style="margin-top:28px;color:#dfe4ff">У гайді <b style="color:#fff">«Як приборкати тягу до солодкого»</b> я розібрала 7 справжніх причин тяги, приховані цукри в продуктах і безпечні альтернативи смаколикам.</div>
  <div class="p" style="color:#dfe4ff">До 31 грудня <b style="color:#fff">310,5 грн</b> замість 621.</div>
  <div class="p" style="margin-top:50px">Напишіть у коментарях слово <span class="wq"><u>«Цукор»</u></span></div>
  <div class="p" style="color:#dfe4ff">і я надішлю вам усе про гайд ❤</div>
</div>""", "cta"),
]

# ===================== 28.11 B · 🔥 Живий продаючий · адвент =====================
S2 = [
    page("green", f"""<div class="full"><img src="{img('g-090.jpg')}" style="object-position:center"></div><div class="shade-b"></div>{top(1, T, True)}
<div style="position:absolute;left:56px;right:56px;bottom:90px;color:#fff">
  <span class="pl2">ПОДАРУНОК ДО СВЯТ</span>
  <h1 style="margin-top:28px">Свята до 31-го, а&nbsp;в&nbsp;січні <i class="s">«живіт як камінь»?</i></h1>
</div>"""),
    page("green", f"""{top(2, T)}
<div class="ph" style="left:70px;right:70px;top:100px;height:400px"><img src="{img('g-088.jpg')}" style="object-position:center 40%"></div>
<div style="position:absolute;left:70px;right:70px;bottom:110px">
  <div class="p">Знаю цей сценарій. Спершу корпоратив, потім день народження подруги, потім Миколай, Святвечір, Новий рік. Салати з майонезом, торти, «ну ще шматочок, це ж свято».</div>
  <div class="p">А в січні важкість, здуття, сонливість після їжі і <b>мінус енергія на весь місяць</b>. Ми ніби платимо за грудень своїм самопочуттям.</div>
  <div class="quote ac" style="margin-top:40px;font-size:52px">Цього року я хочу, щоб у вас було інакше.</div>
</div>"""),
    page("green", f"""{top(3, T)}
<div class="ph" style="left:56px;top:110px;width:520px;height:700px"><img src="{img('advent/prev/1_kalendar.jpg')}" style="object-position:top"></div>
<div style="position:absolute;left:610px;right:56px;top:160px">
  <span class="pl">З 1 ГРУДНЯ</span>
  <h2 style="margin-top:24px;font-size:56px">31 віконце <i class="s ac">«Здорові свята»</i></h2>
</div>
<div style="position:absolute;left:70px;right:70px;top:860px" class="p">Щоранку о 9:00 відкривається одне віконце: святковий рецепт з мого збірника <b>без цукру, глютену і лактози</b> або підказка, як пройти застілля без переїдання.</div>"""),
    page("green", f"""<div class="full"><img src="{img('advent/r/r14.jpg')}" style="object-position:center 35%"></div><div class="shade"></div>{top(4, T, True)}
<div style="position:absolute;left:70px;right:70px;top:300px" class="card">
  <div class="quote" style="font-size:52px">«Значить, олів'є не можна?»</div>
  <div class="p" style="margin-top:22px">Можна! Із запеченими овочами, курячою грудкою і <b>заправкою з грецького йогурту</b> замість майонезу. Смак знайомий, а важкості немає. Це віконце №3.</div>
</div>"""),
    page("green", f"""{top(5, T)}
<div class="ph" style="right:56px;bottom:90px;width:460px;height:690px"><img src="{img('g-049.jpg')}" style="object-position:top"></div>
<div style="position:absolute;left:70px;width:500px;top:150px">
  <h2>А на Святвечір <i class="s ac">подарунок</i> 🎁</h2>
  <div class="p" style="margin-top:28px">Моє <b>«Здорове меню на тиждень»</b>: сніданки, обіди, вечері і конструктор здорової тарілки, щоб після свят повернутись у ритм легко.</div>
  <div class="p" style="font-size:28px;margin-top:30px;opacity:.85">Валентина Швець, нутриціолог, 15+ років допомагаю сім'ям жити без харчових залежностей і хвороб</div>
</div>"""),
    page("green", f"""{top(6, T, True)}
<div style="position:absolute;left:70px;right:70px;top:230px">
  <h2>Хочете такий грудень?</h2>
  <div class="p" style="margin-top:34px">Напишіть у коментарях</div>
  <div style="margin-top:22px"><span class="wf">АДВЕНТ</span></div>
  <div class="p" style="margin-top:36px;color:#e3f3e8">і я надішлю вам календар. Перше віконце відкриється 1 грудня о 9:00 ❤</div>
</div>""", "cta"),
]

SETS = {"d28a": S1, "d28b": S2}


def build(keys):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for key in keys:
            for i, html in enumerate(SETS[key], 1):
                pg.set_content(html, wait_until="load")
                pg.wait_for_timeout(250)
                pg.screenshot(path=os.path.join(OUT, f"{key}_{i}.jpg"), type="jpeg", quality=92)
        b.close()


if __name__ == "__main__":
    build(sys.argv[1:] or list(SETS))
    print("ok")
