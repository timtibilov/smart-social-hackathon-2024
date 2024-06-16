from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import Event, EventDate, db

bp = Blueprint('event', __name__, url_prefix='/events')

@bp.route('/')
def index():
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