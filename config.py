import multiprocessing

CSRF_ENABLED = True
SECRET_KEY = '09apple'

bind = "66.112.216.74:80"
workers = multiprocessing.cpu_count() * 2 + 1

