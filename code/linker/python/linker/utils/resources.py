import os
import pathlib

_RESOURCE_DIR = pathlib.Path(__file__).parent.parent.parent / 'resources'


def resolve_resource_path(resource_name: os.PathLike | str) -> pathlib.Path:
    return _RESOURCE_DIR / resource_name
