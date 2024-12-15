README
=======================

Example description:

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


Run app local
^^^^^^^^^^^^^^

To run app local use::

    $ cd <path_to>/{your_project_name}
    $ poetry env use 3.12
    $ poetry install
    $ poetry update
    $ cp .env.example .env

    # to run app perform:
        * install, run postgres, message broker, actualize .env

    # Run API
    $ uvicorn src.app.main:app --reload --port 8081

    # Run Celery
    # celery -A src.app.extensions.celery_ext.celery_app worker -l INFO -E -B -Q default_queue --concurrency=2 -n default@%h


API docs here::

    # http://<your_domain:port>/docs

To make db schema::

    # use commands

    $ alembic revision --autogenerate -m "some message"
    $ alembic upgrade head


To check code quality[black, flake8, mypy]::

    # use commands
    $ bash beautify.sh


Docs commands::

    # before:
    # install  sphinx
    # mkdir docs
    # cd docs
    # pip sphinx-quickstart

    $ cd <path_to>/docs
    # describe your docs in <path_to>/docs/source/*.rst
    $ make html
    # open /docs/build/index.html

Run tests::

    $

To run app using Docker::

    $ cd <path_to>/{your_project_name}

    # build, run celery
    $ docker build -t celery_img --no-cache -f .launch/celery/Dockerfile .
    $ docker run -d --name my_local_celery --shm-size="512m" --cpus=2 --env-file ./.env -e CELERY_ARGS="worker -l INFO -E -B -Q default_queue --concurrency=2 -n default@%h" celery_img
    $ docker run -d --name my_local_flower -e broker_url=redis://172.17.0.1:6379/11 -e CELERY_BROKER_URL=redis://172.17.0.1:6379/11 -e CELERY_BROKER_API=redis://172.17.0.1:6379/12  -p 5555:5555 mher/flower

    # build, run API
    $ docker build -t api_img --no-cache -f .launch/api/Dockerfile .
    $ docker run -d --env-file ./.env --name my_local_api --shm-size="1g" --cpus=1 -p 8081:8081 api_img
Run tests::

    # run tests
    $ docker-compose -f docker-compose-tests.yml up --abort-on-container-exit
    # clean up
    $ docker-compose -f docker-compose-tests.yml rm -fsv && docker rmi $(docker images '*x_test*' -a -q) && docker system prune
