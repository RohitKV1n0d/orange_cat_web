from celery import Celery
import os
CELERY_BROKER_URL = os.environ.get('REDISGREEN_URL', 'redis://localhost:6379')
# CELERY_BROKER_TLS_URL = os.environ.get('REDIS_TLS_URL', 'redis://localhost:6379')

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=CELERY_BROKER_URL,
        broker=CELERY_BROKER_URL
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery