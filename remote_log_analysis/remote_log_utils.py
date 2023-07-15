import re
from dataclasses import dataclass
import typing
import copy
import abc


def timestamp_format_to_regex(strftime_notation):
    '''
    :param strftime_notation: A string using strtime notation describing a timestamp format
    :return: A regex which can match the timestamp format
    '''
    special_chars = {
        'Y': r'\d{4}',
        'm': r'\d{2}',
        'd': r'\d{2}',
        'H': r'\d{2}',
        'I': r'\d{2}',
        'M': r'\d{2}',
        'S': r'\d{2}',
        'f': r'\d+',
        'z': r'[+-]\d{4}',
        'Z': r'\w+',
        'a': r'\w{3}',
        'A': r'\w+',
        'b': r'\w{3}',
        'B': r'\w+',
        'c': r'.+',
        'x': r'\d{2}/\d{2}/\d{2}',
        'X': r'\d{2}:\d{2}:\d{2}',
        'p': r'(?:AM|PM)',
        's': r'\d+',
        'w': r'\d',
        'j': r'\d{3}',
        'U': r'\d{2}',
        'W': r'\d{2}',
        'g': r'\d{2}',
        'G': r'\d{4}',
        'V': r'\d{2}',
    }

    chars_to_escape = {'{', '}', '[', ']', '(', ')', '|', '*', '+', '?', '.', '\\', '^', '$'}
    escaped_chars = [re.escape(t) if t in chars_to_escape else t for t in strftime_notation]
    strftime_notation = ''.join(escaped_chars)
    pattern = re.compile(r"(%)(.)")

    def replace_special(match):
        if match.group(1) == '%':
            char = match.group(2)
            if char in special_chars:
                return special_chars[char]
            else:
                return (f'%{char}')
        else:
            raise RuntimeError('Unexpected match while processing timestamp format')

    return pattern.sub(replace_special, strftime_notation)


@dataclass(frozen=True)
class LogLineData:
    timestamp: str
    log_level: str
    source: str
    message: str


class LogLineFormatInterface(metaclass=abc.ABCMeta):
    '''
    Interface for a log line format. The only required method is match which returns
    details about the matched line in a LogLineData object if a match occurs. Text log traversal implementations can
    use this interface to extract details about log lines in a variety of formats.
    '''
    @abc.abstractmethod
    def match(self, line: str) -> typing.Optional[LogLineData]:
        '''
        :param line: A line to match
        :return: A LogLineData object if the line matches the format, None otherwise
        '''
        raise NotImplementedError


class CommonRegexLineFormat(LogLineFormatInterface):
    '''
    Describes the format of a log line. A logline is described with the following tokens:
        %t - Timestamp
        %l - Log level
        %s - Source
        %m - Log message
    Other characters are treated as literals.
    The timestamp is further specified in strftime format in timestamp_format.
    The log levels are specified in log_levels in order of increasing severity.

    This class will work well for most common log line formats but certainly will not work well for all log line
    formats.
    In particular, it will not work well for log lines which do not contain a timestamp or log level or in which
    the message text is interspersed with the timestamp, loglevel, or source.

    In such cases, just define a custom LogLineFormatInterface and implement as required for the specific log format.
    '''

    def __init__(self, logline_format: str, timestamp_format: str, log_levels: typing.Iterable[str]):
        '''
        :param logline_format: Specifies the log line format with the tokens described above:
        %t - Timestamp
        %l - Log level
        %s - Source
        %m - Log message
        Other characters are treated as literals.
        :param timestamp_format: The timestamp format in strftime notation
        :param log_levels: A list of log levels in order of increasing severity. These are the acceptable values for %l
        '''
        # escape any special sequences in logline_format before proceeding
        chars_to_escape = {'{', '}', '[', ']', '(', ')', '|', '*', '+', '?', '.', '\\', '^', '$'}
        escaped_chars = [re.escape(t) if t in chars_to_escape else t for t in logline_format]
        logline_format = ''.join(escaped_chars)

        self._logline_format = logline_format
        self._timestamp_format = timestamp_format
        self._log_levels = copy.copy(log_levels)
        self._regex = self._generate_regex(logline_format, timestamp_format, log_levels)

    @property
    def regex(self):
        return self._regex

    @property
    def timestamp_format(self):
        return self._timestamp_format

    @property
    def log_levels(self):
        return self._log_levels

    def match(self, line: str) -> typing.Optional[LogLineData]:
        '''
        :param line: A line from a log file
        :return: A LogLineData object if the line matches the format, otherwise None
        '''
        match_result = self._regex.search(line)
        if not match_result:
            return None

        # source info is not always present.
        match_groups = match_result.groupdict()

        return LogLineData(timestamp=match_groups.get('t', ''),
                           log_level=match_groups.get('l', ''),
                           source=match_groups.get('s', ''),
                           message=match_groups.get('m', ''))

    def _generate_regex(self, logline_format, timestamp_format, log_levels):
        format_chars = {
            't': timestamp_format_to_regex(timestamp_format),
            'l': '(?:' + '|'.join(log_levels) + ')',
            's': r'[^\s]+',
            'm': r'.*',
        }

        def replace_format_char(match):
            token = match.group(1)
            if token in format_chars:
                return f'(?P<{token}>{format_chars[token]})'
            else:
                return token

        regex = re.compile(re.sub(r'%([tlsm])',
                                  lambda x: f'(?P<{x.group(1)}>{format_chars[x.group(1)]})',
                                  logline_format))

        return regex
