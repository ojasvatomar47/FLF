from flask import Blueprint
from controllers.sentiment_controller import analyze_review_sentiment

# Define the Blueprint for sentiment analysis routes
sentiment_bp = Blueprint('sentiment', __name__)

# Add route to Blueprint
sentiment_bp.route('/analyze-sentiment', methods=['POST'])(analyze_review_sentiment)
