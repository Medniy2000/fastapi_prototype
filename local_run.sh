#!/bin/sh
set -euo pipefail

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
. ./.env.example           # or 'source .env' in bash
cp .env.example .env       # create local .env file if it doesn't exist

INPUT_ENV_FILE=".env"
OUTPUT_ENV_FILE=".env_docker"

# ----------------------------------------------------------------------
# Generate .env_docker for Docker containers
# ----------------------------------------------------------------------
SEARCH="127.0.0.1"
REPLACE="172.17.0.1"

# Create or overwrite output file
> "$OUTPUT_ENV_FILE"

# Read .env line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Preserve empty lines and comments
    if [[ -z "$line" || "$line" =~ ^# ]]; then
        echo "$line" >> "$OUTPUT_ENV_FILE"
        continue
    fi

    # Split key and value
    key="${line%%=*}"
    value="${line#*=}"

    # Replace specified substring in the value
    new_value="${value//$SEARCH/$REPLACE}"

    # Write updated line to output file
    echo "$key=$new_value" >> "$OUTPUT_ENV_FILE"
done < "$INPUT_ENV_FILE"


. ./$OUTPUT_ENV_FILE  # or 'source .env_docker' in bash

# ----------------------------------------------------------------------
# Docker configuration
# ----------------------------------------------------------------------
DOCKER_PREFIX="local"
RECREATE=false
RUN_API=false

# Parse script arguments
while [ "$#" -gt 0 ]; do
    case $1 in
        --recreate) RECREATE=true ;;
        --run_api)  RUN_API=true ;;
    esac
    shift
done

# ----------------------------------------------------------------------
# Recreate containers and images if requested
# ----------------------------------------------------------------------
if [ "$RECREATE" = true ]; then
    # Remove old containers
    docker ps -a --filter "name=${DOCKER_PREFIX}*" --format "{{.ID}}" | xargs -r docker rm -f

    # Remove old images
    docker rmi celery_img
    docker rmi consume_img
    docker rmi api_img

    echo "  🗑️  Removed old containers and images"

    # Build new images
    docker build -t celery_img --no-cache -f .launch/celery/Dockerfile .
    echo "  🏗️  Built celery_img image"

    docker build -t consume_img --no-cache -f .launch/consume/Dockerfile .
    echo "  🏗️  Built consume_img image"

    if [ "$RUN_API" = true ]; then
        docker build -t api_img --no-cache -f .launch/api/Dockerfile .
        echo "  🏗️  Built api_img image"
    fi
fi

# ----------------------------------------------------------------------
# Run Docker containers
# ----------------------------------------------------------------------
# Celery container
if [ ! "$(docker ps -aq -f name=${DOCKER_PREFIX}_celery)" ]; then
    docker run -d \
        --name "${DOCKER_PREFIX}_celery" \
        --env-file ./.env_docker \
        --shm-size="512m" \
        --cpus=2 \
        -e CELERY_ARGS="worker -l INFO -E -B -Q default_queue --concurrency=2 -n default@%h" \
        celery_img || true

    docker run -d --name "${DOCKER_PREFIX}_flower" \
        -e broker_url=$CELERY_BROKER_URL \
        -e CELERY_BROKER_URL=$CELERY_BROKER_URL \
        -e CELERY_BROKER_API=$CELERY_RESULT_BACKEND \
        -p 5555:5555 mher/flower
fi
echo "  ✅ ${DOCKER_PREFIX}_celery UP"
echo "  ✅ ${DOCKER_PREFIX}_flower UP"

# Consume container
if [ ! "$(docker ps -aq -f name=${DOCKER_PREFIX}_consume)" ]; then
    docker run -d \
        --name "${DOCKER_PREFIX}_consume" \
        --env-file ./.env_docker \
        --shm-size="512m" \
        --cpus=1 \
        consume_img || true
fi
echo "  ✅ ${DOCKER_PREFIX}_consume UP"

# API container (optional)
if [ -z "$(docker ps -aq -f name=${DOCKER_PREFIX}_api)" ] && [ "$RUN_API" = true ]; then
    docker run -d \
        --name "${DOCKER_PREFIX}_api" \
        --env-file ./.env_docker \
        --shm-size="1g" \
        --cpus=1 \
        -p 8081:8081 \
        api_img || true
fi
if [ "$RUN_API" = true ]; then
echo "  ✅ ${DOCKER_PREFIX}_api UP"
fi


# ----------------------------------------------------------------------
# Print results
# ----------------------------------------------------------------------
echo ""
echo "-----------------------------------------------------------------"
if [ "$RUN_API" = true ]; then
echo "   💎  http://0.0.0.0:8081/docs  - API"
fi
echo "   ⚙️  http://0.0.0.0:5555       - Flower[celery monitoring]"
echo "----------------------------------------------------------------"
