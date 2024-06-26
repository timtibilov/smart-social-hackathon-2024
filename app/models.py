from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class EventImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    event = db.relationship('Event', back_populates='images')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    place = db.Column(db.String(120), nullable=False)
    visitor_count = db.Column(db.Integer, nullable=False)
    dates = db.relationship('EventDate', back_populates='event')
    images = db.relationship('EventImage', back_populates='event')

class EventDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    event = db.relationship('Event', back_populates='dates')

# class Payment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     payment_method = db.Column(db.String(20), nullable=False)
#     status = db.Column(db.String(15), nullable=False)  # 'pending', 'completed' or 'failed'
#     registration = db.relationship('Registration', back_populates='payments')

class MuseumStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event_date_id = db.Column(db.Integer, db.ForeignKey('event_date.id'), nullable=False)
    visitor_name = db.Column(db.String(120), nullable=False)
    visitor_email = db.Column(db.String(120), nullable=False)
    visitor_phone = db.Column(db.String(20), nullable=False)
    ticket_count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'confirmed', 'cancelled'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)

    event = db.relationship('Event')
    event_date = db.relationship('EventDate')

    def reserve(self):
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=20)

    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at and self.status == 'pending'
    
class RefundRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', 'rejected'
    reviewed_at = db.Column(db.DateTime)
    
    order = db.relationship('Order', backref='refund_requests')