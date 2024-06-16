from datetime import timezone
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import Order, RefundRequest, db
from app.utils import confirm_token
from datetime import datetime

bp = Blueprint('staff', __name__, url_prefix='/staff')

@bp.route('/refund_requests')
@login_required  # Убедитесь, что только сотрудники могут доступ к этому маршруту
def refund_requests():
    refund_requests = RefundRequest.query.order_by(RefundRequest.requested_at.desc()).all()
    return render_template('staff/refund_requests.html', refund_requests=refund_requests)

@bp.route('/approve_refund/<int:request_id>')
@login_required
def approve_refund(request_id):
    refund_request = RefundRequest.query.get_or_404(request_id)
    refund_request.status = 'approved'
    refund_request.reviewed_at = datetime.now(timezone.utc)
    refund_request.order.status = 'cancelled'
    db.session.commit()
    flash('Refund request approved.', 'success')
    return redirect(url_for('staff.refund_requests'))

@bp.route('/reject_refund/<int:request_id>')
@login_required
def reject_refund(request_id):
    refund_request = RefundRequest.query.get_or_404(request_id)
    refund_request.status = 'rejected'
    refund_request.reviewed_at = datetime.now(timezone.utc)
    db.session.commit()
    flash('Refund request rejected.', 'danger')
    return redirect(url_for('staff.refund_requests'))

@bp.route('/request_refund/<token>', methods=['GET', 'POST'])
def request_refund(token):
    order_id = confirm_token(token, salt='order-edit-salt')
    if not order_id:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('order.check_order'))
    
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        refund_request = RefundRequest(order_id=order.id)
        db.session.add(refund_request)
        db.session.commit()
        flash('Refund request created successfully.', 'success')
        return redirect(url_for('order.detail', order_id=order.id))
    
    return render_template('order/request_refund.html', order=order)