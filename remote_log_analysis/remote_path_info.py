from dataclasses import dataclass
from enum import StrEnum, auto


class RemotePathType(StrEnum):
    FILE = auto()
    DIR = auto()
    SYMLINK = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class RemotePathInfo:
    path: str  # full path
    type: RemotePathType
    mtime: int = 0  # last modification time
    atime: int = 0  # last access time
    size: int = 0  # size in bytes
