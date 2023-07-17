import pytest
import os
import fabric

@pytest.fixture
def ssh_localhost():
    try:
        c = fabric.Connection(host="127.0.0.1",
                              connect_kwargs={"key_filename": f'{os.environ["HOME"]}/.ssh/id_rsa'})
        c.run("ls", hide=True, in_stream=False)
        yield {}
        c.close()
    except Exception:
        pytest.skip('Unable to ssh to localhost w/ id_rsa private key w/o a password. Skipping localhost tests')