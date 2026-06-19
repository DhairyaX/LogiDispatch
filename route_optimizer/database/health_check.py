import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from route_optimizer.database.connection import MongoDBConnection

logger = logging.getLogger(__name__)

def test_connection() -> bool:
    """
    Execute MongoDB ping command to test connectivity.
    Returns True if connected, raises an Exception if failed.
    """
    try:
        client = MongoDBConnection.get_client()
        # The ping command is cheap and does not require auth, but ensures we can talk to the server.
        # Alternatively, checking server_info() requires auth and validates credentials.
        client.admin.command('ping')
        logger.info("MongoDB connection established")
        return True
    except OperationFailure as e:
        logger.error(f"MongoDB authentication failed: {e}")
        raise
    except ConnectionFailure as e:
        logger.error(f"MongoDB network access denied or connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        raise
