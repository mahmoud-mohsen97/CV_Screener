#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Source environment variables
source .env

# Check for required API key
if [ -z "$PORTKEY_API_KEY" ]; then
    echo "Error: PORTKEY_API_KEY not set in .env file!"
    exit 1
fi

# Create results directory if it doesn't exist
mkdir -p results

# Build and start services
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo "📱 Frontend: http://localhost:7445"
    echo "🔧 Backend API: http://localhost:7444"
    echo "📚 API Docs: http://localhost:7444/docs"
else
    echo "❌ Error: Services failed to start properly"
    docker-compose logs
    exit 1
fi 