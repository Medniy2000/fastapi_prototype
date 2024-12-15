Base Commands
===============

Run app local use::

    $ cd <path_to>/ce_core
    $ cp .env.example .env

    # to run app perform:
        # install, run postgres, mysql message broker, actualize .env

    $ uvicorn src.app.main:app --reload




Run app using Docker::

    $ TODO


API docs::

    # http://<your_domain:port>/docs

Make db schema::

    # use commands

    $ alembic revision --autogenerate -m "some message"
    $ alembic upgrade head


Check code quality[black, flake8, mypy]::

    # use commands

    $ bash beautify.sh


Docs commands::

    # before:
    #   install  sphinx
    #   mkdir docs
    #   cd docs
    #   pip sphinx-quickstart

    $ cd <path_to>/docs
    # describe your docs in <path_to>/docs/source/*.rst
    $ make html
    # open /docs/build/index.html

Run tests::

    $ TODO
