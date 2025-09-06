#!/bin/sh

# Load environment variables
. ./.env.example   # or 'source .env' in bash

# Config
REDIS_PORT=6380
MESSAGE_BROKER_USER="dev"
MESSAGE_BROKER_PASSWORD="dev"
MESSAGE_BROKER_PORT=5672

RECREATE=false

# Parse arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --recreate) RECREATE=true ;;
  esac
  shift
done

echo "🥁 Infrastructure preparing..."

# Remove old containers if requested
if [ "$RECREATE" = true ]; then
  docker ps -a --filter "name=${PROJECT_NAME_SLUG}*" --format "{{.ID}}" | xargs -r docker rm -f
  echo "  🗑️  removed old"
fi

# Redis
if [ ! "$(docker ps -aq -f name=${PROJECT_NAME_SLUG}_redis)" ]; then
  docker run -d --name "${PROJECT_NAME_SLUG}_redis" \
    -p $REDIS_PORT:6379 \
    redis:latest || true
fi
echo "  ✅ ${PROJECT_NAME_SLUG}_redis UP"

# RabbitMQ
if [ ! "$(docker ps -aq -f name=${PROJECT_NAME_SLUG}_rabbitmq)" ]; then
  docker run -d --name "${PROJECT_NAME_SLUG}_rabbitmq" \
    -p 15672:15672 \
    -p $MESSAGE_BROKER_PORT:5672 \
    -e RABBITMQ_DEFAULT_USER=$MESSAGE_BROKER_USER \
    -e RABBITMQ_DEFAULT_PASS=$MESSAGE_BROKER_PASSWORD \
    rabbitmq:3.11.6-management || true
fi
echo "  ✅ ${PROJECT_NAME_SLUG}_rabbitmq UP"

# Postgres
if [ ! "$(docker ps -aq -f name=${PROJECT_NAME_SLUG}_postgres)" ]; then
  docker run -d --name "${PROJECT_NAME_SLUG}_postgres" \
    -e POSTGRES_DB=$DB_NAME \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -p $DB_PORT:5432 \
    postgres:latest || true
fi
echo "  ✅ ${PROJECT_NAME_SLUG}_postgres UP"

echo "✅ Infrastructure UP"
