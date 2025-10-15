#!/bin/bash

# Trading Data Aggregator - Startup Script

echo "======================================"
echo "  Trading Data Aggregator"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠ Virtual environment not found. Run install first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ Created .env file. Please add your API keys if needed."
    echo ""
fi

# Start the server
echo "🚀 Starting server..."
echo "📊 Open http://localhost:8000 in your browser"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
