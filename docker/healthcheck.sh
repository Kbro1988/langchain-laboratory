#!/bin/bash

# Check if FQDN is provided as an argument
if [ -z "$1" ]; then
  echo -e "Missing argument: Please add FQDN as an argument."
  exit 1
fi

FQDN=$1

test_chroma() {
    local RESPONSE=$(curl -s -o /dev/null -I -w "%{http_code}\n" -X GET http://chroma_db:8000/api/v1/heartbeat)
    exit_code="$?"
    response_code="$RESPONSE"

}

test_weaviate() {
    local RESPONSE=$(curl -s -o /dev/null -I -w "%{http_code}\n" -X GET http://weaviate:8080/v1/.well-known/live)
    exit_code="$?"
    response_code="$RESPONSE"

}

echo -e "<<----HEALTHCECK START------------------------------------------------->>"
exit_code=""
response_code=""
test_chroma
if [ "$response_code" !=  "200" ]; then
     echo -e "  Chroma Heartbeat failed with RESPONSE CODE:\t$response_code"
     echo -e "\tExit Code 1."
     echo -e "<<----HEALTHCECK FAILED!------------------------------------------------>>"
     exit 1
else
     echo -e "  Chroma Heartbeat completed with RESPONSE CODE:\t$response_code"

fi
echo -e  "<<--------------------------------------------------------------------->>"
exit_code=""
response_code=""
test_weaviate
if [ "$response_code" !=  "200" ]; then
     echo -e "  Weaviate Ready Check failed with RESPONSE CODE:\t$response_code"
     echo -e "\tExit Code 1."
     echo -e "<<----HEALTHCECK FAILED!------------------------------------------------>>"
     exit 1
else
     echo -e "  Weaviate Ready Check completed with exit code:\t$response_code"
fi
echo -e "<<--------------------------------------------------------------------->>"
nslookup $1 > /dev/null
if [ $? != 0 ]; then
     echo -e "  DNS LOOKUP FAILED CHECK DNS AND FQDN -> $FQDN."
     echo -e "\tExit code 1."
     echo -e "<<----HEALTHCECK FAILED!----------------------------------------------->>"
     exit 1
else
     echo -e "  FQDN: $FQDN. Resolved Successfully!" 
fi
echo -e "<<----HEALTHCECK COMPLETED--------------------------------------------->>"
