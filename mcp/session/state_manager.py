"""
Session state manager for persisting and retrieving session data
"""

from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime

from .models import SessionData, SessionStore
from ..core.exceptions import SessionNotFoundError


class SessionStateManager:
    """
    Manages session state persistence and retrieval.
    Currently uses in-memory storage, but can be extended to use
    Redis, database, or file system persistence.
    """
    
    def __init__(self, persistence_type: str = "memory", config: Optional[Dict[str, Any]] = None):
        self.persistence_type = persistence_type
        self.config = config or {}
        
        # Initialize storage based on type
        if persistence_type == "memory":
            self.store = SessionStore()
        elif persistence_type == "file":
            self.store = SessionStore()
            self.file_path = config.get("file_path", "./sessions")
            os.makedirs(self.file_path, exist_ok=True)
        # Future: Add Redis, database support
        else:
            raise ValueError(f"Unknown persistence type: {persistence_type}")
    
    def create_session(self, session_id: str, case_id: str, user_id: Optional[str] = None) -> SessionData:
        """Create a new session"""
        session = self.store.create_session(session_id, case_id, user_id)
        
        if self.persistence_type == "file":
            self._save_to_file(session)
        
        return session
    
    def get_session(self, session_id: str) -> SessionData:
        """Get session data"""
        session = self.store.get_session(session_id)
        
        if not session and self.persistence_type == "file":
            # Try loading from file
            session = self._load_from_file(session_id)
            if session:
                self.store.sessions[session_id] = session
        
        if not session:
            raise SessionNotFoundError(session_id)
        
        return session
    
    def update_session(self, session_data: SessionData) -> bool:
        """Update session data"""
        session_data.update_timestamp()
        success = self.store.update_session(session_data.session_id, session_data)
        
        if success and self.persistence_type == "file":
            self._save_to_file(session_data)
        
        return success
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        success = self.store.delete_session(session_id)
        
        if success and self.persistence_type == "file":
            self._delete_file(session_id)
        
        return success
    
    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all sessions for a user"""
        return [
            session for session in self.store.sessions.values()
            if session.user_id == user_id
        ]
    
    def get_case_sessions(self, case_id: str) -> List[SessionData]:
        """Get all sessions for a case"""
        return [
            session for session in self.store.sessions.values()
            if session.case_id == case_id
        ]
    
    def cleanup_expired_sessions(self, hours: int = 24):
        """Clean up sessions older than specified hours"""
        self.store.cleanup_old_sessions(hours)
        
        if self.persistence_type == "file":
            # Clean up old files
            cutoff = datetime.utcnow()
            for filename in os.listdir(self.file_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.file_path, filename)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age = (cutoff - mtime).total_seconds() / 3600
                    if age > hours:
                        os.remove(filepath)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        total_sessions = len(self.store.sessions)
        active_sessions = len(self.store.get_active_sessions())
        
        avg_score = 0.0
        total_scored = 0
        
        for session in self.store.sessions.values():
            score = session.get_average_score()
            if score > 0:
                avg_score += score
                total_scored += 1
        
        if total_scored > 0:
            avg_score /= total_scored
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": total_sessions - active_sessions,
            "average_score": avg_score,
            "sessions_by_case": self._count_by_case(),
            "sessions_by_state": self._count_by_state()
        }
    
    # File persistence helpers
    
    def _get_session_filename(self, session_id: str) -> str:
        """Get filename for a session"""
        return os.path.join(self.file_path, f"{session_id}.json")
    
    def _save_to_file(self, session: SessionData):
        """Save session to file"""
        filename = self._get_session_filename(session.session_id)
        with open(filename, 'w') as f:
            json.dump(session.dict(), f, indent=2, default=str)
    
    def _load_from_file(self, session_id: str) -> Optional[SessionData]:
        """Load session from file"""
        filename = self._get_session_filename(session_id)
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return SessionData(**data)
        return None
    
    def _delete_file(self, session_id: str):
        """Delete session file"""
        filename = self._get_session_filename(session_id)
        if os.path.exists(filename):
            os.remove(filename)
    
    # Statistics helpers
    
    def _count_by_case(self) -> Dict[str, int]:
        """Count sessions by case ID"""
        counts = {}
        for session in self.store.sessions.values():
            case_id = session.case_id
            counts[case_id] = counts.get(case_id, 0) + 1
        return counts
    
    def _count_by_state(self) -> Dict[str, int]:
        """Count sessions by state"""
        counts = {}
        for session in self.store.sessions.values():
            state = session.state.value
            counts[state] = counts.get(state, 0) + 1
        return counts