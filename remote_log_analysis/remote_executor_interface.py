from __future__ import annotations
import typing
import io
import abc
from .remote_path_info import RemotePathInfo


class RemoteExecutorInterface(metaclass=abc.ABCMeta):
    '''
    An interface check for executors used by this module. The required methods are stated
    in the required block below.
    '''
    required = ['dir_stat', 'file_stat', 'read_file', 'read_file_range']

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        if not all(hasattr(subclass, attr) for attr in RemoteExecutorInterface.required):
            return NotImplemented

        return (all(callable(getattr(subclass, attr)) for attr in RemoteExecutorInterface.required)
                or NotImplemented)

    @abc.abstractmethod
    def file_stat(self, path) -> RemotePathInfo:
        '''
        Obtain stat info for the specified path
        :param path:
        :return: RemotePathInfo w/ details for specified files
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def dir_stat(self, dirpath) -> typing.List[RemotePathInfo]:
        '''
        Obtain RemotePathInfo for each remote directory entry.
        :param dirpath: Obtain stat info for each contained entry
        :return: List of RemotePathInfo objects
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def read_file(self, filepath: str, text_mode: bool = True) -> typing.Union[io.StringIO, io.BytesIO]:
        '''

        :param filepath: Path to read
        :param text_mode: Indicates if the file contains plain text or binary data
        :return: Specified file's contents as a stream
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def read_file_range(self, filepath: str,
                        offset: int, bytes_to_read: int,
                        text_mode=True) -> typing.Union[io.StringIO, io.BytesIO]:
        '''
        Return the specified range of the remote file.
        :param filepath: Path to read
        :param offset: Offfset to read from
        :param bytes_to_read: Bytes to read
        :param text_mode: Text or binary data indicator
        :return: Specified range of the file as a stream
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        '''
        Reset connection etc. Can be a no-op
        :return:
        '''
        raise NotImplementedError
