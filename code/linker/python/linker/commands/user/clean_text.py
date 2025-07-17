import json
import pathlib
import typing

import alive_progress
import tap

from ...utils import text_cleaning
from ..base import BaseCommand, register


class CleanTextConfig(tap.Tap):
    input_directory: pathlib.Path
    output_directory: pathlib.Path
    mode: typing.Literal[
        'raw',
        'remove-formatting',
        'remove-formatting-and-blocks',
        'remove-formatting-and-replace-blocks',
        'remove-formatting-and-replace-blocks-and-replace-names'
    ]
    issue_type: typing.Literal['jira']


@register('clean-text')
class CleanTextCommand(BaseCommand):

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return CleanTextConfig

    def execute(self):
        assert isinstance(self.config, CleanTextConfig)

        match self.config.mode:
            case 'raw':
                mode = text_cleaning.TextCleanupMode.Raw
            case 'remove-formatting':
                mode = text_cleaning.TextCleanupMode.RemoveFormatting
            case 'remove-formatting-and-blocks':
                mode = text_cleaning.TextCleanupMode.RemoveFormattingAndBlocks
            case 'remove-formatting-and-replace-blocks':
                mode = text_cleaning.TextCleanupMode.RemoveFormattingAndReplaceBlocks
            case 'remove-formatting-and-replace-blocks-and-replace-names':
                mode = text_cleaning.TextCleanupMode.RemoveFormattingAndReplaceBlocksAndReplaceNames
            case _:
                raise ValueError(f'Invalid mode: {self.config.mode}')

        match self.config.issue_type:
            case 'jira':
                cleaner = text_cleaning.JiraTextCleaner(mode)
            case _:
                raise ValueError(f'Invalid issue type: {self.config.issue_type}')

        self.config.output_directory.mkdir(parents=True, exist_ok=True)

        for file in self.config.input_directory.iterdir():
            if file.suffix != '.json':
                continue
            with open(file) as f:
                data = json.load(f)
            with alive_progress.alive_bar(len(data)) as bar:
                for issue in data:
                    body = issue['description']
                    issue['description'] = cleaner.clean(body)
                    bar()

            with open(self.config.output_directory / file.name, 'w') as f:
                json.dump(data, f)
