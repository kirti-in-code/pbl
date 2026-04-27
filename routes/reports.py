from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import ReminderLog, Medicine

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports_page():
    return render_template("reports.html")


@reports_bp.route("/report")
@login_required
def report_api():
    week_ago = datetime.utcnow() - timedelta(days=7)
    logs = (
        ReminderLog.query.join(Medicine)
        .filter(Medicine.user_id == current_user.id, ReminderLog.timestamp >= week_ago)
        .all()
    )
    taken = len([x for x in logs if x.status == "taken"])
    missed = len([x for x in logs if x.status == "missed"])
    return jsonify({"taken": taken, "missed": missed})
