import functools
import contextlib
import tempfile
import shutil

import requests
from nose.tools import istest, assert_equals

import staticserver


def test(func):
    @functools.wraps(func)
    def run_test():
        with _start_server():
            func()
    
    return istest(run_test)

@test
def server_with_no_files_returns_404():
    assert_404("/")
    assert_404("/hello")

@test
def put_with_correct_key_returns_200():
    result = put("/hello", "Hello world!", key=key)
    assert_equals(200, result.status_code)
    
@test
def put_with_incorrect_key_returns_403():
    result = put("/hello", "Hello world!", key="invalid-key")
    assert_equals(403, result.status_code)
    assert_equals("Bad key", result.content)
    
@test
def put_with_correct_key_allows_file_to_be_downloaded_with_get():
    put("/hello", "Hello world!", key=key)
    result = get("/hello")
    assert_equals("Hello world!", result.content)
    
@test
def put_with_incorrect_key_does_not_upload_file():
    put("/hello", "Hello world!", key="invalid-key")
    assert_404("/hello")

def put(path, content, key):
    return requests.put("{0}?key={1}".format(_path_to_url(path), key), content)

def get(path):
    return requests.get(_path_to_url(path))
    
def assert_404(path):
    response = get(path)
    assert_equals(404, response.status_code)

def _path_to_url(path):
    return "http://localhost:{0}{1}".format(_port, path)

@contextlib.contextmanager
def _start_server():
    with _create_temporary_dir() as root:
        with staticserver.start(port=_port, root=root, key=key) as server:
            yield server

@contextlib.contextmanager
def _create_temporary_dir():
    try:
        build_dir = tempfile.mkdtemp()
        yield build_dir
    finally:
        shutil.rmtree(build_dir)


_port = 50080
key = "4f015d188778f73315b3f628cee26ed6080c2e5f"
