import asyncio
import sys
import traceback

from .utils import logs
from . import commands


def main():
    # First, handle platform compatability
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) < 2 or not commands.try_find_command(sys.argv[1]):
        commands.register_all_commands()
        print('Usage: python -m runner <command>')
        print()
        print('Available commands:')
        for command_name in commands.get_command_names():
            print(f'  {command_name}')
        return
    logger = logs.setup_logging()
    command_name = sys.argv[1]
    command_factory = commands.get_command(command_name)
    config = command_factory.config_type()(underscores_to_dashes=True).parse_args(sys.argv[2:])
    command = command_factory(config)
    try:
        command.execute()
    except Exception as e:
        logger.critical('An error occurred. Full traceback: ')
        for block in traceback.format_exception(e):
            for line in block.splitlines():
                logger.critical(line.rstrip())



if __name__ == '__main__':
    main()
