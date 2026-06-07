"""
Accelerator Provider Entry Point

Standalone server for the Accelerator provider that manages GPU/TPU/NPU compute resources.

Uses AcceleratorProviderServer from initialization.server for application lifecycle.

Follows Core provider pattern.
"""

import os
import logging

from .initialization import AcceleratorProviderServer

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the standalone provider"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    host = os.getenv("PROVIDER_HOST", "0.0.0.0")
    port = int(os.getenv("PROVIDER_PORT", "8003"))
    provider_mode = os.getenv("PROVIDER_MODE", "api").lower()
    api_url = os.getenv("CONTROLPLANE_API_URL")
    provider_base_url = os.getenv("PROVIDER_BASE_URL", f"http://localhost:{port}")
    
    logger.info("=" * 80)
    logger.info("ITL Accelerator Provider Configuration")
    logger.info("=" * 80)
    logger.info(f"Mode: {provider_mode.upper()}")
    logger.info(f"Host: {host}:{port}")
    if api_url:
        logger.info(f"API Gateway: {api_url}")
    logger.info("=" * 80)
    
    server = AcceleratorProviderServer()
    server.run(host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
