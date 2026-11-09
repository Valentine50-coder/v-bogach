import sqlite3, time
from config import DB_PATH


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, name TEXT, username TEXT, src TEXT,
            joined INTEGER, int_paid INTEGER DEFAULT 0, course_paid INTEGER DEFAULT 0,
            asked_int INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT);
        """)


def upsert_user(u, src=None):
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO users(id,name,username,src,joined) VALUES(?,?,?,?,?)",
                  (u.id, u.full_name, u.username or "", src or "", int(time.time())))
        c.execute("UPDATE users SET name=?, username=? WHERE id=?", (u.full_name, u.username or "", u.id))


def set_field(uid, field, value):
    assert field in ("int_paid", "course_paid", "asked_int")
    with conn() as c:
        c.execute(f"UPDATE users SET {field}=? WHERE id=?", (value, uid))


def get_user(uid):
    with conn() as c:
        return c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def paid_users(kind):
    col = "int_paid" if kind == "int" else "course_paid"
    with conn() as c:
        return [r["id"] for r in c.execute(f"SELECT id FROM users WHERE {col}=1")]


def stats():
    with conn() as c:
        q = lambda s: c.execute(s).fetchone()[0]
        return dict(total=q("SELECT COUNT(*) FROM users"),
                    hochu=q("SELECT COUNT(*) FROM users WHERE src='hochu'"),
                    asked_int=q("SELECT COUNT(*) FROM users WHERE asked_int=1"),
                    int_paid=q("SELECT COUNT(*) FROM users WHERE int_paid=1"))


def flag_get(k):
    with conn() as c:
        r = c.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
        return r["v"] if r else None


def flag_set(k, v="1"):
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO kv(k,v) VALUES(?,?)", (k, v))
