#!/bin/sh
curl -X POST -d "blockhash=$1" "http://0.0.0.0:5555/alert"
echo "blockhash=$1"