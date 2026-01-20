"""
Timer Controller - Handles timer-related operations
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

class TimerController:
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    def get_session_time(self, session_id: str) -> Dict:
        """Get current session time information"""
        session_info = self.session_manager.get_session_info(session_id)
        
        if not session_info:
            return {
                'elapsed': 0,
                'remaining': 0,
                'total': 0,
                'status': 'not_found'
            }
        
        return {
            'elapsed': session_info.get('elapsed_time', 0),
            'remaining': session_info.get('remaining_time', 0),
            'total': session_info.get('total_duration', 0),
            'status': session_info.get('status', 'unknown')
        }
    
    def format_time(self, seconds: int) -> str:
        """Format seconds into HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def calculate_progress(self, elapsed: int, total: int) -> float:
        """Calculate session progress percentage"""
        if total == 0:
            return 0.0
        
        return min(100.0, (elapsed / total) * 100)
    
    def is_session_complete(self, elapsed: int, total: int) -> bool:
        """Check if session is complete"""
        return elapsed >= total
    
    def get_time_until_break(self, elapsed: int, break_interval: int = 1800) -> int:
        """Calculate time until next break (default 30 minutes)"""
        time_since_last_break = elapsed % break_interval
        return break_interval - time_since_last_break