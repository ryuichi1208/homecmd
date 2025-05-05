from unittest.mock import Mock, patch
import hello

#def test_my_class_my_method():
#    my_class = hello.MyClass()
#    assert my_class.my_method() == 'mocked'

class Lig:
    def __init__(self):
        self.name = "lig"

    def add(self, a, b):
        return a + b


@patch('hello.MyClass.my_method')
def test_my_method_decorator(mock_method: Mock):

    kv = {'key': 'value'}

    mock_method.return_value = kv

    my_class = hello.MyClass()
    assert my_class.my_method()["key"] == "value"

def test_lig_add():
    lig = Lig()
    assert lig.add(1, 2) == 3
    assert lig.add(0, 0) == 0
    assert lig.add(-1, 1) == 0
    assert lig.add(-1, -1) == -2

@patch('test_hello.Lig.add')
def test_lig_mock(mock_method: Mock):
    mock_method.return_value = 5
    lig = Lig()
    assert lig.add(1, 2) == 5

@patch('test_hello.Lig.add')
def test_side_effect(mock_method: Mock):
    mock_method.side_effect = lambda a, b: a - b
    lig = Lig()
    assert lig.add(1, 2) == -1

