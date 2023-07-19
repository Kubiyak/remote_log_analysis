import os.path
import re

from remote_log_analysis import (UnixLogLineSplitter, LineSplitter, DosLineSplitter, RemoteLinuxExecutor,
                                 CommonRegexLineFormat, CommonNonRegexLineFormat, RemoteLinuxLog)
from remote_log_analysis import RemoteFileBase

import pytest


@pytest.fixture
def unix_line_splitter():
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_log_file.log'
    file_base = RemoteFileBase(log_file, executor, text_mode=True, block_size=4096)
    line_regex = CommonNonRegexLineFormat("%t [%l] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    yield UnixLogLineSplitter(file_base, line_regex)


@pytest.fixture
def dos_line_splitter():
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_crlf.log'
    file_base = RemoteFileBase(log_file, executor, text_mode=True, block_size=4096)
    line_regex = CommonRegexLineFormat(r"%t \[%l\] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    yield DosLineSplitter(file_base, line_regex)


@pytest.fixture
def line_splitter_lf():
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_log_file.log'
    file_base = RemoteFileBase(log_file, executor, text_mode=True, block_size=4096)
    line_regex = CommonRegexLineFormat(r"%t \[%l\] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    yield LineSplitter(file_base, line_regex)


@pytest.fixture
def line_splitter_crlf():
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_crlf.log'
    file_base = RemoteFileBase(log_file, executor, text_mode=True, block_size=4096)
    line_regex = CommonNonRegexLineFormat("%t [%l] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    yield LineSplitter(file_base, line_regex)


@pytest.mark.parametrize("line_splitter", ["unix_line_splitter", "dos_line_splitter",
                                           "line_splitter_lf", "line_splitter_crlf"])
def test_log_line_splitter(ssh_localhost, line_splitter, request):
    splitter = request.getfixturevalue(line_splitter)

    count = 0
    ts_regex = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+')

    for line in splitter:
        count += 1
        assert ts_regex.match(line.timestamp)
        assert line.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    assert count == 50


def test_remote_linux_log(ssh_localhost):
    executor = RemoteLinuxExecutor('localhost')
    log_file = os.path.dirname(__file__) + '/data/sample_log_file.log'
    log_format = CommonNonRegexLineFormat("%t [%l] %m", "%Y-%m-%d %H:%M:%S.%f", ["DEBUG", "INFO", "WARNING", "ERROR"])
    log = RemoteLinuxLog(log_file, executor, log_format)

    count = 0

    for chunk in log.read_chunk_iter():
        count += 1
        assert len(chunk.data) > 0

    assert count == 2

    log.rewind()
    for i in range(2):
        log.read_chunk()

    assert log.read_chunk() == None

    count = 0
    log.seek(0)
    for line in log.read_line_iter():
        count += 1

    assert count == 50
