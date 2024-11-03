from flask_mongoengine import MongoEngine
from datetime import datetime, timedelta

db = MongoEngine()

class Listing(db.Document):
    restaurant_id = db.ReferenceField('User', required=True)
    name = db.StringField(required=True)
    quantity = db.IntField(required=True)
    expiry = db.IntField(required=True, choices=[1, 2, 3, 480])  # Expiry in hours
    view = db.StringField(choices=['blocked', 'not blocked'], default='not blocked')
    food_type = db.StringField(required=True)  # New field for type of food
    created_at = db.DateTimeField(default=datetime.utcnow)
    expires_at = db.DateTimeField(default=lambda: datetime.utcnow() + timedelta(hours=1))  # Default to 1 hour from now

    meta = {
        'collection': 'listings',
        'indexes': [
            {
                'fields': ['expires_at'],
                'expireAfterSeconds': 0
            }
        ]
    }
