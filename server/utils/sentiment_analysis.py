import joblib

# Load the pre-trained model and vectorizer
model = joblib.load("utils/sentiment_model.joblib")
vectorizer = joblib.load("utils/vectorizer.joblib")

def analyze_sentiment(text):
    # Transform the input text
    text_vectorized = vectorizer.transform([text])
    # Predict sentiment (0 = Negative, 1 = Positive)
    prediction = model.predict(text_vectorized)[0]
    sentiment = "Positive" if prediction == 1 else "Negative"
    return sentiment
