# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and
# limitations under the License.
import json
import logging
import os

from packaging import version

from common.aws.aws_api import AWSApi
from pcluster.cli_commands.compute_fleet_status_manager import ComputeFleetStatus
from pcluster.models.cluster import Cluster, ClusterActionError, ClusterStack
from pcluster.utils import get_installed_version

LOGGER = logging.getLogger(__name__)


class ApiFailure:
    """Represent a generic api error."""

    def __init__(self, message: str = None, validation_failures: list = None):
        self.message = message or "Something went wrong."
        self.validation_failures = validation_failures or []


class ClusterInfo:
    """
    Minimal representation of a running cluster.

    All the information are retrieved from the stack.
    """

    def __init__(self, stack: ClusterStack):
        # Cluster info
        self.name = stack.cluster_name
        self.status = stack.status  # FIXME
        # Stack info
        self.stack_arn = stack.id
        self.stack_name = stack.name
        self.stack_status = stack.status
        self.region = stack.region
        self.version = stack.version

    def __repr__(self):
        return json.dumps(self.__dict__)


class FullClusterInfo(ClusterInfo):
    """Full representation of a running cluster."""

    def __init__(self, cluster: Cluster):
        super().__init__(cluster.stack)
        # Cluster info
        self.head_node = cluster.head_node_instance
        self.head_node_ip = cluster.head_node_ip
        self.user = cluster.head_node_user
        self.compute_instances = cluster.compute_instances
        # Config info
        self.scheduler = cluster.config.scheduling.scheduler
        # Stack info
        self.stack_outputs = cluster.stack.outputs


class PclusterApi:
    """Proxy class for all Pcluster API commands used in the CLI."""

    def __init__(self):
        pass

    @staticmethod
    def create_cluster(cluster_config: dict, cluster_name: str, region: str, disable_rollback: bool = False):
        """
        Load cluster model from cluster_config and create stack.

        :param cluster_config: cluster configuration (yaml dict)
        :param cluster_name: the name to assign to the cluster
        :param region: AWS region
        :param disable_rollback: Disable rollback in case of failures
        """
        try:
            # Generate model from config dict and validate
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region
            cluster = Cluster(cluster_name, cluster_config)
            cluster.create(disable_rollback)
            return FullClusterInfo(cluster)
        except ClusterActionError as e:
            return ApiFailure(str(e), e.validation_failures)
        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def delete_cluster(cluster_name: str, region: str, keep_logs: bool = True):
        """Delete cluster."""
        try:
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region
            # retrieve cluster config and generate model
            cluster = Cluster(cluster_name)
            PclusterApi._check_version_2(cluster)
            cluster.delete(keep_logs)
            return FullClusterInfo(cluster)
        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def describe_cluster(cluster_name: str, region: str):
        """Get cluster information."""
        try:
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region

            cluster = Cluster(cluster_name)
            PclusterApi._check_version_2(cluster)
            return FullClusterInfo(cluster)
        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def update_cluster(cluster_name: str, region: str):
        """Update existing cluster."""
        try:
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region
            # Check if stack version matches with running version.
            cluster = Cluster(cluster_name)

            installed_version = get_installed_version()
            if cluster.stack.version != installed_version:
                raise ClusterActionError(
                    "The cluster was created with a different version of "
                    f"ParallelCluster: {cluster.stack.version}. Installed version is {installed_version}. "
                    "This operation may only be performed using the same ParallelCluster "
                    "version used to create the cluster."
                )
            return FullClusterInfo(cluster)
        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def list_clusters(region: str):
        """List existing clusters."""
        try:
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region

            stacks = AWSApi.instance().cfn.list_pcluster_stacks()
            return [ClusterInfo(ClusterStack(stack)) for stack in stacks]

        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def update_compute_fleet_status(cluster_name: str, region: str, status: ComputeFleetStatus):
        """Update existing compute fleet status."""
        try:
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region

            cluster = Cluster(cluster_name)
            PclusterApi._check_version_2(cluster)
            if status == ComputeFleetStatus.START_REQUESTED:
                cluster.start()
            elif status == ComputeFleetStatus.STOP_REQUESTED:
                cluster.stop()
            else:
                return ApiFailure(f"Unable to update the compute fleet to status {status}. Not supported.")

        except Exception as e:
            return ApiFailure(str(e))

    @staticmethod
    def _check_version_2(cluster):
        if version.parse(cluster.stack.version) < version.parse("3.0.0"):
            raise ClusterActionError(
                f"The cluster {cluster.name} was created with ParallelCluster {cluster.stack.version}. "
                "This operation may only be performed using the same version used to create the cluster."
            )