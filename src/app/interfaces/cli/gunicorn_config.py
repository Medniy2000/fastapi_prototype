import multiprocessing

from src.app.config.settings import LaunchMode, settings

name = "Gunicorn Config"
bind = f"0.0.0.0:{settings.API_PORT}"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
if settings.LAUNCH_MODE != LaunchMode.PRODUCTION.value:
    workers = 2
