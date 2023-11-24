from .remote_file_base import RemoteFileBase, FileChunk
from .remote_log_utils import LogLineData, LogLineSplitterInterface, UnixLogLineSplitter, LogLineFormatInterface
from .remote_linux_executor import RemoteLinuxExecutor
import typing


class RemoteTextLog:
    '''
        Provides a line oriented and chunk oriented traversal of a RemoteFileBase object.
        The RemoteFileBase object should be a text_mode object.
        The provided LogLineSplitterInterface object is used to split the file into lines.
        The details of splitting a data chunk into lines is delegated to the LogLineSplitterInterface object.

        The chunk oriented traversal reads from the current file offset. Any re-positioning of the underlying
        RemoteFileBase object will discard any cached data.

        It is best to use either the line oriented traversal or the chunk oriented traversal. Mixing the two
        requires care to avoid skipping data.
    '''

    def __init__(self, file: RemoteFileBase, line_splitter: LogLineSplitterInterface):
        self._file = file
        self._line_splitter = line_splitter
        self._offset = self._file.tell()

    @property
    def offset(self):
        return self._offset

    @property
    def block_size(self):
        return self._file.block_size

    @property
    def stat(self):
        return self._file.stat

    @property
    def start_offset(self) -> int:
        return self._file.start_offset

    @property
    def end_offset(self) -> int:
        return self._file.end_offset

    def tell(self) -> int:
        return self._file.tell()

    def seek(self, offset) -> int:
        offset = self._file.seek(offset)
        self._offset = offset
        self._line_splitter.clear()
        return offset

    def rewind(self):
        self._file.rewind()
        self._offset = self._file.tell()
        self._line_splitter.clear()
        return self._offset

    def read_line(self) -> typing.Optional[LogLineData]:
        if self._offset != self._file.tell():
            self._line_splitter.clear()
            self._offset = self._file.tell()

        result = self._line_splitter.read()
        self._offset = self._file.tell()
        return result

    def read_line_iter(self):
        while True:
            line = self.read_line()
            if line is None:
                break
            yield line

    def read_chunk(self) -> typing.Optional[FileChunk]:
        '''
        Read a chunk of data from the file. The chunk size is determined by the underlying RemoteFileBase object.
        :return: FileChunk
        raises EOFError when past end of range.
        '''
        self._line_splitter.clear()
        try:
            return self._file.read()
        except EOFError:
            return None

    def read_chunk_iter(self):
        self._line_splitter.clear()
        for chunk in self._file:
            yield chunk


class RemoteLinuxLog(RemoteTextLog):
    '''
        Provides a line oriented and chunk oriented traversal of a typical log file on a Linux host.
    '''

    def __init__(self, path: str, executor: RemoteLinuxExecutor,
                 log_format: LogLineFormatInterface, start_offset: int = 0, end_offset: typing.Optional[int] = None,
                 block_size: int = 4096):
        '''
        :param path: Path on remote host
        :param executor: RemoteLinuxExecutor for connecting to remote host
        :param log_format: An object that implements the LogLineFormatInterface. Typically, this will be an instance
        of CommonRegexLineFormat
        '''
        file = RemoteFileBase(path, executor, start_offset=start_offset, end_offset=end_offset, block_size=block_size,
                              text_mode=True)
        line_splitter = UnixLogLineSplitter(file, log_format)
        super().__init__(file, line_splitter)