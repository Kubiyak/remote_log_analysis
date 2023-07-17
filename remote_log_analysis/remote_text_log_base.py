from .remote_file_base import RemoteFileBase
from .remote_executor_interface import RemoteExecutorInterface
from .remote_log_utils import LogLineFormatInterface, LogLineData


class RemoteTextLogBase:
    def __init__(self, path, executor: RemoteExecutorInterface,
                 field_extractor: LogLineFormatInterface,
                 start_offset: int = 0, end_offset: int = None,
                 block_size: int = 4096):
        self._file_base = RemoteFileBase(path, executor, start_offset=start_offset, end_offset=end_offset,
                                         text_mode=True, block_size=block_size)
        self._field_extractor = field_extractor

        self._lines = []

    def seek(self, offset: int):
        self._lines = []
        return self._file_base.seek(offset)

    def tell(self):
        return self._file_base.tell()

    def rewind(self):
        return self._file_base.rewind()


