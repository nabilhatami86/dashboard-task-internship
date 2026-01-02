#!/bin/bash

# Deploy script for production
# Usage: ./scripts/deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting deployment to $ENVIRONMENT..."

cd "$PROJECT_DIR"

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "📝 Loading .env.$ENVIRONMENT..."
    export $(grep -v '^#' .env.$ENVIRONMENT | xargs)
else
    echo "❌ Error: .env.$ENVIRONMENT not found!"
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Start containers
echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo "🏥 Checking application health..."
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "⚠️  Backend health check failed, but continuing..."
fi

if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is healthy!"
else
    echo "⚠️  Frontend health check failed, but continuing..."
fi

# Show status
echo "📊 Container status:"
docker-compose -f docker-compose.prod.yml ps

# Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Deployment to $ENVIRONMENT completed successfully!"
echo ""
echo "📝 View logs with: docker-compose -f docker-compose.prod.yml logs -f"
echo "🔍 Check status with: docker-compose -f docker-compose.prod.yml ps"
