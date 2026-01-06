from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=2)  # 2 hour timeout
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new session"""
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "conversation_state": "greeting",
            "user_context": {},
            "conversation_history": [],
            "agent_states": {
                "master": {},
                "sales": {},
                "verification": {},
                "underwriting": {},
                "sanction": {}
            }
        }
        
        self.sessions[session_id] = session_data
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Check if session has expired
            if datetime.now() - session["last_activity"] > self.session_timeout:
                self.end_session(session_id)
                return None
            
            # Update last activity
            session["last_activity"] = datetime.now()
            return session
        
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add message to conversation history"""
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update user context"""
        if session_id in self.sessions:
            self.sessions[session_id]["user_context"].update(context_updates)
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def update_conversation_state(self, session_id: str, new_state: str) -> bool:
        """Update conversation state"""
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_state"] = new_state
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def update_agent_state(self, session_id: str, agent_name: str, agent_state: Dict[str, Any]) -> bool:
        """Update specific agent state"""
        if session_id in self.sessions:
            self.sessions[session_id]["agent_states"][agent_name] = agent_state
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> list:
        """Get conversation history"""
        if session_id in self.sessions:
            history = self.sessions[session_id]["conversation_history"]
            return history[-limit:] if limit else history
        return []
    
    def end_session(self, session_id: str) -> bool:
        """End and cleanup session"""
        if session_id in self.sessions:
            # Log session end
            session = self.sessions[session_id]
            session["ended_at"] = datetime.now()
            
            # Archive session (in production, save to database)
            self._archive_session(session)
            
            # Remove from active sessions
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            return {
                "session_id": session_id,
                "duration": str(datetime.now() - session["created_at"]),
                "message_count": len(session["conversation_history"]),
                "current_state": session["conversation_state"],
                "last_activity": session["last_activity"].isoformat()
            }
        return {}
    
    def _archive_session(self, session: Dict[str, Any]):
        """Archive completed session (mock implementation)"""
        # In production, this would save to database
        archive_data = {
            "session_id": session["session_id"],
            "created_at": session["created_at"].isoformat(),
            "ended_at": session.get("ended_at", datetime.now()).isoformat(),
            "final_state": session["conversation_state"],
            "message_count": len(session["conversation_history"]),
            "user_context": session["user_context"]
        }
        
        # Mock: Save to file (in production use proper database)
        try:
            with open(f"session_archives/{session['session_id']}.json", "w") as f:
                json.dump(archive_data, f, indent=2)
        except:
            pass  # Ignore file errors in demo