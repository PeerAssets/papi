from pypeerassets import RpcNode
from requests.exceptions import ConnectionError
from subprocess import check_output
from urllib.request import Request
from time import sleep
from conf import *
import sys

class Sync:
    def __init__(self):
        self.synced = False
        self.node = None
        self.info = None
        self.recent = []
        self.attempts = 0

        try:
            self.connect()
        except ConnectionError:
            pass

    def connect(self):
        if not isinstance(self.node, RpcNode):
            ''' Initiate RpcNode'''
            self.node = RpcNode(testnet=testnet, username=rpc_username, password=rpc_password,
                            ip=rpc_host, port=rpc_port)
        self.is_synced()

    def is_synced(self):
        self.info = self.node.getinfo()
        if self.info['connections']:
                ''' Making sure node has connections'''
                self.peers = self.node.getpeerinfo()
                ''' Appending connected peers current blockheights'''
                try:
                    self.recent = max([i['startingheight'] for i in self.peers])
                except ValueError:
                    return False

                if self.info['blocks'] < self.recent - 500:
                    ''' Checking if the local node is sync'd at least 500 blocks behind peer with max blocks'''
                    self.synced = False
                else:
                    ''' Node is now synced and the function returns True to begin papi initialization'''
                    self.synced = True
                    
        return self.synced


def attempt_connection(connection):
    while True:
        try:
            connection.connect()
            info = connection.info
            if (connection.node is not None) and connection.synced:
                ''' if node is synced with the network then break and continue papi initialization'''
                node = connection.node
                synced = connection.synced
                sys.stdout.write('\r\nConnected : {}\nTestnet = {}\n'.format(info['version'], info['testnet']))
                break
            else:
                ''' if node is not synced then wait 3 seconds and try again '''
                sys.stdout.write('\rLocal node is not completely synced. Block {} of {}'.format(info['blocks'], max(connection.recent)))
                sleep(3)
                continue

        except (FileNotFoundError, ConnectionError, ValueError, Exception) as e:
            connection.attempts += 1
            if connection.attempts > max_attempts:
                raise Exception('Max connection attempts reached. Stopping papi...')

            if isinstance(e,FileNotFoundError):
                ''' This will occur if local node configuration file is not created/defined with correct RPC parameters'''
                sys.stdout.write('Waiting for RPC parameters\r')
            elif isinstance(e, ConnectionError):
                ''' This will be occur when the local node is not running'''
                sys.stdout.write('Waiting for connection to local node. Attempt(s): {} of {}\r'.format(connection.attempts, max_attempts))
            else:
                sys.stdout.write('Waiting for connection to peers. Attempt(s): {} of {}\r'.format(connection.attempts, max_attempts))
                pass

            sleep(3)
            continue
            
    return connection
