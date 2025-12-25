from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect

from dmtoolkit.filters import add_filters

csrf = CSRFProtect()
# session = Session()

def init_app():
    """Create the app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.DevConfig")

    csrf.init_app(app)
    # session.init_app(app)

    with app.app_context():
        from .inittracker.routes import tracker_bp
        from .players.routes import players_bp
        from .api.routes import api_bp
        from .settings.routes import settings_bp
        from .modules.kibbles.routes import kibbles_bp

        # Register Blueprints
        app.register_blueprint(api_bp)
        app.register_blueprint(tracker_bp)
        app.register_blueprint(players_bp)
        app.register_blueprint(settings_bp)
        app.register_blueprint(kibbles_bp)

        add_filters(app)
    
    return app