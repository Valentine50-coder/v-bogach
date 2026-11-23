"""22.11: /reklama_test (адмін): чи бачить агент рекламний кабінет Meta, сторінку й Instagram.

Нічого не запускає і грошей не витрачає, тільки читає. Змінні Railway:
META_ADS_TOKEN (маркер системного користувача), META_AD_ACCOUNT (цифри кабінету, можна з act_),
META_PAGE_ID (цифри сторінки). Якщо кабінет чи сторінку не вказано, агент шукає їх сам і підказує цифри.
"""
import html
import logging
import os

import httpx

log = logging.getLogger("adtest")
VER = os.environ.get("FB_GRAPH_VER", "v23.0")
NEED = ("ads_management", "ads_read", "business_management", "pages_read_engagement")
STATUS = {1: "активний", 2: "вимкнений", 3: "не оплачено (борг)", 7: "на перевірці", 9: "пільговий період",
          100: "закривається", 101: "закритий"}


HINTS = {  # 22.11: зрозумілі підказки замість англійських помилок Meta
    200: ("Meta не дає застосунку доступ до кабінету. Додайте ID кабінету в застосунок: developers.facebook.com → "
          "застосунок → Налаштування → Додатково → «Рекламні облікові записи» (Authorized ad account IDs). "
          "І перевірте, що в застосунку є сценарій «Реклама через Marketing API». (код 200)"),
    10: ("Системному користувачу не призначена сторінка Facebook. Налаштування бізнесу → Системні користувачі → "
         "Агент → «Призначити об'єкти» → Сторінки Facebook → ваша сторінка, увімкнути доступ. (код 10)"),
    190: "Маркер недійсний або прострочений. Згенеруйте новий і вставте в Railway. (код 190)",
}


def _token():
    return os.environ.get("META_ADS_TOKEN", "").strip() or os.environ.get("FB_ADS_TOKEN", "").strip()


async def _get(c, path, **params):
    params["access_token"] = _token()
    r = await c.get(f"https://graph.facebook.com/{VER}/{path}", params=params, timeout=30)
    try:
        d = r.json()
    except Exception:
        d = {"error": {"message": r.text[:200]}}
    if "error" in d:
        e = d["error"]
        code = e.get("code")
        hint = HINTS.get(code)
        raise RuntimeError(hint or f"{e.get('message', '')} (код {code})")
    return d


async def check():
    """Повертає текст звіту (HTML)."""
    if not _token():
        return ("❌ <b>Маркера немає.</b>\nУ Railway → сервіс агента → Variables не знайдено змінної "
                "<code>META_ADS_TOKEN</code>. Перевірте назву і що натиснули «Save».")
    out = ["🔎 <b>Перевірка реклами Meta</b>\n"]
    ok_all = True
    acc_env = "".join(ch for ch in os.environ.get("META_AD_ACCOUNT", "") if ch.isdigit())
    page_env = "".join(ch for ch in os.environ.get("META_PAGE_ID", "") if ch.isdigit())
    async with httpx.AsyncClient() as c:
        # 1. маркер
        try:
            me = await _get(c, "me", fields="id,name")
            out.append(f"✅ Маркер працює: <b>{html.escape(me.get('name') or me.get('id', ''))}</b>")
        except Exception as e:
            return "\n".join(out + [f"❌ <b>Маркер не працює:</b> {html.escape(str(e))}\n\n"
                                    "Найчастіше маркер скопійовано не повністю або з пробілом. Згенеруйте новий і вставте ще раз."])
        # 2. дозволи
        try:
            perms = await _get(c, "me/permissions")
            granted = {p["permission"] for p in perms.get("data", []) if p.get("status") == "granted"}
            miss = [p for p in NEED if p not in granted]
            if miss:
                ok_all = False
                out.append("⚠️ Бракує дозволів: " + ", ".join(f"<code>{p}</code>" for p in miss)
                           + "\nДодайте їх, коли генеруєте маркер системного користувача, і вставте новий маркер.")
            else:
                out.append("✅ Дозволи для реклами є")
        except Exception as e:
            out.append(f"ℹ️ Дозволи не вдалося прочитати: {html.escape(str(e))}")
        # 3. рекламний кабінет
        try:
            if acc_env:
                a = await _get(c, f"act_{acc_env}", fields="name,account_status,currency,amount_spent")
                st = a.get("account_status")
                mark = "✅" if st == 1 else "⚠️"
                ok_all &= st == 1
                out.append(f"{mark} Рекламний кабінет: <b>{html.escape(a.get('name', ''))}</b> "
                           f"(<code>{acc_env}</code>), {STATUS.get(st, st)}, валюта {a.get('currency', '?')}")
            else:
                ok_all = False
                lst = (await _get(c, "me/adaccounts", fields="name,account_id,account_status", limit=10)).get("data", [])
                if lst:
                    out.append("⚠️ <code>META_AD_ACCOUNT</code> не вказано. Агент бачить кабінети:\n" + "\n".join(
                        f"   • {html.escape(x.get('name', ''))}: <code>{x.get('account_id')}</code>" for x in lst)
                        + "\nВпишіть потрібні цифри в Railway.")
                else:
                    out.append("❌ Рекламних кабінетів не бачу. У налаштуваннях бізнесу призначте системному "
                               "користувачу кабінет з правом «Керувати кампаніями».")
        except Exception as e:
            ok_all = False
            out.append(f"❌ Рекламний кабінет: {html.escape(str(e))}")
        # 4. сторінка і Instagram
        try:
            if page_env:
                p = await _get(c, page_env, fields="name,instagram_business_account{username}")
                out.append(f"✅ Сторінка: <b>{html.escape(p.get('name', ''))}</b> (<code>{page_env}</code>)")
                ig = (p.get("instagram_business_account") or {}).get("username")
                if ig:
                    out.append(f"✅ Instagram, прив'язаний до сторінки: <b>@{html.escape(ig)}</b>")
                else:
                    out.append("⚠️ До сторінки не прив'язаний Instagram (або немає доступу до нього).")
            else:
                ok_all = False
                lst = (await _get(c, "me/accounts", fields="name,id", limit=10)).get("data", [])
                if lst:
                    out.append("⚠️ <code>META_PAGE_ID</code> не вказано. Агент бачить сторінки:\n" + "\n".join(
                        f"   • {html.escape(x.get('name', ''))}: <code>{x.get('id')}</code>" for x in lst)
                        + "\nВпишіть потрібні цифри в Railway.")
                else:
                    out.append("❌ Сторінок не бачу. Призначте системному користувачу сторінку Facebook.")
        except Exception as e:
            ok_all = False
            out.append(f"❌ Сторінка: {html.escape(str(e))}")
        if acc_env:
            try:
                igs = (await _get(c, f"act_{acc_env}/instagram_accounts", fields="username")).get("data", [])
                if igs:
                    out.append("✅ Instagram для реклами в кабінеті: " + ", ".join(
                        "@" + html.escape(x.get("username", "")) for x in igs))
            except Exception:
                pass
    out.append("\n🎉 <b>Усе готово до запуску реклами.</b>" if ok_all
               else "\nВиправте пункти з ⚠️ чи ❌ і напишіть /reklama_test ще раз.")
    out.append("<i>Нічого не запускалось і гроші не витрачались.</i>")
    return "\n".join(out)


async def cmd(update, context, is_admin):
    if not update.effective_user or not is_admin(update.effective_user.id):
        return
    wait = await update.message.reply_text("Перевіряю зв'язок з Meta…")
    try:
        text = await check()
    except Exception as e:
        log.exception("adtest")
        text = f"❌ Перевірка зламалась: {html.escape(str(e))[:300]}"
    try:
        await wait.edit_text(text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
