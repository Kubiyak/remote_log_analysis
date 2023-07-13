from __future__ import annotations
from .remote_executor_interface import RemoteExecutorInterface
from .remote_path_info import RemotePathType, RemotePathInfo
import typing
import re
import copy
from fabric import Connection
import io


class _BytesIOWrapper:
    def __init__(self, bytes_io):
        self._bytes_io = bytes_io

    def write(self, val: str):
        self._bytes_io.write(val.encode('latin-1'))

    def flush(self):
        self._bytes_io.flush()


class RemoteLinuxExecutor(RemoteExecutorInterface):
    '''
    Execute a restricted set of commands remotely to obtain log file data for analysis. The host on which
    commands are executed has to be a linux-like environment where the following binaries are available:
        /usr/bin/find
        /usr/bin/stat
        /bin/dd
    '''

    def __init__(self, hostname: str, username: typing.Optional[str] = None, port: int = 22, **connect_kwargs):
        '''
        :param hostname: Hostname to connect to.
        :param username: Username to connect as
        :param port: port that ssh is listening on. Typically this is 22.
        :param connect_kwargs: Connection args passed to paramiko. See the paramiko documentation
        '''
        self._hostname = hostname
        self._username = username
        self._port = port
        self._connect_kwargs = connect_kwargs
        self._x_connection: typing.Optional[Connection] = None
        self._create_connection()
        self._stat_regex = re.compile(r'^\(name=(.+)\),size=(\d+),mtime=(\d+),atime=(\d+),\(type=([ \w]+)\)')

    def reset(self):
        self._create_connection()

    @property
    def hostname(self):
        return self._hostname

    @property
    def username(self):
        return self._username

    @property
    def port(self):
        return self._port

    @property
    def connection_kwargs(self) -> {}:
        return copy.deepcopy(self._connect_kwargs)

    def read_file_range(self, filepath: str,
                        offset: int,
                        bytes_to_read: int,
                        text_mode=True) -> typing.Union[io.StringIO, io.BytesIO]:
        '''
        :param filepath: File to read
        :param offset: Offset in the file to read from
        :param bytes_to_read: Number of bytes to read
        :param text_mode: Indicate whether data is text or binary data
        :return: bytes object wth the data
        '''
        RemoteLinuxExecutor._check_filepath(filepath)
        dd_command = f'/bin/dd if="{filepath}" skip={offset} count={bytes_to_read} bs=1'

        stream_object = io.StringIO() if text_mode else io.BytesIO()
        stream_object_wrapper = stream_object if text_mode else _BytesIOWrapper(stream_object)
        self._x_connection.run(dd_command, hide=True, out_stream=stream_object)
        stream_object.seek(0)
        return stream_object

    def read_file(self, filepath, text_mode=True) -> typing.Union[io.StringIO, io.BytesIO]:
        RemoteLinuxExecutor._check_filepath(filepath)
        dd_command = f'/bin/dd if="{filepath}"'
        stream_object = io.StringIO() if text_mode else io.BytesIO()
        stream_object_wrapper = stream_object if text_mode else _BytesIOWrapper(stream_object)
        self._x_connection.run(dd_command, hide=True, out_stream=stream_object_wrapper)
        stream_object.seek(0)
        return stream_object

    def dir_stat(self, dirpath) -> typing.List[RemotePathInfo]:
        RemoteLinuxExecutor._check_filepath(dirpath)
        return self._stat_impl(dirpath, directory=True)

    def file_stat(self, filepath) -> RemotePathInfo:
        RemoteLinuxExecutor._check_filepath(filepath)
        return self._stat_impl(filepath, directory=False)[0]

    def _stat_impl(self, path, directory=False):

        dirtext = "/**" if directory else ""
        stat_command = f'/usr/bin/stat --format "(name=%n),size=%s,mtime=%Y,atime=%X,(type=%F)" "{path}"{dirtext}'
        stream_object = io.StringIO()
        self._x_connection.run(stat_command, hide=True, out_stream=stream_object)
        entries = stream_object.getvalue().strip().split('\n')
        result = []
        for e in entries:
            m = re.search(self._stat_regex, e)
            if not m:
                raise RuntimeError(f'Unable to parse output from stat: {e}')
            path_entry: RemotePathInfo = RemotePathInfo(path=m.groups()[0],
                                                        type=RemoteLinuxExecutor._to_remote_path_type(m.groups()[4]),
                                                        mtime=int(m.groups()[2]),
                                                        atime=int(m.groups()[3]),
                                                        size=int(m.groups()[1])
                                                        )
            result.append(path_entry)
        return result

    @staticmethod
    def _to_remote_path_type(stat_file_type: str):
        '''
        :param stat_file_type: File type from /usr/bin/stat --format="%F"
        :return: Corresponding RemotePathType.
        This is only likely to work on Linux systems. This should be extracted
        into some OS translation layer.
        '''
        match stat_file_type:
            case 'regular file' | 'regular empty file':
                return RemotePathType.FILE
            case 'directory':
                return RemotePathType.DIR
            case 'symbolic link':
                return RemotePathType.SYMLINK
            case other:
                return RemotePathType.UNKNOWN

    # TODO implement async variants which can be used w/ asyncio
    @staticmethod
    def _check_filepath(filepath):
        # Note this is more limiting than it needs to be but quote characters in filepaths are rare.
        if '\"' in filepath or "'" in filepath or ';' in filepath:
            raise RuntimeError('Quote and semicolon characters are disallowed in filepath for security')

    def _create_connection(self):
        if self._x_connection:
            try:
                self._x_connection.close()
            except Exception:
                pass
        self._x_connection = Connection(host=self._hostname, user=self._username,
                                        port=self._port,
                                        connect_kwargs=self._connect_kwargs)
        self._x_connection.open()
