from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models import Order, Event, EventDate, db
from app.utils import send_confirmation_email

bp = Blueprint('order', __name__, url_prefix='/orders')

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        event_id = request.form['event_id']
        event_date_id = request.form['event_date_id']
        visitor_name = request.form['visitor_name']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']
        ticket_count = int(request.form['ticket_count'])

        if ticket_count > 5:
            flash('You cannot purchase more than 5 tickets in one order.', 'warning')
            return redirect(url_for('order.create'))

        # Проверяем, доступны ли места
        event_date = EventDate.query.get(event_date_id)
        available_seats = event_date.available_seats - Order.query.filter_by(event_date_id=event_date_id, status='pending')

        if ticket_count > available_seats:
            flash('Not enough seats available.', 'danger')
            return redirect(url_for('order.create'))

        order = Order(
            event_id=event_id,
            event_date_id=event_date_id,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            ticket_count=ticket_count
        )
        order.reserve()

        db.session.add(order)
        db.session.commit()

        flash('Order created successfully! Please confirm your order within 20 minutes.', 'success')
        return redirect(url_for('order.detail', order_id=order.id))

    events = Event.query.all()
    return render_template('order/create.html', events=events)

@bp.route('/<int:order_id>', methods=['GET', 'POST'])
def detail(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        # Mock вызов платёжного сервиса
        payment_success = True  # Замените mock вызов на реальный вызов платёжного сервиса

        if payment_success:
            order.status = 'confirmed'
            db.session.commit()
            # Отправка подтверждения по email
            send_confirmation_email(order)
            flash('Order confirmed successfully!', 'success')
        else:
            flash('Payment failed. Please try again.', 'danger')

    if order.is_expired():
        order.status = 'cancelled'
        db.session.commit()
        flash('Order expired and has been cancelled.', 'danger')
        return redirect(url_for('order.create'))

    return render_template('order/detail.html', order=order)

@bp.route('/check', methods=['GET', 'POST'])
def check_order():
    if request.method == 'POST':
        order_id = request.form['order_id']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']

        order = Order.query.filter_by(id=order_id).first()
        if order and (order.visitor_email == visitor_email or order.visitor_phone == visitor_phone):
            return redirect(url_for('order.detail', order_id=order.id))
        else:
            flash('Order not found or incorrect email/phone provided.', 'danger')

    return render_template('order/check_order.html')
