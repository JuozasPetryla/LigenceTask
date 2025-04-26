#!/usr/bin/bash

docker compose \
  -f infra/docker-compose.yml \
  -f infra/services/storage-deploy.yml \
  -f infra/services/processing-deploy.yml \
  up -d --build