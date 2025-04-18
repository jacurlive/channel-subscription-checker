# 🎥 Telegram Video Code Bot

Этот Telegram-бот позволяет отправлять видео по специальному коду только тем пользователям, которые подписаны на указанные каналы. Он включает админ-функции, проверку заявок на вступление, работу с SQLite и пересылку любого контента.

---

## 🚀 Возможности

- ✅ Проверка подписки и заявок на вступление в каналы
- 📥 Получение видео по коду (если подписан)
- 👮 Только админ может добавлять видео
- 📢 Рассылка сообщений/контента всем пользователям
- 🧠 FSM-состояния (aiogram FSMContext)
- 🗃 SQLite-база данных для пользователей и видео

---

## 🛠️ Используемые технологии

- Python 3.10+
- [Aiogram 3.x](https://docs.aiogram.dev/en/latest/)
- SQLite (`sqlite3`)
- `.env` для хранения конфиденциальных данных
- Локальное хранение видео в `videos/`
- `message.copy_to()` — пересылка любого типа сообщений

---

## 📁 Структура проекта

<pre>
.
├── bot.py                  # Основной запуск бота
├── handlers/               # Хендлеры команд и логики
├── database.py             # SQLite операции (видео, пользователи)
├── states.py               # FSM состояния
├── videos/                 # Папка для видеофайлов
├── users.db                # База пользователей
├── videos.db               # База видеофайлов
├── .env                    # Секреты: токен, ID админа
├── requirements.txt        # Зависимости
└── README.md               # Документация проекта
</pre>

---

## ⚙️ Установка и запуск

1. Клонируй репозиторий:

```bash
git clone https://github.com/yourusername/telegram-video-code-bot.git
cd telegram-video-code-bot
```

2. Установи зависимости:
```bash
pip install -r requirements.txt
```

3. Создай файл .env:

```bash
TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
```

4. Создай папку videos, если её нет:
```bash
mkdir videos
```

5. Запусти бота:
```bash
python bot.py
```

Если есть предложения, баги или вопросы — пиши сюда:
📩 [t.me/@jacurlive](https://t.me/jacurlive)
