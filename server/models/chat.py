from flask_mongoengine import MongoEngine
from datetime import datetime

db = MongoEngine()

class Chat(db.Document):
    message = db.StringField(required=True)
    sender = db.StringField(required=True)
    orderId = db.StringField(required=True)  # Use snake_case for consistency
    timestamp = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'chats'  # Define collection name if different from model name
    }
