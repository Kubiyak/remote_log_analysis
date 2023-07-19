from remote_log_analysis import (RemoteLogSearch, RemoteTextLog, RemoteFileBase, RemotePathInfo, RemotePathType,
                                 CommonNonRegexLineFormat, UnixLogLineSplitter)
from .remote_executor_for_test import RemoteExecutorForTest
import pytest
import datetime
import io


@pytest.fixture
def test_text_log():
    log_start = datetime.datetime.now() - datetime.timedelta(seconds=3600)
    lines = []
    for i in range(1, 3601):
        ts = log_start + datetime.timedelta(seconds=i)
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S.%f")
        if i % 3 == 0 and i % 5 == 0:
            level = "ERROR"
        elif i % 3 == 0:
            level = "WARNING"
        elif i % 5 == 0:
            level = "TRACE"
        else:
            level = "INFO"

        lines.append(f"{ts_str} [{level}] This is logging on line {i}")

    file_text = "\n".join(lines)

    executor = RemoteExecutorForTest(text_stream=io.StringIO(file_text),
                                     file_stat=RemotePathInfo("/foo/bar", mtime=0, atime=0, size=len(file_text),
                                                              type=RemotePathType.FILE))

    file_base = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, text_mode=True)
    log_format = CommonNonRegexLineFormat("%t [%l] %m", timestamp_format="%Y-%m-%d %H:%M:%S.%f",
                                          log_levels=["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"])
    log = RemoteTextLog(file_base, UnixLogLineSplitter(file_base, log_format))
    yield file_text, file_base, log


def test_search(test_text_log):
    field_text, file_base, log = test_text_log
    searcher = RemoteLogSearch(log, log_level_regex="ERROR")
    error_count = 0
    for line in searcher:
        assert line.log_level == "ERROR"
        error_count += 1

    assert error_count == 240

    log.rewind()
    searcher = RemoteLogSearch(log, log_level_regex="TRACE|WARNING")
    count = 0
    for line in searcher:
        assert line.log_level in ("TRACE", "WARNING")
        count += 1

    assert count == 1440


def test_search_with_start(test_text_log):
    field_text, file_base, log = test_text_log
    lines = field_text.split('\n')
    mid = ' '.join(lines[len(lines) // 2].split(' ')[:2])
    mid_ts = datetime.datetime.strptime(mid, "%Y-%m-%d %H:%M:%S.%f")

    searcher = RemoteLogSearch(log, log_level_regex="ERROR", start_time=mid_ts)
    error_count = 0
    for line in searcher:
        assert line.log_level == "ERROR"
        error_count += 1

    assert 120 <= error_count <= 125


def test_search_with_end(test_text_log):
    field_text, file_base, log = test_text_log
    lines = field_text.split('\n')
    mid = ' '.join(lines[len(lines) // 2].split(' ')[:2])
    mid_ts = datetime.datetime.strptime(mid, "%Y-%m-%d %H:%M:%S.%f")

    searcher = RemoteLogSearch(log, log_level_regex="ERROR", end_time=mid_ts)
    error_count = 0
    line = None
    for line in searcher:
        assert line.log_level == "ERROR"
        error_count += 1

    assert 120 <= error_count <= 125
    end_ts = datetime.datetime.strptime(line.timestamp, "%Y-%m-%d %H:%M:%S.%f")
    assert mid_ts + datetime.timedelta(seconds=30) >= end_ts


def test_start_before_first_available(test_text_log):
    field_text, file_base, log = test_text_log
    lines = field_text.split('\n')
    start = ' '.join(lines[0].split(' ')[:2])
    start_ts = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")

    searcher = RemoteLogSearch(log, start_time=start_ts - datetime.timedelta(minutes=30))
    count = 0

    for line in searcher:
        count += 1

    assert count == len(lines)