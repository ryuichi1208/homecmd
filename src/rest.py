#!/usr/local/bin/python3

import concurrent.futures
import netrc
import os
import sys
import time
import urllib.request

import babel

import calc


def main():
    calc.add(10, 20)


if __name__ == "__main__":
    main()
