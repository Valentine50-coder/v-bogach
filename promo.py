"""27.11.2026: знижка 50% на все до 31.12 включно (з нагоди свята Валентини). Тексти цін у розділах агента
підставляються звідси; з 1.01 самі стають повними. Слово для запису під час акції Валентина приймає в особистих."""
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Kyiv")
UNTIL = datetime(2026, 12, 31, 23, 59, 59, tzinfo=TZ)


def on():
    return datetime.now(TZ) <= UNTIL


def fmt(x):
    return (f"{x:.1f}".rstrip("0").rstrip(".")).replace(".", ",")


def price(full):
    """«<s>1980 грн</s> 990 грн зі знижкою 50% до 31 грудня» або просто «1980 грн»."""
    if on():
        return f"<s>{fmt(full)} грн</s> {fmt(full / 2)} грн <i>(знижка 50% до 31 грудня)</i> ‼️"
    return f"{fmt(full)} грн"
