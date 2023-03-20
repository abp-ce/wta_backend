# wta_backend
Парсер задач, API для бота.
### Как запустить проект:

#### Предварительные требования:
- развернутый PostgreSQL и Redis,
- заполненныый .env, см. env.sample

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/abp-ce/wta_backend
```

```
cd wta_backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```
Обновить pip и установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции:

```
alembic upgrade head
```

Запустить celery worker c планировщником:

```
celery -A app.tasks worker -B --loglevel=INFO
```


Запустить проект:

```
uvicorn main:app --reload
```
### Стек:
 - fastapi
 - SQLAlchemy
 - alembic
 - asyncpg
 - celery
 - postqresql
 - redis