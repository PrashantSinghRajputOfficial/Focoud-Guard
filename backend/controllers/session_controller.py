"""
Session Controller - Handles study session management
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class SessionController:
    def __init__(self, session_manager, focus_service):
        self.session_manager = session_manager
        self.focus_service = focus_service
        self.sessions_file = 'data/sessions/sessions.json'
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
        
        # Create empty sessions file if it doesn't exist
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump([], f)
    
    def start_session(self, name: str, duration_minutes: int) -> Dict:
        """Start a new study session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            'id': session_id,
            'name': name,
            'duration': duration_minutes,
            'startTime': datetime.now().isoformat(),
            'endTime': None,
            'status': 'active',
            'elapsedTime': 0,
            'pausedTime': 0,
            'distractions': 0,
            'focusScore': 100,
            'completed': False
        }
        
        # Save session to file
        self._save_session(session_data)
        
        # Start session in session manager
        self.session_manager.start_session(session_id, duration_minutes)
        
        return session_data
        
        return session_data
    
    def pause_session(self, session_id: str) -> bool:
        """Pause an active session"""
        session = self._get_session(session_id)
        if not session:
            return False
        
        session['status'] = 'paused'
        self._update_session(session)
        
        # Pause in session manager
        self.session_manager.pause_session(session_id)
        
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        session = self._get_session(session_id)
        if not session:
            return False
        
        session['status'] = 'active'
        self._update_session(session)
        
        # Resume in session manager
        self.session_manager.resume_session(session_id)
        
        return True
    
    def stop_session(self, session_id: str) -> bool:
        """Stop an active session"""
        session = self._get_session(session_id)
        if not session:
            return False
        
        session['status'] = 'stopped'
        session['endTime'] = datetime.now().isoformat()
        self._update_session(session)
        
        # Stop in session manager
        self.session_manager.stop_session(session_id)
        
        return True
    
    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed"""
        session = self._get_session(session_id)
        if not session:
            return False
        
        session['status'] = 'completed'
        session['completed'] = True
        session['endTime'] = datetime.now().isoformat()
        self._update_session(session)
        
        # Complete in session manager
        self.session_manager.complete_session(session_id)
        
        return True
    
    def update_session_stats(self, session_id: str, elapsed_time: int, distractions: int, focus_score: float):
        """Update session statistics"""
        session = self._get_session(session_id)
        if not session:
            return False
        
        session['elapsedTime'] = elapsed_time
        session['distractions'] = distractions
        session['focusScore'] = focus_score
        self._update_session(session)
        
        return True
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent study sessions"""
        sessions = self._load_sessions()
        
        # Sort by start time (most recent first)
        sessions.sort(key=lambda x: x['startTime'], reverse=True)
        
        return sessions[:limit]
    
    def get_daily_stats(self, date) -> Dict:
        """Get statistics for a specific date"""
        sessions = self._load_sessions()
        
        # Filter sessions for the given date
        date_str = date.strftime('%Y-%m-%d')
        daily_sessions = [
            s for s in sessions 
            if s['startTime'].startswith(date_str)
        ]
        
        if not daily_sessions:
            return {
                'total_time': 0,
                'completed_sessions': 0,
                'focus_score': 0,
                'distractions': 0
            }
        
        # Calculate statistics
        total_time = sum(s.get('elapsedTime', 0) for s in daily_sessions) // 60  # Convert to minutes
        completed_sessions = len([s for s in daily_sessions if s.get('completed', False)])
        avg_focus_score = sum(s.get('focusScore', 0) for s in daily_sessions) // len(daily_sessions)
        total_distractions = sum(s.get('distractions', 0) for s in daily_sessions)
        
        return {
            'total_time': total_time,
            'completed_sessions': completed_sessions,
            'focus_score': avg_focus_score,
            'distractions': total_distractions
        }
    
    def _save_session(self, session_data: Dict):
        """Save a new session to file"""
        sessions = self._load_sessions()
        sessions.append(session_data)
        
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def _update_session(self, updated_session: Dict):
        """Update an existing session in file"""
        sessions = self._load_sessions()
        
        for i, session in enumerate(sessions):
            if session['id'] == updated_session['id']:
                sessions[i] = updated_session
                break
        
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def _get_session(self, session_id: str) -> Optional[Dict]:
        """Get a session by ID"""
        sessions = self._load_sessions()
        
        for session in sessions:
            if session['id'] == session_id:
                return session
        
        return None
    
    def _load_sessions(self) -> List[Dict]:
        """Load all sessions from file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []