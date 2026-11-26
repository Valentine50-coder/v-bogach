"""26.11.2026: сторінка-календар адвенту «Здорові свята» (зелений, білий, рожевий, як каруселі Валентини про кишківник).
Дані беруться з advent_data.W. Запуск: python tools/advent_page.py <папка> → <папка>/index.html, img/, menu.pdf.
Публікується в tafijcuktetana12-coder/agents, папка kyshkivnyk/advent (GitHub Pages), відкривається з агента кнопкою web_app."""
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from advent_data import W  # noqa: E402

BOT = "valentina_shvets_bot"

PAGE = r"""<!doctype html><html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Адвент «Здорові свята»</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">
<style>
:root{--g:#1d5b3c;--g2:#2f7d55;--mint:#e6f4ec;--pink:#e0457b;--ink:#1d2a22}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Montserrat,system-ui,sans-serif;color:var(--ink);min-height:100vh;
background:linear-gradient(180deg,#e3f3e9 0%,#ffffff 55%,#fdf0f4 100%);padding:22px 16px 40px;overflow-x:hidden}
.tag{display:inline-block;background:var(--g);color:#fff;font-weight:800;font-size:11px;letter-spacing:2px;padding:6px 12px;border-radius:20px}
h1{font-weight:800;font-size:34px;line-height:1.05;color:var(--g);margin-top:12px}
h1 i{font-family:'Playfair Display',serif;color:var(--pink)}
.sub{font-size:14px;line-height:1.45;margin:10px 0 4px;color:#3b4a40}
.info{font-size:13px;font-weight:600;color:var(--g2);margin-top:8px}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px 6px;margin:20px 0 10px}
.ball{text-align:center;cursor:pointer;position:relative}
.ball .cap{width:8px;height:7px;background:#c9d6cd;margin:0 auto;border-radius:2px}
.ball .b{width:54px;height:54px;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;
font-weight:800;font-size:17px;box-shadow:0 8px 16px rgba(29,91,60,.25);transition:transform .25s}
.green{background:radial-gradient(circle at 35% 30%,#8fd3ac,#2f7d55 45%,#123d27);color:#fff}
.white{background:radial-gradient(circle at 35% 30%,#ffffff,#eef7f1 50%,#bcd8c6);color:var(--g)}
.pinkb{background:radial-gradient(circle at 35% 30%,#ffc1d6,#e0457b 45%,#8a1d45);color:#fff}
.lock{opacity:.38;filter:saturate(.6)}
.today .b{box-shadow:0 0 0 3px #fff,0 0 0 6px var(--pink),0 0 24px rgba(224,69,123,.6);animation:pulse 1.8s infinite}
.seen .b::after{content:'✓';position:absolute;font-size:11px;margin:38px 0 0 38px;background:#fff;color:var(--g);border-radius:50%;width:18px;height:18px;line-height:18px}
@keyframes pulse{50%{transform:scale(1.08)}}
.gift{position:absolute;top:-6px;right:2px;font-size:15px}
.legend{font-size:12px;color:#5d6b62;text-align:center;margin-bottom:14px}
.ov{position:fixed;inset:0;background:rgba(18,40,28,.55);display:none;align-items:flex-end;justify-content:center;z-index:9}
.ov.on{display:flex}
.card{background:#fff;width:100%;max-width:520px;max-height:88vh;overflow:auto;border-radius:24px 24px 0 0;padding:0 0 20px;animation:up .3s}
@keyframes up{from{transform:translateY(40px);opacity:0}}
.card img{width:100%;display:block;border-radius:24px 24px 0 0}
.cb{padding:16px 18px 0}
.cb small{color:var(--pink);font-weight:800;font-size:12px;letter-spacing:1px}
.cb h3{color:var(--g);font-size:20px;line-height:1.2;margin:6px 0 10px}
.cb p{font-size:15px;line-height:1.55}
.cb code{background:var(--mint);color:var(--g);padding:1px 6px;border-radius:6px;font-weight:800}
.btn{display:block;width:100%;border:0;border-radius:14px;padding:14px;font:800 15px Montserrat,sans-serif;margin-top:12px;cursor:pointer;text-align:center;text-decoration:none}
.bg{background:var(--g);color:#fff}.bp{background:var(--pink);color:#fff}.bl{background:var(--mint);color:var(--g)}
.snow{position:fixed;top:-12px;color:#9fd1b4;pointer-events:none;animation:fall linear infinite;z-index:0}
@keyframes fall{to{transform:translateY(110vh) rotate(180deg)}}
.wrap{position:relative;z-index:1}
.note{font-size:11px;color:#7a877f;text-align:center;margin-top:16px}
</style></head><body><div class="wrap">
<span class="tag">АДВЕНТ · ГРУДЕНЬ</span>
<h1>Здорові <i>свята</i></h1>
<p class="sub">31 віконце: корисні святкові рецепти з мого збірника, поради, як відсвяткувати без наслідків, і подарунок ❤</p>
<div class="info" id="info"></div>
<div class="grid" id="grid"></div>
<div class="legend">🎁 24 грудня подарунок · кожне віконце відкривається у свій день о 9:00</div>
<div class="note">Валентина Швець · нутриціолог, health-коуч<br>Меню не замінює особистої консультації спеціаліста</div>
</div>
<div class="ov" id="ov" onclick="if(event.target.id==='ov')cl()"><div class="card" id="card"></div></div>
<script>
const D=__DATA__,BOT="__BOT__";
const tg=window.Telegram&&Telegram.WebApp;if(tg){tg.expand();tg.setHeaderColor&&tg.setHeaderColor('#e3f3e9')}
for(let i=0;i<22;i++){const s=document.createElement('div');s.className='snow';s.textContent=i%3?'❄':'✦';s.style.left=Math.random()*100+'vw';
s.style.animationDuration=(7+Math.random()*9)+'s';s.style.animationDelay=(-Math.random()*12)+'s';s.style.fontSize=(9+Math.random()*12)+'px';document.body.appendChild(s)}
function kyiv(){const p=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Kyiv',year:'numeric',month:'numeric',day:'numeric',hour:'numeric',hour12:false}).formatToParts(new Date());
 const g=t=>+p.find(x=>x.type===t).value;return{y:g('year'),m:g('month'),d:g('day'),h:g('hour')}}
function openN(){const k=kyiv();if(k.y>2026)return 31;if(k.y<2026||k.m<12)return 0;return k.h>=9?k.d:k.d-1}
let seen={};try{seen=JSON.parse(localStorage.getItem('av_seen')||'{}')}catch(e){}
const N=openN();
function plural(n){const a=n%10,b=n%100;return a==1&&b!=11?'день':a>=2&&a<=4&&(b<10||b>=20)?'дні':'днів'}
function info(){const el=document.getElementById('info');
 if(N==0){const k=kyiv();const left=k.m==11?31-k.d:1;el.textContent='Старт 1 грудня о 9:00 · ще '+left+' '+plural(left);}
 else el.textContent=N>=31?'Усі 31 віконце відкриті ❤':'Сьогодні відкрито віконце '+N+' з 31';}
function draw(){const g=document.getElementById('grid');g.innerHTML='';
 D.forEach((w,i)=>{const n=i+1,op=n<=N;const el=document.createElement('div');
  const col=w.k==='gift'||w.k==='book'?'pinkb':(n%2?'green':'white');
  el.className='ball'+(op?'':' lock')+(n==N?' today':'')+(seen[n]?' seen':'');
  el.innerHTML='<div class="cap"></div><div class="b '+col+'">'+n+'</div>'+(w.k==='gift'?'<span class="gift">🎁</span>':'');
  el.onclick=()=>op?show(n):lockMsg(n);g.appendChild(el)})}
function lockMsg(n){const t='Це віконце відкриється '+n+' грудня о 9:00 😉';if(tg&&tg.showAlert)tg.showAlert(t);else alert(t)}
function link(u){if(tg&&tg.openTelegramLink){tg.openTelegramLink(u)}else location.href=u}
function show(n){const w=D[n-1];seen[n]=1;try{localStorage.setItem('av_seen',JSON.stringify(seen))}catch(e){}
 let h=(w.img?'<img src="img/'+w.img+'.jpg" alt="">':'')+'<div class="cb"><small>ВІКОНЦЕ '+n+' · '+n+' ГРУДНЯ</small><h3>'+w.t+'</h3><p>'+w.x.replace(/\n/g,'<br>')+'</p>';
 if(w.k==='gift')h+='<a class="btn bp" href="menu.pdf" target="_blank">🎁 Забрати «Здорове меню на тиждень»</a>';
 if(w.k==='book')h+='<button class="btn bp" onclick="link(\'https://t.me/'+BOT+'?start=abook\')">🎄 Забронювати за 159 грн</button>';
 h+='<button class="btn bl" onclick="cl()">До календаря</button></div>';
 document.getElementById('card').innerHTML=h;document.getElementById('ov').classList.add('on');draw();
 tg&&tg.HapticFeedback&&tg.HapticFeedback.impactOccurred('light')}
function cl(){document.getElementById('ov').classList.remove('on')}
info();draw();
const q=new URLSearchParams(location.search).get('d');if(q&&+q<=N)show(+q);
</script></body></html>"""


def main(out):
    os.makedirs(os.path.join(out, "img", "r"), exist_ok=True)
    data = []
    for pic, title, text, *k in W:
        data.append({"img": pic, "t": title, "x": text, "k": k[0] if k else ""})
        if pic:
            shutil.copy(os.path.join(ROOT, "images", "advent", pic + ".jpg"), os.path.join(out, "img", pic + ".jpg"))
    shutil.copy(os.path.join(ROOT, "media", "zdorove_menu_tyzhden.pdf"), os.path.join(out, "menu.pdf"))
    html = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__BOT__", BOT)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(html)
    print("ok", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "advent"))
