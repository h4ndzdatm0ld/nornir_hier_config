# pylint: disable=unspecified-encoding
"""General Helpers."""
import hashlib
import json
import logging
import os.path
from typing import Any, Dict, Optional, IO

import yaml
from deepdiff import DeepDiff


def check_file(file_name: Optional[str]) -> bool:
    """Check file_name exists based on input.

    Args:
        file_name (str): file name to check
    """
    try:
        return os.path.isfile(file_name)  # type: ignore
    except TypeError:
        return False


def create_folder(directory: str) -> None:
    """Create a directory.

    Args:
        directory (str): Directory path to create
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as err_ex:
        logging.info("Error when creating %s, %s", directory, err_ex)


def create_parent_dir(path: str) -> IO[str]:
    """Create any parent directories not present.

    Args:
        path (str): Filename with path

    Returns:
        IO: Text Wrapper
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w", encoding="utf-8")


def write_file(text: str, filename: str) -> None:
    """Take input and write a file.

    Args:
        text (str): text to write
        filename (str): filename
    """
    with create_parent_dir(filename) as file:
        file.write(text)


def get_yaml(file_path: str) -> Any:
    """Safe load a YAML file."""
    with open(file_path, encoding="utf-8") as file:
        return yaml.safe_load(file.read())


def compare_files_state(remediation_config: str, remediation_config_string: str) -> Dict[Any, Any]:
    """Evaluate hashes to determine if an existing file has changed.

    Args:
        remediation_config (str): Remediation Config path
        remediation_config_string (str): Generated Remediation string

    Returns:
        result (TypedDict): True or False depending on if files equal each other and diff.
    """
    result: Dict[str, Any] = {"changed": False, "diff": None}
    md5_original = None
    if check_file(remediation_config):
        with open(remediation_config, "r", encoding="utf-8") as original:
            remediation_config_read = original.read()
        md5_original = hashlib.md5(remediation_config_read.encode("utf-8")).hexdigest()  # nosec
    else:
        remediation_config_read = ""
    write_file(remediation_config_string, remediation_config)

    with open(remediation_config, "r", encoding="utf-8") as updated:
        remediation_config_updated = updated.read()
    md5_new = hashlib.md5(remediation_config_updated.encode("utf-8")).hexdigest()  # nosec
    if md5_new != md5_original:
        deepdiff = DeepDiff(remediation_config_read, remediation_config_string)
        result["diff"] = json.loads(deepdiff.to_json())
        result["changed"] = True

    return result
