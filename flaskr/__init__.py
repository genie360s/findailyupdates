"""Flask application factory for Fulusi."""
import os
from datetime import date

from flask import Flask, render_template, g
from dotenv import load_dotenv

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inject today's date into every template
    @app.context_processor
    def inject_globals():
        return {
            'today_date': date.today().strftime('%A, %d %B %Y'),
            'current_user': g.get('user'),
        }

    @app.route('/')
    def index():
        return render_template('index.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)

    return app
