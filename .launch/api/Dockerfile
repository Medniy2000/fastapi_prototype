ARG BASE_IMAGE
FROM $BASE_IMAGE

CMD alembic upgrade head

ENV PYTHONPATH=/app

CMD alembic upgrade head && gunicorn --config src/app/interfaces/cli/gunicorn_config.py src.app.interfaces.cli.main:app
EXPOSE $API_PORT
