from remote_log_analysis import CommonRegexLineFormat, LogLineData


def test_match_format_with_source():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_match_format_without_source():
    logline_format = "[%l] %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45",
        log_level="INFO",
        source="",
        message="This is a log message"
    )
    assert result == expected_result


def test_no_match():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15 14:30:45 - This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)
    result = log_line_format.match(log_line)
    assert result is None


def test_match_format_with_invalid_level():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INVALID_LEVEL] MyApp - 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_match_format_with_custom_source():
    logline_format = "[%l] [%s] %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] [MySource] 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45",
        log_level="INFO",
        source="MySource",
        message="This is a log message"
    )
    assert result == expected_result


def test_match_format_with_microseconds():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15 14:30:45.123456: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45.123456",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_match_format_with_different_formats():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%d/%m/%Y %I:%M:%S %p"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 15/07/2023 02:30:45 PM: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="15/07/2023 02:30:45 PM",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_no_match_empty_line():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = ""
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_no_match_invalid_line():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "Invalid log line format"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_match_format_with_brackets_and_parens():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "[(Date)%Y-%m-%d (Time)%H:%M:%S]"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - [(Date)2023-07-15 (Time)14:30:45]: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="[(Date)2023-07-15 (Time)14:30:45]",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_iso_8601_timestamp_format():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15T14:30:45.123456Z: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15T14:30:45.123456Z",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_rfc_3339_timestamp_format():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15T14:30:45.123456Z: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15T14:30:45.123456Z",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_unix_timestamp_format():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%s"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 1678997445: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="1678997445",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_syslog_timestamp_format():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%b %d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - Jul 15 14:30:45: This is a log message"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="Jul 15 14:30:45",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_iis_log_format():
    logline_format = "%t %s %m"
    timestamp_format = "[%Y-%m-%d %H:%M:%S]"
    log_line = "[2023-07-15 14:30:45] MySite 192.168.0.1 GET /index.html - 80 - 192.168.0.1 Mozilla/5.0 - 200 0 0 300"
    log_line_format = CommonRegexLineFormat(logline_format, timestamp_format, [])

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="[2023-07-15 14:30:45]",
        log_level="",
        source="MySite",
        message="192.168.0.1 GET /index.html - 80 - 192.168.0.1 Mozilla/5.0 - 200 0 0 300"
    )
    assert result == expected_result

