"""
FastAPI Application Factory

Creates and configures the FastAPI application with:
- SDK standard routes (generic, observability)
- Accelerator-specific routes (sparkNodes, sparkOllamaInstances, sparkJobs)
- Middleware (audit, CORS, etc.)
- Lifespan management

Follows Core provider pattern.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from itl_controlplane_sdk.api import (
    setup_generic_routes,
    setup_observability_routes,
    add_audit_middleware,
    setup_standard_openapi_tags,
    register_resource_types,
)

from ..routes import (
    setup_spark_nodes_routes,
    setup_spark_instances_routes,
    setup_spark_jobs_routes,
)
from .lifecycle import app_lifespan

logger = logging.getLogger(__name__)


def create_app(server, engine, provider, registry) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        server: AcceleratorProviderServer instance
        engine: SQLAlchemy storage engine
        provider: AcceleratorProvider instance
        registry: ResourceProviderRegistry instance
        
    Returns:
        Configured FastAPI application
    """
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="ITL Accelerator Resource Provider",
        description="Manages GPU/TPU/NPU compute resources via SparkNodes, SparkOllamaInstances, and SparkJobs",
        version="0.1.0",
        lifespan=lambda app: app_lifespan(app, engine, provider),
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Store references for use in routes
    app.state.engine = engine
    app.state.provider = provider
    app.state.registry = registry
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure from environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # SDK standard middleware
    try:
        add_audit_middleware(app, engine)
        logger.info("Audit middleware registered")
    except Exception as e:
        logger.warning(f"Could not add audit middleware: {e}")
    
    # SDK standard routes
    try:
        setup_generic_routes(app)
        setup_observability_routes(app)
        logger.info("SDK standard routes registered")
    except Exception as e:
        logger.warning(f"Could not setup SDK routes: {e}")
    
    # Setup OpenAPI tags
    try:
        setup_standard_openapi_tags(app)
    except Exception as e:
        logger.warning(f"Could not setup OpenAPI tags: {e}")
    
    # Register provider with registry
    try:
        registry.register(provider)
        logger.info(f"Provider registered: {provider.namespace}")
    except Exception as e:
        logger.warning(f"Could not register provider: {e}")
    
    # Register resource types
    try:
        register_resource_types(app, provider)
        logger.info(f"Resource types registered: {provider.get_resource_types()}")
    except Exception as e:
        logger.warning(f"Could not register resource types: {e}")
    
    # Accelerator-specific routes
    spark_nodes_router = setup_spark_nodes_routes(app, engine, provider)
    spark_instances_router = setup_spark_instances_routes(app, engine, provider)
    spark_jobs_router = setup_spark_jobs_routes(app, engine, provider)
    
    app.include_router(spark_nodes_router, prefix="")
    app.include_router(spark_instances_router, prefix="")
    app.include_router(spark_jobs_router, prefix="")
    
    logger.info("Accelerator provider routes registered")
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with provider metadata"""
        return {
            "service": "ITL Accelerator Resource Provider",
            "namespace": provider.namespace,
            "version": provider.version,
            "resource_types": provider.get_resource_types(),
            "docs": "/docs",
        }
    
    return app
