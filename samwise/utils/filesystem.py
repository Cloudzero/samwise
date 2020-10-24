# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import json
import os
import hashlib
from pathlib import Path

from samwise import constants
from samwise.features.template import get_template_code_path
from samwise.utils.tools import hash_string, yaml_dumps


def hash_directory(path_to_check):
    """
    Return sha256 hash of all file times in a given path. Useful for detecting when files in a folder
    have changed.

    Caveat emptor: performance is O(len(files in path))

    Args:
        path_to_check (str): absolute or relative path

    Returns (str): hash of all file times

    """
    hashed_directory = hashlib.sha256(" ".join(
        [str(os.path.getmtime(os.path.join(dp, f))) for dp, dn, fn in os.walk(os.path.expanduser(path_to_check)) for f
         in fn]).encode("utf-8")).hexdigest()

    return hashed_directory


def get_lambda_package_size(output_location):
    output_location_size_bytes = sum(f.stat().st_size for f in Path(output_location).glob('**/*') if f.is_file())
    return output_location_size_bytes / (1024 * 1024)


def check_for_project_changes(stack_name, base_dir, template):
    """

    Args:
        stack_name: str
        base_dir: str
        template:

    Returns:
        Bool: true/false if project has changes
    """
    globals_hash = hash_string(yaml_dumps(template))

    config_file = Path(constants.SAMWISE_CONFIGURATION_FILE).expanduser()
    if config_file.exists():
        config = json.load(config_file.open())
        stack_config = config.get(stack_name) or {}
    else:
        config = {}
        stack_config = {}

    code_path = get_template_code_path(template)
    if code_path:
        requirements_file = os.path.join(base_dir, "requirements.txt")
        req_modified_time = os.path.getmtime(requirements_file)
        abs_code_path = os.path.abspath(os.path.join(base_dir, code_path))
        src_hash = hash_directory(abs_code_path)
        code_changes = (req_modified_time > stack_config.get(requirements_file, 0)) or (src_hash != stack_config.get(abs_code_path))

        stack_config[requirements_file] = req_modified_time
        stack_config[abs_code_path] = src_hash
    else:
        code_changes = False

    changes = bool(code_changes or globals_hash != stack_config.get("globals_hash"))
    stack_config["globals_hash"] = globals_hash
    config[stack_name] = stack_config
    json.dump(config, config_file.open('w'))
    return changes
