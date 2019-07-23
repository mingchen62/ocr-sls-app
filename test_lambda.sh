#!/bin/bash

aws lambda invoke  --invocation-type RequestResponse  --function-name $1   --region us-east-1  --payload file://eventdata.json outfile

