#!/bin/sh
set -e
curl -X POST -d "txid=$1" "http://papi:80/alert"