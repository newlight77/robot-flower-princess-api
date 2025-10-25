"""Main FastAPI application for ML Player service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logging import logger

from configurator.settings import settings
from hexagons.mlplayer.driver.bff.routers import ml_player_router
from hexagons.health.driver.bff.routers import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"AI ML Player service URL: {settings.game_service_url}")
    logger.info(f"ML models enabled: {settings.enable_ml_models}")
    yield
    logger.info("Shutting down AI ML Player service")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ML-based player for RFP game API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router.router)
app.include_router(ml_player_router.router)
