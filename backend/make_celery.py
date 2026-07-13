from app import create_app
import tasks

flask_app = create_app()
celery_app = flask_app.celery
