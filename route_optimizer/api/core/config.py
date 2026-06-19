from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Calculate the path to the route_optimizer directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    
    # MongoDB Settings
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "logistics_db"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra='ignore')

settings = Settings()
