from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging
from typing import Callable

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_middleware(app):
    """Configure middleware for the FastAPI application"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        request_id = str(int(time.time() * 1000))
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Request {request_id}: {request.method} {request.url.path} from {client_host}")
        
        # Get response
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response {request_id}: {response.status_code}")
        
        # Add request ID header
        response.headers["X-Request-ID"] = request_id
        
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware for timing request processing"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log if process time is long
        if process_time > 1.0:
            logger.warning(f"Long request processing time: {process_time:.2f}s for {request.method} {request.url.path}")
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Log error
            logger.error(f"Unhandled error: {str(e)}")
            
            # Create error response
            error_response = {
                "error": True,
                "message": "An internal server error occurred",
                "type": str(type(e).__name__),
                "path": request.url.path
            }
            
            # Return formatted error
            return Response(
                content=json.dumps(error_response),
                status_code=500,
                media_type="application/json"
            )
