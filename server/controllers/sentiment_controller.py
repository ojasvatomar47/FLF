from flask import jsonify, request
from utils.sentiment_analysis import analyze_sentiment

def analyze_review_sentiment():
    # Get text from request body
    data = request.get_json()
    text = data.get('text', '')
    
    # If text is empty, return an error
    if not text:
        return jsonify({"error": "Text field is required"}), 400
    
    # Analyze sentiment
    sentiment = analyze_sentiment(text)
    
    # Return sentiment result
    return jsonify({"sentiment": sentiment}), 200
