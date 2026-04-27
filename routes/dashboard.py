from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Medicine, ReminderLog

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    meds = Medicine.query.filter_by(user_id=current_user.id).all()
    today = date.today()
    today_logs = (
        ReminderLog.query.join(Medicine)
        .filter(Medicine.user_id == current_user.id, ReminderLog.timestamp >= today)
        .all()
    )
    taken_count = len([log for log in today_logs if log.status == "taken"])
    missed_count = len([log for log in today_logs if log.status == "missed"])
    return render_template(
        "dashboard.html",
        meds=meds,
        taken_count=taken_count,
        missed_count=missed_count,
    )
