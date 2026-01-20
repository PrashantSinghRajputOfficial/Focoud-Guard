"""
Session Manager - Core session management functionality
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
import uuid

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_callbacks = {}
        self._lock = threading.Lock()
    
    def start_session(self, session_id: str, duration_minutes: int) -> bool:
        """Start a new session"""
        with self._lock:
            if session_id in self.active_sessions:
                return False
            
            session_data = {
                'id': session_id,
                'start_time': datetime.now(),
                'duration': duration_minutes * 60,  # Convert to seconds
                'elapsed_time': 0,
                'status': 'active',
                'paused_time': 0,
                'last_update': datetime.now()
            }
            
            self.active_sessions[session_id] = session_data
            
            # Start session timer thread
            timer_thread = threading.Thread(
                target=self._session_timer,
                args=(session_id,),
                daemon=True
            )
            timer_thread.start()
            
            return True
    
    def pause_session(self, session_id: str) -> bool:
        """Pause an active session"""
        with self._lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            if session['status'] != 'active':
                return False
            
            session['status'] = 'paused'
            session['last_update'] = datetime.now()
            
            return True
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        with self._lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            if session['status'] != 'paused':
                return False
            
            session['status'] = 'active'
            session['last_update'] = datetime.now()
            
            return True
    
    def stop_session(self, session_id: str) -> bool:
        """Stop an active session"""
        with self._lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session['status'] = 'stopped'
            session['end_time'] = datetime.now()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return True
    
    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed"""
        with self._lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session['status'] = 'completed'
            session['end_time'] = datetime.now()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        with self._lock:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id].copy()
            
            # Calculate current elapsed time
            if session['status'] == 'active':
                current_time = datetime.now()
                time_diff = (current_time - session['last_update']).total_seconds()
                session['elapsed_time'] += int(time_diff)
                session['last_update'] = current_time
            
            # Calculate remaining time
            remaining_time = max(0, session['duration'] - session['elapsed_time'])
            session['remaining_time'] = remaining_time
            session['total_duration'] = session['duration']
            
            return session
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if session is active"""
        with self._lock:
            return (session_id in self.active_sessions and 
                   self.active_sessions[session_id]['status'] == 'active')
    
    def get_active_sessions(self) -> Dict:
        """Get all active sessions"""
        with self._lock:
            return self.active_sessions.copy()
    
    def register_callback(self, session_id: str, callback: Callable):
        """Register callback for session events"""
        self.session_callbacks[session_id] = callback
    
    def _session_timer(self, session_id: str):
        """Background timer for session"""
        while session_id in self.active_sessions:
            time.sleep(1)  # Update every second
            
            with self._lock:
                if session_id not in self.active_sessions:
                    break
                
                session = self.active_sessions[session_id]
                
                if session['status'] == 'active':
                    session['elapsed_time'] += 1
                    
                    # Check if session is complete
                    if session['elapsed_time'] >= session['duration']:
                        session['status'] = 'completed'
                        session['end_time'] = datetime.now()
                        
                        # Call callback if registered
                        if session_id in self.session_callbacks:
                            try:
                                self.session_callbacks[session_id]('completed', session)
                            except Exception as e:
                                print(f"Error in session callback: {e}")
                        
                        # Remove from active sessions
                        del self.active_sessions[session_id]
                        break