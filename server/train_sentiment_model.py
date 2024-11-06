import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
file_path = r'C:\Users\ojasv\Downloads\archive\training.1600000.processed.noemoticon.csv'
column_names = ["target", "id", "date", "flag", "user", "text"]
data = pd.read_csv(file_path, encoding='latin1', names=column_names)

# Keep only 'target' and 'text' columns, map sentiment target 4 -> 1, 0 -> 0
data = data[['target', 'text']]
data['target'] = data['target'].apply(lambda x: 1 if x == 4 else 0)

# Clean text
def clean_text(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#','', text)
    return text.lower()

data['text'] = data['text'].apply(clean_text)

# Split data
X = data['text']
y = data['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Evaluate and save model
y_pred = model.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))

joblib.dump(model, "utils/sentiment_model.joblib")
joblib.dump(vectorizer, "utils/vectorizer.joblib")
