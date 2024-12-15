from kombu import Exchange, Queue
from celery.schedules import crontab
from src.app.config.settings import env

# CELERY settings
# https://docs.celeryq.dev/en/stable/userguide/configuration.html?highlight=beat_schedule#std-setting-imports
# --------------------------------------------------------------------------

timezone = "UTC"
broker_connection_retry_on_startup: bool = True

broker_url: str = env.str("CELERY_BROKER_URL", "redis://127.0.0.1:6379/11")
result_backend: str = env.str("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/12")

default_exchange = Exchange("default", type="direct")


default_queue = "default_queue"

task_queues = (
    Queue(
        name=default_queue,
        exchange=default_exchange,
        routing_key=default_queue,
    ),
)


imports = ("src.app.core.tasks.example_task",)

TASKS: dict = {
    "example_task": {
        "task": "src.app.core.tasks.example_task.say_meow",  # Every 2 minutes
        "schedule": crontab(*("*/2", "*", "*", "*", "*")),
        "options": {"queue": default_queue},
    },
}


beat_schedule = {**TASKS}
