from collections import Counter
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Medicine, ReminderLog

medicines_bp = Blueprint("medicines", __name__)


def get_smart_suggestion(medicine_id):
    logs = (
        ReminderLog.query.filter_by(medicine_id=medicine_id)
        .order_by(ReminderLog.timestamp.desc())
        .limit(30)
        .all()
    )
    missed_logs = [log for log in logs if log.status == "missed"]
    if len(missed_logs) < 3:
        return None

    hour_counter = Counter(log.timestamp.hour for log in logs if log.status == "taken")
    if not hour_counter:
        return "You often miss this dose. Try reducing frequency temporarily."
    best_hour = hour_counter.most_common(1)[0][0]
    return f"You often miss this dose. Consider rescheduling near {best_hour:02d}:00."


@medicines_bp.route("/medicines")
@login_required
def medicines_page():
    medicines = Medicine.query.filter_by(user_id=current_user.id).all()
    suggestions = {med.id: get_smart_suggestion(med.id) for med in medicines}
    return render_template("medicines.html", medicines=medicines, suggestions=suggestions)


@medicines_bp.route("/add_medicine", methods=["GET", "POST"])
@login_required
def add_medicine():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dosage = request.form.get("dosage", "").strip()
        times = request.form.get("time", "").strip()
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")

        if not all([name, dosage, times, start_date, end_date]):
            flash("Please fill all fields.", "danger")
            return render_template("add_medicine.html")

        medicine = Medicine(
            user_id=current_user.id,
            name=name,
            dosage=dosage,
            time=times,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
        )
        db.session.add(medicine)
        db.session.commit()
        flash("Medicine added successfully.", "success")
        return redirect(url_for("medicines.medicines_page"))
    return render_template("add_medicine.html")


@medicines_bp.route("/medicine/edit/<int:medicine_id>", methods=["POST"])
@login_required
def edit_medicine(medicine_id):
    medicine = Medicine.query.filter_by(id=medicine_id, user_id=current_user.id).first_or_404()
    medicine.name = request.form.get("name", medicine.name)
    medicine.dosage = request.form.get("dosage", medicine.dosage)
    medicine.time = request.form.get("time", medicine.time)
    db.session.commit()
    flash("Medicine updated.", "success")
    return redirect(url_for("medicines.medicines_page"))


@medicines_bp.route("/medicine/delete/<int:medicine_id>", methods=["POST"])
@login_required
def delete_medicine(medicine_id):
    medicine = Medicine.query.filter_by(id=medicine_id, user_id=current_user.id).first_or_404()
    db.session.delete(medicine)
    db.session.commit()
    flash("Medicine deleted.", "info")
    return redirect(url_for("medicines.medicines_page"))


@medicines_bp.route("/get_medicines")
@login_required
def get_medicines():
    medicines = Medicine.query.filter_by(user_id=current_user.id).all()
    return jsonify(
        [
            {
                "id": med.id,
                "name": med.name,
                "dosage": med.dosage,
                "time": med.time,
                "start_date": med.start_date.isoformat(),
                "end_date": med.end_date.isoformat(),
            }
            for med in medicines
        ]
    )


@medicines_bp.route("/mark_taken", methods=["POST"])
@login_required
def mark_taken():
    medicine_id = request.form.get("medicine_id", type=int)
    status = request.form.get("status", "taken")
    medicine = Medicine.query.filter_by(id=medicine_id, user_id=current_user.id).first_or_404()

    log = ReminderLog(medicine_id=medicine.id, status=status)
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Log updated", "status": status})


@medicines_bp.route("/daily_schedule")
@login_required
def daily_schedule():
    today = date.today()
    medicines = Medicine.query.filter(
        Medicine.user_id == current_user.id,
        Medicine.start_date <= today,
        Medicine.end_date >= today,
    ).all()

    schedule = []
    for med in medicines:
        for t in med.time.split(","):
            schedule.append({"medicine": med, "time": t.strip()})
    schedule.sort(key=lambda x: x["time"])
    return render_template("daily_schedule.html", schedule=schedule)


@medicines_bp.route("/streak")
@login_required
def streak():
    # Basic streak: consecutive days with at least one 'taken' log
    logs = (
        ReminderLog.query.join(Medicine)
        .filter(Medicine.user_id == current_user.id, ReminderLog.status == "taken")
        .order_by(ReminderLog.timestamp.desc())
        .all()
    )
    taken_days = {log.timestamp.date() for log in logs}
    streak_days = 0
    day = date.today()
    while day in taken_days:
        streak_days += 1
        day -= timedelta(days=1)
    return jsonify({"streak_days": streak_days})
