from flask import Blueprint, request, jsonify
from models.order import Order
from models.listing import Listing
from models.user import User
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

# Helper function to calculate cosine similarity
def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    if norm_vector1 == 0 or norm_vector2 == 0:
        return 0  # Avoid division by zero if any vector is zero
    return dot_product / (norm_vector1 * norm_vector2)

# Helper function to find k-nearest listings
def get_k_nearest_listings(preference_vector, listing_vectors, k=5):
    # Calculate similarity scores between preference vector and each listing vector
    similarities = [(i, cosine_similarity(preference_vector, listing_vector)) 
                    for i, listing_vector in enumerate(listing_vectors)]
    
    # Sort by similarity score in descending order and select the top-k listings
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    nearest_indices = [index for index, _ in sorted_similarities[:k]]
    
    return nearest_indices

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
    
    # Convert to numpy array for calculation
    listing_vectors_np = np.array(listing_vectors)
    
    # Find the k-nearest listings based on cosine similarity
    nearest_indices = get_k_nearest_listings(ngo_preference_vector, listing_vectors_np, k=5)

    # Retrieve recommended listings based on indices
    recommended_listings = [all_listings[i] for i in nearest_indices]

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
