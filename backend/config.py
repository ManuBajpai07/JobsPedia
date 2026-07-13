import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'jobspedia.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    
    # Mail Config (Mock setup for local dev)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@placement.com'
    MAIL_SUPPRESS_SEND = True # We'll just print to console/log
    
    # Cache Config
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery Beat Schedule
    from celery.schedules import crontab
    CELERYBEAT_SCHEDULE = {
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0), # Every day at 9 AM
        },
        'monthly-activity-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(day_of_month='1', hour=10, minute=0), # 1st of every month at 10 AM
        }
    }
