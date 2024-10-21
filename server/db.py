import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_db():
    try:
        # Fetch MongoDB URI and database name from environment variables
        mongo_uri = os.getenv("MONGO_URI")
        default_db_name = os.getenv("MONGODB_DB_NAME")

        # Create a MongoClient instance with the URI
        client = MongoClient(mongo_uri)
        
        # Access the specified database
        db = client[default_db_name]
        
        print("MongoDB connected successfully")
        return db
    except Exception as e:
        print("MongoDB connection failed:", e)
        # Exit the program if the connection fails
        raise SystemExit(1)
