from flask_mongoengine import MongoEngine
from datetime import datetime

db = MongoEngine()

class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    user_type = db.StringField(choices=['Restaurant', 'Charity/NGO'], required=True)
    verification_code = db.StringField(required=True)
    latitude = db.FloatField(required=True)
    longitude = db.FloatField(required=True)
    location_name = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users'
    }
