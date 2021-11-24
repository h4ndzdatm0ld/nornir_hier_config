"""Hier Config Remediation Nornir Task."""

import logging
from typing import List, Optional, Dict

import yaml
from hier_config import Host
from nornir.core.task import Result, Task

from nornir_hier_config.utilities import check_file, write_file

log = logging.getLogger(__name__)


def remediation(
    task: Task,
    running_config: str,
    generated_config: str,
    remediation_config: str,
    options: Optional[str] = None,  # If options file, read yaml. Else default to "hier_options"
    tags: Optional[str] = None,  # If tags file, read yaml. Else default to "hier_tags"
    exclude_tags: Optional[List[str]] = None,
    include_tags: Optional[List[str]] = None,
) -> Result:
    """Hier Config Remediation Task.

    Args:
        task (Task): Task
        running_config (str): Running Configuration. Path to file or string format.
        generated_config (str): Generated Configuration. Path to file or string format.
        remediation_config (str): Path to where remediation configuration should be placed.
        options (Optional[str], optional): Path to Yaml file. Defaults to None and can be extracted from vars.
        include_tags (Optional[List[str]], optional): [description]. Defaults to None. # TODO: vars?

    Returns:
        Result
    """
    failed = False
    result: Dict[str, str] = {}

    if check_file(options):
        with open(options, encoding="utf-8") as hier_options:  # type: ignore
            options = yaml.safe_load(hier_options.read())
    else:
        options = task.host.extended_data().get("hier_options")

    if check_file(tags):
        with open(tags, encoding="utf-8") as hier_tags:  # type: ignore
            tags = yaml.safe_load(hier_tags.read())
    else:
        tags = task.host.extended_data().get("hier_tags")

    # Create a Host object with our option
    host = Host(task.host, task.host.platform, options)

    # Load Running and Generated config
    if check_file(running_config):
        host.load_running_config_from_file(file=running_config)
    else:
        host.load_running_config(config_text=running_config)
    if check_file(generated_config):
        host.load_generated_config_from_file(file=generated_config)
    else:
        host.load_generated_config(config_text=generated_config)
    # Load tags
    if tags:
        host.load_tags(tags)

    host.remediation_config()
    remediation_obj = host.remediation_config_filtered_text(include_tags=include_tags, exclude_tags=exclude_tags)
    # remediation_config_string = "".join([line for line in remediation_obj])
    remediation_config_string = "".join(list(remediation_obj))

    write_file(text=remediation_config_string, filename=remediation_config)
    return Result(host=task.host, failed=failed, result=result)
