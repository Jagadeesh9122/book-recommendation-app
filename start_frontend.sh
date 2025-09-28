#!/bin/bash

echo "Starting Book Recommendation System Frontend"
echo "============================================"

cd frontend

echo "Installing frontend dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo "Starting React development server..."
npm start
