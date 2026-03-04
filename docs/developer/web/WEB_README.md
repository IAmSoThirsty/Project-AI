<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# Project-AI Web Version

This branch contains a web-based version of Project-AI, converting the PyQt desktop application into a modern web application with React frontend and Flask backend.

## ✨ New Features (Latest Update)

The desktop version now includes:

- **Cloud Sync**: Encrypted cross-device synchronization with device management
- **Advanced ML Models**: RandomForest, GradientBoosting, and Neural Networks
- **Plugin System**: Dynamic plugin loading with hooks and lifecycle management

These features are being integrated into the web version.

## 🌐 Architecture

### Backend (Flask API)

- **Location**: `web/backend/`
- **Framework**: Flask with CORS support
- **Purpose**: RESTful API that wraps the existing Project-AI core functionality
- **Port**: 5000 (default)

### Frontend (React + Vite)

- **Location**: `web/frontend/`
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **State Management**: Zustand (lightweight alternative to Redux)
- **Port**: 3000 (default)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:

```bash
cd web/backend
```

1. Create virtual environment:

```bash
python -m venv venv
```

1. Activate virtual environment:

```bash

# Windows

venv\Scripts\activate

# macOS/Linux

source venv/bin/activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r ../../requirements.txt  # Install core Project-AI dependencies
```

1. Configure environment:

```bash
cp .env.example .env

# Edit .env with your configuration

```

1. Run the backend:

```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd web/frontend
```

1. Install dependencies:

```bash
npm install
```

1. Run development server:

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Running Both Services

You can run both backend and frontend simultaneously. The frontend is configured to proxy API requests to the backend.

## 📁 Project Structure

```
web/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── requirements.txt        # Backend dependencies
│   ├── .env.example           # Environment variables template
│   └── api/                   # API routes (future expansion)
│
└── frontend/
    ├── src/
    │   ├── components/        # React components
    │   │   ├── Login.jsx
    │   │   ├── Dashboard.jsx
    │   │   ├── UserManagement.jsx
    │   │   ├── ImageGeneration.jsx
    │   │   ├── DataAnalysis.jsx
    │   │   ├── LearningPaths.jsx
    │   │   └── SecurityResources.jsx
    │   ├── App.jsx            # Main app component
    │   └── main.jsx           # Entry point
    ├── public/                # Static assets
    ├── package.json           # Frontend dependencies
    └── vite.config.js         # Vite configuration
```

## 🔌 API Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### User Management

- `GET /api/users` - Get all users

### AI Features

- `POST /api/intent` - Detect user intent
- `POST /api/image/generate` - Generate images
- `POST /api/analysis` - Analyze data

### Learning & Resources

- `GET /api/learning-paths` - Get learning paths
- `GET /api/security-resources` - Get security resources

### Emergency

- `POST /api/emergency/alert` - Send emergency alert

## 🎨 Features Converted from Desktop to Web

| Desktop Feature    | Web Implementation | Status      |
| ------------------ | ------------------ | ----------- |
| Login Window       | `/login` route     | ✅ Ready    |
| Dashboard          | `/dashboard` route | ✅ Ready    |
| User Management    | `/users` route     | 🚧 Template |
| Image Generation   | `/image-gen` route | 🚧 Template |
| Data Analysis      | `/analysis` route  | 🚧 Template |
| Learning Paths     | `/learning` route  | 🚧 Template |
| Security Resources | `/security` route  | 🚧 Template |

## 🔧 Development

### Building for Production

**Frontend:**

```bash
cd web/frontend
npm run build
```

**Backend:** The Flask app can be deployed using Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Formatting & Linters (Frontend)

The frontend uses Prettier for code formatting. After pulling changes, run:

```bash
cd web/frontend
npm install
npm run format

# To enable ESLint linting, run `npm init @eslint/config` to create a config file.

```

## 🌟 Next Steps for Integration

1. **Connect Backend to Core Logic**: Wire up the Flask API endpoints to the actual `src/app/core/` modules
1. **Implement Authentication**: Add JWT-based authentication system
1. **Database Integration**: Set up SQLAlchemy models for persistent storage
1. **Complete Frontend Components**: Flesh out the template components with full functionality
1. **State Management**: Implement Zustand stores for global state
1. **Testing**: Add unit and integration tests
1. **Deployment**: Configure for production deployment (Docker, cloud hosting)

## 📝 Notes

- This branch is standalone and ready for integration
- All existing desktop functionality remains in `src/app/` unchanged
- The web version acts as a wrapper around existing core logic
- Can be merged into main when ready without breaking desktop version

## 🤝 Integration with Project-AI

When ready to integrate:

1. Merge this branch into main
1. Desktop app continues to work from `src/app/main.py`
1. Web app runs from `web/backend/app.py`
1. Both share the same core functionality in `src/app/core/`

## 📄 License

Same as Project-AI main project

______________________________________________________________________

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->
