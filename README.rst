Commission Engine Core
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
        # install, run postgres, message broker, actualize .env

    $ uvicorn src.app.main:app --reload --port 8081

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

Run tests::

    # run tests
    $ docker-compose -f docker-compose-tests.yml up --abort-on-container-exit
    # clean up
    $ docker-compose -f docker-compose-tests.yml rm -fsv && docker rmi $(docker images '*x_test*' -a -q) && docker system prune
