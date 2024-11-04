from flask import jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from models.user import User
from mongoengine.errors import NotUniqueError
from bson import ObjectId

# Function to serialize MongoDB ObjectId and other non-serializable fields
def serialize_user(user):
    return {
        "_id": str(user.id),  # MongoDB ObjectId
        "username": user.username,
        "email": user.email,
        "password": user.password,  # Password will be included (hashed)
        "userType": user.user_type,
        "verificationCode": user.verification_code,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "locationName": user.location_name,
        "vegOrders": user.vegorders if user.user_type == 'Charity/NGO' else None,
        "veganOrders": user.veganorders if user.user_type == 'Charity/NGO' else None,
        "nonVegOrders": user.nonvegorders if user.user_type == 'Charity/NGO' else None,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "updatedAt": user.updated_at.isoformat() if user.updated_at else None
    }

# Register User
def register_user(data):
    try:
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType')
        verification_code = data.get('verificationCode')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_name = data.get('locationName')

        # Check if the user already exists
        if User.objects(email=email).first():
            raise NotUniqueError('User already exists with this Email')

        # Hash password
        hashed_password = generate_password_hash(password, method='sha256')

        # Initialize order counters for NGOs
        vegorders = 0 if user_type == 'Charity/NGO' else None
        veganorders = 0 if user_type == 'Charity/NGO' else None
        nonvegorders = 0 if user_type == 'Charity/NGO' else None

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type=user_type,
            verification_code=verification_code,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            vegorders=vegorders,
            veganorders=veganorders,
            nonvegorders=nonvegorders
        )

        # Save user to DB
        new_user.save()

        return jsonify({"message": "User registered successfully"}), 201

    except NotUniqueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

# Login User
def login_user(data):
    try:
        email = data.get('email')
        password = data.get('password')

        # Find the user by email
        user = User.objects(email=email).first()

        if not user:
            return jsonify({"message": "The Email you entered is not registered!"}), 400

        # Verify password
        if not check_password_hash(user.password, password):
            return jsonify({"message": "The password you entered is invalid!"}), 400

        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, 'secretkey', algorithm='HS256')

        # Set the token in a cookie
        response = make_response(jsonify({
            "message": "User logged in successfully",
            "user": serialize_user(user)  # Send the serialized user object
        }))
        response.set_cookie('accessToken', token, httponly=True)

        return response

    except Exception as e:
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

# Logout User
def logout_user():
    try:
        # Clear the accessToken cookie
        response = make_response(jsonify({"message": "User logged out successfully"}))
        response.delete_cookie('accessToken')

        return response

    except Exception as e:
        return jsonify({"message": "Failed to logout user", "error": str(e)}), 500
