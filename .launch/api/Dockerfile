FROM python:3.12.0-slim

# env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
CMD alembic upgrade head

ENV PYTHONPATH=/app

CMD alembic upgrade head && gunicorn --config src/app/gunicorn_config.py src.app.interfaces.cli.main:app
EXPOSE 8081
