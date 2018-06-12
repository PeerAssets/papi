
<h1 align="center">
  <br>
  <a href="https://peerassets.github.io/WhitePaper/"><img src="https://github.com/PeerAssets/logofiles/blob/master/svg/PeerAssets_icon.svg" alt="PeerAssets" width="300"></a>
  <br>
  papi
  <br>
</h1>

<h4 align="center">A minimal PeerAssets API <a href="http://flask.pocoo.org/" target="_blank">Flask</a>.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#todo-list">TODO list</a> •
  <a href="#download">Download</a> •
  <a href="#credits">Credits</a> •
  <a href="#related">Related</a> •
  <a href="#license">License</a>
</p>

![Imgur](https://i.imgur.com/6T5thkm.gif)

## Key Features

* Supports Deck Autoloading
  - Instantly locate all PeerAssets decks on host chain .
* Supports Deck Subscription
  - Gives you the option to subscribe to all decks and downloads all relevant cards from the blockchain.
* Restless
  - Provides a restless API endpoint. `/restless/v1/`
* Mempool Tracking
  - Via walletnotify the server knows when relevant transactions are in the mempool or receive a network confirmation.
* Postgres DB
* Docker with peercoind container
* Nginx server using uwsgi to server the Flask application

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Docker](https://www.docker.com/community-edition). From your command line:

```
# Clone this repository
$ git clone https://github.com/peerassets/papi

# Go into the repository
$ cd papi

# Create this directory
$ mkdir -p /opt/papi/peercoin/

# Install and run
$ docker-compose up

```

## TODO list
* Scan for blockchain reorgs
  - Will remove relevant decks/cards from db and re-calculate deckstates.
* Asynchronous Tasks with Flask and Redis Queue
  - Start the server and run deck/card loading simultaneously
* Suppress `Connection refused`
  - POST requests to papi:5555/alert from walletnotify during peercoind load and before application has started.
* Card parsers for all the protocol-defined issue modes
  - PeerAssets protocol defines various issue modes, papi needs them implemented.

## Download

You can [download](https://github.com/peerassets/papi) latest installable version of papi for Linux.

## Credits

This software uses code from several open source packages.

- [Docker](https://www.docker.com/community-edition)
- [Peercoind](https://peercoin.net/)
- [Flask](http://flask.pocoo.org/)
- [Flask-Restless](https://flask-restless.readthedocs.io/en/stable/)
- [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/)

## Related

[PeerAssets](https://peerassets.github.io/WhitePaper/) - PeerAssets Whitepapaer

## Support

`Peercoin: PT2bYcAZn6pUUiFnaD7ETn71zEvATAPHWi` 

## You may also like...

- [Chizukeki](https://github.com/PeerAssets/chizukeki) - A PeerAssets Wallet
- [pypeerassets](https://github.com/PeerAssets/pypeerassets) - A Python implementation of PeerAssets

## License

MIT
