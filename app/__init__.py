from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        from .models import Event, EventDate, EventImage, MuseumStaff, Order, RefundRequest
        db.create_all()  # Создаем таблицы в базе данных

        from .routes import (
            event_routes, 
            staff_routes, 
            auth_routes, 
            order_routes)
        
        app.register_blueprint(event_routes.bp)
        app.register_blueprint(order_routes.bp)
        app.register_blueprint(staff_routes.bp)
        app.register_blueprint(auth_routes.bp)
                
    return app