#!/bin/sh
curl -X POST -d "txid=$1" "http://0.0.0.0:5555/alert"