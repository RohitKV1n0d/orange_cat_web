from celery import Celery
from time import sleep

app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def reverse(string):
    sleep(5)
    return string[::-1]
