from flask import Blueprint, request, jsonify
from controllers.recommendation_ml import get_ml_recommendations

# Create a Blueprint for recommendations
recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations/ml', methods=['GET'])
def ml_recommendations():
    # Get the NGO ID from the query parameters
    ngo_id = request.args.get('ngo_id')
    
    # Check if the NGO ID is provided
    if not ngo_id:
        return jsonify({"error": "NGO ID is required"}), 400
    
    # Call the controller function to get ML recommendations
    return get_ml_recommendations(ngo_id)
