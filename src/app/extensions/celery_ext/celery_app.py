from celery import Celery

celery_app = Celery("CE_CORE")

celery_app.config_from_object("src.app.config.celery", namespace="CELERY")
