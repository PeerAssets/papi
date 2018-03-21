from os import environ

# db connection URI to be passed to sqlalchemy, as in http://docs.sqlalchemy.org/en/latest/core/engines.html
db_engine = environ.get('DB', 'sqlite:///papi.db')
# run on testnet or not
testnet = environ.get('PA_TESTNET', True)
# follow production P2TH or not
production = environ.get('PA_PRODUCTION', True)
# autoload the decks
autoload = environ.get('AUTOLOAD', True)
# deck version to use
version = environ.get('PA_VERSION', 1)
# ip address of the peercoin node
rpc_host = environ.get('RPC_HOST', 'localhost')
# port of the peercoin node
rpc_port = environ.get('RCP_PORT', '9904')
# username for rpc connection
rpc_username = environ.get('RPC_USERNAME', None)
# password for the rpc_connection
rpc_password = environ.get('RPC_PASSWORD', None)
# subscribed deck list
# Use '*' inside the list to subscribe to all decks or use deck id's to subscribe to specified decks only
subscribed = ['*']
