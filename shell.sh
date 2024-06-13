source .env

docker start $CONTAINER_NAME 
docker exec -it $CONTAINER_NAME bash 
