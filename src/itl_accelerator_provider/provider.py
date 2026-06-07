"""
Accelerator Provider Implementation

Provides GPU/TPU/NPU compute resources via SparkNodes, SparkOllamaInstances, and SparkJobs.
"""

import logging
from typing import Dict, Any, Optional, List

from itl_controlplane_sdk.providers import ResourceProvider
from itl_controlplane_sdk.persistence import StorageEngine

logger = logging.getLogger(__name__)


class AcceleratorProvider(ResourceProvider):
    """
    Accelerator Resource Provider
    
    Manages GPU/TPU/NPU compute resources following ARM resource model.
    """
    
    def __init__(self, engine: StorageEngine):
        """Initialize provider with storage engine"""
        self.engine = engine
        logger.info("Accelerator provider initialized")
    
    @property
    def namespace(self) -> str:
        """Provider namespace"""
        return "ITL.Accelerator"
    
    @property    
    def version(self) -> str:
        """Provider version"""
        return "2024-01-01"
    
    def get_resource_types(self) -> List[str]:
        """Return supported resource types"""
        return [
            "sparkNodes",
            "sparkOllamaInstances",
            "sparkJobs",
        ]
