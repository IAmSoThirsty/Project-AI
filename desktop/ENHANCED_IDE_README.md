# Enhanced Miniature Office - Cognitive IDE

> **Immersive 3D Code Editing with VR/AR, Real-time Collaboration, AI Pair Programming, and Simulation Visualization**

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![VR Ready](https://img.shields.io/badge/VR-Ready-purple)
![Performance](https://img.shields.io/badge/60_FPS-VR-orange)

## 🚀 Features

### 1. **VR/AR Support with WebXR**
- **Immersive 3D editing environment** in virtual reality
- **WebXR API integration** for browser-based VR/AR experiences
- **Interactive VR controllers** for code manipulation
- **Spatial code panels** floating in 3D space
- **Multi-floor office visualization** with language-specific floors
- **60 FPS performance** optimized for VR headsets

### 2. **Real-time Collaborative Editing**
- **Google Docs-style multi-user editing** with live cursors
- **Operational Transformation** using Yjs for conflict-free collaboration
- **User presence indicators** showing who's online
- **Live cursor and selection sharing** across all users
- **WebSocket-based synchronization** for instant updates
- **Document-based collaboration rooms**

### 3. **AI Pair Programming**
- **Context-aware code suggestions** powered by AI
- **Real-time bug detection** with automated fixes
- **Security vulnerability scanning** (SQL injection, XSS, etc.)
- **Performance optimization hints** (async operations, caching, etc.)
- **Code quality improvements** (naming, style, best practices)
- **Quick fixes** integrated into Monaco Editor
- **Confidence scoring** for AI suggestions

### 4. **3D Simulation Visualization**
- **Real-time 3D rendering** of running simulations
- **Multi-floor office environment** with agent visualization
- **Agent status indicators** (active, idle, blocked, completed)
- **Department visualization** with occupancy tracking
- **Interactive camera controls** with orbit, zoom, pan
- **Lighting and atmospheric effects** for immersion
- **Performance stats overlay** (FPS, tick count, agent count)

### 5. **Performance Optimization**
- **Adaptive quality system** adjusting to maintain 60 FPS
- **Level of Detail (LOD)** rendering based on distance
- **Object pooling** for frequently created/destroyed objects
- **Frustum culling** to skip off-screen objects
- **Batch geometry updates** for efficiency
- **Memory management** with automatic cleanup
- **Shadow map optimization** based on quality level
- **Throttle and debounce utilities** for expensive operations

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.10+ (for backend simulation server)
- VR headset (optional, for VR mode)

### Setup

1. **Clone the repository**
```bash
cd desktop/
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the collaboration server**
```bash
node collaboration-server.js
```

4. **Start the development server**
```bash
npm run dev
```

5. **Open in browser**
```
http://localhost:5173
```

## 🎮 Usage

### Desktop Mode
1. Launch the application
2. Select **Desktop Mode** from the header
3. Use the sidebar to switch between:
   - **Code Editor**: Collaborative code editing
   - **Simulation**: 3D visualization of simulations
   - **AI Assistant**: AI pair programming panel

### VR Mode
1. Connect your VR headset
2. Select **VR Mode** from the header
3. Click "Enter VR" button
4. Use VR controllers to:
   - Grab and move code panels
   - Navigate the 3D office environment
   - Interact with floating UI elements

### AR Mode
1. Select **AR Mode** from the header
2. Grant camera permissions
3. AR overlays will appear in your physical environment

### Collaborative Editing
1. Open a file in the Code Editor
2. Share the document URL with team members
3. See real-time cursors and edits from all users
4. User presence shown in the status bar

### AI Pair Programming
1. Start typing code in the editor
2. AI suggestions appear automatically
3. View detected issues in the AI panel
4. Click quick-fix suggestions to apply

### Simulation Visualization
1. Switch to the Simulation panel
2. View 3D representation of agents and floors
3. Use mouse to orbit, zoom, pan
4. Toggle pause/resume with the button

## 🏗️ Architecture

### Components

```
desktop/
├── src/
│   ├── components/
│   │   ├── EnhancedCognitiveIDE.tsx      # Main IDE component
│   │   ├── CognitiveIDE_VR.tsx           # VR/AR implementation
│   │   ├── CollaborativeEditor.tsx       # Multi-user editor
│   │   ├── AIPairProgrammer.tsx          # AI assistance
│   │   └── SimulationVisualizer.tsx      # 3D simulation
│   └── utils/
│       └── PerformanceOptimizer.ts       # VR performance
├── collaboration-server.js               # WebSocket server
└── package.json
```

### Technology Stack

- **Frontend Framework**: React 18 + TypeScript
- **3D Graphics**: Three.js + WebXR
- **Code Editor**: Monaco Editor
- **Collaboration**: Yjs + y-websocket + y-monaco
- **AI Integration**: Custom AI analysis API
- **Build Tool**: Vite
- **Desktop Wrapper**: Electron

## ⚡ Performance

### VR Performance Targets
- **60 FPS** minimum in VR mode
- **16.67ms** frame time budget
- **Adaptive quality** automatically adjusts settings
- **LOD system** reduces polygon count for distant objects

### Optimization Techniques
1. **Frustum culling**: Skip rendering off-screen objects
2. **Object pooling**: Reuse objects instead of creating new ones
3. **Batch updates**: Group geometry updates together
4. **Shadow optimization**: Disable shadows at low quality
5. **Pixel ratio capping**: Limit resolution on lower-end devices
6. **Memory management**: Automatic cleanup of unused objects

### Quality Levels
- **High (100%)**: Full quality, all features enabled
- **Medium (75%)**: Reduced shadows, simplified materials
- **Low (50%)**: No shadows, flat shading, reduced resolution

## 🤖 AI Capabilities

### Supported Detections
- **Security**: SQL injection, XSS, insecure crypto
- **Performance**: Sync operations, memory leaks, N+1 queries
- **Logic**: Uninitialized variables, unreachable code
- **Style**: Line length, naming conventions

### AI Suggestions
- **Code completion**: Context-aware snippets
- **Refactoring**: Improve code structure
- **Optimization**: Performance improvements
- **Bug fixes**: Automated corrections

## 🔌 API

### Simulation API
```typescript
GET /api/simulation/state
// Returns current simulation state

POST /api/simulation/step
// Advance simulation by one tick

POST /api/simulation/start
// Start simulation

POST /api/simulation/stop
// Stop simulation
```

### AI API
```typescript
POST /api/ai/analyze
// Analyze code and return suggestions
Body: {
  code: string,
  context: object,
  position: { line: number, column: number },
  language: string
}
```

## 🎨 Customization

### Themes
Edit the color scheme in component styles:
```typescript
// Main colors
const primaryColor = '#00ff41';   // Green
const secondaryColor = '#ff9f00';  // Orange
const backgroundColor = '#0a0e1a'; // Dark blue
```

### VR Environment
Customize the office layout in `CognitiveIDE_VR.tsx`:
```typescript
const floors = [
  { name: 'Lobby', color: 0xff9f00 },
  { name: 'Python', color: 0x3776ab },
  // Add more floors...
];
```

### AI Rules
Configure AI detection rules in `AIPairProgrammer.tsx`:
```typescript
// Add custom detection patterns
if (line.includes('your-pattern')) {
  bugs.push({
    severity: 'medium',
    category: 'custom',
    description: 'Your custom rule',
  });
}
```

## 🐛 Troubleshooting

### VR Mode Not Working
- Check WebXR browser support: [WebXR Samples](https://immersive-web.github.io/webxr-samples/)
- Ensure VR headset is connected and detected
- Try Chrome or Edge (best WebXR support)

### Low FPS in VR
- Enable adaptive quality in Performance Optimizer
- Reduce number of visible agents/objects
- Lower shadow quality or disable shadows
- Check GPU capabilities

### Collaboration Not Syncing
- Verify collaboration server is running on port 8080
- Check WebSocket connection in browser console
- Ensure firewall allows WebSocket connections
- Try reconnecting to the document

### AI Suggestions Not Appearing
- Verify AI API endpoint is accessible
- Check browser console for errors
- Fallback suggestions should still work offline

## 📝 Development

### Running Tests
```bash
npm test
```

### Building for Production
```bash
npm run build
```

### Electron Packaging
```bash
npm run package           # Current platform
npm run build:win         # Windows
npm run build:mac         # macOS
npm run build:linux       # Linux
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Three.js** for 3D rendering
- **Monaco Editor** for code editing
- **Yjs** for collaborative editing
- **WebXR Device API** for VR/AR support
- **Project AI Team** for the Miniature Office concept

## 📞 Support

For issues, questions, or feature requests:
- GitHub Issues: [Project Issues](https://github.com/your-repo/issues)
- Documentation: [Full Docs](https://your-docs-url.com)

---

**Built with ❤️ for immersive code editing**
