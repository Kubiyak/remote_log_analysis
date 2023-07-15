from .remote_file_base import RemoteFileBase
from .remote_executor_interface import RemoteExecutorInterface


class RemoteTextLog(RemoteFileBase):
    def __init__(self, path, executor:RemoteExecutorInterface,
                 start_offset:int = 0, end_offset:int = None,
                 block_size:int = 4096):
        super().__init__(path, executor, start_offset=start_offset, end_offset=end_offset,
                         text_mode=True, block_size=block_size)
