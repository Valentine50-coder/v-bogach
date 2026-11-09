# v-bogach: агент Валентини Швець

Telegram-агент: воронка «Старт» і воронка «ХОЧУ» (інтенсив «Здоровий кишківник») з автооплатою WayForPay і входом у канал інтенсиву після оплати.

## Посилання
- Звичайний старт: `https://t.me/<логін_агента>`
- Кодове слово ХОЧУ (ManyChat): `https://t.me/<логін_агента>?start=hochu`

## Хостинг: Railway
New project → GitHub Repository → v-bogach. Старт: `python bot.py` (Procfile). Volume з шляхом `/data`.

## Змінні (Railway → Variables, значення тільки там)
- `BOT_TOKEN` токен від BotFather
- `ADMIN_ID` Telegram ID через кому (Валентина, Тетяна)
- `DB_PATH` = `/data/bot.db`
- `WFP_ACCOUNT` Merchant login, `WFP_SECRET` Merchant secret key, `WFP_DOMAIN` домен з поля «Сайт» без https:// (наприклад www.instagram.com). Merchant password не потрібен.

## Де міняти
- Тексти: `texts.py`. Ціна, дати, кнопки старту: `config.py`. Фото: `images/start.jpg`, `images/intensive.jpg`.

## Команди адміна
`/stats`, `/grant ID`, `/wfptest`, `/grupa`, `/help`.

## Вхід у канал після оплати
Додайте агента в канал або групу інтенсиву адміністратором з правом «Запрошувати користувачів». Агент спитає кнопками, що це. Якщо додали раніше, напишіть там `/grupa`. Після оплати людина отримує особисте одноразове посилання.
