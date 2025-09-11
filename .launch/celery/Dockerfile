ARG BASE_IMAGE
FROM $BASE_IMAGE

CMD alembic upgrade head


ENV PYTHONPATH=/app

CMD alembic upgrade head && poetry run celery -A src.app.interfaces.cli.celery_app $CELERY_ARGS
