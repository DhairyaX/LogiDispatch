from fastapi import APIRouter, HTTPException
from route_optimizer.database.connection import get_database
from route_optimizer.database.health_check import test_connection

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("/")
def health_check():
    return {"status": "healthy"}

@router.get("/database")
def database_health():
    try:
        test_connection()
        db = get_database()
        collections = db.list_collection_names()
        return {
            "status": "healthy",
            "database": db.name,
            "collections": collections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
