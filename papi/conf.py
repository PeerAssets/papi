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
# subscribed deck list
subscribed = ['b6a95f94fef093ee9009b04a09ecb9cb5cba20ab6f13fe0926aeb27b8671df43']
