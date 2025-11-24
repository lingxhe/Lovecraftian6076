#!/bin/bash

echo "Starting FastAPI backend..."
python api_server.py &
BACKEND_PID=$!

sleep 3

echo "Starting Next.js frontend..."
cd web && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait

