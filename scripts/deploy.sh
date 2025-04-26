#!/usr/bin/bash

docker compose \
  -f infrastructure/docker-compose.yml \
  -f infrastructure/services/storage-deploy.yml \
  -f infrastructure/services/processing-deploy.yml \
  -f infrastructure/services/validation-deploy.yml \
  -f infrastructure/docker-compose.override.yml \
  up -d --build