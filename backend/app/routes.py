from flask import Blueprint, request, jsonify
from app.model import generate_text

bp = Blueprint("routes", __name__)

@bp.route("/generate", methods=["POST"])
def generate():
    """
    Endpoint to generate README content based on a prompt.
    """
    data = request.json
    prompt = data.get("prompt", "")
    max_length = data.get("max_length", 300)

    try:
        generated_text = generate_text(prompt, max_length)
        return jsonify({"generated_text": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"})
