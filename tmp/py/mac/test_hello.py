from unittest.mock import Mock, patch
import hello
import pytest

# def test_my_class_my_method():
#    my_class = hello.MyClass()
#    assert my_class.my_method() == 'mocked'


class Lig:
    def __init__(self):
        self.name = "lig"

    def add(self, a, b):
        return a + b


@patch("hello.MyClass.my_method")
def test_my_method_decorator(mock_method: Mock):
    kv = {"key": "value"}

    mock_method.return_value = kv

    my_class = hello.MyClass()
    assert my_class.my_method()["key"] == "value"


def test_lig_add():
    lig = Lig()
    assert lig.add(1, 2) == 3
    assert lig.add(0, 0) == 0
    assert lig.add(-1, 1) == 0
    assert lig.add(-1, -1) == -2


@patch("test_hello.Lig.add")
def test_lig_mock(mock_method: Mock):
    mock_method.return_value = 5
    lig = Lig()
    assert lig.add(1, 2) == 5


@patch("test_hello.Lig.add")
def test_side_effect(mock_method: Mock):
    mock_method.side_effect = lambda a, b: a - b
    lig = Lig()
    assert lig.add(1, 2) == -1


import os
from unittest.mock import patch


class TestApp:
    @patch("os.getcwd")
    def test_patch(self, mock_getcwd):
        mock_getcwd.return_value = "mocked"
        print(f"cwd={os.getcwd()}")
        assert os.getcwd() == "mocked"

    def test_with(self):
        with patch("os.getcwd") as mock:
            mock.return_value = "mocked-with"
            print(f"with={os.getcwd()}")

    @pytest.fixture()
    def fixture_mock(self, mocker):
        return mocker.patch("os.getcwd", return_value="mocked_2")

    def test_fixture(self, fixture_mock):
        assert os.getcwd() == "mocked_2"

    def test_fixture2(self, fixture_mock):
        assert os.getcwd() == "mocked_2"


class HTTPGet:
    def __init__(self, url):
        self.url = url

    def get(self):
        return f"original"


class TestHTTPGet:
    @patch("test_hello.HTTPGet.get")
    def test_http_get(self, mock_get):
        mock_get.return_value = "mocked"
        http_get = HTTPGet("http://example.com")
        assert http_get.get() == "mocked"
