import multiprocessing

name = "Gunicorn Config"
bind = "0.0.0.0:8081"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
