"""
FastAPI application entry point for Accelerator Resource Provider
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import structlog

from src.itl_accelerator_provider.config import get_settings
from src.itl_accelerator_provider.routes import spark_nodes, spark_instances, spark_jobs

logger = structlog.get_logger(__name__)
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="ITL Accelerator Resource Provider",
    description="Manage GPU, TPU, and other accelerators in ITL Control Plane",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("Starting Accelerator Resource Provider", version="0.1.0")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Accelerator Resource Provider")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "accelerator-provider"})


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ITL Accelerator Resource Provider",
        "version": "0.1.0",
        "status": "ready",
        "docs": "/docs",
        "health": "/health",
    }


# Each route module exposes a setup_*_routes(app, engine, provider) -> APIRouter
# factory rather than a module-level `router` — none of the handlers inside use
# engine/provider yet (all still TODO: Implement with storage engine), so None
# placeholders are correct until that storage-engine wiring actually exists.
app.include_router(spark_nodes.setup_spark_nodes_routes(app, None, None), prefix="/subscriptions", tags=["sparkNodes"])
app.include_router(spark_instances.setup_spark_instances_routes(app, None, None), prefix="/subscriptions", tags=["sparkOllamaInstances"])
app.include_router(spark_jobs.setup_spark_jobs_routes(app, None, None), prefix="/subscriptions", tags=["sparkJobs"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
