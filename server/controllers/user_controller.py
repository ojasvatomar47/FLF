from flask import jsonify
from models.user import User
from models.order import Order
from datetime import datetime

# Function to get information about a specific NGO by ID
def get_ngo_info(id):
    try:
        ngo = User.objects(id=id, user_type='Charity/NGO').first()
        if not ngo:
            return jsonify({"message": "NGO not found"}), 404

        total_orders = Order.objects(ngo_id=id).count()
        cancelled_orders = Order.objects(ngo_id=id, status='cancelled').count()
        fulfilled_orders = Order.objects(ngo_id=id, status='fulfilled').count()
        dismissed_orders = Order.objects(ngo_id=id, status='dismissed').count()

        # Fetch reviews for the NGO
        ngo_reviews = Order.objects(ngo_id=id).only('rest_review')
        reviews = [order.rest_review for order in ngo_reviews if order.rest_review]

        return jsonify({
            "_id":ngo.id,
            "username": ngo.username,
            "email": ngo.email,
            "location_name": ngo.location_name,
            "total_orders": total_orders,
            "latitude":ngo.latitude,
            "longitude":ngo.longitude,
            "cancelled_orders": cancelled_orders,
            "fulfilled_orders": fulfilled_orders,
            "dismissed_orders": dismissed_orders,
            "reviews": reviews
        }), 200

    except Exception as e:
        return jsonify({"message": "Server Error", "error": str(e)}), 500

# Function to get information about a specific Restaurant by ID
def get_restaurant_info(id):
    try:
        restaurant = User.objects(id=id, user_type='Restaurant').first()
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404

        total_orders = Order.objects(restaurant_id=id).count()
        cancelled_orders = Order.objects(restaurant_id=id, status='cancelled').count()
        fulfilled_orders = Order.objects(restaurant_id=id, status='fulfilled').count()
        dismissed_orders = Order.objects(restaurant_id=id, status='dismissed').count()

        # Fetch reviews for the restaurant
        restaurant_reviews = Order.objects(restaurant_id=id).only('ngo_review')
        reviews = [order.ngo_review for order in restaurant_reviews if order.ngo_review]

        return jsonify({
            "username": restaurant.username,
            "email": restaurant.email,
            "location_name": restaurant.location_name,
            "total_orders": total_orders,
            "cancelled_orders": cancelled_orders,
            "fulfilled_orders": fulfilled_orders,
            "dismissed_orders": dismissed_orders,
            "reviews": reviews
        }), 200

    except Exception as e:
        return jsonify({"message": "Server Error", "error": str(e)}), 500
