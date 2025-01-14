from flask import Blueprint, request
from controllers.auth_controller import register_user, login_user, logout_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return register_user(data)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return login_user(data)

@auth_bp.route('/logout', methods=['GET'])
def logout():
    return logout_user()
