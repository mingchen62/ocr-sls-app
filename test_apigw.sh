#!/bin/bash
#echo "API key in customer header"
curl -X POST -H "content-type: application/json, X-API-KEY: PNhuKQCO7a1cMsP3stp8EuhaxaNrhtK61UnFS51j" -d @$1 https://4gshff13u2.execute-api.us-east-1.amazonaws.com/Prod  | jq '.'
