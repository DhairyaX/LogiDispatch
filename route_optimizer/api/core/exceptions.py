from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class OptimizationError(Exception):
    def __init__(self, message: str):
        self.message = message

class OSRMError(Exception):
    def __init__(self, message: str):
        self.message = message

def add_exception_handlers(app):
    @app.exception_handler(OptimizationError)
    async def optimization_exception_handler(request: Request, exc: OptimizationError):
        logger.error(f"Optimization Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.message, "type": "optimization_error"},
        )

    @app.exception_handler(OSRMError)
    async def osrm_exception_handler(request: Request, exc: OSRMError):
        logger.error(f"OSRM Error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": exc.message, "type": "osrm_error"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "type": "validation_error"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Internal Server Error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred.", "type": "internal_error"},
        )
