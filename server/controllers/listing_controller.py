from flask import jsonify, request
from models.listing import Listing
from models.user import User
from datetime import datetime
from bson import ObjectId
import geopy.distance

# Get listings created by a particular restaurant
def get_restaurant_listings(restaurant_id):
    try:
        now = datetime.utcnow()
        listings = Listing.objects(restaurant_id=ObjectId(restaurant_id), expires_at__gte=now)
        return jsonify([serialize_doc(listing.to_mongo().to_dict()) for listing in listings])
    except Exception as e:
        return jsonify({"message": "Server Error", "error": str(e)}), 500

# Create a new listing
# def create_listing():
#     data = request.json
#     try:
#         # Ensure that 'expiry' is an integer
#         if 'expiry' in data:
#             data['expiry'] = int(data['expiry'])

#         new_listing = Listing(**data)
#         new_listing.save()
#         return jsonify(serialize_doc(new_listing.to_mongo().to_dict())), 201
#     except Exception as e:
#         return jsonify({"message": "Server Error", "error": str(e)}), 500

def create_listing():
    data = request.json
    print("Received data:", data)  # Debugging line
    try:
        # Ensure 'expiry' is an integer and valid
        if 'expiry' in data:
            data['expiry'] = int(data['expiry'])
            if data['expiry'] not in [1, 2, 3, 480]:  # Validate expiry
                return jsonify({"message": "Invalid expiry value"}), 400

        # Validate restaurant_id and food_type fields
        if 'restaurantId' not in data or 'food_type' not in data:
            return jsonify({"message": "restaurantId and food_type are required"}), 400

        # Create and save the new listing
        new_listing = Listing(
            restaurant_id=ObjectId(data['restaurantId']),
            name=data['name'],
            quantity=data['quantity'],
            expiry=data['expiry'],
            view=data.get('view', 'not blocked'),  # Default to 'not blocked'
            food_type=data['food_type']  # Add food_type to the listing
        )
        new_listing.save()
        return jsonify(serialize_doc(new_listing.to_mongo().to_dict())), 201
    except Exception as e:
        print("Error:", str(e))  # Print the error message
        return jsonify({"message": "Server Error", "error": str(e)}), 500

# Update a listing
# def update_listing(id):
#     data = request.json
#     try:
#         # Ensure that 'expiry' is an integer
#         if 'expiry' in data:
#             data['expiry'] = int(data['expiry'])

#         updated_listing = Listing.objects.get(id=ObjectId(id))
#         updated_listing.update(**data)
#         return jsonify(serialize_doc(updated_listing.to_mongo().to_dict()))
#     except Listing.DoesNotExist:
#         return jsonify({"message": "Listing not found"}), 404
#     except Exception as e:
#         return jsonify({"message": "Server Error", "error": str(e)}), 500

def update_listing(id):
    data = request.json
    print("Incoming Data:", data)  # Print incoming data
    try:
        # Retrieve the listing to be updated
        updated_listing = Listing.objects.get(id=ObjectId(id))

        # Update specific fields if they exist in the request data
        if 'name' in data:
            updated_listing.update(name=data['name'])
        if 'quantity' in data:
            updated_listing.update(quantity=int(data['quantity']))  # Ensure quantity is an integer
        if 'expiry' in data:
            updated_listing.update(expiry=int(data['expiry']))  # Ensure expiry is an integer
        if 'food_type' in data:
            updated_listing.update(food_type=data['food_type'])  # Update food_type if provided

        updated_listing.reload()  # Reload the updated document
        print("Updated Listing:", updated_listing.to_json())  # Print the updated listing

        return jsonify(serialize_doc(updated_listing.to_mongo().to_dict())), 200
    except Listing.DoesNotExist:
        return jsonify({"message": "Listing not found"}), 404
    except Exception as e:
        return jsonify({"message": "Server Error", "error": str(e)}), 500

# Delete a listing
def delete_listing(id):
    try:
        listing = Listing.objects.get(id=ObjectId(id))
        listing.delete()
        return jsonify({"message": "Listing deleted successfully"})
    except Listing.DoesNotExist:
        return jsonify({"message": "Listing not found"}), 404
    except Exception as e:
        return jsonify({"message": "Server Error", "error": str(e)}), 500

# Calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geopy.distance.great_circle(coords_1, coords_2).km

# Get nearby listings based on NGO location
def get_nearby_listings():
    try:
        # Retrieve parameters from the request
        ngo_id = request.args.get('ngoId')
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        # print(ngo_id, latitude, longitude)

        # Ensure latitude and longitude are provided and valid
        if latitude is None or longitude is None or ngo_id is None:
            return jsonify({"message": "ngoId, latitude, and longitude are required"}), 400

        # Query the NGO (User)
        ngo = User.objects.get(id=ObjectId(ngo_id))
        if not ngo:
            return jsonify({"message": "NGO not found"}), 404

        # Get listings with 'not blocked' view
        listings = Listing.objects(view='not blocked').only('name', 'restaurant_id', 'quantity', 'expiry', 'food_type')
        nearby_listings = []
        
        # print("nearby: ", nearby_listings)

        for listing in listings:
            # 'restaurant_id' is a reference to a User object, not an ObjectId
            restaurant = listing.restaurant_id

            # Ensure restaurant has valid latitude and longitude
            if restaurant and restaurant.latitude is not None and restaurant.longitude is not None:
                distance = calculate_distance(
                    latitude,
                    longitude,
                    restaurant.latitude,
                    restaurant.longitude
                )
                print(distance)
                # Filter listings within a specific distance (e.g., 10 km)
                if distance <= 10000000:
                    nearby_listings.append({
                        "name": listing.name,
                        "listingId": str(listing.id),
                        "restaurantId": str(restaurant.id),
                        "restaurantName": restaurant.username,
                        "quantity": listing.quantity,
                        "food_type": listing.food_type,
                        "expiry": listing.expiry
                    })
                    print(nearby_listings)

        return jsonify(nearby_listings)
    except ValueError:
        return jsonify({"message": "Invalid latitude or longitude format"}), 400
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    if isinstance(doc, dict):
        return {key: serialize_doc(value) for key, value in doc.items()}
    elif isinstance(doc, datetime):
        return doc.isoformat()
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    return doc
