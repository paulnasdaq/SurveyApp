from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevConfig')

    db.init_app(app)
    login_manager.init_app(app)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', title='404'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html', title='500'), 500

    @app.errorhandler(403)
    def server_error(error):
        return render_template('errors/403.html', title='403'), 403

    with app.app_context():
        db.create_all()
        from .auth import auth
        from .main import main
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(main.main_bp)

        return app
