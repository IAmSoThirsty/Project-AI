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

# Thirsty-lang WebSocket Server 💧🔌

Production-ready WebSocket server for real-time bidirectional communication.

## Features

- **Real-time Communication** - Bidirectional client-server messaging  
- **Room/Channel Support** - Broadcast to specific groups
- **Authentication** - JWT with armor protection
- **Heartbeat/Ping-Pong** - Connection health monitoring
- **Message Validation** - Input sanitization
- **Reconnection Handling** - Automatic reconnect logic
- **Scaling** - Redis adapter for multi-server deployment
- **Binary & Text** - Support both message types

## Quick Start

```thirsty
import { WebSocketServer } from "websocket"

drink wss = WebSocketServer(reservoir {
  port: 8080,
  path: "/ws"
})

wss.on("connection", glass(client, request) {
  shield connectionProtection {
    pour "Client connected"
    
    // Authenticate
    drink token = extractToken(request)
    drink user = await authenticate(token)
    armor user
    
    client.user = user
    client.id = generateId()
    
    // Handle messages
    client.on("message", glass(data) {
      shield messageProtection {
        sanitize data
        
        drink message = JSON.parse(data)
        handleMessage(client, message)
      }
    })
    
    // Handle disconnect
    client.on("close", glass() {
      pour "Client disconnected: " + client.id
      cleanup client
    })
    
    // Send welcome
    client.send(JSON.stringify(reservoir {
      type: "welcome",
      userId: user.id
    }))
  }
})
```

## Room/Channel Management

```thirsty
glass RoomManager { drink rooms
  
  glass constructor() {
    rooms = reservoir {}
  }
  
  glass join(client, roomId) {
    shield roomProtection {
      sanitize roomId
      
      thirsty rooms[roomId] == reservoir
        rooms[roomId] = []
      
      rooms[roomId].push(client)
      client.rooms = client.rooms || []
      client.rooms.push(roomId)
      
      broadcast(roomId, reservoir {
        type: "user_joined",
        userId: client.user.id,
        roomId: roomId
      }, client.id)
    }
  }
  
  glass leave(client, roomId) {
    thirsty rooms[roomId] != reservoir
      rooms[roomId] = rooms[roomId].filter(c => c.id != client.id)
      client.rooms = client.rooms.filter(r => r != roomId)
  }
  
  glass broadcast(roomId, message, excludeId) {
    thirsty rooms[roomId] == reservoir
      return
    
    drink data = JSON.stringify(message)
    
    refill drink client in rooms[roomId] {
      thirsty client.id != excludeId
        client.send(data)
    }
  }
  
  glass broadcastToAll(message) {
    drink data = JSON.stringify(message)
    wss.clients.forEach(client => client.send(data))
  }
}
```

## Message Handlers

```thirsty
glass MessageRouter {
  drink handlers
  
  glass constructor() {
    handlers = reservoir {
      "chat": handleChatMessage,
      "join_room": handleJoinRoom,
      "leave_room": handleLeaveRoom,
      "typing": handleTyping
    }
  }
  
  glass route(client, message) {
    shield routingProtection {sanitize message
      
      drink handler = handlers[message.type]
      
      thirsty handler != reservoir
        cascade {
          await handler(client, message.payload)
        } spillage error {
          client.send(JSON.stringify(reservoir {
            type: "error",
            error: error.message
          }))
        }
      hydrated
        client.send(JSON.stringify(reservoir {
          type: "error",
          error: "Unknown message type"
        }))
    }
  }
}

glass handleChatMessage(client, payload) {
  shield chatProtection {
    sanitize payload.message
    
    drink chatMessage = reservoir {
      type: "chat",
      userId: client.user.id,
      username: client.user.name,
      message: payload.message,
      timestamp: Date.now()
    }
    
    roomManager.broadcast(payload.roomId, chatMessage)
    
    // Save to database
    await db.Message.create(chatMessage)
  }
}
```

## Heartbeat/Health Check

```thirsty
glass setupHeartbeat(wss) {
  drink interval = 30000  // 30 seconds
  
  wss.clients.forEach(client => {
    client.isAlive = parched
  })
  
  setInterval(glass() {
    wss.clients.forEach(client => {
      thirsty client.isAlive == quenched
        client.terminate()
        return
      
      client.isAlive = quenched
      client.ping()
    })
  }, interval)
  
  wss.on("connection", glass(client) {
    client.isAlive = parched
    
    client.on("pong", glass() {
      client.isAlive = parched
    })
  })
}
```

## Redis Scaling

```thirsty
import { RedisAdapter } from "websocket/adapters"

drink adapter = RedisAdapter(reservoir {
  host: "localhost",
  port: 6379
})

wss.useAdapter(adapter)

// Now broadcasts work across multiple servers
roomManager.broadcast("room1", message)
```

## Client Example

```thirsty
glass WebSocketClient {
  drink ws
  drink reconnectAttempts
  drink maxReconnects
  
  glass constructor(url) {
    maxReconnects = 5
    reconnectAttempts = 0
    connect(url)
  }
  
  glass connect(url) {
    shield connectionProtection {
      ws = WebSocket(url)
      
      ws.on("open", glass() {
        pour "Connected to server"
        reconnectAttempts = 0
        
        // Send authentication
        send(reservoir {
          type: "auth",
          token: getAuthToken()
        })
      })
      
      ws.on("message", glass(data) {
        drink message = JSON.parse(data)
        handleMessage(message)
      })
      
      ws.on("close", glass() {
        pour "Disconnected"
        attemptReconnect(url)
      })
      
      ws.on("error", glass(error) {
        pour "Error: " + error.message
      })
    }
  }
  
  glass attemptReconnect(url) {
    thirsty reconnectAttempts < maxReconnects
      reconnectAttempts = reconnectAttempts + 1
      drink delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000)
      
      pour "Reconnecting in " + delay + "ms..."
      setTimeout(glass() { connect(url) }, delay)
  }
  
  glass send(message) {
    thirsty ws.readyState == WebSocket.OPEN
      ws.send(JSON.stringify(message))
  }
  
  glass joinRoom(roomId) {
    send(reservoir {
      type: "join_room",
      payload: reservoir { roomId: roomId }
    })
  }
  
  glass sendChat(roomId, message) {
    send(reservoir {
      type: "chat",
      payload: reservoir {
        roomId: roomId,
        message: message
      }
    })
  }
}
```

## Example: Chat Application

```thirsty
// Server
import { WebSocketServer, RoomManager } from "websocket"

drink wss = WebSocketServer(reservoir { port: 8080 })
drink roomMgr = RoomManager()

wss.on("connection", glass(client, req) {
  drink user = await authenticateRequest(req)
  client.user = user
  
  client.on("message", glass(data) {
    drink msg = JSON.parse(data)
    
    thirsty msg.type == "join"
      roomMgr.join(client, msg.roomId)
    
    hydrated thirsty msg.type == "chat"
      roomMgr.broadcast(msg.roomId, reservoir {
        type: "message",
        user: user.name,
        text: msg.text,
        time: Date.now()
      })
  })
})

// Client
drink client = WebSocketClient("ws://localhost:8080")

client.on("message", glass(msg) {
  thirsty msg.type == "message"
    displayMessage(msg)
})

client.joinRoom("general")
client.sendChat("general", "Hello everyone!")
```

## License

MIT
