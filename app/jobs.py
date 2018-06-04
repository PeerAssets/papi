from utils.extensions import rq
from utils.sync import node
import pypeerassets as pa
from transaction import Queue
from conf import *
from datetime import timedelta
import sys

@rq.job('default')
def process_mempool():
    batch_data = [ ('gettransaction', [i] ) for i in Queue.read() ]
    txs = [ i for i in node.batch( batch_data ) if i['error'] is None ]
    return print(txs)

def start_process_mempool():
    process_mempool.schedule(timedelta(seconds=10))
    scheduler = rq.get_scheduler(interval=10)