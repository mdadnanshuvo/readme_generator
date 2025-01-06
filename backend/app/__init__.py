from flask import Flask
from flask_cors import CORS

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing
    return app
