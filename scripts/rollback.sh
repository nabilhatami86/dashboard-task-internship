#!/bin/bash

# Rollback script for production
# Usage: ./scripts/rollback.sh [tag]

set -e

TAG=${1:-previous}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "⏮️  Starting rollback to tag: $TAG..."

cd "$PROJECT_DIR"

# Load environment variables
if [ -f ".env.production" ]; then
    export $(grep -v '^#' .env.production | xargs)
else
    echo "❌ Error: .env.production not found!"
    exit 1
fi

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
if [ "$TAG" != "previous" ]; then
    echo "📥 Checking out tag: $TAG..."
    git fetch --tags
    git checkout "tags/$TAG"
else
    echo "📥 Reverting to previous commit..."
    git reset --hard HEAD~1
fi

# Pull specific image tag
if [ "$TAG" != "previous" ]; then
    echo "📦 Pulling Docker images for tag: $TAG..."
    export IMAGE_TAG=$TAG
else
    echo "📦 Pulling previous Docker images..."
fi

docker-compose -f docker-compose.prod.yml pull

# Start containers
echo "🚀 Starting containers with previous version..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🏥 Checking application health..."
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Rollback successful! Application is healthy."
else
    echo "❌ Rollback may have failed. Please check logs."
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

echo "📊 Container status:"
docker-compose -f docker-compose.prod.yml ps

echo "✅ Rollback completed!"
