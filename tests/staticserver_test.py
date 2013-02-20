import functools
import contextlib
import tempfile
import shutil

import requests
from nose.tools import istest, assert_equals, assert_true

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
def files_can_be_put_into_sub_directories():
    put("/message/hello", "Hello world!", key=key)
    result = get("/message/hello")
    assert_equals("Hello world!", result.content)
    
@test
def subsequent_puts_are_ignored_and_return_403():
    put("/hello", "Hello world!", key=key)
    second_put = put("/hello", "Goodbye!", key=key)
    assert_equals(403, second_put.status_code)
    result = get("/hello")
    assert_equals("Hello world!", result.content)
    
@test
def content_type_is_guessed_for_files():
    put("/hello.xml", "<p>Hello world!</p>", key=key)
    result = get("/hello.xml")
    assert_true(result.headers["content-type"].startswith("application/xml;"))
    
@test
def put_with_incorrect_key_does_not_upload_file():
    put("/hello", "Hello world!", key="invalid-key")
    assert_404("/hello")
    
@test
def cannot_put_to_root():
    put("/", "Hello world!", key=key)
    assert_404("/")
    
@test
def cannot_put_to_directory():
    put("/hello/", "Hello world!", key=key)
    assert_404("/hello/")

def put(path, content, key):
    url = "{0}?key={1}".format(_path_to_url(path), key)
    return _check_response(requests.put(url, content))

def get(path):
    return _check_response(requests.get(_path_to_url(path)))
    
def assert_404(path):
    response = get(path)
    assert_equals(404, response.status_code)


def _check_response(response):
    if response.status_code // 100 == 5:
        raise AssertionError("Server error: {0}".format(response.status_code))
    else:
        return response

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
