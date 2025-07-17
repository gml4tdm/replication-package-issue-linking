import abc
import importlib
import os
import pathlib

import tap

from ..utils import logs


class BaseCommand(abc.ABC):

    def __init__(self, config: tap.Tap):
        self.config = config
        self.logger = logs.get_logger(self.__class__.__name__)

    @staticmethod
    @abc.abstractmethod
    def config_type() -> type[tap.Tap]:
        pass

    @abc.abstractmethod
    def execute(self):
        pass



_registered_commands = {}

def register(name: str):
    def decorator(cls: type[BaseCommand]):
        _registered_commands[name] = cls
        return cls
    return decorator


def get_command(name: str) -> type[BaseCommand]:
    return _registered_commands[name]


def get_command_names() -> list[str]:
    return list(_registered_commands)


def try_find_command(name: str):
    expected_name = name.replace('-', '_') + '.py'
    path = pathlib.Path(__file__).parent / 'user' / expected_name
    if not path.exists():
        return False
    qualified_name = f'{__package__}.user.{expected_name.removesuffix(".py")}'
    importlib.import_module(qualified_name)
    return True


def register_all_commands():
    global _initialised
    if _initialised:
        return False
    _initialised = True
    _import_user_commands()
    return True


_initialised = False


def _import_user_commands():
    path = pathlib.Path(__file__).parent / 'user'
    for filename in os.listdir(path):
        if not filename.endswith('.py'):
            continue
        module_name = filename.removesuffix('.py')
        qualified_name = f'{__package__}.user.{module_name}'
        importlib.import_module(qualified_name)
