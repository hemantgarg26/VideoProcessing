from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.core.config import settings
from app.utils.logger import get_logger
from app.api.health import router as health_router
from app.api.video_processing import router as video_processing_router
from app.utils.db_connect import mongodb

logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="APIs for Deal Running Agents",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
    Adding middleware for Authorization, Authentication and Logging
'''
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0]
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"Request received: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Calculate and log processing time
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    
    # Add processing time header to response
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include Routers
app.include_router(health_router, prefix="/api/health")
app.include_router(video_processing_router, prefix="/api/video")

'''
    DB Setup
'''
@app.on_event("startup")
async def startup_event():
    await mongodb.connect()
    logger.info("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_event():
    await mongodb.close()

@app.get("/")
async def root():
    """
    Root endpoint.
    Returns:
        dict: Welcome message with API info
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION
    } 