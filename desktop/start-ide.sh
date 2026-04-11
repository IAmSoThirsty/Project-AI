#!/bin/bash
# Enhanced Cognitive IDE Launcher
# Starts all required services

echo "======================================"
echo "Enhanced Cognitive IDE Launcher"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $COLLAB_PID 2>/dev/null
    kill $API_PID 2>/dev/null
    kill $DEV_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Start collaboration server
echo -e "${YELLOW}🚀 Starting collaboration server...${NC}"
node collaboration-server.js &
COLLAB_PID=$!
echo -e "${GREEN}✅ Collaboration server started (PID: $COLLAB_PID)${NC}"
sleep 2

# Start API server
echo -e "${YELLOW}🚀 Starting API server...${NC}"
python3 api_server.py &
API_PID=$!
echo -e "${GREEN}✅ API server started (PID: $API_PID)${NC}"
sleep 2

# Start development server
echo -e "${YELLOW}🚀 Starting development server...${NC}"
npm run dev &
DEV_PID=$!
echo -e "${GREEN}✅ Development server started (PID: $DEV_PID)${NC}"
sleep 3

echo ""
echo "======================================"
echo -e "${GREEN}✨ Enhanced Cognitive IDE is running!${NC}"
echo "======================================"
echo ""
echo "Services:"
echo "  - Vite Dev Server:    http://localhost:5173"
echo "  - API Server:         http://localhost:8000"
echo "  - Collaboration:      ws://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait
