#!/bin/bash
set -e

echo "🛑 Stopping containers..."
docker compose down

echo "🧹 Removing old images and volumes..."
docker compose down --rmi all -v --remove-orphans

echo "🚀 Rebuilding and starting..."
docker compose up --build
