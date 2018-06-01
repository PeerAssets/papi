#!/usr/bin/env python3
import redis
from requests import post
from requests.exceptions import ConnectionError
from conf import batch
from sys import argv

def wallet_notify(txid, batch = batch):
    if not batch:
        try:
            post('http://0.0.0.0:5555/alert', data ={'txid':txid})
        except ConnectionError:
            pass
    else:
        try:
            Queue.add(txid)
        except Exception as e:
            pass

class Queue(object):

    conn = redis.StrictRedis(host = 'localhost', charset='utf-8', decode_responses=True)

    @classmethod
    def add(cls, txid):
        valid = cls.is_hex(txid)

        if valid:
            cls.conn.sadd('txids',txid)
        return valid


    @classmethod
    def read(cls):
        txids = cls.conn.smembers('txids')
        return txids

    @classmethod
    def clear(cls):
        cls.conn.flushdb()
            
    @staticmethod
    def is_hex(txid):
        try:
            int(txid,16) and (len(txid) == 64)
            return True
        except:
            return False

if __name__ == '__main__':
    wallet_notify(argv[1])