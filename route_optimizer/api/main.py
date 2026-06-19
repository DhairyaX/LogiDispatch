from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from route_optimizer.api.core.config import settings
from route_optimizer.api.core.exceptions import add_exception_handlers
from route_optimizer.api.routers import health, drivers, vehicles, deliveries, optimization, analytics, debug, routes

from route_optimizer.database.connection import close_mongodb_connection
from route_optimizer.database.health_check import test_connection

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Mask password in URI
        safe_uri = settings.MONGODB_URI
        if "@" in safe_uri:
            parts = safe_uri.split("@")
            prefix = parts[0].split("://")[0]
            safe_uri = f"{prefix}://***:***@{parts[1]}"
            
        logger.info(f"Connecting to MongoDB with URI: {safe_uri}")
        logger.info(f"Database name: {settings.MONGODB_DB_NAME}")
        
        if test_connection():
            print("✅ MongoDB Atlas Connected")
            logger.info("✅ MongoDB Atlas Connected")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        logger.error(f"❌ MongoDB Connection Failed: {e}")
    yield
    close_mongodb_connection()

app = FastAPI(
    title="Logistics Route Optimization API",
    description="Backend API for Logistics Operations Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://logi-dispatch-gfkvrkrot-dhairyaxs-projects.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
add_exception_handlers(app)

# Include Routers
app.include_router(health.router)
app.include_router(debug.router)
app.include_router(drivers.router)
app.include_router(vehicles.router)
app.include_router(deliveries.router)
app.include_router(optimization.router)
app.include_router(analytics.router)
app.include_router(routes.router)
