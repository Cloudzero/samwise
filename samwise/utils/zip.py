import os
from os.path import basename


def zipdir(path, ziph):
    """
    Zip a folder

    Args:
        path (str): path to zip
        ziph: zipfile handle

    Returns:

    """
    for root, dirs, files in os.walk(path):
        for file in files:
            rel_path_file = os.path.join(root[len(path)+1:], file)
            ziph.write(os.path.join(root, file), arcname=rel_path_file)

    return True
