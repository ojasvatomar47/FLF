from flask import Flask, jsonify
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from datetime import datetime
import json
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB connection
app.config['MONGODB_SETTINGS'] = {
    'db': 'test',  # Replace with your actual database name
    'host': os.getenv('MONGO_URI')
}

# Initialize MongoEngine
db = MongoEngine()
db.init_app(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

# Enable CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# Custom JSON Encoder
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 format
        elif isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)

app.json_encoder = MongoJSONEncoder

# Import blueprints
from routes.order_routes import order_bp
from routes.listing_routes import listing_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.recommendation_routes import recommendations_bp
from models.chat import Chat  # Import the Chat model

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(order_bp)
app.register_blueprint(listing_bp)
app.register_blueprint(user_bp)
app.register_blueprint(recommendations_bp)

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    print('A user connected!')

@socketio.on('join_chat_room')
def handle_join_chat_room(orderId):
    join_room(orderId)
    print(f'User joined room for order {orderId}')

@socketio.on('send_chat_message')
def handle_send_chat_message(data):
    message = data.get('message')
    order_id = data.get('orderId')
    sender = data.get('sender')

    # Save message to MongoDB
    new_message = Chat(message=message, sender=sender, orderId=order_id)
    try:
        new_message.save()
        print('Message saved successfully!')
        emit('receive_chat_message', {'message': message, 'sender': sender}, to=order_id)
    except Exception as e:
        print(f'Error saving message: {str(e)}')

@socketio.on('disconnect')
def handle_disconnect():
    print('A user disconnected!')

# Run the app with SocketIO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 8800)), debug=True)
