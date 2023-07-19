from .remote_executor_for_test import RemoteExecutorForTest
from remote_log_analysis import RemoteFileBase, RemotePathInfo, RemotePathType
import pytest
import io


@pytest.fixture
def text_stream_1mm():
    yield io.StringIO('ABCDEFGHIJKLMNOPQRSTUVWXYZ012345' * (32 * 1024))


@pytest.fixture
def binary_stream_1mm():
    yield io.BytesIO(('ABCDEFGHIJKLMNOPQRSTUVWXYZ012345' * (32 * 1024)).encode('latin-1'))


def test_read_section(text_stream_1mm):
    executor = RemoteExecutorForTest(text_stream=text_stream_1mm,
                                     file_stat=RemotePathInfo(path="/foo/bar", size=1048576, atime=0, mtime=0,
                                                              type=RemotePathType.FILE))
    reader = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, start_offset=8192)
    result = reader.read()
    assert len(result.data) == 4096


def test_read_section_binary(binary_stream_1mm):
    executor = RemoteExecutorForTest(binary_stream=binary_stream_1mm,
                                     file_stat=RemotePathInfo(path="/foo/bar", size=1048576, atime=0, mtime=0,
                                                              type=RemotePathType.FILE))

    reader = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, text_mode=False)
    result = reader.read()
    assert len(result.data) == 4096


def test_misc(binary_stream_1mm):
    executor = RemoteExecutorForTest(binary_stream=binary_stream_1mm,
                                     file_stat=RemotePathInfo(path="/foo/bar", size=1048576, atime=0, mtime=0,
                                                              type=RemotePathType.FILE))

    reader = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, text_mode=False)
    reader.rewind()
    reader.reset()
    assert reader.start_offset == 0
    assert reader.stat.size == 1048576
    assert reader.path == '/foo/bar'

    count = 0
    reader.seek(0)
    for chunk in reader:
        count += 1

    assert count * 4096 == 1048576

    with pytest.raises(EOFError):
        reader.read()


def test_lowlevel_fails(binary_stream_1mm):
    executor = RemoteExecutorForTest(binary_stream=binary_stream_1mm,
                                     file_stat=RemotePathInfo(path="/foo/bar", size=1048576, atime=0, mtime=0,
                                                              type=RemotePathType.FILE), fail_read=True)

    reader = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, text_mode=False)

    with pytest.raises(EOFError):
        reader.read()

    executor = RemoteExecutorForTest(binary_stream=binary_stream_1mm,
                                     file_stat=RemotePathInfo(path="/foo/bar", size=1048576, atime=0, mtime=0,
                                                              type=RemotePathType.FILE), fail_stat=True)

    with pytest.raises(OSError):
        reader = RemoteFileBase("/foo/bar", executor=executor, block_size=4096, text_mode=False)


def test_remote_log():
    pass