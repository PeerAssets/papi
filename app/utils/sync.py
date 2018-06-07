import pypeerassets as pa
from requests.exceptions import ConnectionError
from time import sleep
from conf import *
import sys

class Sync:
    def __init__(self, node = None):
        self.synced = False
        self.info = None
        if node is None:
            self.node = pa.RpcNode(testnet=testnet, username=rpc_username, password=rpc_password,
                            ip=rpc_host, port=rpc_port)
        else:
            self.node = node
            
    def connect(self):
        connection = attempt_connection(self.node)
        return connection

    def get_recent(self):
        self.peers = self.node.getpeerinfo()
        recent = [i['startingheight'] for i in self.peers]
        return recent

    @property
    def is_synced(self):
        self.info = self.node.getinfo()
        recent = self.get_recent()

        if recent:
                threshold = max(recent) - 500
                if 'blocks' in self.info:
                    if self.info['blocks'] < threshold:
                        ''' Checking if the local node is sync'd at least 500 blocks behind peer with max blocks'''
                        self.synced = False
                    else:
                        ''' Node is now synced and the function returns True to begin papi initialization'''
                        self.synced = True
                else:
                    return False
                    
        return self.synced

class ExceededAttempts(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = 'Max Attempts Exceeded'

def attempt_check(attempts):
    if attempts > max_attempts:
        raise ExceededAttempts


def attempt_connection(node):
    attempts = 0
    info = None

    while True:
        
        try:
            info = node.getinfo()
        except ConnectionError:
            ''' This will be occur when the local node is not running'''
            attempts += 1
            
            if attempts > max_attempts:
                break

            sys.stdout.write('\rWaiting for connection to local node. Attempt(s): {} of {}\n'.format(attempts, max_attempts))
            sys.stdout.flush()
            sleep(1)
            continue

        try:
            connection = Sync(node)
            recent = connection.get_recent()
            info = node.getinfo()
            if connection.is_synced:
                ''' if node is synced with the network then break and continue papi initialization'''
                return connection
                break
            elif recent:
                ''' if node is not synced then wait 3 seconds and try again '''
                sys.stdout.write('\rLocal node is not completely synced. Block {} of {}'.format(self.info['blocks'], max(recent)))
                sys.stdout.flush()
                sleep(3)
                continue
            else:
                pass

        except (FileNotFoundError, ValueError, Exception) as e:
            attempts += 1
            if isinstance(e,FileNotFoundError):
                ''' This will occur if local node configuration file is not created/defined with correct RPC parameters'''
                sys.stdout.write('Waiting for RPC parameters\r') 
                sys.stdout.flush()
            else:
                print(e)
                try:
                    attempt_check(attempts)
                    sys.stdout.write('Waiting for connection to peers. Attempt(s): {} of {}\r'.format(attempts, max_attempts))
                    sys.stdout.flush()
                except ExceededAttempts as error:
                    print('Exceeded max attempts": {}'.format(error.message))

            sleep(3)
            continue