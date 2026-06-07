"""
Accelerator Provider Server Configuration

Standalone server for the Accelerator provider with:
- SQLAlchemy async storage engine
- Audit system integration
- API mode, ServiceBus mode, and Hybrid mode support
- API Gateway registration capability

Follows Core provider pattern.
"""

import os
import logging
import uvicorn
from typing import Optional

from fastapi import FastAPI

from itl_controlplane_sdk.api import BaseProviderServer
from itl_controlplane_sdk.persistence import SQLAlchemyStorageEngine
from itl_controlplane_sdk.providers import ResourceProviderRegistry

from ..accelerator import AcceleratorProvider
from .app_factory import create_app

logger = logging.getLogger(__name__)


class AcceleratorProviderServer(BaseProviderServer):
    """
    Standalone server for Accelerator provider — SDK-based architecture
    
    Inherits common lifecycle management from BaseProviderServer:
    - Configuration validation
    - Audit system initialization
    - Graceful shutdown handling
    - API Gateway registration
    """
    
    def __init__(self):
        """Initialize server with storage engine and provider"""
        self.engine = SQLAlchemyStorageEngine()
        self.provider = AcceleratorProvider(engine=self.engine)
        self.registry = ResourceProviderRegistry()
        self.app = None
        self.audit_publisher = None
        self.event_handler = None
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application with Accelerator provider resources"""
        return create_app(self, self.engine, self.provider, self.registry)
    
    def run(self, host: str = "0.0.0.0", port: int = 8003, **kwargs):
        """
        Run the provider in the configured mode.
        
        Mode is determined by PROVIDER_MODE environment variable:
        - "api" (default): Run HTTP API FastAPI server
        - "servicebus": Run as RabbitMQ message consumer
        - "hybrid": Run both API and message consumer
        """
        provider_mode = os.getenv("PROVIDER_MODE", "api").lower()
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        
        # Validate and log configuration
        self._validate_and_log_config(host, port, provider_mode)
        
        if provider_mode == "api":
            self._run_api_mode(host, port, **kwargs)
        elif provider_mode == "servicebus":
            self._run_servicebus_mode(rabbitmq_url)
        elif provider_mode == "hybrid":
            self._run_hybrid_mode(host, port, rabbitmq_url, **kwargs)
        else:
            raise ValueError(f"Invalid PROVIDER_MODE: {provider_mode}")
    
    def _validate_and_log_config(self, host: str, port: int, mode: str):
        """Validate configuration and log startup info"""
        logger.info("=" * 80)
        logger.info("ITL Accelerator Provider Configuration")
        logger.info("=" * 80)
        logger.info(f"Mode: {mode.upper()}")
        logger.info(f"Host: {host}:{port}")
        logger.info(f"Provider: {self.provider.namespace} v{self.provider.version}")
        logger.info(f"Resource Types: {', '.join(self.provider.get_resource_types())}")
        
        api_url = os.getenv("CONTROLPLANE_API_URL")
        if api_url:
            logger.info(f"API Gateway: {api_url}")
        
        logger.info("=" * 80)
    
    def _run_api_mode(self, host: str, port: int, **kwargs):
        """Run as HTTP API server"""
        logger.info("Starting Accelerator provider in API mode")
        self.app = self.create_app()
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=kwargs.get("log_level", "info"),
        )
    
    def _run_servicebus_mode(self, rabbitmq_url: str):
        """Run as ServiceBus message consumer"""
        logger.info("Starting Accelerator provider in ServiceBus mode")
        logger.warning("ServiceBus mode not yet implemented for Accelerator provider")
        # TODO: Implement message consumer
    
    def _run_hybrid_mode(self, host: str, port: int, rabbitmq_url: str, **kwargs):
        """Run both API server and ServiceBus consumer"""
        logger.info("Starting Accelerator provider in Hybrid mode")
        logger.warning("Hybrid mode not yet implemented for Accelerator provider")
        # TODO: Implement hybrid mode
