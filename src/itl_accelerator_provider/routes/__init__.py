"""Routes package for Accelerator Provider"""

from .spark_nodes import setup_spark_nodes_routes
from .spark_instances import setup_spark_instances_routes
from .spark_jobs import setup_spark_jobs_routes

__all__ = [
    "setup_spark_nodes_routes",
    "setup_spark_instances_routes",
    "setup_spark_jobs_routes",
]
