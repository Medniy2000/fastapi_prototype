ARG BASE_IMAGE
FROM $BASE_IMAGE

CMD alembic upgrade head

ENV PYTHONPATH=/app

CMD alembic upgrade head && python -m src.app.interfaces.cli.consume
