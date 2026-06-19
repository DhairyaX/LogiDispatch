import logging
from pymongo import MongoClient
from pymongo.database import Database
from route_optimizer.api.core.config import settings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    _client: MongoClient | None = None
    _db: Database | None = None

    @classmethod
    def connect_to_mongodb(cls):
        """Establish connection to MongoDB Atlas."""
        if cls._client is None:
            try:
                # Mask password for logging
                safe_uri = settings.MONGODB_URI
                if "@" in safe_uri:
                    parts = safe_uri.split("@")
                    prefix = parts[0].split("://")[0]
                    safe_uri = f"{prefix}://***:***@{parts[1]}"

                logger.info(f"Initializing MongoDB connection to: {safe_uri}")
                # Connect to MongoDB
                cls._client = MongoClient(settings.MONGODB_URI)
                cls._db = cls._client[settings.MONGODB_DB_NAME]
                logger.info(f"Database selected: {cls._db.name}")
            except Exception as e:
                logger.error(f"Failed to initialize MongoDB connection: {e}")
                raise

    @classmethod
    def get_database(cls) -> Database:
        """Get the database instance."""
        if cls._db is None:
            cls.connect_to_mongodb()
        return cls._db

    @classmethod
    def get_client(cls) -> MongoClient:
        """Get the MongoClient instance."""
        if cls._client is None:
            cls.connect_to_mongodb()
        return cls._client

    @classmethod
    def close_mongodb_connection(cls):
        """Close the MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB connection closed.")

def get_database() -> Database:
    """Helper to get database."""
    return MongoDBConnection.get_database()

def connect_to_mongodb():
    """Helper to connect."""
    MongoDBConnection.connect_to_mongodb()

def close_mongodb_connection():
    """Helper to close."""
    MongoDBConnection.close_mongodb_connection()
