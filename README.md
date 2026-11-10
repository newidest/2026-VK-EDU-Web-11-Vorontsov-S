# AskPupkin 
Vorontsov Stepan web11

## Варианты запуска проекта

### Вариант 1: Локальный запуск

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Вариант 2: Контейнер

```bash
cp .env.example .env
docker compose up --build
```