# server/routes/route_routes.py
from flask import Blueprint
from controllers.route_controller import calculate_route

route_bp = Blueprint('route_bp', __name__)

# Define the route for calculating routes
route_bp.route('/calculate_route', methods=['POST'])(calculate_route)


