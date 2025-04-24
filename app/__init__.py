# __init__

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret-fsmp-key"
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    return app