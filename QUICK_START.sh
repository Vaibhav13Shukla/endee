#!/bin/bash
# Quick Start Commands - The Monk AI Full System
# Run these commands in order to start the entire application

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          THE MONK AI - QUICK START COMMANDS                   ║"
echo "║            Complete System Startup Script                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"

PROJECT_DIR="/home/vishal/endee/the_monk_ai"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Step 1: Verify System Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$PROJECT_DIR"
.venv/bin/python3 system_check.py | tail -15

echo -e "\n${BLUE}Step 2: Set GROQ API Key (Required)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}ACTION REQUIRED:${NC}"
echo "Get your API key from: https://console.groq.com/keys"
echo ""
echo "Option A - Add to .env file:"
echo "  echo 'GROQ_API_KEY=gsk_your_api_key_here' >> .env"
echo ""
echo "Option B - Export as environment variable:"
echo "  export GROQ_API_KEY=gsk_your_api_key_here"
echo ""
echo -e "${YELLOW}After setting GROQ_API_KEY, continue:${NC}"

echo -e "\n${BLUE}Step 3: Verify Endee Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Ensure Endee is running:"
echo "  cd endee/"
echo "  docker-compose up -d"
echo ""
echo "Check status:"
curl -s http://localhost:8080/health >/dev/null 2>&1 && echo "✓ Endee server is running" || echo "✗ Endee server not running"

echo -e "\n${BLUE}Step 4: Load Knowledge Base (Optional)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Currently indexed: 3 documents"
echo "Want to add more scripture data?"
echo "  python knowledge_base_loader.py"

echo -e "\n${BLUE}Step 5: Start Backend Server${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "In Terminal 1, run:"
echo "  cd $PROJECT_DIR"
echo "  source .venv/bin/activate"  
echo "  python main.py"
echo ""
echo "Server will start on: http://localhost:8000"

echo -e "\n${BLUE}Step 6: Start Frontend (In New Terminal)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "In Terminal 2, run:"
echo "  cd $PROJECT_DIR"
echo "  source .venv/bin/activate"
echo "  streamlit run frontend/streamlit_app.py"
echo ""
echo "Frontend will open on: http://localhost:8501"

echo -e "\n${BLUE}Step 7: Access the Application${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Open browser to: http://localhost:8501"
echo "2. Register a new account"
echo "3. Login with your credentials"
echo "4. Start asking questions about Hindu scriptures!"
echo ""
echo "Example queries:"
echo "  • What is the Bhagavad Gita?"
echo "  • Explain the concept of karma"
echo "  • What are the four Vedas?"
echo "  • Tell me about Dharma in Hinduism"

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        System Ready! Follow the steps above to start          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
