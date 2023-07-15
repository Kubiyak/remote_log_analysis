from remote_log_analysis import RemoteExecutorInterface, RemotePathInfo, RemotePathType
import io
import copy
import typing
import time


class RemoteExecutorForTest(RemoteExecutorInterface):

    def __init__(self, text_stream: typing.Optional[io.StringIO] = None,
                 binary_stream: typing.Optional[io.BytesIO] = None,
                 file_stat: typing.Optional[RemotePathInfo] = None,
                 fail_read = False, fail_stat = False):
        self._text_stream = text_stream or io.StringIO()
        self._binary_stream = binary_stream or io.BytesIO()
        mtime = time.time()
        self._file_stat = file_stat or RemotePathInfo(path='/foo', size=8192, mtime=mtime,
                                                      atime=mtime, type=RemotePathType.FILE)
        self._fail_read = fail_read
        self._fail_stat = fail_stat

    def dir_stat(self, dirpath) -> typing.List[RemotePathInfo]:
        raise RuntimeError('dir_stat not implemented')

    def read_file_range(self, filepath: str, offset: int,
                        bytes_to_read: int, text_mode=True) -> typing.Union[io.StringIO, io.BytesIO]:

        if self._fail_read:
            raise EOFError

        if text_mode:
            self._text_stream.seek(offset)
            return io.StringIO(self._text_stream.read(bytes_to_read))
        else:
            self._binary_stream.seek(offset)
            return io.BytesIO(self._binary_stream.read(bytes_to_read))

    def reset(self):
        pass

    def file_stat(self, path) -> RemotePathInfo:
        if self._fail_stat:
            raise OSError

        result = RemotePathInfo(path=path, size=self._file_stat.size,
                                atime=self._file_stat.atime, mtime=self._file_stat.mtime, type=RemotePathType.FILE)
        return result

    def read_file(self, filepath: str, text_mode: bool = True) -> typing.Union[io.StringIO, io.BytesIO]:
        if self._fail_read:
            raise EOFError

        if text_mode:
            self._text_stream.seek(0)
            return copy.deepcopy(self._text_stream)
        else:
            self._binary_stream.seek(0)
            return copy.deepcopy(self._binary_stream)
