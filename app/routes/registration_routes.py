from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import Registration, Event, EventDate, db

bp = Blueprint('registration', __name__, url_prefix='/registrations')

@bp.route('/')
@login_required
def index():
    registrations = Registration.query.all()
    return render_template('registration/list.html', registrations=registrations)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    search_query = request.args.get('q')
    events = Event.query
    
    if search_query:
        events = events.filter((Event.name.ilike(f'%{search_query}%')) | (Event.description.ilike(f'%{search_query}%')))

    events = events.all()
    
    if request.method == 'POST':
        event_id = request.form['event_id']
        event_date_id = request.form['event_date_id']
        visitor_name = request.form['visitor_name']
        visitor_email = request.form['visitor_email']
        visitor_phone = request.form['visitor_phone']

        registration = Registration(
            event_id=event_id,
            status='registered',
            event_date_id=event_date_id,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone
        )
        db.session.add(registration)
        db.session.commit()
        flash('Registration created successfully!', 'success')
        return redirect(url_for('registration.index'))

    return render_template('registration/create.html', events=events)

@bp.route('/<int:registration_id>')
@login_required
def detail(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    return render_template('registration/detail.html', registration=registration)

@bp.route('/<int:registration_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    events = Event.query.all()
    if request.method == 'POST':
        registration.event_id = request.form['event_id']
        registration.event_date_id = request.form['event_date_id']
        registration.visitor_name = request.form['visitor_name']
        registration.visitor_email = request.form['visitor_email']
        registration.visitor_phone = request.form['visitor_phone']

        db.session.commit()
        flash('Registration updated successfully!', 'success')
        return redirect(url_for('registration.detail', registration_id=registration.id))

    return render_template('registration/edit.html', registration=registration, events=events)

@bp.route('/<int:registration_id>/delete', methods=['POST'])
@login_required
def delete(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    registration.status = 'canceled'
    db.session.commit()
    flash('Registration deleted successfully!', 'success')
    return redirect(url_for('registration.index'))
