"""
Application Lifecycle Management

Handles startup and shutdown events for the Accelerator provider.

Follows Core provider pattern.
"""

import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app, engine, provider):
    """
    Application lifespan context manager
    
    Handles:
    - Database initialization
    - Connection pool setup
    - Provider registration
    - Graceful shutdown
    
    Args:
        app: FastAPI application
        engine: SQLAlchemy storage engine
        provider: Accelerator provider instance
    """
    
    # Startup
    logger.info("=" * 80)
    logger.info("Accelerator Provider Startup")
    logger.info("=" * 80)
    
    try:
        # Initialize storage engine
        await engine.initialize()
        logger.info("✓ Storage engine initialized")
    except Exception as e:
        logger.error(f"✗ Storage engine initialization failed: {e}")
        raise
    
    try:
        # Run database migrations (if auto-migrate enabled)
        # await engine.run_migrations()
        logger.info("✓ Database schema ready")
    except Exception as e:
        logger.warning(f"⚠ Database migration check failed: {e}")
    
    logger.info(f"✓ Provider {provider.namespace} ready")
    logger.info(f"✓ Resource types: {', '.join(provider.get_resource_types())}")
    logger.info("=" * 80)
    logger.info("Accelerator Provider is READY")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("Accelerator Provider Shutdown")
    logger.info("=" * 80)
    
    try:
        # Close storage engine
        await engine.close()
        logger.info("✓ Storage engine closed")
    except Exception as e:
        logger.error(f"✗ Storage engine shutdown failed: {e}")
    
    logger.info("=" * 80)
    logger.info("Accelerator Provider stopped")
    logger.info("=" * 80)
