"""
Alert Notifier - Handles alert notifications and sounds
"""

import threading
import time
import os
from typing import Dict, List, Callable
from datetime import datetime

# Try to import sound libraries
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not available - using system beep for alerts")

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

class AlertNotifier:
    def __init__(self):
        self.is_initialized = False
        self.alert_callbacks = []
        self.current_alerts = []
        self.alert_settings = {
            'sound_enabled': True,
            'visual_enabled': True,
            'volume': 70,
            'alert_frequency': 800,  # Hz
            'alert_duration': 0.5    # seconds
        }
        
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialize audio system"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.is_initialized = True
                print("Audio initialized with pygame")
                return
            except Exception as e:
                print(f"Failed to initialize pygame audio: {e}")
        
        if WINSOUND_AVAILABLE:
            self.is_initialized = True
            print("Audio initialized with winsound")
            return
        
        # Fallback to system beep
        self.is_initialized = True
        print("Using system beep for alerts")
    
    def register_callback(self, callback: Callable):
        """Register callback for alert events"""
        self.alert_callbacks.append(callback)
    
    def update_settings(self, settings: Dict):
        """Update alert settings"""
        self.alert_settings.update(settings)
    
    def trigger_distraction_alert(self, message: str = "Please return to study posture"):
        """Trigger distraction alert"""
        alert_data = {
            'type': 'distraction',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'warning'
        }
        
        self._process_alert(alert_data)
    
    def trigger_session_complete_alert(self, message: str = "Session completed successfully!"):
        """Trigger session completion alert"""
        alert_data = {
            'type': 'session_complete',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'success'
        }
        
        self._process_alert(alert_data)
    
    def trigger_break_reminder(self, message: str = "Time for a break!"):
        """Trigger break reminder alert"""
        alert_data = {
            'type': 'break_reminder',
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'info'
        }
        
        self._process_alert(alert_data)
    
    def trigger_custom_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Trigger custom alert"""
        alert_data = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': severity
        }
        
        self._process_alert(alert_data)
    
    def _process_alert(self, alert_data: Dict):
        """Process and handle alert"""
        self.current_alerts.append(alert_data)
        
        # Keep only last 10 alerts
        if len(self.current_alerts) > 10:
            self.current_alerts = self.current_alerts[-10:]
        
        # Play sound alert if enabled
        if self.alert_settings['sound_enabled']:
            self._play_alert_sound(alert_data['severity'])
        
        # Trigger visual alert through callbacks
        if self.alert_settings['visual_enabled']:
            self._trigger_visual_alert(alert_data)
        
        # Notify registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                print(f"Error in alert callback: {e}")
    
    def _play_alert_sound(self, severity: str):
        """Play alert sound based on severity"""
        if not self.is_initialized:
            return
        
        # Different frequencies for different severities
        frequency_map = {
            'info': 600,
            'warning': 800,
            'error': 1000,
            'success': 500
        }
        
        frequency = frequency_map.get(severity, 800)
        duration = self.alert_settings['alert_duration']
        
        # Play sound in separate thread to avoid blocking
        sound_thread = threading.Thread(
            target=self._play_sound,
            args=(frequency, duration),
            daemon=True
        )
        sound_thread.start()
    
    def _play_sound(self, frequency: int, duration: float):
        """Play sound with specified frequency and duration"""
        try:
            if PYGAME_AVAILABLE and pygame.mixer.get_init():
                # Generate tone using pygame
                sample_rate = 22050
                frames = int(duration * sample_rate)
                arr = []
                
                for i in range(frames):
                    wave = 4096 * (i % (sample_rate // frequency) < (sample_rate // frequency) // 2) - 2048
                    arr.append([wave, wave])
                
                sound = pygame.sndarray.make_sound(arr)
                volume = self.alert_settings['volume'] / 100.0
                sound.set_volume(volume)
                sound.play()
                
                # Wait for sound to finish
                time.sleep(duration)
                
            elif WINSOUND_AVAILABLE:
                # Use winsound for Windows
                duration_ms = int(duration * 1000)
                winsound.Beep(frequency, duration_ms)
            else:
                # Fallback to simple print (for systems without sound)
                print(f"🔔 ALERT: {frequency}Hz beep for {duration}s")
                
        except Exception as e:
            print(f"Error playing alert sound: {e}")
            # Fallback to print
            print(f"🔔 ALERT: Sound notification")
    
    def _trigger_visual_alert(self, alert_data: Dict):
        """Trigger visual alert (handled by frontend)"""
        # This will be handled by the frontend JavaScript
        # The alert data is available through get_current_alerts()
        pass
    
    def get_current_alerts(self) -> List[Dict]:
        """Get current active alerts"""
        return self.current_alerts.copy()
    
    def clear_alerts(self):
        """Clear all current alerts"""
        self.current_alerts.clear()
    
    def clear_alert_by_type(self, alert_type: str):
        """Clear alerts of specific type"""
        self.current_alerts = [
            alert for alert in self.current_alerts 
            if alert['type'] != alert_type
        ]
    
    def stop_all_sounds(self):
        """Stop all playing sounds"""
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            pygame.mixer.stop()
    
    def test_alert_system(self):
        """Test the alert system"""
        print("Testing alert system...")
        
        # Test different alert types
        self.trigger_custom_alert('test', 'Testing info alert', 'info')
        time.sleep(1)
        
        self.trigger_custom_alert('test', 'Testing warning alert', 'warning')
        time.sleep(1)
        
        self.trigger_custom_alert('test', 'Testing success alert', 'success')
        
        print("Alert system test completed")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_all_sounds()
        
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            pygame.mixer.quit()