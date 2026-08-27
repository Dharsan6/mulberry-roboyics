import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database.connection import engine, Base
from backend.app.api import telemetry, samples, analysis, predictions, prescriptions, simulator_api, missions

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("precision_sericulture_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Precision Sericulture Database Tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Precision Sericulture Backend Started Successfully.")
    yield
    logger.info("Precision Sericulture Backend Shutting Down.")

app = FastAPI(
    title="Precision Sericulture API Backend",
    description="Automated Rover Soil Sensing & Mulberry Agronomy Intelligence API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router)
app.include_router(samples.router)
app.include_router(analysis.router)
app.include_router(predictions.router)
app.include_router(prescriptions.router)
app.include_router(simulator_api.router)
app.include_router(missions.router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "Precision Sericulture Backend",
        "mock_mode": settings.MOCK_MODE,
        "database": "sqlite/postgresql ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
