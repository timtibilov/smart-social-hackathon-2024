import requests
import xml.etree.ElementTree as ET
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
from app.models import Event, EventImage
from app import mail, db

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

def send_aproval_email(order):
    pass

def send_rejection_email(order):
    pass

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

def fetch_and_parse_xml(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        return root
    except requests.exceptions.RequestException as e:
        print(f'Error fetching the XML: {e}')
        return None
    except ET.ParseError as e:
        print(f'Error parsing the XML: {e}')
        return None

def add_events_to_db(xml_root):
    for item in xml_root.findall('./channel/item'):
        link = item.find('link').text
        if not Event.query.filter_by(link=link).first():
            title = item.find('title').text or 'Unknown Title'
            description = item.find('description').text or 'No Description'
            place = 'Unknown Location'
            visitor_count = 0
            
            event = Event(link=link, name=title, description=description, place=place, visitor_count=visitor_count)
            db.session.add(event)
            db.session.commit()

            image_url = item.find('./enclosure').attrib.get('url') if item.find('./enclosure') is not None else None
            if image_url:
                event_image = EventImage(event_id=event.id, image_url=image_url)
                db.session.add(event_image)
                db.session.commit()
