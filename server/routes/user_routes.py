from flask import Blueprint
from controllers.user_controller import get_ngo_info, get_restaurant_info

user_bp = Blueprint('user_bp', __name__)

# Route to get information about a specific NGO by ID
@user_bp.route('/ngo/profile/<id>', methods=['GET'])
def ngo_profile(id):
    return get_ngo_info(id)

# Route to get information about a specific Restaurant by ID
@user_bp.route('/restaurant/profile/<id>', methods=['GET'])
def restaurant_profile(id):
    return get_restaurant_info(id)
