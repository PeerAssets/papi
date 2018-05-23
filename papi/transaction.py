#!/usr/bin/env python

from requests import post
from sys import argv
from data import connection

def wallet_notify(txid):
    if not connection.synced:
        pass
    else:
        try:
            post('http://0.0.0.0:5555/alert', data={'txid':txid})
        except Exception as e:
            print(e)

if __name__ == '__main__':
    wallet_notify(argv[1])