from flask import Blueprint, render_template, redirect

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return redirect('events')
