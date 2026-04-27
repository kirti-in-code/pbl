from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Medicine, ReminderLog
from datetime import datetime

caretaker_bp = Blueprint("caretaker", __name__)


@caretaker_bp.route("/caretaker")
@login_required
def caretaker_dashboard():
    if current_user.role not in ["caretaker", "admin"]:
        return render_template("unauthorized.html"), 403

    elderly_users = User.query.filter_by(role="elderly").all()
    rows = []
    
    for user in elderly_users:
        # Get all medicines for this user
        medicines = Medicine.query.filter_by(user_id=user.id).all()
        
        med_details = []
        total_missed = 0
        total_taken = 0
        
        for med in medicines:
            # Count logs for each medicine
            taken_count = ReminderLog.query.filter_by(medicine_id=med.id, status="taken").count()
            missed_count = ReminderLog.query.filter_by(medicine_id=med.id, status="missed").count()
            
            total_taken += taken_count
            total_missed += missed_count
            
            med_details.append({
                "name": med.name,
                "dosage": med.dosage,
                "time": med.time,
                "taken": taken_count,
                "missed": missed_count
            })
            
        rows.append({
            "user": user, 
            "med_count": len(medicines), 
            "missed_count": total_missed,
            "taken_count": total_taken,
            "medicines": med_details
        })
        
    return render_template("caretaker.html", rows=rows)
