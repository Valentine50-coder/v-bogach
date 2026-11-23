"""23.11: реклама Meta через агента Валентини (перенесено з realtor-bot annads.py, той самий механізм, що в Тетяни й Анни).

Реклама з готового допису Instagram за посиланням (/reklama_post), повторний показ тим, хто взаємодіяв,
статистика і керування (/reklama_stat), сповіщення адмінам про людей з реклами (?start=ads9).
Змінні Railway: META_ADS_TOKEN, META_AD_ACCOUNT, META_PAGE_ID.
"""
import asyncio
import html
import json
import logging
import math
import os
import time

import httpx
from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from telegram.constants import ParseMode

log = logging.getLogger("adsrun")
VER = os.environ.get("FB_GRAPH_VER", "v23.0")
G = f"https://graph.facebook.com/{VER}"
HERE = os.path.dirname(os.path.abspath(__file__))
LINK = "https://t.me/valentina_shvets_bot?start=ads"


def link(n):
    """22.11: у кожного ролика своє посилання (ads1..ads3), щоб видно, який привів людину."""
    return f"{LINK}{n}"
USD = 5  # 23.11: рекомендований бюджет на добу
INTERESTS = ["Nutrition", "Healthy diet", "Health & wellness", "Dietary supplement", "Gastroenterology"]  # 23.11: тема здоров'я кишківника
TEXT = ("Здуття, важкість, закрепи чи висипання часто починаються в кишківнику.\n\n"
        "Пройдіть коротку діагностику в Telegram і дізнайтесь, з чого почати саме вам 👇")
VARS = {}  # готових роликів у Валентини немає: реклама з її дописів
ALL, POST = 0, 9  # 23.11: 0 = усі 3 ролики в одному показі (Meta сама дає гроші найкращому), 9 = готовий допис з Instagram
VALID = {POST}
LABELS = {**VARS, ALL: "усі 3 ролики разом", POST: "допис з Instagram"}
BUDGETS = (1, 3, 5, 10)


def _kv(k, v=None):
    import db
    if v is None:
        return db.flag_get(k) or ""
    db.flag_set(k, v)
    return v


def _admins():
    import config as C
    return list(C.ADMIN_IDS)


def _admin():
    a = _admins()
    return a[0] if a else 0


def _is_adm(uid):
    return uid in _admins()


def token():
    t = os.environ.get("META_ADS_TOKEN", "").strip() or os.environ.get("FB_ADS_TOKEN", "").strip()
    if t:
        return t
    return ""


class MetaError(Exception):
    pass


async def _req(c, method, path, **kw):
    params = dict(kw.pop("params", {}) or {})
    params["access_token"] = token()
    r = await c.request(method, G + "/" + path.lstrip("/"), params=params, **kw)
    try:
        j = r.json()
    except Exception:
        raise MetaError(f"HTTP {r.status_code}")
    if "error" in j:
        e = j["error"]
        raise MetaError((e.get("error_user_msg") or e.get("message") or str(e))[:400])
    return j


async def setup_info(c):
    """Повертає dict: perms, account{id,currency,name}, page{id,name}, ig."""
    me = await _req(c, "GET", "me/permissions")
    perms = {p["permission"] for p in me.get("data", []) if p.get("status") == "granted"}
    acc_env = os.environ.get("META_AD_ACCOUNT", "").strip()
    accs = (await _req(c, "GET", "me/adaccounts", params={"fields": "account_id,name,currency,account_status", "limit": 50})).get("data", [])
    acc = None
    for a in accs:
        if acc_env and acc_env.replace("act_", "") == a.get("account_id"):
            acc = a
            break
    if not acc:
        acc = next((a for a in accs if a.get("account_status") == 1), accs[0] if accs else None)
    page_env = os.environ.get("META_PAGE_ID", "").strip()
    pages = (await _req(c, "GET", "me/accounts", params={"fields": "id,name,instagram_business_account", "limit": 50})).get("data", [])
    page = next((p for p in pages if p["id"] == page_env), pages[0] if pages else None)
    ig = ((page or {}).get("instagram_business_account") or {}).get("id") or _kv("fb_ig_id") or ""
    return {"perms": perms, "acc": acc, "accs": len(accs), "page": page, "ig": ig}


async def _budget(cur, usd=USD):
    """usd доларів у мінімальних одиницях валюти кабінету (копійки, центи)."""
    cur = (cur or "USD").upper()
    if cur == "USD":
        return usd * 100
    rate = None
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
            d = {x["cc"]: x["rate"] for x in r.json()}
        if cur == "UAH":
            rate = d["USD"]
        elif cur in d:
            rate = d["USD"] / d[cur]
    except Exception as e:
        log.warning("nbu: %s", e)
    if not rate:
        rate = 42.0 if cur == "UAH" else 1.0
    return int(math.ceil(usd * rate)) * 100


def _app_rows():
    return []  # в агента Валентини немає застосунку (без веб-сервера)


async def cmd(update, context):
    if not _is_adm(update.effective_user.id):
        return
    await show(context.bot, update.effective_chat.id)


async def show(bot, chat):
    if not token():
        await bot.send_message(chat, "📣 <b>Реклама через агента</b>\n\nУ Railway немає змінної <code>META_ADS_TOKEN</code>. "
                                     "Перевірка: /reklama_test", parse_mode=ParseMode.HTML)
        return
    await bot.send_message(chat, "📣 <b>Реклама через агента</b>\n\n"
                                 "Беремо ваш <b>готовий допис чи рілс з Instagram</b> і показуємо його як рекламу з кнопкою «Детальніше», "
                                 "яка веде в агента. Агент сам пише вам про кожну людину з реклами.\n\n"
                                 "<b>Як запустити:</b> скопіюйте посилання на допис (під дописом «Поділитися» → «Копіювати посилання») і надішліть так:\n"
                                 "<code>/reklama_post https://www.instagram.com/p/…</code>\n\n"
                                 "<i>Агент порадить: 3 дні, $5 на добу, Meta сама підбирає аудиторію. Не підійде допис з музикою з бібліотеки Instagram.</i>\n\n"
                                 "Статистика і керування: /reklama_stat · перевірка доступу: /reklama_test", parse_mode=ParseMode.HTML)


async def on_callback(update, context, data):
    q = update.callback_query
    if not _is_adm(q.from_user.id):
        return
    p = data.split(":")
    if p[1] in ("m", "v", "d", "b", "g"):
        await _flow(q, p)
        return
    if p[1] == "x":
        await _manage(q, p)
        return
    if p[1] == "pst":  # 23.11: реклама з готового допису
        await q.message.reply_text("Надішліть посилання на допис так:\n<code>/reklama_post https://www.instagram.com/p/…</code>\n\n"
                                   "<i>Скопіювати посилання: під дописом «Поділитися» → «Копіювати посилання». "
                                   "Не підійде допис з музикою з бібліотеки Instagram.</i>", parse_mode=ParseMode.HTML)
        return
    n = int(p[2]) if len(p) > 2 and p[2].isdigit() else 0
    if n not in VARS:
        return
    if p[1] == "ask":
        if _kv(f"adr_done:{n}"):
            await q.message.reply_text(f"Варіант {n} уже запущено ❤ Подивитися: /reklama_stat")
            return
        await q.message.reply_text(f"Запускаю <b>варіант {n}</b> на 1 добу з бюджетом близько <b>${USD}</b> з вашого рекламного кабінету. Точно?",
                                   parse_mode=ParseMode.HTML, reply_markup=M([[B("✅ Так, запустити", callback_data=f"adr:go:{n}")]]))
    elif p[1] == "go":
        if _kv(f"adr_done:{n}"):
            return
        _kv(f"adr_done:{n}", "busy")
        await q.message.reply_text(f"⏳ Запускаю варіант {n}: завантажую ролик і налаштовую. Це 1-3 хвилини…")
        try:
            res = await launch(n)
            _kv(f"adr_done:{n}", json.dumps(res))
            _save_run(n, "cold", res)
            await q.message.reply_text(
                f"✅ <b>Варіант {n} запущено</b>\nБюджет: {res['budget_txt']} на добу, до {res['end']}\n"
                f"Інтереси: {html.escape(', '.join(res['interests']) or 'широка аудиторія')}\n"
                "<i>Meta спершу перевіряє оголошення, зазвичай до кількох годин. Результати: /reklama_stat</i>",
                parse_mode=ParseMode.HTML)
        except Exception as e:
            _kv(f"adr_done:{n}", "")
            log.warning("adr launch %s: %s", n, e)
            await q.message.reply_text("❌ Не вдалося запустити: <i>" + html.escape(str(e)) + "</i>", parse_mode=ParseMode.HTML)


async def launch(n, mode="cold", days=1, usd=USD):
    async with httpx.AsyncClient(timeout=300) as c:
        s = await setup_info(c)
        if "ads_management" not in s["perms"]:
            raise MetaError("немає дозволу ads_management: підключіть Facebook з дозволом на рекламу")
        if not s["acc"] or not s["page"]:
            raise MetaError("не знайдено рекламний кабінет або сторінку Facebook")
        act = "act_" + s["acc"]["account_id"]
        cur = s["acc"].get("currency", "USD")
        budget = await _budget(cur, usd)
        ints, names = [], []
        auds = []
        if mode == "warm":
            auds = await audiences(c, act, s)
        for q in (INTERESTS if mode == "cold" else []):
            try:
                r = await _req(c, "GET", "search", params={"type": "adinterest", "q": q, "limit": 1, "locale": "uk_UA"})
                for it in r.get("data", [])[:1]:
                    if it["id"] not in {i["id"] for i in ints}:
                        ints.append({"id": it["id"], "name": it["name"]})
                        names.append(it["name"])
            except Exception as e:
                log.info("interest %s: %s", q, e)
        stamp = time.strftime("%d.%m %H:%M")
        camp = await _req(c, "POST", f"{act}/campaigns", data={
            "name": f"Агент: {'повторно' if mode == 'warm' else 'нові'} {LABELS.get(n, n)} {stamp}", "objective": "OUTCOME_TRAFFIC", "status": "ACTIVE",
            "special_ad_categories": "[]", "is_adset_budget_sharing_enabled": "false"})
        now = int(time.time()) + 120
        if mode == "warm":
            targeting = {"geo_locations": {"countries": ["UA"]}, "age_min": 18,
                         "custom_audiences": [{"id": a["id"]} for a in auds], "targeting_automation": {"advantage_audience": 0}}
            names = [a["label"] for a in auds]
        else:
            # 23.11: автоматичний підбір аудиторії Meta (Advantage+), інтереси лише підказка; жорстко тільки Україна і 22+
            targeting = {"geo_locations": {"countries": ["UA"]}, "age_min": 22,
                         "targeting_automation": {"advantage_audience": 1}}
            if ints:
                targeting["flexible_spec"] = [{"interests": ints}]
        try:
            return await _rest(c, n, s, act, cur, budget, camp, now, targeting, ints, names, stamp, days, usd, mode)
        except Exception:
            try:  # 21.11: щоб після збою не лишалось порожніх кампаній
                await _req(c, "DELETE", camp["id"])
            except Exception as e2:
                log.warning("adr delete camp: %s", e2)
            raise


def _swap_deprecated(msg, ints, names):
    """21.11: Meta пише deprecated_interest_id і alternative_interest_id: міняємо застарілі інтереси на нові."""
    import re
    try:
        alts = json.loads(re.search(r"\[\{.*\}\]", msg).group(0))
    except Exception:
        return False
    changed = False
    for a in alts:
        old_id, new_id = str(a.get("deprecated_interest_id")), a.get("alternative_interest_id")
        for i, it in enumerate(list(ints)):
            if it["id"] == old_id:
                if new_id and str(new_id) not in {x["id"] for x in ints}:
                    ints[i] = {"id": str(new_id), "name": a.get("alternative_interest_name") or ""}
                    names[i] = ints[i]["name"]
                else:
                    ints.pop(i)
                    names.pop(i)
                changed = True
    return changed


async def _rest(c, n, s, act, cur, budget, camp, now, targeting, ints, names, stamp, days=1, usd=USD, mode="cold"):
    for attempt in range(3):
        if mode != "warm":
            if ints:
                targeting["flexible_spec"] = [{"interests": ints}]
            else:
                targeting.pop("flexible_spec", None)
        try:
            adset = await _req(c, "POST", f"{act}/adsets", data={
                "name": f"v{n} {'повторно 30 днів' if mode == 'warm' else 'UA 22+ авто'}", "campaign_id": camp["id"],
                "daily_budget": str(budget),
                "start_time": str(now), "end_time": str(now + 86400 * days), "billing_event": "IMPRESSIONS",
                "optimization_goal": "LINK_CLICKS", "bid_strategy": "LOWEST_COST_WITHOUT_CAP", "destination_type": "WEBSITE",
                "targeting": json.dumps(targeting), "status": "ACTIVE"})
            break
        except MetaError as e:
            if attempt < 2 and "deprecated_interest" in str(e) and _swap_deprecated(str(e), ints, names):
                continue
            raise
    ads = []
    vid = {"id": ""}
    if n == POST:
        m = json.loads(_kv("adr_post") or "{}")
        if not m.get("id"):
            raise MetaError("не знайдено допис: надішліть посилання ще раз")
        cre = await _req(c, "POST", f"{act}/adcreatives", data={
            "name": f"post {m['id']}", "object_id": s["page"]["id"], "instagram_user_id": s["ig"], "source_instagram_media_id": m["id"],
            "call_to_action": json.dumps({"type": "LEARN_MORE", "value": {"link": link(POST)}})})
        ads.append(await _req(c, "POST", f"{act}/ads", data={"name": f"допис {stamp}", "adset_id": adset["id"],
                                                         "creative": json.dumps({"creative_id": cre["id"]}), "status": "ACTIVE"}))
    for k in ([1, 2, 3] if n == ALL else [] if n == POST else [n]):
        vid = await _video_ad(c, k, s, act, adset, stamp)
        ads.append(vid.pop("ad"))
    end = time.strftime("%d.%m %H:%M", time.gmtime(now + 86400 * days + 7200))
    btxt = f"${usd}" if cur == "USD" else f"{budget // 100} {cur} (≈ ${usd})"
    return {"campaign": camp["id"], "adset": adset["id"], "ad": ads[0]["id"], "ads": [a["id"] for a in ads], "act": act, "budget_txt": btxt,
            "end": end + " (Київ)", "interests": names, "video": vid["id"], "days": days, "mode": mode}


async def _video_ad(c, n, s, act, adset, stamp):
    """Один ролик ads/v<n>.mp4 як оголошення в наборі adset (своє посилання ?start=ads<n>)."""
    with open(os.path.join(HERE, "ads", f"v{n}.mp4"), "rb") as fh:
        vid = await _req(c, "POST", f"{act}/advideos", data={"name": f"agent_carousel_v{n}"},
                         files={"source": (f"v{n}.mp4", fh, "video/mp4")})
    for _ in range(36):  # до 3 хв чекаємо обробку відео
        st = await _req(c, "GET", vid["id"], params={"fields": "status"})
        vs = (st.get("status") or {}).get("video_status")
        if vs == "ready":
            break
        if vs == "error":
            raise MetaError("Meta не змогла обробити ролик")
        await asyncio.sleep(5)
    with open(os.path.join(HERE, "ads", f"thumb{n}.jpg"), "rb") as fh:
        img = await _req(c, "POST", f"{act}/adimages", files={"filename": (f"thumb{n}.jpg", fh, "image/jpeg")})
    ih = next(iter((img.get("images") or {}).values()), {}).get("hash")
    spec = {"page_id": s["page"]["id"], "video_data": {
        "video_id": vid["id"], "image_hash": ih, "message": TEXT, "title": VARS[n],
        "call_to_action": {"type": "LEARN_MORE", "value": {"link": link(n)}}}}
    if s["ig"]:
        spec["instagram_user_id"] = s["ig"]
    cre = await _req(c, "POST", f"{act}/adcreatives", data={"name": f"agent_carousel_v{n}", "object_story_spec": json.dumps(spec)})
    ad = await _req(c, "POST", f"{act}/ads", data={"name": f"v{n} {stamp}", "adset_id": adset["id"],
                                                 "creative": json.dumps({"creative_id": cre["id"]}), "status": "ACTIVE"})
    return {"id": vid["id"], "ad": ad}


async def find_post(url):
    """23.11: допис з Instagram за посиланням: id, прев'ю і чи можна його рекламувати (boost_eligibility_info)."""
    import re
    m = re.search(r"instagram\.com/(?:[^/?#]+/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)", url or "")
    if not m:
        raise MetaError("це не схоже на посилання на допис Instagram (має бути instagram.com/p/… або /reel/…)")
    code = m.group(1)
    async with httpx.AsyncClient(timeout=60) as c:
        s = await setup_info(c)
        if not s["ig"]:
            raise MetaError("до сторінки Facebook не прив'язаний Instagram")
        path = f"{s['ig']}/media"
        params = {"fields": "id,permalink,media_type,thumbnail_url,media_url,caption,boost_eligibility_info", "limit": 50}
        pages = 0
        while pages < 6:  # до 300 останніх дописів
            try:
                r = await _req(c, "GET", path, params=params)
            except MetaError as e:
                if "boost_eligibility_info" in params["fields"]:
                    params["fields"] = params["fields"].replace(",boost_eligibility_info", "")
                    continue
                raise MetaError(f"агент не бачить дописи Instagram ({e}). Потрібен дозвіл instagram_basic у маркері")
            pages += 1
            for it in r.get("data", []):
                if f"/{code}" in (it.get("permalink") or ""):
                    be = it.get("boost_eligibility_info") or {}
                    if be and be.get("eligible_to_boost") is False:
                        raise MetaError("Meta не дозволяє рекламувати цей допис: "
                                        + str(be.get("boost_ineligible_reason") or "музика з бібліотеки Instagram або ефекти"))
                    return {"id": it["id"], "url": it.get("permalink"), "thumb": it.get("thumbnail_url") or it.get("media_url") or "",
                            "caption": (it.get("caption") or "")[:120]}
            paging = r.get("paging") or {}
            if not paging.get("next"):
                break
            params["after"] = (paging.get("cursors") or {}).get("after")
    raise MetaError("не знайшла цей допис серед останніх 300 у вашому Instagram")


async def post_cmd(update, context):
    """/reklama_post <посилання>: реклама з готового допису Instagram."""
    if not _is_adm(update.effective_user.id):
        return
    url = " ".join(context.args or []).strip()
    if not url:
        await update.message.reply_text("Надішліть так: <code>/reklama_post https://www.instagram.com/p/…</code>", parse_mode=ParseMode.HTML)
        return
    await post_pick(update.message, url)


async def post_pick(msg, url):
    w = await msg.reply_text("Шукаю допис у вашому Instagram…")
    try:
        m = await find_post(url)
    except Exception as e:
        await w.edit_text("❌ " + html.escape(str(e)), parse_mode=ParseMode.HTML)
        return
    _kv("adr_post", json.dumps(m))
    await w.edit_text(f"✅ Знайшла допис: <i>{html.escape(m['caption'] or m['url'])}</i>\n\nКому показуємо?", parse_mode=ParseMode.HTML,
                      reply_markup=M([[B("📣 Нові люди", callback_data=f"adr:v:cold:{POST}")],
                                      [B("🎯 Ті, хто вже взаємодіяв", callback_data=f"adr:v:warm:{POST}")]]))


async def stat_cmd(update, context):
    if not _is_adm(update.effective_user.id):
        return
    out = ["📊 <b>Реклама через агента</b>"]
    runs = _runs()
    for n in (1, 2, 3):  # перші запуски 21.11, до історії
        raw = _kv(f"adr_done:{n}") or ""
        if raw.startswith("{"):
            r = json.loads(raw)
            if not any(x.get("ad") == r.get("ad") for x in runs):
                runs.insert(0, dict(r, n=n, mode="cold"))
    async with httpx.AsyncClient(timeout=40) as c:
        for r in runs[-10:]:
            label = f"{'🎯 Повторно' if r.get('mode') == 'warm' else '📣 Нові люди'}, варіант {r.get('n', '?')}"
            try:
                st = await _req(c, "GET", r["ad"], params={"fields": "effective_status"})
                ins = (await _req(c, "GET", f"{r['ad']}/insights", params={"fields": "spend,impressions,reach,inline_link_clicks,cost_per_inline_link_click,actions"})).get("data") or [{}]
                i = ins[0]
                out.append(f"\n<b>{label}</b> (до {html.escape(r.get('end', '?'))}): {html.escape(_st_ua(st.get('effective_status', '?')))}\n"
                           f"Покази {i.get('impressions', 0)}, людей {i.get('reach', 0)}, переходи в агента {i.get('inline_link_clicks', 0)}, "
                           f"витрачено ${i.get('spend', 0)}, перехід {('$' + i['cost_per_inline_link_click']) if i.get('cost_per_inline_link_click') else '—'}"
                           + _actions_line(i.get("actions")))
            except Exception as e:
                out.append(f"\n<b>{label}</b>: не вдалося прочитати ({html.escape(str(e)[:120])})")
        aud = _aud()
        if aud:
            out.append("\n<b>Аудиторії для повторного показу:</b>")
            for a in aud:
                try:
                    j = await _req(c, "GET", a["id"], params={"fields": "approximate_count_lower_bound,approximate_count_upper_bound"})
                    lo, hi = j.get("approximate_count_lower_bound", -1), j.get("approximate_count_upper_bound", -1)
                    size = "поки менше 1000 людей" if (lo is None or lo < 1000) else f"{lo}-{hi} людей"
                except Exception:
                    size = "розмір ще рахується"
                out.append(f"• {html.escape(a['label'])}: {size}")
    if len(out) == 1:
        out.append("Ще нічого не запущено. /reklama")
    out.append(_people_block())
    text = "\n".join(out)
    for k in range(0, len(text), 3800):
        await update.effective_message.reply_text(text[k:k + 3800], parse_mode=ParseMode.HTML)
    seen, rows = set(), []
    for r in reversed(runs[-10:]):
        if r.get("adset") and r["adset"] not in seen and len(rows) < 6:
            seen.add(r["adset"])
            lab = f"{'🎯' if r.get('mode') == 'warm' else '📣'} в{r.get('n', '?')}"
            rows.append([B(f"⏸ {lab}", callback_data=f"adr:x:p:{r['adset']}"), B(f"▶️ {lab}", callback_data=f"adr:x:r:{r['adset']}"),
                         B(f"➕ $ {lab}", callback_data=f"adr:x:b:{r['adset']}"), B(f"📅+3 {lab}", callback_data=f"adr:x:e:{r['adset']}")])
    app = _app_rows()
    if app:
        await update.effective_message.reply_text(
            "<b>Керування рекламою</b> тепер у застосунку: зупинити, відновити, бюджет, +3 дні, нова реклама і люди з реклами 😉",
            parse_mode=ParseMode.HTML, reply_markup=M(app))
    elif rows:
        await update.effective_message.reply_text(
            "<b>Керування оголошеннями</b> (📣 нові люди, 🎯 повторно, в1-в3 номер ролика):\n⏸ зупинити · ▶️ відновити · ➕ $ бюджет на добу · 📅+3 подовжити на 3 дні",
            parse_mode=ParseMode.HTML, reply_markup=M(rows))


ACT_UA = {"video_view": "переглянули відео (3 с)", "post_engagement": "взаємодій з оголошенням", "post_reaction": "реакцій",
          "comment": "коментарів", "onsite_conversion.post_save": "збережень", "post": "поширень",
          "landing_page_view": "відкрили посилання", "like": "вподобали сторінку"}


def _actions_line(actions):
    """22.11: що ще зробили люди з оголошенням; підписки й переходи в профіль, якщо Meta їх віддає."""
    got = []
    for a in actions or []:
        t, v = a.get("action_type", ""), a.get("value", "0")
        if "follow" in t:
            got.append(f"підписались {v}")
        elif "profile" in t and "visit" in t:
            got.append(f"зайшли в профіль {v}")
        elif t in ACT_UA:
            got.append(f"{ACT_UA[t]} {v}")
    return ("\n" + ", ".join(got)) if got else ""


def _people_block():
    """Хто зайшов в агента з реклами (?start=ads…)."""
    try:
        import db
        from datetime import datetime, timedelta, timezone
        with db.conn() as c:
            rows = c.execute("SELECT k, v FROM kv WHERE k LIKE 'adr_in:%' ORDER BY v DESC LIMIT 15").fetchall()
            if not rows:
                return "\n👤 <b>Люди з реклами в агенті:</b> поки нікого"
            lines = [f"\n👤 <b>Люди з реклами в агенті: {len(rows)}</b>"]
            for r in rows:
                uid = int(r["k"].split(":")[1])
                u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
                name = ((u["name"] if u and "name" in u.keys() else "") or str(uid))
                nick = f" @{u['username']}" if u and "username" in u.keys() and u["username"] else ""
                paid = " 💰 <b>оплатила</b>" if (u and any(k in u.keys() and u[k] for k in ("int_paid", "course_paid"))) or _kv(f"cons:{uid}") == "paid" or _kv(f"jan:{uid}") else ""
                when = datetime.fromtimestamp(int(r["v"] or 0), timezone(timedelta(hours=2))).strftime("%d.%m %H:%M")
                lines.append(f"• <b>{html.escape(name)}</b>{html.escape(nick)}, {when}{paid}")
        return "\n".join(lines)
    except Exception as e:
        log.warning("ads people: %s", e)
        return ""


async def notify_visit(bot, user, is_new):
    """22.11: Адмінам одне повідомлення на кожну людину, яка прийшла з реклами."""
    if _is_adm(user.id) or _kv(f"adr_in:{user.id}"):
        return
    _kv(f"adr_in:{user.id}", str(int(time.time())))
    nick = f" @{user.username}" if user.username else ""
    v = _kv(f"adr_var:{user.id}")
    vtxt = (f"\nПривів <b>{'допис з Instagram' if int(v) == POST else 'ролик ' + v}</b>"
            f"{'' if int(v) == POST else ' (' + html.escape(VARS.get(int(v), '')) + ')'}.") if v and v.isdigit() and int(v) in (set(VARS) | {POST}) else ""
    for adm in _admins():
        try:
            await bot.send_message(adm, f"📣 <b>З реклами в агента прийшла людина:</b> {html.escape(user.full_name or '')}{html.escape(nick)}{vtxt}"
                                        f"\n{'Нова, раніше в агенті не була' if is_new else 'Уже була в агенті раніше'}. "
                                        "Список: /reklama_stat", parse_mode=ParseMode.HTML)
        except Exception as e:
            log.warning("ads notify %s: %s", adm, e)


def _st_ua(x):
    return {"ACTIVE": "✅ показується", "PAUSED": "⏸ на паузі", "PENDING_REVIEW": "⏳ на перевірці Meta",
            "DISAPPROVED": "❌ відхилено Meta", "CAMPAIGN_PAUSED": "⏸ кампанія на паузі", "ADSET_PAUSED": "⏸ на паузі",
            "WITH_ISSUES": "⚠️ є проблема", "IN_PROCESS": "⏳ обробляється", "ARCHIVED": "📦 в архіві",
            "DELETED": "видалено"}.get(x, x)


def _runs():
    try:
        return json.loads(_kv("adr_runs") or "[]")
    except Exception:
        return []


def _save_run(n, mode, res):
    runs = _runs()
    runs.append(dict(res, n=n, mode=mode, at=int(time.time())))
    _kv("adr_runs", json.dumps(runs[-30:]))


def _aud():
    try:
        return json.loads(_kv("adr_aud") or "[]")
    except Exception:
        return []


TOS_HINT = ("Meta просить один раз прийняти умови для власних аудиторій. Відкрийте з браузера "
            "<code>business.facebook.com/ads/manage/customaudiences/tos/?act={act}</code>, натисніть «Прийняти», "
            "і натисніть кнопку в агенті ще раз.")


async def _our_videos(c, act):
    """Ролики, які агент уже завантажував для реклами (для аудиторії «дивились від 50%»)."""
    ids = [r["video"] for r in _runs() if r.get("video")]
    for n in (1, 2, 3):  # перші запуски 21.11 зберегли тільки id оголошення: відео беремо з їхніх креативів
        raw = _kv(f"adr_done:{n}") or ""
        if raw.startswith("{"):
            try:
                cr = await _req(c, "GET", json.loads(raw)["ad"], params={"fields": "creative{video_id,object_story_spec}"})
                cre = cr.get("creative") or {}
                v = cre.get("video_id") or ((cre.get("object_story_spec") or {}).get("video_data") or {}).get("video_id")
                if v and v not in ids:
                    ids.append(v)
            except Exception as e:
                log.info("ad video %s: %s", n, e)
    try:
        j = await _req(c, "GET", f"{act}/advideos", params={"fields": "id,title", "limit": 50})
        for v in j.get("data", []):
            if (v.get("title") or "").startswith("agent_carousel") and v["id"] not in ids:
                ids.append(v["id"])
    except Exception as e:
        log.info("advideos: %s", e)
    return ids[:50]


async def audiences(c, act, s):
    """Аудиторії Meta для повторного показу: створюються один раз, далі Meta оновлює їх сама.
    Instagram: усі, хто взаємодіяв з профілем або рекламою за 30 днів. Відео: хто дивився наші ролики від 50% (30 днів)."""
    have = {a["key"]: a for a in _aud()}
    out = []
    try:
        if s.get("ig"):
            if "ig30" not in have:
                rule = {"inclusions": {"operator": "or", "rules": [{
                    "event_sources": [{"id": s["ig"], "type": "ig_business"}], "retention_seconds": 2592000,
                    "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": "ig_business_profile_all"}]}}]}}
                j = await _req(c, "POST", f"{act}/customaudiences", data={
                    "name": "Агент: взаємодіяли з Instagram 30 днів", "subtype": "ENGAGEMENT", "rule": json.dumps(rule),
                    "prefill": "true"})
                have["ig30"] = {"key": "ig30", "id": j["id"], "label": "взаємодіяли з Instagram за 30 днів"}
            out.append(have["ig30"])
        vids = await _our_videos(c, act)
        if vids:
            vkey = "vid50:" + ",".join(sorted(vids))
            old = next((a for k, a in have.items() if k.startswith("vid50")), None)
            if not old or old["key"] != vkey:
                rule = {"inclusions": {"operator": "or", "rules": [{
                    "event_sources": [{"id": v, "type": "video"} for v in vids], "retention_seconds": 2592000,
                    "filter": {"operator": "and", "filters": [{"field": "event", "operator": "eq", "value": "video_view_50_percent"}]}}]}}
                if old:
                    try:
                        await _req(c, "POST", old["id"], data={"rule": json.dumps(rule)})
                        new = dict(old, key=vkey)
                    except MetaError:
                        new = None
                else:
                    new = None
                if not new:
                    j = await _req(c, "POST", f"{act}/customaudiences", data={
                        "name": "Агент: дивились наші ролики від 50%", "subtype": "ENGAGEMENT", "rule": json.dumps(rule),
                        "prefill": "true"})
                    new = {"key": vkey, "id": j["id"], "label": "дивились наші рекламні ролики від половини"}
                have = {k: a for k, a in have.items() if not k.startswith("vid50")}
                have[vkey] = new
            out.append(have[vkey])
    except MetaError as e:
        if "term" in str(e).lower() or "умов" in str(e).lower() or "2654" in str(e):
            raise MetaError("TOS")
        raise
    finally:
        _kv("adr_aud", json.dumps(list(have.values())))
    if not out:
        raise MetaError("не вдалося зібрати аудиторію: немає Instagram і ще немає запущених роликів")
    return out


async def _flow(q, p):
    """Кнопки «Продовжити» / «Показати повторно»: adr:m:<mode> → adr:v:<mode>:<n> → adr:d:...:<days> → adr:b:...:<usd> → adr:g."""
    msg = q.message
    mode = p[2] if len(p) > 2 and p[2] in ("cold", "warm") else "cold"
    what = "тим, хто вже взаємодіяв" if mode == "warm" else "на нових людей"
    if p[1] == "m":
        await msg.reply_text(f"Що показуємо {what}?",
                             parse_mode=ParseMode.HTML, reply_markup=M(
            ([[B("📌 Той самий допис", callback_data=f"adr:v:{mode}:{POST}")]] if _kv("adr_post") else [])
            + [[B("📌 Інший допис з Instagram", callback_data="adr:pst")]]))
    elif p[1] == "v":
        n = p[3]
        await msg.reply_text("На скільки днів?\n<i>Раджу 3 дні: за добу Meta ще не встигає зрозуміти, кому показувати.</i>", parse_mode=ParseMode.HTML,
                             reply_markup=M([[B(f"{'✅ ' if d == 3 else ''}{d} {'доба' if d == 1 else 'дні' if d == 3 else 'днів'}", callback_data=f"adr:d:{mode}:{n}:{d}") for d in (1, 3, 7)]]))
    elif p[1] == "d":
        n, d = p[3], p[4]
        await msg.reply_text("Скільки на добу?\n<i>Раджу від $5: з меншим бюджетом Meta не встигає навчитись, кому показувати.</i>",
                             parse_mode=ParseMode.HTML, reply_markup=M([[B(f"{'✅ ' if u == 5 else ''}${u}", callback_data=f"adr:b:{mode}:{n}:{d}:{u}") for u in BUDGETS]]))
    elif p[1] == "b":
        n, d, u = int(p[3]), int(p[4]), int(p[5])
        who = ("тим, хто <b>взаємодіяв з вашим Instagram за 30 днів</b> і хто <b>дивився наші ролики від половини</b>"
               if mode == "warm" else "<b>новим людям</b>: Україна 22+, Meta сама підбирає аудиторію")
        note = ("\n\n<i>Якщо таких людей поки мало, Meta показуватиме повільно або не покаже зовсім. "
                "Тоді краще спершу покрутити рекламу на нових людей кілька днів.</i>" if mode == "warm" else "")
        await msg.reply_text(f"Запускаю <b>{LABELS.get(n, n)}</b> {who}: <b>${u} на добу × {d}</b> = до <b>${u * d}</b> з вашого кабінету. Точно?{note}",
                             parse_mode=ParseMode.HTML, reply_markup=M([[B("✅ Так, запустити", callback_data=f"adr:g:{mode}:{n}:{d}:{u}")]]))
    elif p[1] == "g":
        n, d, u = int(p[3]), int(p[4]), int(p[5])
        if d not in (1, 3, 7) or u not in BUDGETS or n not in VALID:
            return
        lock = f"adr_go:{q.id}"
        if _kv(lock) or _kv("adr_busy") == "1":
            return
        _kv(lock, "1")
        _kv("adr_busy", "1")
        try:
            await msg.reply_text("⏳ Запускаю: завантажую ролик і налаштовую. Це 1-3 хвилини…")
            res = await launch(n, mode, d, u)
            _save_run(n, mode, res)
            await msg.reply_text(
                f"✅ <b>Запущено: {LABELS.get(n, n)}, {('повторний показ' if mode == 'warm' else 'нові люди')}</b>\n"
                f"Бюджет: {res['budget_txt']} на добу, до {res['end']}\n"
                f"{'Аудиторії' if mode == 'warm' else 'Інтереси'}: {html.escape(', '.join(res['interests']) or 'широка аудиторія')}\n"
                "<i>Meta спершу перевіряє оголошення, зазвичай до кількох годин. Результати: /reklama_stat</i>",
                parse_mode=ParseMode.HTML)
        except Exception as e:
            log.warning("adr flow %s: %s", n, e)
            if str(e) == "TOS":
                acc = ""
                try:
                    async with httpx.AsyncClient(timeout=30) as c:
                        acc = ((await setup_info(c))["acc"] or {}).get("account_id", "")
                except Exception:
                    pass
                await msg.reply_text("⚠️ " + TOS_HINT.format(act=acc), parse_mode=ParseMode.HTML)
            else:
                await msg.reply_text("❌ Не вдалося запустити: <i>" + html.escape(str(e)) + "</i>", parse_mode=ParseMode.HTML)
        finally:
            _kv("adr_busy", "")


async def _manage(q, p):
    """22.11: кнопки під /reklama_stat: adr:x:<p|r|b|B<usd>|e>:<adset_id>."""
    msg = q.message
    if len(p) < 4 or not p[3].isdigit():
        return
    op, adset = p[2], p[3]
    if op == "b":
        await msg.reply_text("Який бюджет поставити на добу?", reply_markup=M([[B(f"${u}", callback_data=f"adr:x:B{u}:{adset}") for u in (1, 3, 5, 10)]]))
        return
    try:
        async with httpx.AsyncClient(timeout=40) as c:
            if op == "p":
                await _req(c, "POST", adset, data={"status": "PAUSED"})
                await msg.reply_text("⏸ Зупинила. Відновити можна кнопкою ▶️ у /reklama_stat")
            elif op == "r":
                info = await _req(c, "GET", adset, params={"fields": "end_time"})
                end = info.get("end_time")
                await _req(c, "POST", adset, data={"status": "ACTIVE"})
                await msg.reply_text("▶️ Відновила." + (f" Діє до {html.escape(end[:16].replace('T', ' '))}. Якщо дата вже минула, натисніть 📅+3" if end else ""))
            elif op.startswith("B") and op[1:].isdigit() and int(op[1:]) in (1, 3, 5, 10):
                u = int(op[1:])
                s = await setup_info(c)
                cur = ((s.get("acc") or {}).get("currency") or "USD")
                budget = await _budget(cur, u)
                await _req(c, "POST", adset, data={"daily_budget": str(budget)})
                await msg.reply_text(f"➕ Тепер бюджет <b>${u} на добу</b>" + ("" if cur == "USD" else f" ({budget // 100} {html.escape(cur)})"), parse_mode=ParseMode.HTML)
            elif op == "e":
                info = await _req(c, "GET", adset, params={"fields": "end_time,status"})
                from datetime import datetime
                try:
                    old = int(datetime.fromisoformat(info["end_time"]).timestamp())
                except Exception:
                    old = 0
                new = max(old, int(time.time()) + 300) + 3 * 86400
                await _req(c, "POST", adset, data={"end_time": str(new), "status": "ACTIVE"})
                await msg.reply_text("📅 Подовжила на 3 дні, до " + time.strftime("%d.%m %H:%M", time.gmtime(new + 7200)) + " (Київ). Реклама знову показується.")
    except Exception as e:
        log.warning("adr manage %s: %s", op, e)
        await msg.reply_text("❌ Не вдалося: <i>" + html.escape(str(e)) + "</i>", parse_mode=ParseMode.HTML)


# ================== 22.11: дані й дії для вкладки «Реклама» в застосунку /app ==================
