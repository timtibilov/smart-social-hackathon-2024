from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from sqlalchemy import func
from app.models import Event, EventDate, Order
from app import db
from app.utils import fetch_and_parse_xml, add_events_to_db

bp = Blueprint('event', __name__, url_prefix='/events')

@bp.route('/')
def index():
    # обновляем базу данных ивентов
    xml = fetch_and_parse_xml(current_app.config['URL_TO_PARSE'])
    add_events_to_db(xml)

    filter_type = request.args.get('filter', 'all')  # по умолчанию 'all'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('q')  # Новый параметр поиска
    
    events = Event.query

    # Фильтрация по статусу (прошедшие/текущие)
    if filter_type == 'past':
        events = events.filter(EventDate.date_time < datetime.now())
    elif filter_type == 'current':
        events = events.filter(EventDate.date_time >= datetime.now())

    # Фильтрация по цене
    if min_price:
        events = events.filter(EventDate.price >= float(min_price))
    if max_price:
        events = events.filter(EventDate.price <= float(max_price))

    # Фильтрация по дате
    if start_date:
        events = events.filter(EventDate.date_time >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        events = events.filter(EventDate.date_time <= datetime.strptime(end_date, '%Y-%m-%d'))

    # Поиск по названию и описанию
    if search_query:
        events = events.filter((Event.name.ilike(f'%{search_query}%')) | (Event.description.ilike(f'%{search_query}%')))

    events = events.all()
    return render_template('event/list.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        place = request.form['place']
        visitor_count = request.form['visitor_count']
        
        event = Event(name=name, description=description, place=place, visitor_count=visitor_count)
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('event.index'))
    
    return render_template('event/create.html')

@bp.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event/detail.html', event=event)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form['description']
        event.place = request.form['place']
        event.visitor_count = request.form['visitor_count']
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event.detail', event_id=event.id))
    
    return render_template('event/edit.html', event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('event.index'))

@bp.route('/<int:event_id>/order', methods=['GET', 'POST'])
def order(event_id):
    if request.method == 'POST':
        event_date_id = request.form['event_date_id']
        visitor_name = request.form['visitor_name']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']
        ticket_count = int(request.form['ticket_count'])

        if ticket_count > 5:
            flash('You cannot purchase more than 5 tickets in one order.', 'warning')
            return redirect(url_for('event.order'))

        # Проверяем, доступны ли места
        event_date = EventDate.query.get(event_date_id)
        ordered_seats = db.session.query(
            func.sum(Order.ticket_count)
        ).filter(
            Order.event_date_id == event_date_id,
            Order.status != 'cancelled'
        ).scalar()

        if ordered_seats is None:
            ordered_seats = 0

        available_seats = event_date.available_seats - ordered_seats

        if ticket_count > available_seats:
            flash('Not enough seats available.', 'danger')
            return redirect(url_for('order.order'))

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

    event = Event.query.get_or_404(event_id)
    return render_template('order/create.html', event=event)