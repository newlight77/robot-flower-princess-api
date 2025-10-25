from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hexagons.game.driver.bff.routers import game_router
from hexagons.aiplayer.driver.bff.routers import aiplayer_router

app = FastAPI(
    title="Robot-Flower-Princess Game API",
    description="A strategic puzzle game API where you guide a robot to collect flowers and deliver them to a princess",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_router.router)
app.include_router(aiplayer_router.router)


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {
        "message": "Welcome to Robot-Flower-Princess Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "healthy",
        "service": "robot-flower-princess-api",
    }
