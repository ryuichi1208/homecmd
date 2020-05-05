import os
import sys


def add(x, y):
    return x + y


def minus(x, y):
    return x - y


def reverse(arr: list):
    arr.reverse()
    return arr


def lambda_c(a: list):
    return list(map(lambda x: x * x, a))
