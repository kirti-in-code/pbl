from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="elderly", nullable=False)

    medicines = db.relationship("Medicine", backref="user", lazy=True, cascade="all,delete")
    health_records = db.relationship(
        "HealthRecord", backref="user", lazy=True, cascade="all,delete"
    )
    emergency_contact = db.relationship(
        "EmergencyContact", backref="user", uselist=False, cascade="all,delete"
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    time = db.Column(
        db.String(120), nullable=False
    )  # Comma-separated HH:MM values for simplicity
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    logs = db.relationship("ReminderLog", backref="medicine", lazy=True, cascade="all,delete")


class ReminderLog(db.Model):
    __tablename__ = "reminders_log"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # taken or missed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class HealthRecord(db.Model):
    __tablename__ = "health_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bp = db.Column(db.String(20), nullable=False)
    sugar = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=date.today)


class EmergencyContact(db.Model):
    __tablename__ = "emergency_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
