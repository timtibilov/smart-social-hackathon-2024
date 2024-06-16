from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from werkzeug.security import generate_password_hash

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

        # # Создание тестовых данных для Event
        # test_events = [
        #     Event(link='https://example.com/event1', name='Event 1', description='Description for Event 1', place='Location 1', visitor_count=100),
        #     Event(link='https://example.com/event2', name='Event 2', description='Description for Event 2', place='Location 2', visitor_count=150),
        #     Event(link='https://example.com/event3', name='Event 3', description='Description for Event 3', place='Location 3', visitor_count=200),
        #     Event(link='https://example.com/event4', name='Event 4', description='Description for Event 4', place='Location 4', visitor_count=250)
        # ]

        # db.session.bulk_save_objects(test_events)

        # # Получаем события из базы данных, чтобы использовать их в других таблицах
        # events = Event.query.all()

        # # Создание тестовых данных для EventImage
        # test_images = [
        #     EventImage(event_id=events[0].id, image_url='https://example.com/event1/image1.jpg'),
        #     EventImage(event_id=events[0].id, image_url='https://example.com/event1/image2.jpg'),
        #     EventImage(event_id=events[1].id, image_url='https://example.com/event2/image1.jpg'),
        #     EventImage(event_id=events[1].id, image_url='https://example.com/event2/image2.jpg'),
        #     EventImage(event_id=events[2].id, image_url='https://example.com/event3/image1.jpg'),
        #     EventImage(event_id=events[2].id, image_url='https://example.com/event3/image2.jpg'),
        #     EventImage(event_id=events[3].id, image_url='https://example.com/event4/image1.jpg'),
        #     EventImage(event_id=events[3].id, image_url='https://example.com/event4/image2.jpg')
        # ]

        # db.session.bulk_save_objects(test_images)

        # # Создание тестовых данных для EventDate
        # test_dates = [
        #     EventDate(event_id=events[0].id, date_time=datetime(2023, 10, 10, 18, 00), available_seats=50, price=20.0),
        #     EventDate(event_id=events[0].id, date_time=datetime(2023, 10, 11, 18, 00), available_seats=50, price=20.0),
        #     EventDate(event_id=events[1].id, date_time=datetime(2023, 10, 12, 18, 00), available_seats=75, price=25.0),
        #     EventDate(event_id=events[1].id, date_time=datetime(2023, 10, 13, 18, 00), available_seats=75, price=25.0),
        #     EventDate(event_id=events[2].id, date_time=datetime(2023, 10, 14, 18, 00), available_seats=100, price=30.0),
        #     EventDate(event_id=events[2].id, date_time=datetime(2023, 10, 15, 18, 00), available_seats=100, price=30.0),
        #     EventDate(event_id=events[3].id, date_time=datetime(2023, 10, 16, 18, 00), available_seats=125, price=35.0),
        #     EventDate(event_id=events[3].id, date_time=datetime(2023, 10, 17, 18, 00), available_seats=125, price=35.0)
        # ]

        # db.session.bulk_save_objects(test_dates)

        # # Получаем даты событий из базы данных
        # event_dates = EventDate.query.all()
        # # Создание тестовых данных для Order
        # test_orders = [
        #     Order(event_id=events[0].id, event_date_id=event_dates[0].id, visitor_name='John Doe', visitor_email='john.doe@example.com', visitor_phone='111-222-3333', ticket_count=2, status='confirmed', expires_at=datetime.now(timezone.utc) + timedelta(minutes=20)),
        #     Order(event_id=events[1].id, event_date_id=event_dates[2].id, visitor_name='Jane Smith', visitor_email='jane.smith@example.com', visitor_phone='444-555-6666', ticket_count=3, status='pending', expires_at=datetime.now(timezone.utc) + timedelta(minutes=20)),
        #     Order(event_id=events[2].id, event_date_id=event_dates[4].id, visitor_name='Alice Johnson', visitor_email='alice.johnson@example.com', visitor_phone='777-888-9999', ticket_count=1, status='cancelled', expires_at=datetime.now(timezone.utc) + timedelta(minutes=20)),
        #     Order(event_id=events[3].id, event_date_id=event_dates[6].id, visitor_name='Bob Brown', visitor_email='bob.brown@example.com', visitor_phone='000-123-4567', ticket_count=4, status='confirmed', expires_at=datetime.now(timezone.utc) + timedelta(minutes=40))
        # ]

        # db.session.bulk_save_objects(test_orders)

        # # Получаем заказы из базы данных
        # orders = Order.query.all()

        # # Создание тестовых данных для RefundRequest
        # test_refunds = [
        #     RefundRequest(order_id=orders[0].id, status='approved', reviewed_at=datetime.now(timezone.utc)),
        #     RefundRequest(order_id=orders[1].id, status='pending'),
        #     RefundRequest(order_id=orders[2].id, status='rejected', reviewed_at=datetime.now(timezone.utc)),
        #     RefundRequest(order_id=orders[3].id, status='approved', reviewed_at=datetime.now(timezone.utc))
        # ]

        # db.session.bulk_save_objects(test_refunds)

        # # Создание тестовых данных для MuseumStaff
        # test_staff = [
        #     MuseumStaff(name='Admin', email='Admin@example.com', phone='123-456-7890', password_hash=generate_password_hash('password')),
        # ]
        # db.session.bulk_save_objects(test_staff)
        # db.session.commit()

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