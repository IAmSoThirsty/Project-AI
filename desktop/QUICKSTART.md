# Enhanced Cognitive IDE - Quick Start Guide

## Installation & Setup

### 1. Install Dependencies
```bash
cd desktop/
npm install
pip install fastapi uvicorn websockets
```

### 2. Start All Services (Windows)
```bash
start-ide.bat
```

### 2. Start All Services (Linux/Mac)
```bash
chmod +x start-ide.sh
./start-ide.sh
```

### 3. Access the IDE
Open your browser to: http://localhost:5173/cognitive-ide

## Features Overview

### Desktop Mode
- **Code Editor**: Monaco-based editor with syntax highlighting
- **Real-time Collaboration**: Multiple users can edit simultaneously
- **AI Assistance**: Automatic code analysis and suggestions
- **Simulation View**: 3D visualization of agent simulations

### VR Mode
- **WebXR Integration**: Works with any WebXR-compatible headset
- **Immersive Environment**: 3D office with floating code panels
- **VR Controllers**: Interact with code using VR controllers
- **60 FPS Performance**: Optimized rendering for smooth VR experience

### AI Features
- Security vulnerability detection
- Performance optimization hints
- Code quality improvements
- Automated bug fixes
- Context-aware completions

## Keyboard Shortcuts

### Editor
- `Ctrl/Cmd + S` - Save file
- `Ctrl/Cmd + F` - Find
- `Ctrl/Cmd + /` - Toggle comment
- `Ctrl/Cmd + Space` - Trigger AI suggestions
- `F12` - Go to definition

### Simulation
- `Space` - Pause/Resume simulation
- `+/-` - Adjust simulation speed
- `R` - Reset simulation

### VR Mode
- **Trigger** - Select/interact
- **Grip** - Grab panels
- **Thumbstick** - Move/rotate

## Configuration

### API Endpoints
Edit `desktop/api_server.py` to customize:
- Port (default: 8000)
- AI model settings
- Simulation parameters

### Collaboration Server
Edit `desktop/collaboration-server.js` to customize:
- Port (default: 8080)
- Max users per document
- Session timeout

### Performance
Edit `desktop/src/utils/PerformanceOptimizer.ts` to customize:
- Target FPS (default: 60)
- Quality levels
- LOD distances

## Troubleshooting

### "Cannot connect to collaboration server"
1. Ensure collaboration-server.js is running
2. Check port 8080 is not in use
3. Verify firewall allows WebSocket connections

### "Low FPS in VR"
1. Enable adaptive quality
2. Reduce number of agents in simulation
3. Lower shadow quality settings

### "AI suggestions not working"
1. Check API server is running on port 8000
2. Verify network connectivity
3. Check browser console for errors

## Production Deployment

### Build for Production
```bash
npm run build
```

### Package as Electron App
```bash
npm run package
```

### Deploy to Server
1. Build the app: `npm run build`
2. Copy `dist/` folder to server
3. Run API server: `python api_server.py`
4. Run collaboration server: `node collaboration-server.js`
5. Serve static files with nginx/apache

## Support

For issues or questions:
- Check ENHANCED_IDE_README.md for full documentation
- Review logs in browser console
- Check server logs for API/collaboration issues

---

**Happy Coding in VR! 🚀**
