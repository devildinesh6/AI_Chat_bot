import pymongo
from datetime import datetime

# 1. Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    # Creates/Selects the database
    db = client["ollama_chat_history"]
    # Creates/Selects the collection (table)
    logs_collection = db["logs"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

def save_log(file_name, original_text, summary_text):
    """
    Saves a single processed row to MongoDB.
    """
    record = {
        "timestamp": datetime.now(),
        "file_name": file_name,
        "input_text": original_text,
        "ai_summary": summary_text
    }
    
    try:
        logs_collection.insert_one(record)
    except Exception as e:
        print(f"❌ Error saving log: {e}")