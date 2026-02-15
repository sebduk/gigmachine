"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.tasks.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop background scheduler with the app."""
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="GigFinder",
    description="A talent agent for academics — matching researchers with funding opportunities",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from backend.routers.health import router as health_router  # noqa: E402
from backend.routers.academic_profiles import router as profiles_router  # noqa: E402
from backend.routers.funding_opportunities import router as opportunities_router  # noqa: E402
from backend.routers.data_sources import router as sources_router  # noqa: E402
from backend.routers.matches import router as matches_router  # noqa: E402

app.include_router(health_router)
app.include_router(profiles_router)
app.include_router(opportunities_router)
app.include_router(sources_router)
app.include_router(matches_router)
