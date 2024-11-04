# controllers/recommendation_ml.py
from models.listing import Listing
from flask import jsonify
import numpy as np
from utils.data_preparation import create_user_item_matrix
from utils.matrix_factorization import train_collaborative_filtering_model

def get_ml_recommendations(ngo_id):
    # Create the user-item matrix and map of NGO IDs
    user_item_matrix, ngo_ids = create_user_item_matrix()
    
    # Train the collaborative filtering model
    transformed_matrix = train_collaborative_filtering_model(user_item_matrix)
    
    # Find the row index for the given NGO in the transformed matrix
    try:
        ngo_index = ngo_ids.index(ngo_id)
    except ValueError:
        return jsonify({"error": "NGO ID not found"}), 404

    # Get the predicted preferences for the specified NGO
    ngo_preferences = transformed_matrix[ngo_index]
    
    # Map food types to predicted scores for readability
    food_type_scores = {
        "Vegetarian": ngo_preferences[0],
        "Vegan": ngo_preferences[1],
        "Non-Vegetarian": ngo_preferences[2]
    }
    
    # Fetch all available listings
    listings = Listing.objects(view="not blocked")  # Use objects() to query
    print("Number of listings found:", listings.count())
    
    # Score listings based on predicted food type preferences
    scored_listings = []
    for listing in listings:
        if listing.food_type in food_type_scores:
            score = food_type_scores[listing.food_type]
            scored_listings.append((listing, score))
    
    # Sort listings by score in descending order
    scored_listings.sort(key=lambda x: x[1], reverse=True)
    
    # Format the response to include all listing details and scores
    response = [
        {
            **listing.to_mongo().to_dict(),  # Include all listing details
            "score": score  # Add the score
        } 
        for listing, score in scored_listings
    ]
    
    return jsonify(response), 200
