#!/usr/bin/env python3
"""
Tata Capital Agentic Loan Chatbot - Backend Runner
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("generated_docs", exist_ok=True)
    os.makedirs("session_archives", exist_ok=True)
    
    print("🚀 Starting Tata Capital Agentic Loan Chatbot Backend...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/{session_id}")
    print("🌐 Health check: http://localhost:8000/health")
    print("📄 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )