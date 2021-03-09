#!/bin/bash

while read -r line; do
    line=$(sed -e 's/[[:space:]]*$//' <<< ${line})
    if [ -n "$line" ];then eval export "$line";fi
done <<< $(cat env_docker.txt && echo -e "\n")

docker stop ecom_auth
docker rm ecom_auth
docker image build -t ecom_auth:$APP_TAG .
docker run -d -p $API_LOCAL_IP_ADDRESS:$API_LOCAL_IP_PORT:8080 \
--restart always --log-driver=syslog --log-opt tag=ecom_auth \
-e TZ=Europe/Moscow \
-e API_LOCAL_IP_ADDRESS=$API_LOCAL_IP_ADDRESS \
-e API_LOCAL_IP_PORT=$API_LOCAL_IP_PORT \
-e WORKERS_COUNT=$WORKERS_COUNT \
-e LOGGING_LEVEL=$LOGGING_LEVEL \
-e DB_USER_NAME=$DB_USER_NAME \
-e DB_USER_PASSWORD=$DB_USER_PASSWORD \
-e DB_IP_ADDRESS=$DB_IP_ADDRESS \
-e DB_IP_PORT=$DB_IP_PORT \
-e DB_NAME=$DB_NAME \
-e DB_MIN_CONNECTIONS=$DB_MIN_CONNECTIONS \
-e DB_MAX_CONNECTIONS=$DB_MAX_CONNECTIONS \
-e AUTH_PRIVATE_KEY_FILE=$AUTH_PRIVATE_KEY_FILE \
-e API_DOMAIN=$API_DOMAIN \
-e API_PATH=$API_PATH \
--name ecom_auth ecom_auth:$APP_TAG
--network ecom-lan
