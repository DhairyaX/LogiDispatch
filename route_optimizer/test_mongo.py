import os
from dotenv import load_dotenv
import logging
from pymongo import MongoClient

# Configure basic logging for test script
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main():
    # Load environment variables
    load_dotenv()
    
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "logistics_db")
    
    if not uri:
        logging.error("MONGODB_URI environment variable not set.")
        return

    try:
        # Connect to MongoDB Atlas
        client = MongoClient(uri)
        
        # Execute ping command
        client.admin.command("ping")
        print("MongoDB Connected Successfully")
        
        # Access database
        db = client[db_name]
        print(f"Database: {db_name}")
        
        # Print existing collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
    except Exception as e:
        print(f"❌ MongoDB Connection Failed")
        print(f"Detailed error: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()

if __name__ == "__main__":
    main()
