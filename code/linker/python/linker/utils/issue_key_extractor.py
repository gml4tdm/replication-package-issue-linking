import enum
import logging
import re


class KeyFinderResult(enum.Enum):
    NoMessage = enum.auto()
    NoMatches = enum.auto()
    ExactMatch = enum.auto()
    MultipleMatches = enum.auto()



class IssueKeyExtractor:

    def __init__(self, pattern: str, *, multiple_key_handling: str = 'first'):
        self._pattern = re.compile(pattern, flags=re.IGNORECASE)
        if multiple_key_handling not in ['first', 'last', 'ignore', 'all']:
            raise ValueError(f'Unknown multiple key handling {multiple_key_handling}')
        self._multiple_key_handling = multiple_key_handling

    def get_key_from_message(self,
                             message: str | None,
                             logger: logging.Logger | None = None) -> tuple[KeyFinderResult, list[str] | None]:

        if message is None:
            return KeyFinderResult.NoMessage, None
        matches = [x.upper() for x in self._pattern.findall(message)]
        unique_matches = set(matches)
        if not matches:
            if logger is not None:
                logger.debug(f'No matches for %s', message)
            return KeyFinderResult.NoMatches, None
        if len(unique_matches) > 1:
            if logger is not None:
                logger.warning(f'Multiple matches (%s) for %s', matches, message)
            match self._multiple_key_handling:
                case 'first':
                    issue_key = matches[0]
                case 'last':
                    issue_key = matches[-1]
                case 'ignore':
                    return KeyFinderResult.MultipleMatches, None
                case 'all':
                    return KeyFinderResult.MultipleMatches, list(unique_matches)
                case _:
                    raise ValueError(f'Unknown multiple key handling '
                                     f'{self._multiple_key_handling}')
            return KeyFinderResult.MultipleMatches, [issue_key]
        else:
            issue_key = matches[0]
            return KeyFinderResult.ExactMatch, [issue_key]
