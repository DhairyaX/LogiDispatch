from fastapi import APIRouter, HTTPException
from route_optimizer.database.connection import get_database

router = APIRouter(prefix="/api/v1/debug", tags=["Debug"])

@router.get("/database")
def debug_database():
    try:
        db = get_database()
        collections = db.list_collection_names()
        
        counts = {}
        for coll in ["drivers", "vehicles", "deliveries", "routes", "analytics"]:
            if coll in collections:
                counts[coll] = db[coll].count_documents({})
            else:
                counts[coll] = 0
                
        return {
            "database": db.name,
            **counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
