from kombu import Exchange, Queue

from src.app.config.settings import env

# CELERY settings
# https://docs.celeryq.dev/en/stable/userguide/configuration.html?highlight=beat_schedule#std-setting-imports
# --------------------------------------------------------------------------

timezone = "UTC"

broker_url: str = env.str("CELERY_BROKER_URL", "redis://127.0.0.1:6379/11")
result_backend: str = env.str("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/12")

default_exchange = Exchange("default", type="direct")


transactional_tasks_queue = "transactional_tasks_queue"

task_queues = Queue(
    name=transactional_tasks_queue,
    exchange=default_exchange,
    routing_key=transactional_tasks_queue,
)


imports = ()

TASKS: dict = {}


beat_schedule = {**TASKS}
