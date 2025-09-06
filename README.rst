Readme
======

A Python project template built with **Domain-Driven Design (DDD)** and the **Onion Architecture**.

.. note::
   While not yet production-ready — with several components still incomplete — this template provides a solid foundation that can be extended into future production-grade projects.

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Black code style

Tech Stack
==========

- **API Layer**
  - `FastAPI <https://fastapi.tiangolo.com/>`_
  - gRPC
- **Background / Async Tasks**
  - `Celery <https://docs.celeryq.dev/>`_ (with Redis)
- **Messaging (Publish / Consume)**
  - RabbitMQ
  - Kafka
- **Database**
  - `SQLAlchemy <https://www.sqlalchemy.org/>`_
  - Alembic
  - PostgreSQL
- **Tests**
  - `Pytest <https://pypi.org/project/pytest/>`_
- **Code Quality**
  - `Mypy <https://pypi.org/project/mypy/>`_
  - `Flake8 <https://pypi.org/project/flake8/>`_
  - `Black <https://pypi.org/project/black/>`_
- **Documentation**
  - `Sphinx <https://sphinx-tutorial.readthedocs.io/>`_
- **Containerization**
  - Docker

Project Structure
=================

.. code-block:: text

          fastapi_prototype/
      ├── .launch/                     # Docker launch configurations
      │   ├── api/
      │   ├── celery/
      │   ├── consume/
      │   └── tests/
      ├── docs/                        # Documentation
      │   └── source/
      ├── src/                         # Main source code
      │   └── app/
      │       ├── application/         # Application layer
      │       │   ├── common/
      │       │   └── services/
      │       ├── config/              # Configuration
      │       ├── domain/              # Domain layer
      │       ├── infrastructure/      # Infrastructure layer
      │       │   ├── common/
      │       │   ├── extensions/
      │       │   ├── messaging/
      │       │   ├── persistence/
      │       │   ├── repositories/
      │       │   ├── tasks/
      │       │   └── utils/
      │       └── interfaces/          # API interfaces
      ├── static/                      # Static files
      ├── tests/                       # Test files
      │   ├── application/
      │   ├── domain/
      │   ├── fixtures/
      │   └── infrastructure/
      ├── .env.example                # Environment variables example
      ├── pyproject.toml              # Python dependencies
      ├── README.rst                  # Project documentation
      ├── alembic.ini                 # Database migrations
      └── docker-compose-tests.yml    # Test environment

Running the App via scripts, docker::

    # launch required infrastructure containers
    bash local_prepare.sh
    # use --recreate if recreate, rebuild required
    # example: bash local_prepare.sh --recreate

    # launch app
    bash local_run.sh
    # use flags:
    #           --recreate if recreate, rebuild required
    #           --run_api  if run API container required
    # example: bash local_run.sh --recreate --run_api



Running the App locally::

    cd <path_to>/{your_project_name}
    poetry env use 3.12
    poetry install
    poetry update
    bash local_prepare.sh  # launch required containers
    # !! make sure all required containers were launched before running the app.


    # run API
    uvicorn src.app.interfaces.cli.main:app --reload --port 8081

    # run Celery
    celery -A src.app.interfaces.cli.celery_app worker -l INFO -E -B -Q default_queue --concurrency=2 -n default@%h

    # run Consumer
    python -m src.app.consume


API Documentation::

    http://<your_domain:port>/docs

Database Migrations::

    alembic revision --autogenerate -m "some message"
    alembic upgrade head

gRPC::

    # Generate services

    python -m grpc_tools.protoc \
        --proto_path ./src/app/interfaces/grpc/protos \
        --python_out=./src/app/interfaces/grpc/pb/debug \
        --grpc_python_out=./src/app/interfaces/grpc/pb/debug ./src/app/interfaces/grpc/protos/debug.proto

    python -m grpc_tools.protoc \
        --proto_path ./src/app/interfaces/grpc/protos \
        --python_out=./src/app/interfaces/grpc/pb/example \
        --grpc_python_out=./src/app/interfaces/grpc/pb/example ./src/app/interfaces/grpc/protos/example.proto

    # Run server
    $ python -m src.app.interfaces.grpc.server

    # Run test client
    $ python -m src.app.interfaces.grpc.client


Code Quality Checks::

    bash beautify.sh


Documentation Commands::

    # Initial setup
    pip install sphinx
    mkdir docs
    cd docs
    sphinx-quickstart

    # Build documentation
    cd <path_to>/docs
    # describe your docs in <path_to>/docs/source/*.rst
    make html
    # open /docs/build/index.html

Docker Commands::

    docker build -t api_img --no-cache -f .launch/api/Dockerfile .
    docker build -t celery_img --no-cache -f .launch/celery/Dockerfile .
    docker build -t consume_img --no-cache -f .launch/consume/Dockerfile .

    docker run -d --env-file --name my_local_api \
        --env-file ./.env \
        --shm-size="1g" \
        --cpus=1 -p 8081:8081 \
        api_img

    docker run -d --name my_local_celery \
        --shm-size="512m" \
        --cpus=2 \
        --env-file ./.env \
        -e CELERY_ARGS="worker -l INFO -E -B -Q default_queue --concurrency=2 -n default@%h" \
        celery_img

    docker run -d --name my_local_consume \
        --env-file .env \
        --shm-size="512m" \
        --cpus=1 \
        consume_img

    docker run -d --name my_local_flower \
        -e broker_url=redis://172.17.0.1:6379/11 \
        -e CELERY_BROKER_URL=redis://172.17.0.1:6379/11 \
        -e CELERY_BROKER_API=redis://172.17.0.1:6379/12 \
        -p 5555:5555 mher/flower

Running Tests::

    docker-compose -f docker-compose-tests.yml up --abort-on-container-exit
    docker-compose -f docker-compose-tests.yml rm -fsv && docker rmi $(docker images '*x_test*' -a -q) && docker system prune
