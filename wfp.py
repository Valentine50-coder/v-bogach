"""Автоматична оплата через WayForPay без веб-сервера (Render Background Worker).
Агент сам створює рахунок на оплату (CREATE_INVOICE), потім раз на хвилину питає у WayForPay
статус (CHECK_STATUS). Коли статус Approved, відкриває доступ.
Ключі беруться тільки зі змінних Render (Environment): WFP_ACCOUNT, WFP_SECRET, WFP_DOMAIN."""
import hashlib
import hmac
import logging
import os, re
import time

import httpx

import db

log = logging.getLogger("wfp")
API = "https://api.wayforpay.com/api"

ACCOUNT = os.environ.get("WFP_ACCOUNT", "").strip()
SECRET = os.environ.get("WFP_SECRET", "").strip()
DOMAIN = os.environ.get("WFP_DOMAIN", "").strip() or "t.me"
LAST_ERROR = ""                  # остання причина, чому рахунок не створився (без секретів)
HOLD_SECONDS = 3 * 24 * 3600     # скільки днів після створення рахунку чекаємо оплату


def configured():
    return bool(ACCOUNT and SECRET)


def sign(*parts):
    s = ";".join(str(p) for p in parts)
    return hmac.new(SECRET.encode(), s.encode(), hashlib.md5).hexdigest()


def init_table():
    with db.conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS payments(
            ref TEXT PRIMARY KEY, uid INTEGER, kind TEXT, amount INTEGER, currency TEXT,
            status TEXT DEFAULT 'pending', created INTEGER, done INTEGER DEFAULT 0)""")


def env_report():
    """Діагностика змінних. Логін і домен не секретні, показуємо. Ключ: лише довжина й 4 останні символи."""
    dom = os.environ.get("WFP_DOMAIN", "").strip()
    hint = ""
    if dom and (not re.fullmatch(r"[A-Za-z0-9.-]+", dom) or "_" in dom or re.fullmatch(r"[0-9a-fA-F]{24,}", dom) or "." not in dom):
        hint = "  ⚠️ це не схоже на домен (потрібно щось на кшталт www.site.com)"
    return (f"WFP_ACCOUNT: {ACCOUNT or 'НЕ ЗАДАНО'}\n"
            f"WFP_SECRET: {('є, довжина ' + str(len(SECRET)) + ', закінчується на ' + SECRET[-4:]) if SECRET else 'НЕ ЗАДАНО'}\n"
            f"WFP_DOMAIN: {dom or 'не задано (використовується t.me)'}{hint}")


async def create_invoice(uid, kind, amount, currency, name):
    """Повертає посилання на оплату або None. Причина невдачі лежить у LAST_ERROR."""
    global LAST_ERROR
    LAST_ERROR = ""
    if not amount:
        LAST_ERROR = "сума для оплати не вказана в config.py"
        return None
    if not configured():
        miss = [n for n, v in (("WFP_ACCOUNT", ACCOUNT), ("WFP_SECRET", SECRET)) if not v]
        LAST_ERROR = "у Render → Environment не задано: " + ", ".join(miss)
        return None
    ref = f"vb{kind}_{uid}_{int(time.time())}"
    odate = int(time.time())
    body = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": ACCOUNT,
        "merchantAuthType": "SimpleSignature",
        "merchantDomainName": DOMAIN,
        "apiVersion": 1,
        "language": "ua",
        "orderReference": ref,
        "orderDate": odate,
        "amount": amount,
        "currency": currency,
        "orderTimeout": HOLD_SECONDS,
        "productName": [name],
        "productPrice": [amount],
        "productCount": [1],
        "merchantSignature": sign(ACCOUNT, DOMAIN, ref, odate, amount, currency, name, 1, amount),
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(API, json=body)
            data = r.json()
    except Exception as e:
        log.warning("wfp create error: %s", e)
        LAST_ERROR = f"немає зв'язку з WayForPay: {str(e)[:150]}"
        return None
    try:
        url = data.get("invoiceUrl") if isinstance(data, dict) else None
        if not url:
            log.warning("wfp create failed: %s", str(data)[:300])
            if isinstance(data, dict):
                LAST_ERROR = f"WayForPay відповів: код {data.get('reasonCode')}, {str(data.get('reason') or data)[:200]}"
            else:
                LAST_ERROR = f"WayForPay відповів несподіваним форматом: {str(data)[:200]}"
            return None
        with db.conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS payments(ref TEXT PRIMARY KEY, uid INTEGER, kind TEXT, amount INTEGER, currency TEXT, "
                      "status TEXT DEFAULT 'pending', created INTEGER, done INTEGER DEFAULT 0)")
            c.execute("INSERT OR REPLACE INTO payments(ref,uid,kind,amount,currency,created) VALUES(?,?,?,?,?,?)",
                      (ref, uid, kind, amount, currency, int(time.time())))
        return url
    except Exception as e:
        log.exception("wfp create: помилка після відповіді")
        LAST_ERROR = f"{type(e).__name__}: {str(e)[:200]}"
        return None


async def check_status(ref):
    body = {"transactionType": "CHECK_STATUS", "merchantAccount": ACCOUNT, "orderReference": ref,
            "merchantSignature": sign(ACCOUNT, ref), "apiVersion": 1}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(API, json=body)
            return r.json()
    except Exception as e:
        log.warning("wfp check %s: %s", ref, e)
        return {}


async def poll(on_paid):
    """Для всіх рахунків, що чекають оплати, питає статус. on_paid(uid, kind, ref, amount) викликається один раз."""
    if not configured():
        return
    now = int(time.time())
    with db.conn() as c:
        rows = c.execute("SELECT * FROM payments WHERE done=0").fetchall()
    for p in rows:
        if now - p["created"] > HOLD_SECONDS + 3600:
            with db.conn() as c:
                c.execute("UPDATE payments SET done=1, status='expired' WHERE ref=?", (p["ref"],))
            continue
        data = await check_status(p["ref"])
        st = str(data.get("transactionStatus", ""))
        if st == "Approved":
            try:
                paid = float(data.get("amount") or 0)
            except ValueError:
                paid = 0
            if paid + 0.01 < float(p["amount"]):
                log.warning("wfp %s: сума %s менша за очікувану %s", p["ref"], paid, p["amount"])
                continue
            with db.conn() as c:        # позначаємо до відправки, щоб доступ не видався двічі
                c.execute("UPDATE payments SET done=1, status='Approved' WHERE ref=? AND done=0", (p["ref"],))
                changed = c.execute("SELECT changes()").fetchone()[0]
            if changed:
                await on_paid(p["uid"], p["kind"], p["ref"], p["amount"], p["currency"])
        elif st in ("Declined", "Expired", "Refunded", "Voided"):
            with db.conn() as c:
                c.execute("UPDATE payments SET done=1, status=? WHERE ref=?", (st, p["ref"]))
