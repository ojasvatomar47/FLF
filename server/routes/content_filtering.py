from flask import Blueprint, request, jsonify
from sklearn.neighbors import NearestNeighbors
from models.order import Order
from models.listing import Listing
from models.user import User  # Import User model to fetch restaurant names
import numpy as np

# Initialize Blueprint
content_filter_bp = Blueprint('content_filter', __name__)

# One-hot encoding for food types
food_type_encoding = {
    "Vegetarian": [1, 0, 0, 0],
    "Non-Vegetarian": [0, 1, 0, 0],
    "Vegan": [0, 0, 1, 0],
    "other": [0, 0, 0, 1]
}

# Helper function to generate feature vector
def generate_feature_vector(listing_detail):
    expiry = listing_detail.expiry
    quantity = listing_detail.quantity
    food_type_vector = food_type_encoding.get(listing_detail.food_type, [0, 0, 0, 1])  # Handle unknown food types
    return [expiry] + food_type_vector + [quantity]

# Route for content-based filtering
@content_filter_bp.route('/content-based-recommendations', methods=['GET'])
def content_based_recommendations():
    ngo_id = request.args.get("ngo_id")
    
    # Fetch past orders for the NGO and calculate the preference vector
    ngo_orders = Order.objects(ngo_id=ngo_id)
    ngo_vectors = []
    
    for order in ngo_orders:
        for listing_detail in order.listings:
            ngo_vectors.append(generate_feature_vector(listing_detail))
    
    # Calculate the average preference vector for the NGO
    ngo_preference_vector = np.mean(ngo_vectors, axis=0) if ngo_vectors else [0] * 6  # Fallback to zero vector if no orders

    # Retrieve all listings from the database and calculate feature vectors
    all_listings = list(Listing.objects())  # Convert QuerySet to list
    listing_vectors = [generate_feature_vector(listing) for listing in all_listings]
    
    # Convert list to numpy array for k-NN
    listing_vectors_np = np.array(listing_vectors)
    
    # Initialize k-NN model and fit with listing feature vectors
    knn_model = NearestNeighbors(n_neighbors=5, metric='cosine')  # Adjust `n_neighbors` as needed
    knn_model.fit(listing_vectors_np)

    # Find the k-nearest listings to the NGO's preference vector
    ngo_preference_vector_np = np.array([ngo_preference_vector])
    distances, indices = knn_model.kneighbors(ngo_preference_vector_np)

    # Retrieve recommended listings based on indices
    recommended_listings = [all_listings[i] for i in indices.flatten()]  # Flatten indices to get a 1D array

    # Format the response to include all listing details and restaurant names
    response = []
    for listing in recommended_listings:
        try:
            restaurant = User.objects(id=listing.restaurant_id.id).first()
            restaurant_name = restaurant.username if restaurant else "Unknown"
        except Exception as e:
            print(f"Database query error: {e}")
            restaurant_name = "Unknown"
        
        response.append({
            **listing.to_mongo().to_dict(),  # Include all listing details
            "restaurant_name": restaurant_name  # Add the restaurant name
        })
    
    return jsonify({"recommendations": response}), 200
