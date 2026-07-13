from flask import Flask
from config import Config
from extensions import db, jwt, cors, mail, cache
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('result_backend', 'redis://localhost:6379/0'),
        broker=app.config.get('broker_url', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    # Fix for CELERYBEAT_SCHEDULE warning
    celery.conf.beat_schedule = app.config.get('CELERYBEAT_SCHEDULE', {})
    celery.set_default()
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    
    # Initialize Celery
    app.celery = make_celery(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    # Initialize database
    with app.app_context():
        import models  # Ensure models are loaded
        db.create_all()
        
        # Seed admin user if not exists
        from models.user import User
        from werkzeug.security import generate_password_hash
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@placement.com')
        if not User.query.filter_by(email=admin_email).first():
            admin_user = User(
                email=admin_email,
                password_hash=generate_password_hash('admin123'),
                role='ADMIN'
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Seeded admin user: {admin_email}")
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
