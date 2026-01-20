"""
Focus Service - Handles focus tracking and analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

class FocusService:
    def __init__(self):
        self.focus_data_file = 'data/focus_data.json'
        self.ensure_data_file()
        self.current_focus_score = 100.0
        self.distraction_count = 0
        self.focus_history = []
    
    def ensure_data_file(self):
        """Ensure focus data file exists"""
        os.makedirs(os.path.dirname(self.focus_data_file), exist_ok=True)
        
        if not os.path.exists(self.focus_data_file):
            with open(self.focus_data_file, 'w') as f:
                json.dump({
                    'sessions': [],
                    'daily_stats': {}
                }, f)
    
    def update_focus_status(self, is_focused: bool, attention_level: float = 0.0):
        """Update current focus status"""
        timestamp = datetime.now()
        
        focus_entry = {
            'timestamp': timestamp.isoformat(),
            'is_focused': is_focused,
            'attention_level': attention_level
        }
        
        self.focus_history.append(focus_entry)
        
        # Update focus score based on current status
        if is_focused:
            # Gradually improve focus score when focused
            self.current_focus_score = min(100.0, self.current_focus_score + 0.5)
        else:
            # Decrease focus score when distracted
            self.current_focus_score = max(0.0, self.current_focus_score - 2.0)
            self.distraction_count += 1
        
        # Keep only last 100 entries to manage memory
        if len(self.focus_history) > 100:
            self.focus_history = self.focus_history[-100:]
    
    def get_current_focus_score(self) -> float:
        """Get current focus score (0-100)"""
        return self.current_focus_score
    
    def get_distraction_count(self) -> int:
        """Get current distraction count"""
        return self.distraction_count
    
    def calculate_session_focus_score(self, session_duration: int) -> float:
        """Calculate overall focus score for a session"""
        if not self.focus_history:
            return 100.0
        
        # Calculate based on focus history
        focused_time = sum(1 for entry in self.focus_history if entry['is_focused'])
        total_entries = len(self.focus_history)
        
        if total_entries == 0:
            return 100.0
        
        focus_percentage = (focused_time / total_entries) * 100
        
        # Apply penalty for distractions
        distraction_penalty = min(20.0, self.distraction_count * 2.0)
        
        final_score = max(0.0, focus_percentage - distraction_penalty)
        
        return round(final_score, 1)
    
    def get_focus_trends(self, hours: int = 24) -> Dict:
        """Get focus trends for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_history = [
            entry for entry in self.focus_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_history:
            return {
                'average_focus': 0.0,
                'focus_periods': 0,
                'distraction_periods': 0,
                'trend': 'stable'
            }
        
        focused_periods = sum(1 for entry in recent_history if entry['is_focused'])
        distracted_periods = len(recent_history) - focused_periods
        average_focus = (focused_periods / len(recent_history)) * 100
        
        # Determine trend (simplified)
        if len(recent_history) >= 10:
            recent_focus = sum(1 for entry in recent_history[-10:] if entry['is_focused']) / 10
            earlier_focus = sum(1 for entry in recent_history[:10] if entry['is_focused']) / 10
            
            if recent_focus > earlier_focus + 0.1:
                trend = 'improving'
            elif recent_focus < earlier_focus - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'average_focus': round(average_focus, 1),
            'focus_periods': focused_periods,
            'distraction_periods': distracted_periods,
            'trend': trend
        }
    
    def reset_session_data(self):
        """Reset data for a new session"""
        self.current_focus_score = 100.0
        self.distraction_count = 0
        self.focus_history = []
    
    def save_session_data(self, session_id: str):
        """Save current session focus data"""
        try:
            with open(self.focus_data_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {'sessions': [], 'daily_stats': {}}
        
        session_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'final_focus_score': self.current_focus_score,
            'distraction_count': self.distraction_count,
            'focus_history': self.focus_history.copy()
        }
        
        data['sessions'].append(session_data)
        
        # Keep only last 50 sessions
        if len(data['sessions']) > 50:
            data['sessions'] = data['sessions'][-50:]
        
        with open(self.focus_data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_recommendations(self) -> List[str]:
        """Get focus improvement recommendations"""
        recommendations = []
        
        if self.current_focus_score < 70:
            recommendations.append("Consider taking a short break to refresh your mind")
            recommendations.append("Ensure your study environment is free from distractions")
        
        if self.distraction_count > 5:
            recommendations.append("Try the Pomodoro technique: 25 minutes focused study, 5 minute break")
            recommendations.append("Put your phone in another room or use focus apps")
        
        if self.current_focus_score > 90:
            recommendations.append("Great focus! Keep up the excellent work")
            recommendations.append("Consider extending your study session if you feel energized")
        
        return recommendations