/**
 * WebSocket Collaboration Server
 * Handles real-time collaborative editing using Yjs
 */

const WebSocket = require('ws');
const http = require('http');
const Y = require('yjs');
const { setupWSConnection } = require('y-websocket/bin/utils');

const PORT = process.env.COLLAB_PORT || 8080;

// Create HTTP server
const server = http.createServer((request, response) => {
  response.writeHead(200, { 'Content-Type': 'text/plain' });
  response.end('Cognitive IDE Collaboration Server\n');
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Track active documents and users
const documents = new Map();
const userSessions = new Map();

wss.on('connection', (ws, req) => {
  console.log('New connection established');

  setupWSConnection(ws, req, {
    gc: true, // Enable garbage collection
  });

  // Track session
  const sessionId = generateSessionId();
  userSessions.set(sessionId, {
    ws,
    connectedAt: new Date(),
    documentId: null,
  });

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      handleMessage(sessionId, data);
    } catch (error) {
      // Binary messages are handled by y-websocket
    }
  });

  ws.on('close', () => {
    console.log(`Session ${sessionId} disconnected`);
    userSessions.delete(sessionId);
  });

  ws.on('error', (error) => {
    console.error(`WebSocket error for session ${sessionId}:`, error);
  });
});

// Handle custom messages
function handleMessage(sessionId, data) {
  const session = userSessions.get(sessionId);
  if (!session) return;

  switch (data.type) {
    case 'join_document':
      handleJoinDocument(sessionId, data.documentId);
      break;

    case 'leave_document':
      handleLeaveDocument(sessionId);
      break;

    case 'cursor_update':
      broadcastCursorUpdate(sessionId, data.cursor);
      break;

    case 'selection_update':
      broadcastSelectionUpdate(sessionId, data.selection);
      break;

    default:
      console.log('Unknown message type:', data.type);
  }
}

// Handle document joining
function handleJoinDocument(sessionId, documentId) {
  const session = userSessions.get(sessionId);
  if (!session) return;

  session.documentId = documentId;

  if (!documents.has(documentId)) {
    documents.set(documentId, {
      ydoc: new Y.Doc(),
      users: new Set(),
      createdAt: new Date(),
    });
  }

  const doc = documents.get(documentId);
  doc.users.add(sessionId);

  console.log(`Session ${sessionId} joined document ${documentId}`);
  console.log(`Document ${documentId} now has ${doc.users.size} user(s)`);

  // Notify other users
  broadcastToDocument(documentId, sessionId, {
    type: 'user_joined',
    sessionId,
    totalUsers: doc.users.size,
  });
}

// Handle document leaving
function handleLeaveDocument(sessionId) {
  const session = userSessions.get(sessionId);
  if (!session || !session.documentId) return;

  const documentId = session.documentId;
  const doc = documents.get(documentId);

  if (doc) {
    doc.users.delete(sessionId);
    console.log(`Session ${sessionId} left document ${documentId}`);

    // Notify other users
    broadcastToDocument(documentId, sessionId, {
      type: 'user_left',
      sessionId,
      totalUsers: doc.users.size,
    });

    // Clean up empty documents
    if (doc.users.size === 0) {
      documents.delete(documentId);
      console.log(`Document ${documentId} deleted (no users)`);
    }
  }

  session.documentId = null;
}

// Broadcast cursor update
function broadcastCursorUpdate(sessionId, cursor) {
  const session = userSessions.get(sessionId);
  if (!session || !session.documentId) return;

  broadcastToDocument(session.documentId, sessionId, {
    type: 'cursor_update',
    sessionId,
    cursor,
  });
}

// Broadcast selection update
function broadcastSelectionUpdate(sessionId, selection) {
  const session = userSessions.get(sessionId);
  if (!session || !session.documentId) return;

  broadcastToDocument(session.documentId, sessionId, {
    type: 'selection_update',
    sessionId,
    selection,
  });
}

// Broadcast message to all users in a document (except sender)
function broadcastToDocument(documentId, excludeSessionId, message) {
  const doc = documents.get(documentId);
  if (!doc) return;

  const messageStr = JSON.stringify(message);

  doc.users.forEach((userId) => {
    if (userId === excludeSessionId) return;

    const userSession = userSessions.get(userId);
    if (userSession && userSession.ws.readyState === WebSocket.OPEN) {
      userSession.ws.send(messageStr);
    }
  });
}

// Generate unique session ID
function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
}

// Start server
server.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('🚀 Cognitive IDE Collaboration Server Started');
  console.log('='.repeat(60));
  console.log(`WebSocket server listening on port ${PORT}`);
  console.log(`Server time: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\nShutting down collaboration server...');
  
  // Close all connections
  wss.clients.forEach((client) => {
    client.close();
  });

  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
});

module.exports = { server, wss };
