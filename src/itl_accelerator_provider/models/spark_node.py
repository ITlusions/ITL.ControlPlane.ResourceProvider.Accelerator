"""
SparkNode models for request/response

Follows Core provider pattern using SDK base classes.
"""

from typing import Any, Dict, Optional
from pydantic import Field, ConfigDict
from itl_controlplane_sdk.api.base.models import GenericResourceBase


class SparkNodeRequest(GenericResourceBase):
    """Request to create/update a SparkNode"""
    
    name: str = Field(..., min_length=1, max_length=260, description="Node name")
    location: str = Field(..., description="Geographic location")
    sku: Dict[str, Any] = Field(..., description="SKU configuration")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    subscription_id: Optional[str] = Field(None, description="Subscription ID")
    resource_group: Optional[str] = Field(None, description="Resource Group")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "dgx-node-01",
                "location": "westeurope",
                "sku": {"name": "DGX-H100-8GPU", "tier": "Standard"},
                "properties": {
                    "gpu_count": 8,
                    "gpu_model": "H100",
                    "total_memory_gb": 640
                },
                "tags": {"environment": "production"}
            }
        }
    )


class SparkNodeResponse(GenericResourceBase):
    """Response for a SparkNode"""
    
    id: str = Field(..., description="ARM-style resource ID")
    name: str = Field(..., description="Node name")
    type: str = Field(default="ITL.Accelerator/sparkNodes", description="Resource type")
    location: str = Field(..., description="Geographic location")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    provisioning_state: str = Field(default="Succeeded", description="Provisioning state")
    status: Optional[str] = Field(None, description="Node operational status")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": "/subscriptions/sub-123/resourceGroups/rg-prod/providers/ITL.Accelerator/sparkNodes/dgx-node-01",
                "name": "dgx-node-01",
                "type": "ITL.Accelerator/sparkNodes",
                "location": "westeurope",
                "properties": {
                    "gpu_count": 8,
                    "gpu_model": "H100",
                    "status": "Active"
                },
                "provisioning_state": "Succeeded",
                "status": "Active"
            }
        }
    )
