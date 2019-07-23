#!/bin/bash
echo "case 1: no API key"
curl -X POST -H "content-type: application/json" -d @$1 https://bprnd1eb50.execute-api.us-east-1.amazonaws.com/Prod  | jq '.'
#echo "case 2: API key in customer header"
#curl -H "X-API-KEY: 80DuE6p3EY8pqZNQrxVQx3l9NlPryGhp12aNX7oA" -X POST --data-binary @$1 https://sy1uci2mx4.execute-api.us-east-1.amazonaws.com/beta |jq '.'
