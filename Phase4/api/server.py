"""FastAPI server for managing calls and webhooks."""

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.config import config
from .routes import calls_router, webhooks_router

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Appointment Agent API",
    description="API for managing outbound calls and receiving Twilio webhooks",
    version="0.3.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calls_router)
app.include_router(webhooks_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Appointment Agent API",
        "version": "0.3.0",
        "phase": 3,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(
        "api_server_starting",
        host=config.api_host,
        port=config.api_port,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("api_server_shutting_down")


def run_server():
    """Run the API server."""
    uvicorn.run(
        "api.server:app",
        host=config.api_host,
        port=config.api_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
