import os
import hashlib


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
