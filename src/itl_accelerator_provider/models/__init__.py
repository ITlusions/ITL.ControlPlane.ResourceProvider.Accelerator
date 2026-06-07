"""Models package for Accelerator Provider"""

# Import base class from SDK for reuse
from itl_controlplane_sdk.api.base.models import GenericResourceBase

# Import provider-specific models
from .spark_node import SparkNodeRequest, SparkNodeResponse

__all__ = [
    "GenericResourceBase",
    "SparkNodeRequest",
    "SparkNodeResponse",
]
