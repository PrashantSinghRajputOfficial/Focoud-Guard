# FocusGuard 🎯

**Vision-Based Study Time Enforcement System**

FocusGuard ek AI-powered system hai jo ensure karta hai ki student apne pre-set study time ke dauran focused posture me laptop ke samne rahe. Agar student study session ke dauran attention lose karta hai, system alert mode activate karta hai jab tak user wapas study posture me nahi aata.

## Key Features

- ⏱️ **Smart Timer**: User sets study duration, timer sirf study posture detect hone par start hota hai
- 👁️ **Vision Monitoring**: Laptop camera continuously monitor karta hai face position aur attention
- 🚨 **Alert System**: Agar user study chor deta hai → alarm ON + timer pause
- 📊 **Progress Tracking**: Real-time statistics aur focus score tracking
- 🎯 **Session Management**: Complete session management with pause/resume functionality

## Technology Stack

- **Backend**: Python, Flask
- **Computer Vision**: OpenCV, MediaPipe
- **Frontend**: HTML5, CSS3, JavaScript
- **Audio**: Pygame, Winsound
- **Data Storage**: JSON files

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open Dashboard

Open your browser and go to: `http://127.0.0.1:5000`

## How to Use

### Starting a Study Session

1. **Set Duration**: Enter study duration in minutes (default: 120 minutes)
2. **Session Name**: Give your session a name (optional)
3. **Click "Start Focus Session"**: Session will begin

### During Study Session

- **Green Indicators**: Camera active, face detected, good posture, high attention
- **Yellow/Red Indicators**: Issues detected - adjust your position
- **Timer**: Shows elapsed time and remaining time
- **Pause/Resume**: Use controls to pause/resume session

### Vision Monitoring

- **Camera Status**: Shows if camera is working
- **Face Detection**: Detects if your face is visible
- **Study Posture**: Checks if you're in proper study position
- **Attention Level**: Measures your attention level (0-100%)

### Alerts & Notifications

- **Distraction Alert**: Modal popup when you're not focused
- **Sound Alerts**: Audio notifications (can be disabled)
- **Visual Alerts**: On-screen notifications
- **Volume Control**: Adjust alert volume

## Dashboard Features

### 📚 Session Setup
- Set study duration
- Name your session
- Start/stop controls

### ⏱️ Current Session Status
- Real-time timer display
- Session information
- Pause/resume/stop controls

### 👁️ Vision Monitoring
- Camera feed status
- Face detection indicator
- Posture monitoring
- Attention level tracking

### 📊 Statistics
- Today's total study time
- Sessions completed
- Focus score percentage
- Distraction count

### 📝 Recent Sessions
- History of recent study sessions
- Session duration and status
- Performance tracking

### 🔔 Alerts & Settings
- Sound/visual alert toggles
- Volume control
- Current active alerts

## File Structure

```
FocusGuard/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── frontend/                      # Frontend files
│   ├── dashboard.html            # Main dashboard
│   ├── css/dashboard.css         # Dashboard styles
│   └── js/dashboard.js           # Dashboard functionality
├── backend/                       # Backend controllers & services
│   ├── controllers/
│   │   ├── session_controller.py # Session management
│   │   └── timer_controller.py   # Timer operations
│   └── services/
│       └── focus_service.py      # Focus tracking
├── timer_engine/                  # Core timer functionality
│   └── session_manager.py        # Session management core
├── vision_engine/                 # Computer vision
│   └── camera.py                 # Camera management
├── alert_engine/                  # Alert system
│   └── notifier.py               # Alert notifications
└── data/                         # Data storage
    ├── sessions/                 # Session data
    └── reports/                  # Reports and analytics
```

## API Endpoints

### Session Management
- `POST /api/session/start` - Start new session
- `POST /api/session/pause` - Pause current session
- `POST /api/session/resume` - Resume paused session
- `POST /api/session/stop` - Stop current session
- `POST /api/session/complete` - Complete session

### Vision & Monitoring
- `GET /api/vision/status` - Get vision monitoring status

### Statistics
- `GET /api/stats/today` - Get today's statistics
- `GET /api/sessions/recent` - Get recent sessions

## Troubleshooting

### Camera Issues
- Ensure camera permissions are granted
- Check if other applications are using the camera
- Try restarting the application

### Audio Issues
- Check system volume settings
- Ensure pygame is properly installed
- Try running: `pip install pygame --upgrade`

### Performance Issues
- Close other resource-intensive applications
- Ensure good lighting for face detection
- Check system requirements

## System Requirements

- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.8 or higher
- **Camera**: Built-in or external webcam
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check troubleshooting section
- Review system requirements
- Ensure all dependencies are installed

---

**Happy Studying! 📚✨**