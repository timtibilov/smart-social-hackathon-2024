from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
from app import mail

def generate_token(order_id, salt='order-edit-salt'):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(order_id, salt=salt)

def confirm_token(token, expiration=3600, salt='order-edit-salt'):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        order_id = serializer.loads(token, salt=salt, max_age=expiration)
    except Exception:
        return False
    return order_id

def send_confirmation_email(order):
    edit_token = generate_token(order.id, salt='order-edit-salt')
    
    msg = Message(
        subject=f'Order Confirmation - Order #{order.id}',
        recipients=[order.visitor_email],
    )
    msg.body = f"""
    Dear {order.visitor_name},

    Thank you for your order #{order.id}!

    Event: {order.event.name}
    Event Date: {order.event_date.date_time}
    Ticket Count: {order.ticket_count}
    Status: {order.status}

    You can view your order using the following link:
    {url_for('order.detail', order_id=order.id, _external=True)}
    
    You can edit your order using the following link:
    {url_for('order.edit', token=edit_token, _external=True)}
    
    You can request for a refund using the following link:
    {url_for('staff.request_refund', token=edit_token, _external=True)}

    Best regards,
    Your Museum Team
    """
    mail.send(msg)
