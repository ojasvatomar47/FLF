from mongoengine import Document, StringField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField, ReferenceField, IntField
from datetime import datetime, timedelta
from models.listing import Listing  # Import the Listing model
from models.user import User  # Import the User model

class ListingDetail(EmbeddedDocument):
    listing = ReferenceField(Listing, required=True)  # Reference to Listing model
    name = StringField(required=True)
    quantity = IntField(required=True)
    expiry = IntField(required=True, choices=[1, 2, 3, 480])  # Expiry options in hours
    restaurant_id = ReferenceField(User, required=True)  # Reference to User model for restaurant
    restaurant_name = StringField(required=True)
    view = StringField(choices=['blocked', 'not blocked'], default='not blocked')
    food_type = StringField(required=True, choices=['Vegetarian', 'Non-Vegetarian', 'Vegan', 'other'])  # Add food type
    created_at = DateTimeField(default=datetime.utcnow)

class Order(Document):
    restaurant_id = ReferenceField(User, required=True)  # Reference to User model for restaurant
    ngo_id = ReferenceField(User, required=True)  # Reference to User model for NGO
    listings = ListField(EmbeddedDocumentField(ListingDetail))  # List of embedded ListingDetail documents
    status = StringField(choices=['accepted', 'declined', 'requested', 'fulfilled', 'cancelled', 'dismissed'], default='requested')
    rest_code = StringField()
    ngo_code = StringField()
    rest_review = StringField(default='')
    ngo_review = StringField(default='')
    rest_sentiment = StringField(default='')
    ngo_sentiment = StringField(default='')
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'orders'  # Explicitly set the collection name
    }

    # Pre-save hook for auto-decline and auto-dismiss
    def clean(self):
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)

        if self.status == 'requested' and self.created_at <= two_hours_ago:
            self.status = 'declined'
            # Set all associated listings to 'not blocked'
            for listing_detail in self.listings:
                listing = Listing.objects(id=listing_detail.listing.id).first()
                if listing:
                    listing.view = 'not blocked'
                    listing.save()

        if self.status == 'accepted' and self.created_at <= two_hours_ago:
            self.status = 'dismissed'
            # Set all associated listings to 'not blocked'
            for listing_detail in self.listings:
                listing = Listing.objects(id=listing_detail.listing.id).first()
                if listing:
                    listing.view = 'not blocked'
                    listing.save()
