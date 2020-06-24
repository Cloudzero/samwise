# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import json
import os
import hashlib
from pathlib import Path

from samwise import constants
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


def check_for_code_changes(base_dir, template_globals):
    """

    Args:
        base_dir:
        template_globals:

    Returns:
        Bool: true/false if code has changes
    """
    code_path = template_globals['Function']['CodeUri']
    config_file = Path(constants.SAMWISE_CONFIGURATION_FILE).expanduser()
    if config_file.exists():
        config = json.load(config_file.open())
    else:
        config = {}
    requirements_file = os.path.join(base_dir, "requirements.txt")
    req_modified_time = os.path.getmtime(requirements_file)

    abs_code_path = os.path.abspath(os.path.join(base_dir, code_path))
    src_hash = hash_directory(abs_code_path)

    globals_hash = hash_string(yaml_dumps(template_globals))

    changes = bool(req_modified_time > config.get(requirements_file, 0) or
                   (src_hash != config.get(abs_code_path)) or
                   globals_hash != config.get(f"{code_path}|globals_hash"))

    config[requirements_file] = req_modified_time
    config[abs_code_path] = src_hash
    config[f"{code_path}|globals_hash"] = globals_hash
    json.dump(config, config_file.open('w'))
    return changes