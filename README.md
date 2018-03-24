# papi
### PeerAssets API
*Requires Python 3.4+ and pypeerassets*

## Dependencies:
```
pip install flask, flask-sqlalchemy
```
## Configure (conf.py)
- **testnet**:
    Boolean dictating whether the network is mainnet or testnet

- **production**:
    Boolean dictating whether to query production assets or non-production assets.

- **autoload**:
    Boolean which, when True, loads the P2TH key corresponding to the current network
    and production state into the local node. If walletnotify is going to be used it is
    recommended that autoload is set to False. If False then papi is informed of only new 
    transactions pertaining to subscribed decks.

- **version**:
    Integer corresponding to the PeerAssets protocol version being used.

- **subscribed**:
    List of deck id's that will be taken as P2TH keys, imported into the local node, and
    be processed into the local database. This process includes recording one entry into 
    the Deck table and continual entries into the Card table.
## Running the Flask Server
```
python app.py
```
This will create the local sqlite database file named *papi.db*

## running in docker

`docker-compose up -d`