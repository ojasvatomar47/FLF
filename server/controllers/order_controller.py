from flask import jsonify, request
from models.order import Order
from models.listing import Listing
from models.order import ListingDetail
from bson import ObjectId
from datetime import datetime
import random
import string
from models.user import User  # Import the User model

def create_order():
    data = request.json
    try:
        # Extract fields from request body
        restaurant_id = data.get('restaurantId')
        ngo_id = data.get('ngoId')
        listings_data = data.get('listings')

        listings_details = []
        for item in listings_data:
            listing_detail = {
                'listing': str(ObjectId(item['listing'])),  # Convert ObjectId to string
                'name': item.get('name'),
                'quantity': item.get('quantity'),
                'expiry': item.get('expiry'),
                'restaurant_id': str(ObjectId(item['restaurant_id'])),  # Convert ObjectId to string
                'restaurant_name': item.get('restaurant_name'),
                'view': item.get('view'),
                'food_type': item.get('food_type')
            }
            listings_details.append(listing_detail)

        # Update NGO food type count based on listings
        ngo_user = User.objects.get(id=ObjectId(ngo_id))
        for item in listings_data:
            food_type = item.get('food_type')
            if food_type == 'Vegetarian':
                ngo_user.update(inc__vegorders=1)
            elif food_type == 'Vegan':
                ngo_user.update(inc__veganorders=1)
            elif food_type == 'Non-Vegetarian':
                ngo_user.update(inc__nonvegorders=1)

        # Create a new Order object
        new_order = Order(
            restaurant_id=ObjectId(restaurant_id),  # Convert restaurantId to ObjectId
            ngo_id=ObjectId(ngo_id),  # Convert ngoId to ObjectId
            listings=listings_details,  # Use the processed ListingDetail objects
            status=data.get('status'),  # Get status from request data
        )

        # Save the new order
        new_order.save()
        
         # Fetch the saved order to verify
        saved_order = Order.objects.get(id=new_order.id)
        print("\n--- Saved Order Details ---")
        print(saved_order.to_json())  # This will show what has been save

        # Prepare response data
        response_data = {
            "_id": str(new_order.id),  # Convert ObjectId to string
            "restaurant_id": str(new_order.restaurant_id.id),  # Convert ObjectId to string
            "ngo_id": str(new_order.ngo_id.id),  # Convert ObjectId to string
            "listings": listings_details,  # This is already in a JSON-friendly format
            "status": new_order.status,
            "created_at": new_order.created_at.isoformat()
        }

        return jsonify({
            "status": "success",
            "data": response_data
        }), 201

    except Exception as e:
        return jsonify({
            "status": "failure",
            "error": str(e)
        }), 500

def get_orders_by_restaurant():
    try:
        # Get restaurant_id from query params
        restaurant_id = request.args.get('restaurant_id')
        print(f"Restaurant ID: {restaurant_id}")

        # Query orders by restaurant_id (convert it to ObjectId)
        orders = Order.objects(restaurant_id=ObjectId(restaurant_id))

        # Prepare the response data
        response_data = []
        for order in orders:
            # Convert the order document to a dictionary and serialize it
            order_dict = serialize_doc(order.to_mongo().to_dict())
            response_data.append(order_dict)

            # Print the details of each fetched order
            print("\n--- Fetched Order Details ---")
            print(order_dict)

        # Return JSON response with the orders inside an array
        return jsonify({
            "data": response_data  # This is already an array of orders
        }), 200

    except Exception as e:
        print("\n--- Error Occurred ---")
        print(str(e))  # Print the exception error
        return jsonify({
            "status": "failure",
            "error": str(e)
        }), 500

def get_orders_by_ngo():
    try:
        # Get ngo_id from query params
        ngo_id = request.args.get('ngo_id')
        print(f"NGO ID: {ngo_id}")

        # Query orders by ngo_id (convert it to ObjectId)
        orders = Order.objects(ngo_id=ObjectId(ngo_id))

        # Prepare the response data
        response_data = []
        for order in orders:
            # Convert the order document to a dictionary and serialize it
            order_dict = serialize_doc(order.to_mongo().to_dict())
            response_data.append(order_dict)

            # Print the details of each fetched order
            print("\n--- Fetched Order Details ---")
            print(order_dict)

        # Return JSON response with the orders inside an array
        return jsonify({
            "data": response_data  # This is already an array of orders
        }), 200

    except Exception as e:
        print("\n--- Error Occurred ---")
        print(str(e))  # Print the exception error
        return jsonify({
            "status": "failure",
            "error": str(e)
        }), 500



def get_order_info(order_id):
    try:
        order = Order.objects.get(id=ObjectId(order_id))
        return jsonify({
            "status": "success",
            "data": serialize_doc(order.to_mongo().to_dict())
        })
    except Order.DoesNotExist:
        return jsonify({
            "status": "failure",
            "error": "Order not found"
        }), 404

def decline_order(order_id):
    try:
        order = Order.objects.get(id=ObjectId(order_id))
        order.update(set__status='declined')
        return jsonify({
            "status": "success",
            "data": serialize_doc(order.to_mongo().to_dict())
        })
    except Order.DoesNotExist:
        return jsonify({
            "status": "failure",
            "error": "Order not found"
        }), 404


# def accept_order(order_id):
#     try:
#         order = Order.objects.get(id=ObjectId(order_id))
#         order.update(set__status='accepted')
#         return jsonify({
#             "sentNidata": serialize_doc(order.to_mongo().to_dict())
#         })
#     except Order.DoesNotExist:
#         return jsonify({
#             "status": "failure",
#             "error": "Order not found"
#         }), 404





def generate_code(length=6):
    """Generate a random code of specified length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))



def accept_order(order_id):
    try:
        # Fetch the order by ID
        order = Order.objects.get(id=ObjectId(order_id))
        
        # Generate unique codes for NGO and restaurant
        ngo_code = generate_code(6)  
        rest_code = generate_code(6)  

        # Update the order's status and codes
        order.update(set__status='accepted', set__ngo_code=ngo_code, set__rest_code=rest_code)

        # Block the view of each listing in the order
        for listing_detail in order.listings:
            listing_id = None  # Initialize listing_id here
            
            try:
                # Ensure that the listing reference is stored correctly and retrieve ObjectId directly
                if isinstance(listing_detail.listing, ObjectId):
                    listing_id = listing_detail.listing
                else:
                    listing_id = listing_detail.listing.id  # Should handle `Listing` references properly

                # Fetch the listing document by its ObjectId
                listing = Listing.objects.get(id=ObjectId(listing_id))

                # Update the 'view' field to 'blocked'
                listing.update(set__view='blocked')
                print(f"Listing {listing.id} view set to blocked.")
                
            except Listing.DoesNotExist:
                print(f"Listing with ID {listing_id} not found.")
            except Exception as e:
                print(f"Error updating listing with ID {listing_id}: {e}")

        # Print the updated order details for debugging
        print("Updated Order:", order.to_json())

        # Return the updated order details in the response
        return jsonify({
            "sentNidata": serialize_doc(order.to_mongo().to_dict())
        }), 200
        
    except Order.DoesNotExist:
        return jsonify({
            "status": "failure",
            "error": "Order not found"
        }), 404
    except Exception as e:
        print("\n--- Error Occurred ---")
        print(str(e))  # Print the exception error
        return jsonify({
            "status": "failure",
            "error": str(e)
        }), 500


def cancel_order(order_id):
    try:
        # Get the request body data
        data = request.get_json()
        code = data.get('code')
        user_type = data.get('user_type')

        # Fetch the order by ID
        order = Order.objects.get(id=ObjectId(order_id))

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Determine which code (NGO or Restaurant) to check based on user type
        party_code = None
        if user_type == 'Restaurant':
            party_code = order.ngo_code
        elif user_type == 'Charity/NGO':
            party_code = order.rest_code
        else:
            return jsonify({"message": "Invalid user type"}), 400

        # Validate the provided code
        if not party_code or code != party_code:
            return jsonify({"message": "Invalid code"}), 400

        # # Unblock view for listings associated with the order
        # for listing_detail in order.listings:
        #     listing_id = listing_detail.listing.id
        #     listing = Listing.objects.get(id=ObjectId(listing_id))
        #     if listing:
        #         listing.update(set__view='not blocked')

        # Update the order status to "cancelled"
        order.update(set__status='cancelled')

        # Return success response
        return jsonify({"message": "Order cancelled successfully"}), 200

    except Order.DoesNotExist:
        return jsonify({"message": "Order not found"}), 404
    except Exception as e:
        print(f"Error cancelling order: {e}")
        return jsonify({"message": "Server Error", "error": str(e)}), 500



def fulfill_order(order_id):
    try:
        # Get the request body data
        data = request.get_json()
        code = data.get('code')
        user_type = data.get('user_type')

        # Fetch the order by ID
        order = Order.objects.get(id=ObjectId(order_id))

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Check if the requesting party matches the order's restaurant or NGO
        party_code = None
        if user_type == 'Restaurant':
            party_code = order.ngo_code
        elif user_type == 'Charity/NGO':
            party_code = order.rest_code

        if not party_code:
            return jsonify({"message": "Invalid user type"}), 400

        if code != party_code:
            return jsonify({"message": "Invalid code"}), 400

        # Delete listings associated with the order
        for listing_detail in order.listings:
            listing_id = listing_detail.listing.id
            Listing.objects(id=ObjectId(listing_id)).delete()

        # Update the order's status to 'fulfilled'
        order.update(set__status='fulfilled')

        # Return success response
        return jsonify({"message": "Order fulfilled successfully"}), 200

    except Order.DoesNotExist:
        return jsonify({"message": "Order not found"}), 404
    except Exception as e:
        print(f"Error fulfilling order: {e}")
        return jsonify({"message": "Server Error", "error": str(e)}), 500


def get_messages_by_order_id(order_id):
    # Implement your logic to get messages by order_id
    pass




def add_rest_review(order_id):
    try:
        # Get the review data from the request body
        data = request.get_json()
        review = data.get('review')

        # Fetch the order by order_id
        order = Order.objects.get(id=ObjectId(order_id))

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Check if the review for the restaurant already exists
        if order.rest_review:
            return jsonify({"message": "Review already added"}), 400

        # Add the restaurant review to the order
        order.update(set__rest_review=review)

        # Return success response
        return jsonify({"message": "Review added successfully"}), 201

    except Order.DoesNotExist:
        return jsonify({"message": "Order not found"}), 404
    except Exception as e:
        print(f"Error adding review: {e}")
        return jsonify({"message": "Server Error", "error": str(e)}), 500


def add_ngo_review(order_id):
    try:
        # Get the review data from the request body
        data = request.get_json()
        review = data.get('review')

        # Fetch the order by order_id
        order = Order.objects.get(id=ObjectId(order_id))

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Check if the review for the restaurant already exists
        if order.ngo_review:
            return jsonify({"message": "Review already added"}), 400

        # Add the restaurant review to the order
        order.update(set__ngo_review=review)

        # Return success response
        return jsonify({"message":review}), 201

    except Order.DoesNotExist:
        return jsonify({"message": "Order not found"}), 404
    except Exception as e:
        print(f"Error adding review: {e}")
        return jsonify({"message": "Server Error", "error": str(e)}), 500


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
