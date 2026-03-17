#!/bin/bash

echo "Starting ATA System..."
echo ""

if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key"
    exit 1
fi

if ! grep -q "sk-proj" .env && ! grep -q "sk-[a-zA-Z0-9]" .env; then
    echo "Warning: OpenAI API key not set in .env file"
    echo "Please add your OpenAI API key to the .env file"
    exit 1
fi

echo "Building and starting Docker containers..."
docker-compose up --build

echo ""
echo "ATA System is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
