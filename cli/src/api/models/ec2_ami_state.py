# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at http://aws.amazon.com/apache2.0/
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=R0801


from api import util
from api.models.base_model_ import Model


class Ec2AmiState(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    INVALID = "INVALID"
    DEREGISTERED = "DEREGISTERED"
    TRANSIENT = "TRANSIENT"
    FAILED = "FAILED"
    ERROR = "ERROR"

    def __init__(self):
        """Ec2AmiState - a model defined in OpenAPI"""
        self.openapi_types = {}

        self.attribute_map = {}

    @classmethod
    def from_dict(cls, dikt) -> "Ec2AmiState":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Ec2AmiState of this Ec2AmiState.
        :rtype: Ec2AmiState
        """
        return util.deserialize_model(dikt, cls)