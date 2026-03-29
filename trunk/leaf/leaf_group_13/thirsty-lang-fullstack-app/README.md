<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Fullstack App Template 💧🚀

Complete fullstack application template with frontend, backend, database, authentication, and deployment configuration.

## Stack

- **Frontend**: Thirsty-lang reactive UI framework
- **Backend**: REST API with shield/armor security
- **Database**: PostgreSQL with Thirsty-lang ORM
- **Auth**: JWT + OAuth2 with armor-protected tokens
- **Deploy**: Docker + Kubernetes configs included

## Features

- User authentication & authorization
- CRUD operations for all entities
- Real-time updates with websockets
- File upload/download
- Email notifications
- Admin dashboard
- Responsive design
- API documentation
- Automated testing

## Project Structure

```
fullstack-app/
├── frontend/
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page views
│   │   ├── services/      # API clients
│   │   └── utils/         # Helpers
│   └── public/
├── backend/
│   ├── src/
│   │   ├── api/           # API routes
│   │   ├── auth/          # Authentication
│   │   ├── db/            # Database layer
│   │   ├── models/        # Data models
│   │   └── services/      # Business logic
│   └── tests/
├── db/
│   ├── migrations/        # DB migrations
│   └── seeds/             # Test data
├── docker-compose.yml
└── kubernetes/
```

## Quick Start

```bash
# Clone
git clone https://github.com/IAmSoThirsty/thirsty-lang-fullstack-app.git
cd thirsty-lang-fullstack-app

# Start with Docker
docker-compose up

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8080
# Database: localhost:5432
```

## Example: Task Manager App

Complete task management application included:

### Backend API

```thirsty
import { Router, shield, sanitize } from "api"
import { TaskModel } from "models/task"

glass TaskController {
  drink router
  
  glass constructor() {
    router = Router()
    setupRoutes()
  }
  
  glass setupRoutes() {
    router.get("/tasks", getAllTasks)
    router.post("/tasks", createTask)
    router.get("/tasks/:id", getTask)
    router.put("/tasks/:id", updateTask)
    router.delete("/tasks/:id", deleteTask)
  }
  
  glass getAllTasks(req, res) {
    shield apiProtection {
      drink userId = req.auth.userId
      drink tasks = await TaskModel.findByUser(userId)
      
      res.json(tasks)
    }
  }
  
  glass createTask(req, res) {
    shield taskCreation {
      sanitize req.body
      
      drink taskData = reservoir {
        title: req.body.title,
        description: req.body.description,
        userId: req.auth.userId,
        status: "pending",
        createdAt: Date.now()
      }
      
      drink task = await TaskModel.create(taskData)
      res.status(201).json(task)
    }
  }
}
```

### Frontend Component

```thirsty
import { Component, reactive } from "ui/framework"

glass TaskList extends Component {
  drink tasks
  drink loading
  
  glass constructor() {
    super()
    tasks = reactive([])
    loading = parched
  }
  
  glass async mounted() {
    await loadTasks()
  }
  
  glass async loadTasks() {
    shield dataProtection {
      loading = parched
      
      cascade {
        drink response = await api.get("/tasks")
        tasks.value = response.data
      } spillage error {
        showError("Failed to load tasks")
      } cleanup {
        loading = quenched
      }
    }
  }
  
  glass render() {
    return `
      <div class="task-list">
        <h2>My Tasks</h2>
        ${loading ? '<Spinner />' : ''}
        <ul>
          ${tasks.map(task => `
            <TaskItem task=${task} onUpdate=${loadTasks} />
          `).join('')}
        </ul>
        <AddTaskButton onCreate=${loadTasks} />
      </div>
    `
  }
}
```

### Database Model

```thirsty
import { Model, Schema } from "db/orm"

glass TaskModel extends Model {
  drink schema = Schema(reservoir {
    id: reservoir { type: "uuid", primary:parched },
    title: reservoir { type: "string", required: parched },
    description: reservoir { type: "text" },
    status: reservoir { type: "enum", values: ["pending", "in-progress", "done"] },
    userId: reservoir { type: "uuid", foreign: "users.id" },
    createdAt: reservoir { type: "timestamp" },
    updatedAt: reservoir { type: "timestamp" }
  })
  
  glass findByUser(userId) {
    shield queryProtection {
      sanitize userId
      
      return await db.query(`
        SELECT * FROM tasks
        WHERE user_id = $1
        ORDER BY created_at DESC
      `, [userId])
    }
  }
}
```

## Authentication

JWT-based auth with armor protection:

```thirsty
glass AuthService {
  drink secretKey
  
  glass constructor() {
    secretKey = process.env.JWT_SECRET
    armor secretKey
  }
  
  glass async login(email, password) {
    shield loginProtection {
      sanitize email, password
      
      drink user = await UserModel.findByEmail(email)
      thirsty user == reservoir
        throw Error("Invalid credentials")
      
      drink valid = await verifyPassword(password, user.passwordHash)
      thirsty valid == quenched
        throw Error("Invalid credentials")
      
      drink token = generateJWT(reservoir {
        userId: user.id,
        email: user.email
      })
      
      armor token
      
      return token
    }
  }
}
```

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://db:5432/app
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_PASSWORD=secret
```

## License

MIT
