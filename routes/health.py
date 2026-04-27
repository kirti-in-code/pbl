from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, HealthRecord

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
@login_required
def health_page():
    records = (
        HealthRecord.query.filter_by(user_id=current_user.id)
        .order_by(HealthRecord.date.desc())
        .all()
    )
    return render_template("health.html", records=records)


@health_bp.route("/health/add", methods=["POST"])
@login_required
def add_health_record():
    bp = request.form.get("bp", "").strip()
    sugar = request.form.get("sugar", type=float)
    weight = request.form.get("weight", type=float)
    date_value = request.form.get("date", "")

    if not all([bp, sugar, weight, date_value]):
        flash("All health fields are required.", "danger")
        return redirect(url_for("health.health_page"))

    record = HealthRecord(
        user_id=current_user.id,
        bp=bp,
        sugar=sugar,
        weight=weight,
        date=datetime.strptime(date_value, "%Y-%m-%d").date(),
    )
    db.session.add(record)
    db.session.commit()
    flash("Health record saved.", "success")
    return redirect(url_for("health.health_page"))


@health_bp.route("/health/data")
@login_required
def health_data():
    records = (
        HealthRecord.query.filter_by(user_id=current_user.id)
        .order_by(HealthRecord.date.asc())
        .all()
    )
    return jsonify(
        {
            "labels": [r.date.isoformat() for r in records],
            "sugar": [r.sugar for r in records],
            "weight": [r.weight for r in records],
        }
    )
