"""Hier Config Remediation Nornir Task."""

import logging
from typing import List

from hier_config import Host
from nornir.core.task import Result, Task

log = logging.getLogger(__name__)


def remediation(
    task: Task,
    running_config: str,
    generated_config: str,
    remediation_config: str,
    options: str,
    exclude_tags: List,
    include_tags: List,
):
    """Configuration Remediation Task."""
    hostname = task.host
    failed = False
    result = {}

    host = Host(task.host, task.host.operating_system, options)

    return Result(host=task.host, failed=failed, result=result)
