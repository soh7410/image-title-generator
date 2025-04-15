#!/bin/bash

# Stop and remove Docker containers
echo "Stopping and removing containers..."
docker-compose down

# Rebuild Docker images with no cache
echo "Rebuilding images with no cache..."
docker-compose build --no-cache

# Start containers
echo "Starting containers..."
docker-compose up -d

# View logs (press Ctrl+C to exit)
echo "Viewing logs (press Ctrl+C to exit):"
docker-compose logs -f
