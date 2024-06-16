from flask import Blueprint, request, render_template, redirect, url_for, flash
from app import db
from app.models import Order, Event, EventDate
from app.utils import send_confirmation_email, confirm_token

bp = Blueprint('order', __name__, url_prefix='/orders')

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

@bp.route('/edit/<token>', methods=['GET', 'POST'])
def edit(token):
    order_id = confirm_token(token, salt='order-edit-salt')
    if not order_id:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('order.check_order'))

    order = Order.query.get_or_404(order_id)
    if order.is_expired() and order.status == 'pending':
        order.status = 'cancelled'
        db.session.commit()
        flash('Order expired and has been cancelled.', 'danger')
        return redirect(url_for('order.create'))

    if request.method == 'POST':
        # Обработка изменений или отмены заказа
        action = request.form.get('action')
        if action == 'cancel':
            order.status = 'cancelled'
            db.session.commit()
            flash('Order has been cancelled.', 'success')
            return redirect(url_for('order.create'))

        visitor_name = request.form['visitor_name']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']
        ticket_count = int(request.form['ticket_count'])

        if ticket_count > 5:
            flash('You cannot purchase more than 5 tickets in one order.', 'warning')
            return redirect(url_for('order.edit', token=token))

        # Проверяем, доступны ли места
        event_date = order.event_date
        available_seats = event_date.available_seats - Order.query.filter_by(event_date_id=event_date.id, status='pending').count() + order.ticket_count
        
        if ticket_count > available_seats:
            flash('Not enough seats available.', 'danger')
            return redirect(url_for('order.edit', token=token))

        order.visitor_name = visitor_name
        order.visitor_email = visitor_email
        order.visitor_phone = visitor_phone
        order.ticket_count = ticket_count
        db.session.commit()
        
        flash('Order updated successfully.', 'success')
        return redirect(url_for('order.detail', order_id=order.id))

    return render_template('order/edit.html', order=order)

