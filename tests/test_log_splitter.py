import os.path
import re

from remote_log_analysis import UnixLogLineSplitter, CommonRegexLineFormat, RemoteLinuxExecutor, RemoteFileBase
import pytest


def test_log_line_splitter(ssh_localhost):
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_log_file.log'
    file_base = RemoteFileBase(log_file, executor, text_mode=True, block_size=4096)
    line_regex = CommonRegexLineFormat("%t [%l] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    splitter = UnixLogLineSplitter(file_base, line_regex)

    count = 0
    ts_regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+')

    for line in splitter:
        count += 1
        assert ts_regex.match(line.timestamp)
        assert line.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    assert count == 50
