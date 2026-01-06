from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import os
from typing import Dict, Any
import uuid
from datetime import datetime

from agents.master_agent import MasterAgent
from mock_services.crm_api import CRMService
from mock_services.credit_bureau import CreditBureauService
from utils.session_manager import SessionManager

app = FastAPI(title="Tata Capital Agentic Loan Chatbot")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
crm_service = CRMService()
credit_service = CreditBureauService()
session_manager = SessionManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    # Initialize master agent for this session
    master_agent = MasterAgent(
        session_id=session_id,
        crm_service=crm_service,
        credit_service=credit_service,
        session_manager=session_manager
    )
    
    try:
        # Send welcome message
        welcome_response = await master_agent.start_conversation()
        
        # Handle both old string format and new dict format
        if isinstance(welcome_response, dict):
            await manager.send_message(session_id, {
                "type": "message",
                "content": welcome_response["content"],
                "sender": "bot",
                "timestamp": datetime.now().isoformat(),
                "metadata": welcome_response.get("metadata", {}),
                "suggestions": welcome_response.get("suggestions", [])
            })
        else:
            # Backward compatibility for string responses
            await manager.send_message(session_id, {
                "type": "message",
                "content": welcome_response,
                "sender": "bot",
                "timestamp": datetime.now().isoformat()
            })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through master agent
            response = await master_agent.process_message(message_data["content"])
            
            # Send response back - handle both dict and string responses
            if isinstance(response, dict):
                await manager.send_message(session_id, {
                    "type": "message",
                    "content": response["content"],
                    "sender": "bot",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": response.get("metadata", {}),
                    "suggestions": response.get("suggestions", [])
                })
            else:
                # Backward compatibility for string responses
                await manager.send_message(session_id, {
                    "type": "message",
                    "content": response,
                    "sender": "bot",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        session_manager.end_session(session_id)

@app.post("/upload-salary-slip/{session_id}")
async def upload_salary_slip(session_id: str, file: UploadFile = File(...)):
    """Handle salary slip upload for loan verification"""
    try:
        # Save file temporarily
        file_path = f"temp/{session_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process through master agent
        master_agent = MasterAgent(
            session_id=session_id,
            crm_service=crm_service,
            credit_service=credit_service,
            session_manager=session_manager
        )
        
        result = await master_agent.process_salary_slip(file_path)
        
        return {"status": "success", "message": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated sanction letter"""
    file_path = f"generated_docs/{filename}"
    
    if os.path.exists(file_path):
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
    else:
        return {"error": "File not found"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Tata Capital Agentic Chatbot"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)