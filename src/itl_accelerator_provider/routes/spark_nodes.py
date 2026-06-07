"""
SparkNode routes — hardware management

Follows Core provider pattern with setup function.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import structlog

from ..models.spark_node import SparkNodeRequest, SparkNodeResponse

logger = structlog.get_logger(__name__)


def setup_spark_nodes_routes(app, engine, provider) -> APIRouter:
    """
    Setup SparkNode routes
    
    Args:
        app: FastAPI application
        engine: Storage engine
        provider: Accelerator provider instance
        
    Returns:
        Configured router
    """
    router = APIRouter(tags=["sparkNodes"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_name}",
        response_model=SparkNodeResponse,
        status_code=201,
    )
    async def create_spark_node(
        subscription_id: str,
        resource_group: str,
        node_name: str,
        request: SparkNodeRequest,
    ) -> SparkNodeResponse:
        """Create a new SparkNode (hardware registration)"""
        logger.info(
            "create_spark_node",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_name=node_name,
        )

        # TODO: Implement with storage engine
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_name}"
        
        return SparkNodeResponse(
            id=resource_id,
            name=node_name,
            type="ITL.Accelerator/sparkNodes",
            location=request.location,
            properties=request.properties,
            provisioning_state="Succeeded",
            status="Active",
        )

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes",
        response_model=dict,
    )
    async def list_spark_nodes(
        subscription_id: str,
        resource_group: str,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        """List SparkNodes in a resource group"""
        logger.info(
            "list_spark_nodes",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        # TODO: Implement with storage engine
        return {
            "value": [],
            "nextLink": None,
        }

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_name}",
        response_model=SparkNodeResponse,
    )
    async def get_spark_node(
        subscription_id: str,
        resource_group: str,
        node_name: str,
    ) -> SparkNodeResponse:
        """Get a specific SparkNode"""
        logger.info(
            "get_spark_node",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_name=node_name,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="SparkNode not found")

    @router.put(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_name}",
        response_model=SparkNodeResponse,
    )
    async def update_spark_node(
        subscription_id: str,
        resource_group: str,
        node_name: str,
        request: SparkNodeRequest,
    ) -> SparkNodeResponse:
        """Update a SparkNode"""
        logger.info(
            "update_spark_node",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_name=node_name,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="SparkNode not found")

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_name}",
        status_code=204,
    )
    async def delete_spark_node(
        subscription_id: str,
        resource_group: str,
        node_name: str,
    ) -> None:
        """Delete a SparkNode"""
        logger.info(
            "delete_spark_node",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_name=node_name,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="SparkNode not found")
    
    return router
