# AskPupkin
Vorontsov Stepan, web11

Веб-приложение сервиса вопросов и ответов на Django и PostgreSQL.

## Скрин с проектированием БД лежит в 'bd_pic.png'

## Варианты запуска проекта

### Вариант 1: Локальный запуск (Django на хосте + PostgreSQL в Docker)

1. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Подготовьте файл переменных окружения `.env.local` (убедитесь, что указан `POSTGRES_HOST=127.0.0.1`):
```bash
cp .env.example .env.local
```

3. Запустите контейнер с базой данных PostgreSQL:
```bash
docker compose up -d db
```

4. Примените миграции и запустите сервер разработки:
```bash
python manage.py migrate
python manage.py runserver
```

После запуска приложение будет доступно по адресу `http://127.0.0.1:8000/`.

---

### Вариант 2: Полный запуск в Docker-контейнерах

1. Подготовьте файл переменных окружения `.env.local` (для контейнеров укажите `POSTGRES_HOST=db`):
```bash
cp .env.example .env.local
```

2. Соберите образ и запустите контейнеры (при первом запуске миграции применятся автоматически, база будет пустой):
```bash
docker compose up --build
```

---

## Дополнительные команды

### Наполнение базы данных тестовыми данными
Скрипт генерирует пользователей, вопросы, ответы, теги и лайки в заданной пропорции (`ratio` — количество пользователей; вопросов создаётся `10 * ratio`, ответов — `100 * ratio`, лайков — `200 * ratio`):

* **Локально:**
```bash
python manage.py fill_db 10000
```

* **Внутри контейнера:**
```bash
docker compose exec web python manage.py fill_db 10000
```

### Запуск тестов
* **Локально:**
```bash
python manage.py test
```

* **Внутри контейнера:**
```bash
docker compose exec web python manage.py test
```

### Сброс базы данных (для проверки на пустой БД)
```bash
docker compose down -v
docker compose up --build
```