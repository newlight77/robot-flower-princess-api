"""Health check router for monitoring and status endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    """
    Health check endpoint.

    Returns system status and basic API information.
    Used by monitoring tools and load balancers.
    """
    return {
        "message": "Welcome to Robot-Flower-Princess Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "healthy",
        "service": "robot-flower-princess-api",
    }
