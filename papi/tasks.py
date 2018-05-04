import time
from data import *
from huey import crontab
from conf import huey

#Rescan blockchain and update database every hour
@huey.task(crontab(minute='*/60'))
def rescan_blockchain_and_update():
    init_decks()
    print('Blockchain rescanned and database updated.')