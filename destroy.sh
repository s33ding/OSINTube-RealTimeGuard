source .env

docker rm -f $CONTAINER_NAME
docker rmi $IMG_NAME
