from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
from routes import (
    auth_bp,
    medicines_bp,
    health_bp,
    reports_bp,
    emergency_bp,
    caretaker_bp,
    dashboard_bp,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(caretaker_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role in ["caretaker", "admin"]:
                return redirect(url_for("caretaker.caretaker_dashboard"))
            return redirect(url_for("dashboard.home"))
        return render_template("intro.html")

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "ok"}

    @app.route("/start")
    def start():
        if current_user.is_authenticated:
            if current_user.role in ["caretaker", "admin"]:
                return redirect(url_for("caretaker.caretaker_dashboard"))
            return redirect(url_for("dashboard.home"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
