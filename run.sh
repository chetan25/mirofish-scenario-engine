#!/bin/bash

# Side Hustle Simulator - Quick Start
# Usage: bash run.sh [dev|prod]

set -e

MODE=${1:-dev}
echo "🚀 Starting Side Hustle Simulator in $MODE mode..."

if [ "$MODE" = "prod" ]; then
    echo "📦 Building Docker images..."
    docker-compose build
    
    echo "🐳 Starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Services running!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend: http://localhost:5001"
    echo "   API: http://localhost:5001/health"
    
elif [ "$MODE" = "dev" ]; then
    echo "📂 Development mode"
    
    # Check if backend is running
    if ! curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo "⚠️  Backend not running. Starting..."
        cd /tmp/MiroFish/backend
        source venv/bin/activate
        python simulator_api.py &
        sleep 3
    fi
    
    # Check if frontend is running
    if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "⚠️  Frontend not running. Starting..."
        cd /root/side-hustle-simulator
        python -m http.server 3000 &
        sleep 2
    fi
    
    echo "✅ Services running!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend: http://localhost:5001"
    
else
    echo "Usage: bash run.sh [dev|prod]"
    exit 1
fi

echo ""
echo "📖 Open http://localhost:3000 in your browser"
