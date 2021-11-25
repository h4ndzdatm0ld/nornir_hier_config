# pylint: disable=too-many-locals
"""Hier Config Remediation Nornir Task."""

import logging
from typing import Any, Dict, List, Optional

from hier_config import Host
from nornir.core.task import Result, Task

from nornir_hier_config.utilities import (
    check_file,
    compare_files_state,
    get_yaml,
    write_file,
)

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
        options (Optional[str], optional): Path to Yaml file. Defaults to None but must be supplied as vars.
        exclude_tags (Optional[List[str]], optional): Exclude tags. Defaults to None but can be supplied as vars.
        include_tags (Optional[List[str]], optional): Include tags. Defaults to None but can be supplied as vars.

    Returns:
        Result

    Example:
        ```
        nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/remediation_config.txt",
        )
        ```

        If no YAML file with Options and Tags, you must specify them in Group Vars. The following keys are accessed
        to retrieve the corresponding data:

        - `hier_options` - Hier Config Options for device platform
        - `hier_tags` - Hier Config Tags for device platform
        - `hier_include_tags` - Hier Config Include Tags for remediation output
        - `hier_exclude_tags` - Hier Config Exclude Tags for remediation output

        This is what group vars should look like. This pattern applies for the above
        keys.

        ```
        ---
        iosxr:
        username: "some_user"
        password: "some_password"
        port: 830
        platform: "iosxr"
        data:
            hier_options:  <--- All keys of interest fall under `data`.
            style: "iosxr"
        ```
    """
    failed: bool = False
    changed: bool = False
    diff: str = ""
    result: Dict[Any, Any] = {}

    # Required args:
    required = (running_config, generated_config, remediation_config)

    if all(required):
        # Get Tags and Options
        # Get data inherited from group vars
        ext_data = task.host.extended_data()

        opts = get_yaml(options) if check_file(options) else ext_data.get("hier_options")  # type: ignore
        tags = get_yaml(tags) if check_file(tags) else ext_data.get("hier_tags")  # type: ignore

        # Create a Host object with our option
        host = Host(task.host.name, task.host.platform, opts)

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

        # Get Include or Exclude Tags
        inc = get_yaml(include_tags) if check_file(include_tags) else ext_data.get("hier_include_tags")  # type: ignore
        exc = get_yaml(exclude_tags) if check_file(exclude_tags) else ext_data.get("hier_exclude_tags")  # type: ignore

        remediation_obj = host.remediation_config_filtered_text(include_tags=inc, exclude_tags=exc)
        # remediation_config_string = "".join([line for line in remediation_obj])
        remediation_config_string = "".join(list(remediation_obj))

        file_state = compare_files_state(remediation_config, remediation_config_string)
        changed = file_state["changed"]

        # Deepdiff is performed if files hash have changed only.
        diff = file_state["diff"]

        write_file(text=remediation_config_string, filename=remediation_config)
    else:
        failed = True
        result["msg"] = f"Missing a required arg from the following: {required}"

    return Result(host=task.host, failed=failed, diff=diff, changed=changed, result=result)
