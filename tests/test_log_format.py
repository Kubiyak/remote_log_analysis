from remote_log_analysis import CommonRegexLineFormat, CommonNonRegexLineFormat, LogLineData


def test_match_format_with_source():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_match_format_without_source():
    logline_format = r"\[%l\] %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = r"[INFO] 2023-07-15 14:30:45: This is a log message"
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
    log_line = r"\[INFO\] MyApp - 2023-07-15 14:30:45 - This is a log message"
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)
    result = log_line_format.match(log_line)
    assert result is None


def test_match_format_with_invalid_level():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INVALID_LEVEL] MyApp - 2023-07-15 14:30:45: This is a log message"
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_match_format_with_custom_source():
    logline_format = r"\[%l\] \[%s\] %t: %m"
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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="2023-07-15 14:30:45.123456",
        log_level="INFO",
        source="MyApp",
        message="This is a log message"
    )
    assert result == expected_result


def test_match_format_with_different_formats():
    logline_format = r"\[%l\] %s - %t: %m"
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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_no_match_invalid_line():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "Invalid log line format"
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

    result = log_line_format.match(log_line)

    assert result is None


def test_match_format_with_brackets_and_parens():
    logline_format = "[%l] %s - %t: %m"
    timestamp_format = "[(Date)%Y-%m-%d (Time)%H:%M:%S]"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line = "[INFO] MyApp - [(Date)2023-07-15 (Time)14:30:45]: This is a log message"
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, log_levels)

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
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, [])

    result = log_line_format.match(log_line)

    expected_result = LogLineData(
        timestamp="[2023-07-15 14:30:45]",
        log_level="",
        source="MySite",
        message="192.168.0.1 GET /index.html - 80 - 192.168.0.1 Mozilla/5.0 - 200 0 0 300"
    )
    assert result == expected_result


def test_gnu_radius_format():
    # A mult-line log format w/ just a timestamp at top level. Ensure the multi-line format does not interfere
    # w/ the timestamp match
    logline_format= "%t"
    timestamp_format = "%a %b %d %H:%M:%S %Y"
    log_line =     \
    '''
    Wed Sep 01 15:30:45 2021
      User-Name = "john_doe"
      NAS-IP-Address = 192.168.1.100
      NAS-Port-Id = 5
      Called-Station-Id = "00-11-22-33-44-55"
      Service-Type = Login-User
      Acct-Authentic = Local
      Timestamp = 1630521045
      Request-Authenticator = Verified
    '''
    log_line_format = CommonNonRegexLineFormat(logline_format, timestamp_format, [])
    result = log_line_format.match(log_line)
    assert result.timestamp == "Wed Sep 01 15:30:45 2021"


def test_regex_format():
    # Some log formats have variable spacing between fields. This is a test to ensure that the regex
    # format can handle this
    logline_format = r"%t %l\s*:%m"
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    log_levels = ['INFO', 'WARNING', 'ERROR']
    log_line_info =    "2023-07-15 14:30:45 INFO    :This is a INFO log message"
    log_line_warning = "2023-07-15 14:30:45 WARNING:This is a WARNING log message"
    log_format = CommonRegexLineFormat(logline_format, timestamp_format, log_levels)
    result = log_format.match(log_line_info)
    assert result.timestamp == "2023-07-15 14:30:45"
    assert result.message == "This is a INFO log message"

    result = log_format.match(log_line_warning)
    assert result.timestamp == "2023-07-15 14:30:45"
    assert result.message == "This is a WARNING log message"
