# Source environment variables
source .env

docker run \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e GCP_CRED=$GCP_CRED \
    -e OPENAI_CRED=$OPENAI_CRED \
    -itd --name "$CONTAINER_NAME" -p "$CONTAINER_PORT" -v "$(pwd)/app:/app" "$IMG_NAME"
