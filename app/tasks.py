import asyncio

from celery import Celery
from celery.schedules import crontab

from .service import Parse

celery = Celery("tasks", broker="redis://localhost")


celery.conf.beat_schedule = {
    "add-every-hour": {
        "task": "app.tasks.celery_parse",
        "schedule": crontab(minute=10),
    },
}


@celery.task
def celery_parse():
    asyncio.run(Parse().parse_site())
