from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/hello')
def hello():
    return jsonify({"message": "Hello from Flask COE App!"}), 200