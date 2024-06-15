from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    place = db.Column(db.String(120), nullable=True)
    visitor_count = db.Column(db.Integer, nullable=False)

class Exhibit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event = db.relationship('Event', back_populates='exhibits')

class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'audio' or 'text'
    content = db.Column(db.Text, nullable=False)
    event = db.relationship('Event', back_populates='guides')

class EventDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)  # Добавляем поле price
    event = db.relationship('Event', back_populates='dates')

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_date_id = db.Column(db.Integer, db.ForeignKey('event_date.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.String(15), nullable=False)  # 'registered' or 'canceled'
    event_date = db.relationship('EventDate', back_populates='registrations')
    customer = db.relationship('Customer', back_populates='registrations')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20),

nullable=False)
    status = db.Column(db.String(15), nullable=False)  # 'pending', 'completed' or 'failed'
    registration = db.relationship('Registration', back_populates='payments')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    registrations = db.relationship('Registration', back_populates='customer')

class MuseumStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)