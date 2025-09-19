ARG BASE_IMAGE
FROM $BASE_IMAGE

CMD alembic upgrade head && celery -A src.app.interfaces.cli.celery_app $CELERY_ARGS
