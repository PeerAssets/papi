from os import getenv

# db connection URI to be passed to sqlalchemy, as in http://docs.sqlalchemy.org/en/latest/core/engines.html
db_engine = getenv('DB', 'sqlite:///papi.db')
# run on testnet or not
testnet = getenv('PA_TESTNET', True)
# follow production P2TH or not
production = getenv('PA_PRODUCTION', True)
# autoload the decks
autoload = getenv('AUTOLOAD', True)
# deck version to use
version = getenv('PA_VERSION', 1)
# ip address of the peercoin node
rpc_host = getenv('RPC_HOST', 'localhost')
# port of the peercoin node
rpc_port = getenv('RCP_PORT', '9904')
# username for rpc connection
rpc_username = getenv('RCP_USER', None)
# password for the rpc_connection
rpc_password = getenv('RPC_PASS', None)
# subscribed deck list
# Use '*' inside the list to subscribe to all decks or use deck id's to subscribe to specified decks only
subscribed = ['*']
