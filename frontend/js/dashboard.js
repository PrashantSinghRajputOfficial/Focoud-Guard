// FocusGuard Dashboard - Updated with Sound Alerts
console.log('🎯 FocusGuard Dashboard Loading...');

// Global Variables
let sessionActive = false;
let isPaused = false;
let elapsedTime = 0;
let totalSeconds = 0;
let sessionTimer = null;
let cameraStream = null;
let faceDetectionInterval = null;
let continuousAlertInterval = null; // For continuous distraction alerts

// Session tracking variables
let currentSessionData = {
    name: '',
    startTime: null,
    endTime: null,
    plannedDuration: 0,
    actualDuration: 0,
    distractions: 0,
    focusTime: 0,
    pausedTime: 0
};

// Daily statistics
let dailyStats = {
    totalStudyTime: 0,
    sessionsCompleted: 0,
    totalDistractions: 0,
    focusScore: 0
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Dashboard loaded successfully');
    
    // Load saved statistics
    loadDailyStats();
    loadRecentSessions();
    updateStatisticsDisplay();
    
    // Setup volume slider with preview sound
    const volumeSlider = document.getElementById('alertVolume');
    const volumeValue = document.getElementById('volumeValue');
    if (volumeSlider && volumeValue) {
        volumeSlider.addEventListener('input', (e) => {
            volumeValue.textContent = e.target.value + '%';
            // Play preview sound when adjusting volume
            playVolumePreview();
        });
    }
    
    showAlert('🎯 Dashboard ready! Enter duration and click Start Focus Session.', 'success');
});

// Main Session Start Function
function startSession() {
    console.log('🎯 Starting session...');
    
    // Get form values
    const duration = parseInt(document.getElementById('studyDuration').value) || 120;
    const sessionName = document.getElementById('sessionName').value || 'Study Session';
    
    console.log('Session details:', { duration, sessionName });
    
    // Validate input
    if (duration < 1 || duration > 480) {
        showAlert('❌ Please enter a valid duration (1-480 minutes)', 'error');
        return;
    }
    
    // Initialize session data
    currentSessionData = {
        name: sessionName,
        startTime: new Date(),
        endTime: null,
        plannedDuration: duration,
        actualDuration: 0,
        distractions: 0,
        focusTime: 0,
        pausedTime: 0
    };
    
    // Update button immediately
    const startBtn = document.getElementById('startSession');
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';
    
    // Set session state
    sessionActive = true;
    isPaused = false;
    elapsedTime = 0;
    totalSeconds = duration * 60;
    
    // Hide setup card and update UI
    hideSetupCard();
    updateSessionInfo(sessionName, duration);
    startTimer();
    updateButtons();
    
    // Auto-start camera
    startCamera();
    
    showAlert('✅ Focus session started! Timer is running.', 'success');
    console.log('✅ Session started successfully');
}

// Hide Setup Card Function
function hideSetupCard() {
    const setupCard = document.getElementById('sessionSetupCard');
    const dashboardGrid = document.getElementById('dashboardGrid');
    
    if (setupCard) {
        setupCard.classList.add('hidden');
        console.log('✅ Setup card hidden');
    }
    
    if (dashboardGrid) {
        dashboardGrid.classList.add('session-active');
    }
}

// Show Setup Card Function
function showSetupCard() {
    const setupCard = document.getElementById('sessionSetupCard');
    const dashboardGrid = document.getElementById('dashboardGrid');
    
    if (setupCard) {
        setupCard.classList.remove('hidden');
        console.log('✅ Setup card shown');
    }
    
    if (dashboardGrid) {
        dashboardGrid.classList.remove('session-active');
    }
}

// Update Session Info Function
function updateSessionInfo(sessionName, duration) {
    console.log('📝 Updating session info...');
    
    // Update session details
    document.getElementById('currentSessionName').textContent = sessionName;
    document.getElementById('sessionStatus').textContent = 'Active';
    document.getElementById('sessionStatus').className = 'status-active';
    document.getElementById('sessionDuration').textContent = duration + ' minutes';
    document.getElementById('sessionProgress').textContent = '0%';
    
    // Add active animation
    const sessionCard = document.querySelector('.session-status');
    if (sessionCard) {
        sessionCard.classList.add('session-active');
    }
    
    console.log('✅ Session info updated');
}

// Timer Functions
function startTimer() {
    console.log('⏰ Starting timer...');
    
    sessionTimer = setInterval(() => {
        if (!isPaused && sessionActive) {
            elapsedTime++;
            updateTimerDisplay();
            
            // Check if session complete
            if (elapsedTime >= totalSeconds) {
                completeSession();
            }
        }
    }, 1000);
    
    console.log('✅ Timer started');
}

function stopTimer() {
    if (sessionTimer) {
        clearInterval(sessionTimer);
        sessionTimer = null;
        console.log('⏰ Timer stopped');
    }
}

function updateTimerDisplay() {
    // Format elapsed time
    const hours = Math.floor(elapsedTime / 3600);
    const minutes = Math.floor((elapsedTime % 3600) / 60);
    const seconds = elapsedTime % 60;
    
    const elapsedStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Format remaining time
    const remaining = Math.max(0, totalSeconds - elapsedTime);
    const remHours = Math.floor(remaining / 3600);
    const remMinutes = Math.floor((remaining % 3600) / 60);
    const remSeconds = remaining % 60;
    
    const remainingStr = `${remHours.toString().padStart(2, '0')}:${remMinutes.toString().padStart(2, '0')}:${remSeconds.toString().padStart(2, '0')}`;
    
    // Update display
    document.getElementById('currentTime').textContent = elapsedStr;
    document.getElementById('remainingTime').textContent = remainingStr;
    
    // Update progress
    const progress = totalSeconds > 0 ? Math.round((elapsedTime / totalSeconds) * 100) : 0;
    document.getElementById('sessionProgress').textContent = progress + '%';
}

// Update Buttons Function
function updateButtons() {
    const pauseBtn = document.getElementById('pauseSession');
    const stopBtn = document.getElementById('stopSession');
    const newBtn = document.getElementById('newSession');
    
    if (sessionActive) {
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
        newBtn.style.display = 'none';
        pauseBtn.textContent = isPaused ? 'Resume' : 'Pause';
    } else {
        pauseBtn.disabled = true;
        stopBtn.disabled = true;
        newBtn.style.display = 'inline-block';
        pauseBtn.textContent = 'Pause';
    }
}

// Pause Session Function
function pauseSession() {
    console.log('⏸️ Pause/Resume session...');
    
    isPaused = !isPaused;
    
    if (isPaused) {
        document.getElementById('sessionStatus').textContent = 'Paused';
        document.getElementById('sessionStatus').className = 'status-paused';
        showAlert('⏸️ Session paused', 'warning');
    } else {
        document.getElementById('sessionStatus').textContent = 'Active';
        document.getElementById('sessionStatus').className = 'status-active';
        showAlert('▶️ Session resumed', 'success');
    }
    
    updateButtons();
}

// Stop Session Function
function stopSession() {
    console.log('🛑 Stopping session...');
    
    if (confirm('Are you sure you want to stop the session?')) {
        sessionActive = false;
        isPaused = false;
        stopTimer();
        
        // Stop all continuous alerts
        stopAllContinuousAlerts();
        window.lastDistractionAlert = null;
        window.lastFaceDetectionAlert = null;
        window.lastPostureAlert = null;
        
        // Reset display
        resetSessionDisplay();
        updateButtons();
        
        showAlert('🛑 Session stopped', 'info');
    }
}

// New Session Function
function newSession() {
    console.log('🆕 Starting new session...');
    
    // Reset everything
    sessionActive = false;
    isPaused = false;
    elapsedTime = 0;
    totalSeconds = 0;
    
    if (sessionTimer) {
        clearInterval(sessionTimer);
        sessionTimer = null;
    }
    
    // Stop all continuous alerts
    stopAllContinuousAlerts();
    window.lastDistractionAlert = null;
    window.lastFaceDetectionAlert = null;
    window.lastPostureAlert = null;
    
    // Show setup card
    showSetupCard();
    resetSessionDisplay();
    
    // Reset start button
    const startBtn = document.getElementById('startSession');
    startBtn.disabled = false;
    startBtn.textContent = 'Start Focus Session';
    
    showAlert('Ready for new session! 🎯', 'success');
}

// Complete Session Function
function completeSession() {
    console.log('🎉 Session completed!');
    
    stopTimer();
    sessionActive = false;
    
    // Stop all continuous alerts
    stopAllContinuousAlerts();
    window.lastDistractionAlert = null;
    window.lastFaceDetectionAlert = null;
    window.lastPostureAlert = null;
    
    // Calculate session statistics
    currentSessionData.endTime = new Date();
    currentSessionData.actualDuration = elapsedTime;
    currentSessionData.focusTime = elapsedTime; // Time actually spent focused
    
    // Calculate focus score (percentage of time actually focused vs planned)
    const focusScore = Math.round((currentSessionData.focusTime / (currentSessionData.plannedDuration * 60)) * 100);
    currentSessionData.focusScore = Math.min(100, focusScore);
    
    // Save session data
    saveSessionData();
    updateDailyStats();
    updateStatisticsDisplay();
    updateRecentSessions();
    
    document.getElementById('sessionStatus').textContent = 'Completed';
    document.getElementById('sessionStatus').className = 'status-active';
    
    updateButtons();
    
    // Show completion summary
    showSessionSummary();
    
    // Play completion sound
    playCompletionSound();
}

// Reset Session Display Function
function resetSessionDisplay() {
    document.getElementById('currentSessionName').textContent = 'No active session';
    document.getElementById('sessionStatus').textContent = 'Idle';
    document.getElementById('sessionStatus').className = 'status-idle';
    document.getElementById('sessionDuration').textContent = '0 minutes';
    document.getElementById('sessionProgress').textContent = '0%';
    document.getElementById('currentTime').textContent = '00:00:00';
    document.getElementById('remainingTime').textContent = '00:00:00';
    
    // Remove active animation
    const sessionCard = document.querySelector('.session-status');
    if (sessionCard) {
        sessionCard.classList.remove('session-active');
    }
}

// Camera Functions
async function startCamera() {
    console.log('📹 Starting camera...');
    
    try {
        const video = document.getElementById('cameraFeed');
        
        // Request camera permission
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        
        // Set video source
        video.srcObject = cameraStream;
        
        // Update status
        updateVisionStatus('cameraStatus', 'active');
        
        // Start face detection
        startFaceDetection();
        
        console.log('✅ Camera started');
        showAlert('📹 Camera started successfully!', 'success');
        
    } catch (error) {
        console.error('❌ Camera error:', error);
        updateVisionStatus('cameraStatus', 'error');
        
        let errorMessage = 'Camera failed: ';
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Permission denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else {
            errorMessage += error.message;
        }
        
        showAlert('❌ ' + errorMessage, 'error');
    }
}

function stopCamera() {
    console.log('🛑 Stopping camera...');
    
    try {
        // Stop face detection
        if (faceDetectionInterval) {
            clearInterval(faceDetectionInterval);
            faceDetectionInterval = null;
        }
        
        // Stop camera stream
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
        
        // Clear video element
        const video = document.getElementById('cameraFeed');
        if (video) {
            video.srcObject = null;
        }
        
        // Update status indicators
        updateVisionStatus('cameraStatus', 'error');
        updateVisionStatus('faceDetection', 'error');
        updateVisionStatus('postureStatus', 'error');
        updateVisionStatus('attentionStatus', 'error');
        
        showAlert('🛑 Camera stopped', 'info');
        
    } catch (error) {
        console.error('❌ Error stopping camera:', error);
    }
}

function startFaceDetection() {
    console.log('👤 Starting face detection...');
    
    const video = document.getElementById('cameraFeed');
    if (!video || !cameraStream) return;
    
    // Create canvas for image processing
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 320;
    canvas.height = 240;
    
    faceDetectionInterval = setInterval(() => {
        if (!video.videoWidth) return;
        
        try {
            // Draw current frame to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Get image data for analysis
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            // Analyze frame for face detection
            const result = analyzeFaceInFrame(imageData);
            
            // Update vision indicators and provide specific voice alerts
            updateVisionStatus('faceDetection', result.faceDetected ? 'active' : 'warning');
            updateVisionStatus('postureStatus', result.goodPosture ? 'active' : 'warning');
            updateVisionStatus('attentionStatus', result.attentionLevel > 0.7 ? 'active' : 'warning');
            
            // Debug logging
            console.log('Face Detection:', result.faceDetected, 'Good Posture:', result.goodPosture, 'Session Active:', sessionActive, 'Is Paused:', isPaused);
            
            // Specific alerts for different detection issues
            if (sessionActive && !isPaused) {
                if (!result.faceDetected) {
                    handleFaceDetectionLost();
                } else if (!result.goodPosture) {
                    handlePostureLost();
                }
            }
            
            // Handle return to good posture during paused session
            if (sessionActive && result.goodPosture && result.faceDetected && isPaused && (window.lastFaceDetectionAlert || window.lastPostureAlert)) {
                console.log('🔄 Attempting to resume session - conditions met');
                handleGoodPosture();
            }
            
        } catch (error) {
            console.error('Face detection error:', error);
        }
    }, 2000); // Check every 2 seconds
}

function analyzeFaceInFrame(imageData) {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;
    
    let brightPixels = 0;
    let skinColorPixels = 0;
    let centerBrightness = 0;
    
    // Analyze center region (where face should be)
    const centerX = Math.floor(width / 2);
    const centerY = Math.floor(height / 2);
    const regionSize = 50;
    
    for (let y = centerY - regionSize; y < centerY + regionSize; y++) {
        for (let x = centerX - regionSize; x < centerX + regionSize; x++) {
            if (x >= 0 && x < width && y >= 0 && y < height) {
                const i = (y * width + x) * 4;
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                
                const brightness = (r + g + b) / 3;
                centerBrightness += brightness;
                
                // Simple skin color detection
                if (r > 95 && g > 40 && b > 20 && 
                    Math.max(r, g, b) - Math.min(r, g, b) > 15 &&
                    Math.abs(r - g) > 15 && r > g && r > b) {
                    skinColorPixels++;
                }
                
                if (brightness > 100) {
                    brightPixels++;
                }
            }
        }
    }
    
    const totalCenterPixels = (regionSize * 2) * (regionSize * 2);
    const avgCenterBrightness = centerBrightness / totalCenterPixels;
    const skinRatio = skinColorPixels / totalCenterPixels;
    
    // Determine face detection and posture
    const faceDetected = skinRatio > 0.1 && avgCenterBrightness > 80;
    const goodPosture = faceDetected && avgCenterBrightness > 90 && skinRatio > 0.12; // Made more lenient
    const attentionLevel = Math.min(1.0, (skinRatio * 3 + avgCenterBrightness / 255) / 2);
    
    // Debug logging for face detection
    console.log('Face Analysis - Skin Ratio:', skinRatio.toFixed(3), 'Brightness:', avgCenterBrightness.toFixed(1), 'Face:', faceDetected, 'Posture:', goodPosture);
    
    return {
        faceDetected,
        goodPosture,
        attentionLevel
    };
}

function handleFaceDetectionLost() {
    // Throttle face detection alerts (once every 8 seconds)
    const now = Date.now();
    if (!window.lastFaceDetectionAlert || now - window.lastFaceDetectionAlert > 8000) {
        window.lastFaceDetectionAlert = now;
        
        // Track distraction
        currentSessionData.distractions++;
        
        console.log('❌ Face detection lost!');
        showAlert('❌ Face detection lost! Please position yourself in front of the camera.', 'error');
        
        // Auto-pause session
        if (sessionActive && !isPaused) {
            isPaused = true;
            document.getElementById('sessionStatus').textContent = 'Paused';
            document.getElementById('sessionStatus').className = 'status-paused';
            updateButtons();
        }
        
        // Start continuous face detection alerts
        startContinuousFaceAlert();
    }
}

function handlePostureLost() {
    // Throttle posture alerts (once every 10 seconds)
    const now = Date.now();
    if (!window.lastPostureAlert || now - window.lastPostureAlert > 10000) {
        window.lastPostureAlert = now;
        
        // Track distraction
        currentSessionData.distractions++;
        
        console.log('⚠️ Study posture lost!');
        showAlert('⚠️ Study posture lost! Please return to your study position.', 'warning');
        
        // Auto-pause session
        if (sessionActive && !isPaused) {
            isPaused = true;
            document.getElementById('sessionStatus').textContent = 'Paused';
            document.getElementById('sessionStatus').className = 'status-paused';
            updateButtons();
        }
        
        // Start continuous posture alerts
        startContinuousPostureAlert();
    }
}

function handleDistraction() {
    // This is now handled by more specific functions above
    handlePostureLost();
}

function handleGoodPosture() {
    console.log('🔍 handleGoodPosture called');
    console.log('Session Active:', sessionActive);
    console.log('Is Paused:', isPaused);
    console.log('Face Alert Flag:', window.lastFaceDetectionAlert);
    console.log('Posture Alert Flag:', window.lastPostureAlert);
    
    // Resume session when user returns to good posture
    if (sessionActive && isPaused && (window.lastFaceDetectionAlert || window.lastPostureAlert)) {
        console.log('✅ Good posture detected - Resuming session');
        showAlert('✅ Good posture detected! Session resumed.', 'success');
        
        // Resume session (toggle from paused to active)
        isPaused = false;
        document.getElementById('sessionStatus').textContent = 'Active';
        document.getElementById('sessionStatus').className = 'status-active';
        updateButtons();
        
        // Clear distraction flags
        window.lastFaceDetectionAlert = null;
        window.lastPostureAlert = null;
        window.lastDistractionAlert = null;
        
        // Stop all continuous alerts
        stopAllContinuousAlerts();
    } else {
        console.log('❌ Resume conditions not met');
    }
}

function startContinuousFaceAlert() {
    stopAllContinuousAlerts();
    
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) return;
    
    console.log('🔊 Starting continuous face detection alerts...');
    
    continuousAlertInterval = setInterval(() => {
        if (sessionActive && isPaused && window.lastFaceDetectionAlert) {
            speakText("Face detection lost. Please position yourself in front of the camera.");
        } else {
            stopAllContinuousAlerts();
        }
    }, 6000);
}

function startContinuousPostureAlert() {
    stopAllContinuousAlerts();
    
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) return;
    
    console.log('🔊 Starting continuous posture alerts...');
    
    continuousAlertInterval = setInterval(() => {
        if (sessionActive && isPaused && window.lastPostureAlert) {
            speakText("Study position lost. Please return to your study position.");
        } else {
            stopAllContinuousAlerts();
        }
    }, 5000);
}

function stopAllContinuousAlerts() {
    if (continuousAlertInterval) {
        clearInterval(continuousAlertInterval);
        continuousAlertInterval = null;
        console.log('🔇 All continuous alerts stopped');
    }
    
    // Stop any ongoing speech
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

function updateVisionStatus(elementId, status) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `indicator-dot ${status}`;
    }
}

// Sound Functions
function playVolumePreview() {
    // Check if sound alerts are enabled
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) {
        return;
    }
    
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Play a pleasant preview tone
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
        
        // Get volume from slider
        const volumeSlider = document.getElementById('alertVolume');
        const volume = volumeSlider ? (volumeSlider.value / 100) * 0.3 : 0.3;
        gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.2);
        
    } catch (error) {
        console.log('Audio not available:', error);
    }
}

function startContinuousAlert() {
    // This function is now replaced by more specific alert functions
    startContinuousPostureAlert();
}

function stopContinuousAlert() {
    // This function is now replaced by stopAllContinuousAlerts
    stopAllContinuousAlerts();
}

function playAlertSound(type = 'info') {
    // Check if sound alerts are enabled
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) {
        return;
    }
    
    // Only use voice for specific alert types, beep for others
    if (type === 'warning' || type === 'error') {
        let message = '';
        
        switch(type) {
            case 'warning':
                message = 'Study position lost. Please return to your study position.';
                break;
            case 'error':
                message = 'Face detection lost. Please position yourself in front of the camera.';
                break;
        }
        
        speakText(message);
    } else {
        // Use beep sound for success and info alerts
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Different frequencies for different alert types
            let frequency = 600; // Default
            let duration = 0.3;
            
            switch(type) {
                case 'success':
                    frequency = 800;
                    duration = 0.2;
                    break;
                case 'info':
                    frequency = 600;
                    duration = 0.3;
                    break;
            }
            
            oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
            
            // Get volume from slider
            const volumeSlider = document.getElementById('alertVolume');
            const volume = volumeSlider ? (volumeSlider.value / 100) * 0.3 : 0.3;
            gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            
            oscillator.start();
            oscillator.stop(audioContext.currentTime + duration);
            
        } catch (error) {
            console.log('Audio not available:', error);
        }
    }
}

function speakText(text, volumeOverride = null) {
    try {
        // Check if browser supports speech synthesis
        if (!window.speechSynthesis) {
            console.log('Speech synthesis not supported');
            return;
        }
        
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        // Create speech utterance
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Get volume from slider or use override
        const volumeSlider = document.getElementById('alertVolume');
        const volume = volumeOverride || (volumeSlider ? volumeSlider.value / 100 : 0.7);
        
        // Configure voice settings
        utterance.volume = Math.min(1.0, volume);
        utterance.rate = 1.0; // Normal speed
        utterance.pitch = 1.0; // Normal pitch
        
        // Try to use a clear English voice
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(voice => 
            voice.lang.startsWith('en') && 
            (voice.name.includes('Google') || voice.name.includes('Microsoft') || voice.name.includes('Alex'))
        ) || voices.find(voice => voice.lang.startsWith('en'));
        
        if (englishVoice) {
            utterance.voice = englishVoice;
        }
        
        // Speak the text
        window.speechSynthesis.speak(utterance);
        
        console.log('🗣️ Speaking:', text);
        
    } catch (error) {
        console.log('Speech synthesis error:', error);
        // Fallback to beep sound if speech fails
        playBeepSound();
    }
}

function playBeepSound() {
    // Fallback beep sound if speech synthesis fails
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
        
        const volumeSlider = document.getElementById('alertVolume');
        const volume = volumeSlider ? (volumeSlider.value / 100) * 0.3 : 0.3;
        gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
        
    } catch (error) {
        console.log('Audio not available:', error);
    }
}

function playCompletionSound() {
    // Check if sound alerts are enabled
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) {
        return;
    }
    
    try {
        // Create completion melody
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const volumeSlider = document.getElementById('alertVolume');
        const volume = volumeSlider ? (volumeSlider.value / 100) * 0.3 : 0.3;
        
        // Play a pleasant completion melody
        const notes = [
            { freq: 523, time: 0 },    // C5
            { freq: 659, time: 0.2 },  // E5
            { freq: 784, time: 0.4 },  // G5
            { freq: 1047, time: 0.6 }  // C6
        ];
        
        notes.forEach(note => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(note.freq, audioContext.currentTime + note.time);
            gainNode.gain.setValueAtTime(volume, audioContext.currentTime + note.time);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + note.time + 0.3);
            
            oscillator.start(audioContext.currentTime + note.time);
            oscillator.stop(audioContext.currentTime + note.time + 0.3);
        });
        
    } catch (error) {
        console.log('Audio not available:', error);
    }
}

// Alert Function with Sound
function showAlert(message, type = 'info') {
    console.log(`Alert [${type}]:`, message);
    
    // Play sound for alert
    playAlertSound(type);
    
    const alertsDiv = document.getElementById('currentAlerts');
    if (!alertsDiv) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; cursor: pointer; font-size: 18px; padding: 5px;">×</button>
    `;
    
    // Clear old alerts if too many
    if (alertsDiv.children.length > 2) {
        alertsDiv.innerHTML = '';
    }
    
    alertsDiv.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

function playCompletionSound() {
    // Check if sound alerts are enabled
    const soundEnabled = document.getElementById('soundAlerts');
    if (!soundEnabled || !soundEnabled.checked) {
        return;
    }
    
    try {
        // Create completion melody
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const volumeSlider = document.getElementById('alertVolume');
        const volume = volumeSlider ? (volumeSlider.value / 100) * 0.3 : 0.3;
        
        // Play a pleasant completion melody
        const notes = [
            { freq: 523, time: 0 },    // C5
            { freq: 659, time: 0.2 },  // E5
            { freq: 784, time: 0.4 },  // G5
            { freq: 1047, time: 0.6 }  // C6
        ];
        
        notes.forEach(note => {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(note.freq, audioContext.currentTime + note.time);
            gainNode.gain.setValueAtTime(volume, audioContext.currentTime + note.time);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + note.time + 0.3);
            
            oscillator.start(audioContext.currentTime + note.time);
            oscillator.stop(audioContext.currentTime + note.time + 0.3);
        });
        
    } catch (error) {
        console.log('Audio not available:', error);
    }
}

// Statistics and Session Management Functions
function saveSessionData() {
    const sessions = JSON.parse(localStorage.getItem('focusGuardSessions') || '[]');
    sessions.unshift(currentSessionData); // Add to beginning of array
    
    // Keep only last 10 sessions
    if (sessions.length > 10) {
        sessions.splice(10);
    }
    
    localStorage.setItem('focusGuardSessions', JSON.stringify(sessions));
    console.log('📊 Session data saved:', currentSessionData);
}

function loadRecentSessions() {
    const sessions = JSON.parse(localStorage.getItem('focusGuardSessions') || '[]');
    return sessions;
}

function updateRecentSessions() {
    const sessions = loadRecentSessions();
    const sessionsList = document.getElementById('sessionsList');
    
    if (!sessionsList) return;
    
    if (sessions.length === 0) {
        sessionsList.innerHTML = '<div class="no-sessions">No recent sessions found</div>';
        return;
    }
    
    sessionsList.innerHTML = sessions.map(session => {
        const duration = Math.floor(session.actualDuration / 60);
        const focusScore = session.focusScore || 0;
        const date = new Date(session.startTime).toLocaleDateString();
        const time = new Date(session.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        return `
            <div class="session-item">
                <div class="session-details">
                    <h4>${session.name}</h4>
                    <p>${date} at ${time}</p>
                </div>
                <div class="session-stats">
                    <span class="session-duration">${duration}m</span>
                    <span class="session-focus">Focus: ${focusScore}%</span>
                    <span class="session-distractions">${session.distractions} distractions</span>
                </div>
            </div>
        `;
    }).join('');
}

function loadDailyStats() {
    const today = new Date().toDateString();
    const savedStats = localStorage.getItem('focusGuardDailyStats');
    const savedDate = localStorage.getItem('focusGuardStatsDate');
    
    if (savedDate === today && savedStats) {
        dailyStats = JSON.parse(savedStats);
    } else {
        // Reset stats for new day
        dailyStats = {
            totalStudyTime: 0,
            sessionsCompleted: 0,
            totalDistractions: 0,
            focusScore: 0
        };
        localStorage.setItem('focusGuardStatsDate', today);
    }
}

function updateDailyStats() {
    dailyStats.totalStudyTime += currentSessionData.actualDuration;
    dailyStats.sessionsCompleted++;
    dailyStats.totalDistractions += currentSessionData.distractions;
    
    // Calculate average focus score
    const sessions = loadRecentSessions();
    const todaySessions = sessions.filter(s => 
        new Date(s.startTime).toDateString() === new Date().toDateString()
    );
    
    if (todaySessions.length > 0) {
        const avgFocus = todaySessions.reduce((sum, s) => sum + (s.focusScore || 0), 0) / todaySessions.length;
        dailyStats.focusScore = Math.round(avgFocus);
    }
    
    // Save to localStorage
    localStorage.setItem('focusGuardDailyStats', JSON.stringify(dailyStats));
}

function updateStatisticsDisplay() {
    const totalHours = Math.floor(dailyStats.totalStudyTime / 3600);
    const totalMinutes = Math.floor((dailyStats.totalStudyTime % 3600) / 60);
    
    document.getElementById('totalStudyTime').textContent = `${totalHours}h ${totalMinutes}m`;
    document.getElementById('sessionsCompleted').textContent = dailyStats.sessionsCompleted;
    document.getElementById('focusScore').textContent = dailyStats.focusScore + '%';
    document.getElementById('totalDistractions').textContent = dailyStats.totalDistractions;
}

function showSessionSummary() {
    const duration = Math.floor(currentSessionData.actualDuration / 60);
    const plannedMinutes = currentSessionData.plannedDuration;
    const focusScore = currentSessionData.focusScore || 0;
    const distractions = currentSessionData.distractions;
    
    const summaryMessage = `
        🎉 Session Complete!
        
        📚 ${currentSessionData.name}
        ⏱️ Duration: ${duration}/${plannedMinutes} minutes
        🎯 Focus Score: ${focusScore}%
        ⚠️ Distractions: ${distractions}
        
        ${focusScore >= 80 ? 'Excellent focus! 🌟' : 
          focusScore >= 60 ? 'Good job! Keep improving 👍' : 
          'Room for improvement. Try to minimize distractions next time 💪'}
    `;
    
    showAlert(summaryMessage, 'success');
}

console.log('✅ FocusGuard Dashboard loaded successfully');