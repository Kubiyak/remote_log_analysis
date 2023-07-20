from .remote_text_log import RemoteTextLog
import typing
from datetime import datetime
from dateutil import parser as dateparser
import re


class RemoteLogSearch:
    def __init__(self,
                 log: RemoteTextLog,
                 message_regex: typing.Optional[str] = None,
                 start_time: typing.Union[datetime, str, None] = None,
                 end_time: typing.Union[datetime, str, None] = None,
                 log_level_regex: typing.Optional[str] = None):
        '''
        :param log: RemoteTextLog object to search for specified criteria within the specified time range.
        The timestamps in the log must be parseable with dateutil.parser.parse. The entire log file will be
        considered to fit within the time range if there is no timestamp in the log format.
        :param message_regex: Optional regex to match against the message portion of the log line.
        :param start_time: Optional start time for the search. If not specified, the beginning of the log will be used.
        :param end_time: Optional end time for the search. If not specified, the end of the log will be used.
        :param log_level_regex: Lines with a loglevel which don't match this regex are discarded if specified.

        Note: The results will extend slightly beyond the specified time range for efficiency.
        '''
        self._log = log
        self._message_regex = re.compile(message_regex) if message_regex is not None else None
        self._log_level_regex = re.compile(log_level_regex) if log_level_regex is not None else None

        if start_time:
            self._start_time = start_time if isinstance(start_time, datetime) else dateparser.parse(start_time)
        else:
            self._start_time = None

        if end_time:
            self._end_time = end_time if isinstance(end_time, datetime) else dateparser.parse(end_time)
        else:
            self._end_time = None

    def _locate_start(self):
        if self._start_time is None:
            return

        block_size = self._log.block_size
        start_offset = self._log.tell()
        end_offset = self._log.end_offset
        mid = self._log.seek((end_offset + start_offset) // 2)

        while start_offset + block_size < end_offset:
            line = self._log.read_line()
            if line is None:
                raise EOFError

            if not line.timestamp:
                return # Means ignore timestamps

            line_time = dateparser.parse(line.timestamp)
            if line_time > self._start_time:
                end_offset = mid
                mid = self._log.seek((end_offset + start_offset) // 2)

            elif line_time < self._start_time:
                start_offset = mid
                mid = self._log.seek((end_offset + start_offset) // 2)
            else:
                break

        self._log.seek(mid)

    def rewind(self):
        self._log.rewind()

    def seek(self, offset:int):
        return self._log.seek(offset)

    def __iter__(self):
        try:
            self._locate_start()
        except EOFError:
            return

        count = 0

        for line in self._log.read_line_iter():
            count += 1
            if self._end_time and line.timestamp and count % 20 == 0:
                ts = dateparser.parse(line.timestamp)
                if self._end_time < ts:
                    return  # end iteration as end time has been reached

            if self._log_level_regex and not self._log_level_regex.match(line.log_level):
                continue
            if self._message_regex and not self._message_regex.search(line.message, re.MULTILINE):
                continue
            yield line
