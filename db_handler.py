import pymongo
from datetime import datetime

# 1. Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["ollama_chat_history"]
    logs_collection = db["logs"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

def save_log(file_name, original_text, summary_text):
    record = {
        "timestamp": datetime.now(),
        "file_name": file_name,
        "input_text": original_text,
        "ai_summary": summary_text
    }
    try:
        logs_collection.insert_one(record)
        print(f"✅ Saved to DB: {original_text[:20]}...")
    except Exception as e:
        print(f"❌ Error saving log: {e}")

# ---------------------------------------------------------
# ✅ UPDATED: Return Raw Data for the UI
# ---------------------------------------------------------
def get_recent_chats(limit=10):
    """
    Fetches the last 'limit' chats as a list of dictionaries.
    """
    try:
        # Get chats tagged as 'Chat_Mode'
        cursor = logs_collection.find({"file_name": "Chat_Mode"}).sort("timestamp", -1).limit(limit)
        return list(cursor)[::-1] # Reverse to get Oldest -> Newest
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return []