import io

from .remote_executor_interface import RemoteExecutorInterface
from .remote_path_info import RemotePathInfo, RemotePathType
import typing
import functools
from dataclasses import dataclass
import io


@dataclass(frozen=True)
class FileChunk:
    '''
    RemoteFileBase caches chunks of a file using this type.
    '''
    offset: int
    size: int
    data: typing.Union[memoryview, str]  # memoryview for binary data. str for text mode


class RemoteFileBase:
    '''
    Base remote file functionality. The underlying file should be an append-only file such as a log file or
    a static file which is not changing for the duration of interaction with RemoteFileBase and sub-classes.
    '''

    def __init__(self, path: str, executor: RemoteExecutorInterface,
                 block_size: int = 1048576,
                 start_offset: int = 0,
                 end_offset: typing.Optional[int] = None,
                 text_mode: bool = True,
                 max_cached_blocks: int = 64):
        '''
        :param path: Remote file path to read
        :param executor: Low level I/O interface to remote host
        :param block_size: Chunk size to read in
        :param start_offset: Start offset in the file. Seeks to file offsets less than this are updated to
                             seeks to this value.
        :param end_offset: Offset beyond which no data will be returned. Seeks beyond this location are
                           set to this offset.

        :param max_cached_blocks: Parameter to functools.lrucache
        start_offset is rounded down to a multiple of block_size and end_offset is
        rounded up to a multiple of block_size if specified.
        '''
        self._path = path
        self._executor = executor
        self._block_size = block_size
        self._start_offset = (start_offset // self._block_size) * self._block_size
        self._end_offset = end_offset
        self._offset = self._start_offset
        self._text_mode = text_mode
        self._max_cached_blocks = max_cached_blocks
        self._stat_file()
        self._size = self._stat.size
        self._reader = None
        self.reset()
        self._validate()

    def reset(self):
        self._stat_file()
        self._size = self._stat.size
        self._offset = self._start_offset
        self._reader = functools.lru_cache(self._max_cached_blocks)(self._read_impl)

    def _validate(self):
        if self._block_size < 4096 or self._block_size > 16 * (1024 ** 2):
            raise ValueError('block_size must be between 4096 and 16M')

        if (self._block_size - 1) & self._block_size:
            raise ValueError('block_size must be a power of 2')

        if self._start_offset > self._size:
            raise ValueError('start_offset cannot be beyond the end of the file')

        if self._end_offset:
            # round up to next highest multiple of block_size unless already a multiple of block_size
            self._end_offset = ((self._end_offset - 1) // self._block_size + 1) * self._block_size

    def _stat_file(self):
        self._stat = self._executor.file_stat(self._path)
        if self._stat.type != RemotePathType.FILE:
            raise FileNotFoundError('Path must refer to a regular file')

    @property
    def path(self) -> str:
        return self._path

    @property
    def executor(self) -> RemoteExecutorInterface:
        return self._executor

    @property
    def block_size(self) -> int:
        return self._block_size

    @property
    def start_offset(self) -> int:
        return self._start_offset

    @property
    def end_offset(self) -> typing.Optional[int]:
        return self._end_offset

    @property
    def stat(self) -> RemotePathInfo:
        return self._stat

    @property
    def text_mode(self):
        return self._text_mode

    def seek(self, offset: int) -> int:
        '''
        Seek to the specified offset or nearby location subject to rounding to the block size.
        :param offset: Offset to seek to
        :return: Actual offset positioned to subject to startoffset/endoffset and file size checks.
        Positioning beyond the end of the file is allowed but will raise EOFError when attempting to read from there
        '''
        offset = (offset // self._block_size) * self._block_size

        if offset < self._start_offset:
            offset = self._start_offset
        elif self._end_offset and offset > self._end_offset:
            offset = self._end_offset

        self._offset = offset
        return self._offset

    def tell(self) -> int:
        ''' Return current offset '''
        return self._offset

    def rewind(self) -> int:
        ''' Convenience method to seek to start offset '''
        self._offset = self._start_offset
        return self._offset

    def read(self) -> FileChunk:
        # read upto a block_size of data and return it
        # raises EOFError when past end of range.
        if ((self._end_offset and self._offset >= self._end_offset) or
                (self._offset >= self._size)):
            raise EOFError

        result = self._reader(self._offset)
        self._offset += result.size
        return result

    def __iter__(self):
        end_value = self._end_offset if self._end_offset else self._size
        while self._offset < end_value:
            try:
                yield self.read()
            except EOFError:
                return

    def _read_impl(self, offset):
        if self._end_offset and offset >= self._end_offset:
            raise EOFError

        success = False
        result = None
        bytes_to_read = 0

        for i in range(2):
            try:
                bytes_to_read = self._block_size
                if self._end_offset and offset + self._block_size > self._end_offset:
                    bytes_to_read = self._end_offset - offset
                elif self._size < offset + self._block_size:
                    bytes_to_read = self._size - offset
                result = self._executor.read_file_range(self._path, offset=offset, bytes_to_read=bytes_to_read,
                                                        text_mode=self._text_mode)
                success = True
                break
            except EOFError:
                raise
            except Exception:
                self._executor.reset()

        if not success:
            raise EOFError

        chunk = FileChunk(offset=offset, size=bytes_to_read,
                          data=(result.getbuffer().toreadonly() if not self._text_mode
                                else result.getvalue()))
        return chunk
