#!/usr/bin/env python3
"""C
"""
from __future__ import annotations

import logging

from pyhaopenmotics.helpers import base64_encode, base64_decode


def main():
    print('Enter the bearer token:')
    bt = input()
    benc = base64_encode(bt)
    print("btoa: " + benc)
    bdec = base64_decode(benc)
    print("atob: " + bdec)

if __name__ == "__main__":
    main()