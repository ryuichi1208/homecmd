import sys
import os
import pytest
import requests 
from unittest.mock import patch
from pytest_mock import MockerFixture

class Mock:
    def __init__(self, name):
        self.name = name

    def hello(self):
        return f"{self.name}"

    def hello2(self):
        return f"{self.name}2"


@patch("test_hello2.Mock.hello")
def test_hello(mock):
    mock.return_value = "Test1"
    obj = Mock("Test")
    result = obj.hello()
    assert result == "Test1"
    mock.assert_called_once()


@pytest.fixture
def mock_method(mocker: MockerFixture):
    return mocker.patch("test_hello2.Mock.hello")


@pytest.fixture
def mock_method_2(mocker: MockerFixture):
    return mocker.patch("test_hello2.Mock.hello2")


def test_hello2(mock_method, mock_method_2):
    mock_method.return_value = "Test1"
    mock_method_2.return_value = "Test2"
    obj = Mock("Test")
    result = obj.hello()
    assert result == "Test1"
    mock_method.assert_called_once()
    result2 = obj.hello2()
    assert result2 == "Test2"
    mock_method_2.assert_called_once()


class HTTP:
    def __init__(self, url):
        self.url = url


    def get(self):
        res = requests.get(self.url)
        return res

def do():
    url = "http://example.com"
    http = HTTP(url)
    res = http.get()
    print(res.status_code)
    print(res.text)

def test_http(mocker: MockerFixture):
    mock_get = mocker.patch("test_hello2.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Hello World"
    
    url = "http://example.com"
    http = HTTP(url)
    res = http.get()
    
    assert res.status_code == 200
    assert res.text == "Hello World"
    mock_get.assert_called_once_with(url)

do()

def add(x, y) -> list:
    """
    2つの数値を受け取り、加算、減算、乗算、除算の結果をリストで返す関数
    :param x: 数値1
    :param y: 数値2
    :return: [加算結果, 減算結果, 乗算結果, 除算結果]
    """
    return [x + y, x - y, x * y, x / y]

# テーブルドリブンテスト
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, [3, -1, 2, 0.5]),
        (3, 4, [7, -1, 12, 0.75]),
        (5, 6, [11, -1, 30, 0.8333333333333334]),
    ],
)
def test_add(x, y, expected):
    result = add(x, y)
    assert result == expected
    assert isinstance(result, list)
    assert len(result) == 4
    assert all(isinstance(i, (int, float)) for i in result)
