from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, EmergencyContact
from sms_service import send_sms_alert

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.route("/emergency", methods=["GET", "POST"])
@login_required
def emergency_page():
    contact = EmergencyContact.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not phone:
            flash("Name and phone are required.", "danger")
            return redirect(url_for("emergency.emergency_page"))

        if contact:
            contact.name = name
            contact.phone = phone
        else:
            contact = EmergencyContact(user_id=current_user.id, name=name, phone=phone)
            db.session.add(contact)
        db.session.commit()
        flash("Emergency contact updated.", "success")
        return redirect(url_for("emergency.emergency_page"))

    return render_template("emergency.html", contact=contact)


@emergency_bp.route("/emergency/send-alert", methods=["POST"])
@login_required
def trigger_alert():
    contact = EmergencyContact.query.filter_by(user_id=current_user.id).first()
    if not contact:
        return jsonify({"success": False, "message": "No emergency contact found."}), 404

    message = f"EMERGENCY ALERT: Your patient {current_user.name} needs immediate assistance! Please check the MedCare app."
    success, result_message = send_sms_alert(contact.phone, message)

    return jsonify({"success": success, "message": result_message})
