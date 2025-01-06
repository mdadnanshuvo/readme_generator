import sys
import os

# Add the backend directory to PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app import create_app
from app.routes import bp

app = create_app()
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
