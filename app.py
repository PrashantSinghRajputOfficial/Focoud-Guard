"""
FocusGuard - Vision-Based Study Time Enforcement System
Main Flask Application
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime, timedelta
import json
import os
import logging
from threading import Thread

# Import our custom modules (with error handling)
try:
    from timer_engine.session_manager import SessionManager
    from backend.services.focus_service import FocusService
    from backend.controllers.session_controller import SessionController
    from backend.controllers.timer_controller import TimerController
except ImportError as e:
    print(f"Import error: {e}")

# Optional imports (camera and alerts)
try:
    from vision_engine.camera import CameraManager
    CAMERA_AVAILABLE = True
except ImportError:
    print("Camera module not available - running without vision features")
    CAMERA_AVAILABLE = False
    
try:
    from alert_engine.notifier import AlertNotifier
    ALERTS_AVAILABLE = True
except ImportError:
    print("Alert module not available - running without sound alerts")
    ALERTS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           static_folder='frontend',
           template_folder='frontend')

# Initialize core components
session_manager = SessionManager()
focus_service = FocusService()

# Initialize optional components
if CAMERA_AVAILABLE:
    camera_manager = CameraManager()
else:
    camera_manager = None

if ALERTS_AVAILABLE:
    alert_notifier = AlertNotifier()
else:
    alert_notifier = None

# Initialize controllers
session_controller = SessionController(session_manager, focus_service)
timer_controller = TimerController(session_manager)

# Global state
current_session = None
vision_status = {
    'camera': False,
    'faceDetected': False,
    'studyPosture': False,
    'attentionLevel': 0.0
}

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Alternative route for dashboard"""
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/camera')
def camera_test():
    """Serve camera test page"""
    return send_from_directory('.', 'camera_test.html')

@app.route('/simple')
def simple_dashboard():
    """Serve simple dashboard"""
    return send_from_directory('.', 'simple_dashboard.html')

@app.route('/test')
def test():
    """Serve test page"""
    return send_from_directory('.', 'test.html')

@app.route('/dashboard')
def dashboard():
    """Alternative route for dashboard"""
    return send_from_directory('frontend', 'dashboard.html')

# Static file serving
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('frontend/js', filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('frontend/images', filename)

# API Routes for Session Management
@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new study session"""
    global current_session
    
    try:
        data = request.get_json()
        duration = data.get('duration', 120)  # Default 2 hours
        name = data.get('name', 'Study Session')
        
        # Start session using controller
        session_data = session_controller.start_session(name, duration)
        current_session = session_data
        
        # Start vision monitoring
        start_vision_monitoring()
        
        logger.info(f"Started session: {name} for {duration} minutes")
        
        return jsonify({
            'success': True,
            'session': session_data,
            'message': 'Session started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/pause', methods=['POST'])
def pause_session():
    """Pause the current session"""
    global current_session
    
    try:
        if current_session:
            session_controller.pause_session(current_session['id'])
            logger.info("Session paused")
            
            return jsonify({
                'success': True,
                'message': 'Session paused'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
            
    except Exception as e:
        logger.error(f"Error pausing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/resume', methods=['POST'])
def resume_session():
    """Resume the paused session"""
    global current_session
    
    try:
        if current_session:
            session_controller.resume_session(current_session['id'])
            logger.info("Session resumed")
            
            return jsonify({
                'success': True,
                'message': 'Session resumed'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
            
    except Exception as e:
        logger.error(f"Error resuming session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop the current session"""
    global current_session
    
    try:
        if current_session:
            session_controller.stop_session(current_session['id'])
            current_session = None
            
            # Stop vision monitoring
            stop_vision_monitoring()
            
            logger.info("Session stopped")
            
            return jsonify({
                'success': True,
                'message': 'Session stopped'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
            
    except Exception as e:
        logger.error(f"Error stopping session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/complete', methods=['POST'])
def complete_session():
    """Mark session as completed"""
    global current_session
    
    try:
        if current_session:
            session_controller.complete_session(current_session['id'])
            current_session = None
            
            # Stop vision monitoring
            stop_vision_monitoring()
            
            logger.info("Session completed successfully")
            
            return jsonify({
                'success': True,
                'message': 'Session completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
            
    except Exception as e:
        logger.error(f"Error completing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API Routes for Vision Monitoring
@app.route('/api/vision/status', methods=['GET'])
def get_vision_status():
    """Get current vision monitoring status"""
    global vision_status
    
    try:
        # Update vision status from camera manager
        if CAMERA_AVAILABLE and camera_manager and camera_manager.is_active():
            vision_data = camera_manager.get_current_status()
            vision_status.update(vision_data)
        else:
            # Mock data when camera is not available
            vision_status = {
                'camera': False,
                'faceDetected': False,
                'studyPosture': True,  # Assume good posture for demo
                'attentionLevel': 0.8
            }
        
        return jsonify(vision_status)
        
    except Exception as e:
        logger.error(f"Error getting vision status: {str(e)}")
        return jsonify({
            'camera': False,
            'faceDetected': False,
            'studyPosture': False,
            'attentionLevel': 0.0,
            'error': str(e)
        })

# API Routes for Statistics
@app.route('/api/stats/today', methods=['GET'])
def get_today_stats():
    """Get today's study statistics"""
    try:
        today = datetime.now().date()
        stats = session_controller.get_daily_stats(today)
        
        return jsonify({
            'totalStudyTime': stats.get('total_time', 0),
            'sessionsCompleted': stats.get('completed_sessions', 0),
            'focusScore': stats.get('focus_score', 0),
            'distractions': stats.get('distractions', 0)
        })
        
    except Exception as e:
        logger.error(f"Error getting today stats: {str(e)}")
        return jsonify({
            'totalStudyTime': 0,
            'sessionsCompleted': 0,
            'focusScore': 0,
            'distractions': 0,
            'error': str(e)
        })

@app.route('/api/sessions/recent', methods=['GET'])
def get_recent_sessions():
    """Get recent study sessions"""
    try:
        sessions = session_controller.get_recent_sessions(limit=10)
        
        return jsonify(sessions)
        
    except Exception as e:
        logger.error(f"Error getting recent sessions: {str(e)}")
        return jsonify([])

# Vision monitoring functions
def start_vision_monitoring():
    """Start vision monitoring in background thread"""
    def monitor():
        try:
            if CAMERA_AVAILABLE and camera_manager:
                camera_manager.start()
                logger.info("Vision monitoring started")
            else:
                logger.info("Vision monitoring not available - running in demo mode")
        except Exception as e:
            logger.error(f"Error starting vision monitoring: {str(e)}")
    
    monitor_thread = Thread(target=monitor, daemon=True)
    monitor_thread.start()

def stop_vision_monitoring():
    """Stop vision monitoring"""
    try:
        if CAMERA_AVAILABLE and camera_manager:
            camera_manager.stop()
            logger.info("Vision monitoring stopped")
    except Exception as e:
        logger.error(f"Error stopping vision monitoring: {str(e)}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/sessions', exist_ok=True)
    os.makedirs('data/reports', exist_ok=True)
    
    # Initialize components
    logger.info("Initializing FocusGuard application...")
    
    try:
        # Test camera initialization if available
        if CAMERA_AVAILABLE and camera_manager:
            camera_manager.initialize()
            logger.info("Camera initialized successfully")
        else:
            logger.info("Running without camera - demo mode")
    except Exception as e:
        logger.warning(f"Camera initialization failed: {str(e)}")
    
    # Start Flask app
    logger.info("Starting FocusGuard dashboard server...")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )