"""28.11.2026 (Тетяна: «каруселі мають бути повноцінні»): доповнення до вже зібраних каруселей Валентини без переписування збирачів.
X[ключ][номер слайда] = HTML-абзац(и), додаються після останнього абзацу тексту (div.p) на слайді.
R[ключ][номер слайда] = [(старий текст, новий текст), ...] заміни (напр. прибрати порожню обіцянку «Дочитайте…»).
S[ключ][номер слайда] = CSS, що додається в <style> слайда (зменшити фото, підняти блок тощо).
Підключено в кожному plan*.py: SETS = extra.patch(SETS)."""
X, R, S = {}, {}, {}


def _insert(html, add):
    i = html.rfind('<div class="p"')
    if i < 0:
        return html
    j = html.find("</div>", i)
    if j < 0:
        return html
    return html[:j + 6] + add + html[j + 6:]


def patch(sets):
    out = {}
    for key, slides in sets.items():
        new = []
        for n, h in enumerate(slides, 1):
            for a, b in R.get(key, {}).get(n, []):
                h = h.replace(a, b)
            add = X.get(key, {}).get(n)
            if add:
                h = _insert(h, add)
            css = S.get(key, {}).get(n)
            if css:
                h = h.replace("</style>", css + "</style>", 1)
            new.append(h)
        out[key] = new
    return out


def P(text, size=None):
    st = f' style="font-size:{size}px"' if size else ""
    return f'<div class="p"{st}>{text}</div>'


import extra_data  # noqa: E402,F401  (дані доповнень)
