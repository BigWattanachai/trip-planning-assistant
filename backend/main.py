from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import time
import json
from datetime import datetime

from config.settings import settings

# Import routers
from routers.activity_router import router as activity_router
from routers.restaurant_router import router as restaurant_router
from routers.flight_router import router as flight_router
from routers.accommodation_router import router as accommodation_router
from routers.video_router import router as video_router
from routers.travel_plan_router import router as travel_plan_router

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Travel Planning Assistant API",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request to {request.url.path} took {process_time:.4f}s")
    return response

# Include routers with API prefix
api_prefix = settings.API_PREFIX
app.include_router(activity_router, prefix=api_prefix)
app.include_router(restaurant_router, prefix=api_prefix)
app.include_router(flight_router, prefix=api_prefix)
app.include_router(accommodation_router, prefix=api_prefix)
app.include_router(video_router, prefix=api_prefix)
app.include_router(travel_plan_router, prefix=api_prefix)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Travel Planner API", "version": settings.VERSION}

# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "api": "Travel Planner API"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.DEBUG else None}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
