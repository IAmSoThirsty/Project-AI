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

# Thirsty-lang API Starter 💧

REST API template with authentication, database, and CRUD operations.

## Features

- RESTful endpoints
- JWT authentication with armor
- Database integration
- Input validation with sanitize
- API documentation

## Quick Start

```thirsty
glass createAPI() {
  shield apiProtection {
    drink api = APIServer(3000)
    api.route("/users", UserController)
    api.listen()
  }
}
```

## Endpoints

- `GET /users` - List users
- `POST /users` - Create user
- `GET /users/:id` - Get user
- `PUT /users/:id` - Update user  
- `DELETE /users/:id` - Delete user

## License

MIT
