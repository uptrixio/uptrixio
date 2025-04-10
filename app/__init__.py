import time

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required

from config import Config

from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

login = LoginManager()
login.login_view = 'auth.request_otp'
login.login_message = 'Необходимо подтверждение через Telegram для доступа к этой странице.'

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)

    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from . import models

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.route('/admin')
    @login_required
    def admin_index():
        return redirect(url_for('admin.list_posts'))

    return app