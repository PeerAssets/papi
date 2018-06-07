#!/usr/bin/env python3

from requests import post
from requests.exceptions import ConnectionError
from sys import argv


def wallet_notify(txid, batch=batch):
    try:
        post('http://0.0.0.0:5555/alert', data={'txid': txid})
    except ConnectionError:
        pass


if __name__ == '__main__':
    wallet_notify(argv[1])
