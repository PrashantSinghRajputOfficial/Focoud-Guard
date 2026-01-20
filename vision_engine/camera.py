"""
Camera Manager - Handles camera operations and vision processing
"""

import threading
import time
from typing import Dict, Optional, Tuple
import random

# Try to import OpenCV, fallback to mock if not available
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not available - using mock camera data")

class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.vision_data = {
            'camera': False,
            'faceDetected': False,
            'studyPosture': False,
            'attentionLevel': 0.0
        }
        self._lock = threading.Lock()
        self.capture_thread = None
        
        # Initialize face detection if OpenCV is available
        if OPENCV_AVAILABLE:
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except Exception as e:
                print(f"Warning: Could not load face cascade: {e}")
                self.face_cascade = None
        else:
            self.face_cascade = None
    
    def initialize(self) -> bool:
        """Initialize camera"""
        if not OPENCV_AVAILABLE:
            # Mock initialization
            print("Mock camera initialized")
            return True
            
        try:
            self.camera = cv2.VideoCapture(0)  # Default camera
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
            
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start camera capture"""
        if not OPENCV_AVAILABLE:
            # Mock start
            with self._lock:
                self.is_running = True
                self.vision_data['camera'] = True
            
            # Start mock capture thread
            self.capture_thread = threading.Thread(target=self._mock_capture_loop, daemon=True)
            self.capture_thread.start()
            return True
            
        if not self.initialize():
            return False
        
        with self._lock:
            if self.is_running:
                return True
            
            self.is_running = True
            self.vision_data['camera'] = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        return True
    
    def stop(self):
        """Stop camera capture"""
        with self._lock:
            self.is_running = False
            self.vision_data['camera'] = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if OPENCV_AVAILABLE and self.camera:
            self.camera.release()
            self.camera = None
    
    def is_active(self) -> bool:
        """Check if camera is active"""
        with self._lock:
            return self.is_running
    
    def get_current_frame(self) -> Optional:
        """Get current camera frame"""
        if not OPENCV_AVAILABLE:
            return None
            
        with self._lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_current_status(self) -> Dict:
        """Get current vision status"""
        with self._lock:
            return self.vision_data.copy()
    
    def _mock_capture_loop(self):
        """Mock camera capture loop for demo"""
        while self.is_running:
            try:
                # Simulate changing vision data
                with self._lock:
                    # Randomly simulate face detection and posture
                    self.vision_data.update({
                        'faceDetected': random.choice([True, True, False]),  # 66% chance
                        'studyPosture': random.choice([True, True, True, False]),  # 75% chance
                        'attentionLevel': random.uniform(0.6, 1.0)
                    })
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Error in mock capture loop: {e}")
                time.sleep(1)
    
    def _capture_loop(self):
        """Main camera capture loop"""
        if not OPENCV_AVAILABLE:
            return
            
        while self.is_running:
            try:
                if not self.camera or not self.camera.isOpened():
                    time.sleep(0.1)
                    continue
                
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                with self._lock:
                    self.current_frame = frame.copy()
                
                # Process frame for vision analysis
                self._process_frame(frame)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, frame):
        """Process frame for vision analysis"""
        if not OPENCV_AVAILABLE:
            return
            
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            face_detected = False
            study_posture = False
            attention_level = 0.0
            
            if self.face_cascade is not None:
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    face_detected = True
                    
                    # Analyze largest face
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = largest_face
                    
                    # Simple posture analysis based on face position and size
                    frame_center_x = frame.shape[1] // 2
                    frame_center_y = frame.shape[0] // 2
                    face_center_x = x + w // 2
                    face_center_y = y + h // 2
                    
                    # Check if face is reasonably centered and sized
                    center_threshold = 100
                    size_threshold = 80
                    
                    if (abs(face_center_x - frame_center_x) < center_threshold and
                        abs(face_center_y - frame_center_y) < center_threshold and
                        w > size_threshold and h > size_threshold):
                        study_posture = True
                        attention_level = min(1.0, (w * h) / (size_threshold * size_threshold))
                    else:
                        attention_level = 0.3  # Partial attention
            
            # Update vision data
            with self._lock:
                self.vision_data.update({
                    'faceDetected': face_detected,
                    'studyPosture': study_posture,
                    'attentionLevel': attention_level
                })
                
        except Exception as e:
            print(f"Error processing frame: {e}")
    
    def get_frame_with_annotations(self) -> Optional:
        """Get current frame with vision annotations"""
        if not OPENCV_AVAILABLE:
            return None
            
        frame = self.get_current_frame()
        if frame is None:
            return None
        
        try:
            # Draw face detection rectangles
            if self.face_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    # Draw rectangle around face
                    color = (0, 255, 0) if self.vision_data['studyPosture'] else (0, 255, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    # Add status text
                    status = "Study Posture" if self.vision_data['studyPosture'] else "Not Focused"
                    cv2.putText(frame, status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Add attention level indicator
            attention_text = f"Attention: {self.vision_data['attentionLevel']:.1%}"
            cv2.putText(frame, attention_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return frame
            
        except Exception as e:
            print(f"Error adding annotations: {e}")
            return frame