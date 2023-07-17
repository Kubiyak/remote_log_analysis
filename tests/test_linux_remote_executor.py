import io

import pytest
from remote_log_analysis import RemoteLinuxExecutor
import fabric
import os


# Note:
# This test requires pytest to be run with the -s option.





def test_read_file_localhost(ssh_localhost):
    linux_exec = RemoteLinuxExecutor('localhost')
    read_result = linux_exec.read_file(__file__)
    assert 'def test_read_file' in read_result.getvalue()


def test_read_file_binary_localhost(ssh_localhost):
    linux_exec = RemoteLinuxExecutor('localhost')
    read_result = linux_exec.read_file(__file__, text_mode=False)
    assert 'def test_read_file_binary' in read_result.getvalue().decode('latin-1')


def test_stat_dir_localhost(ssh_localhost):
    linux_exec = RemoteLinuxExecutor('localhost')
    stat_result = linux_exec.dir_stat(os.path.dirname(__file__))
    assert any(e.path == __file__ for e in stat_result)


def test_stat_file_localhost(ssh_localhost):
    linux_exec = RemoteLinuxExecutor('localhost')
    stat_result = linux_exec.file_stat(__file__)
    assert stat_result.path == __file__

def test_executor_methods(ssh_localhost):
    linux_exec = RemoteLinuxExecutor('localhost')
    assert linux_exec.hostname == 'localhost'
    assert linux_exec.port == 22
    assert linux_exec.username == None
    linux_exec.reset()
    text = linux_exec.read_file(__file__)
    assert 'def test_executor_methods' in text.getvalue()