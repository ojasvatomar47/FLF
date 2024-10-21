from flask import Blueprint, jsonify, request
from controllers.order_controller import (
    create_order, get_orders_by_restaurant, get_orders_by_ngo,
    get_order_info, decline_order, accept_order, fulfill_order,
    cancel_order, get_messages_by_order_id, add_rest_review, add_ngo_review
)

order_bp = Blueprint('order', __name__)

# Create a new order request
@order_bp.route('/orders', methods=['POST'])
def create_order_route():
    return create_order()

# Get all orders for a particular restaurant
@order_bp.route('/orders/restaurant', methods=['GET'])
def get_orders_by_restaurant_route():
    return get_orders_by_restaurant()

# Get all orders for a particular NGO
@order_bp.route('/orders/ngo', methods=['GET'])
def get_orders_by_ngo_route():
    return get_orders_by_ngo()

# Route to get a specific order's information
@order_bp.route('/orders/<order_id>', methods=['GET'])
def get_order_info_route(order_id):
    return get_order_info(order_id)

# Decline an order request
@order_bp.route('/orders/<order_id>/decline', methods=['PUT'])
def decline_order_route(order_id):
    return decline_order(order_id)

# Accept an order
@order_bp.route('/orders/<order_id>/accept', methods=['PUT'])
def accept_order_route(order_id):
    return accept_order(order_id)

# Cancel an order
@order_bp.route('/orders/<order_id>/cancel', methods=['PUT'])
def cancel_order_route(order_id):
    return cancel_order(order_id)

# Fulfill an order
@order_bp.route('/orders/<order_id>/fulfill', methods=['PUT'])
def fulfill_order_route(order_id):
    return fulfill_order(order_id)

# Get chat messages for an order id
@order_bp.route('/orders/<order_id>/messages', methods=['GET'])
def get_messages_by_order_id_route(order_id):
    return get_messages_by_order_id(order_id)

# Add a review for the restaurant
@order_bp.route('/addRestReview/<order_id>', methods=['POST'])
def add_rest_review_route(order_id):
    return add_rest_review(order_id)

# Add a review for the NGO
@order_bp.route('/addNgoReview/<order_id>', methods=['POST'])
def add_ngo_review_route(order_id):
    return add_ngo_review(order_id)
