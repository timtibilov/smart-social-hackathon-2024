from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        from .routes import event_routes, registration_routes, staff_routes, payment_routes, auth_routes
        
        app.register_blueprint(event_routes.bp)
        app.register_blueprint(registration_routes.bp)
        app.register_blueprint(staff_routes.bp)
        app.register_blueprint(payment_routes.bp)
        app.register_blueprint(auth_routes.bp)
        
        db.create_all()  # Создаем таблицы в базе данных
        
    return app