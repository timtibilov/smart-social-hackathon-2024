from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import Event, db

bp = Blueprint('event', __name__, url_prefix='/events')

@bp.route('/')
def index():
    events = Event.query.all()
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