/**
 * Real-time Collaborative Code Editor
 * Google Docs-style multi-user editing with Operational Transformation
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { MonacoBinding } from 'y-monaco';
import * as monaco from 'monaco-editor';

interface User {
  id: string;
  name: string;
  color: string;
  cursor: { line: number; column: number } | null;
  selection: { start: monaco.Position; end: monaco.Position } | null;
}

interface CollaborativeEditorProps {
  documentId: string;
  initialCode?: string;
  language?: string;
  onCodeChange?: (code: string) => void;
}

export const CollaborativeEditor: React.FC<CollaborativeEditorProps> = ({
  documentId,
  initialCode = '',
  language = 'typescript',
  onCodeChange,
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [editor, setEditor] = useState<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User>({
    id: generateUserId(),
    name: 'User ' + Math.floor(Math.random() * 1000),
    color: generateUserColor(),
    cursor: null,
    selection: null,
  });
  const [isConnected, setIsConnected] = useState(false);
  const ydocRef = useRef<Y.Doc | null>(null);
  const providerRef = useRef<WebsocketProvider | null>(null);
  const bindingRef = useRef<MonacoBinding | null>(null);

  // Initialize Yjs document and WebSocket provider
  useEffect(() => {
    if (!editorRef.current) return;

    // Create Monaco editor
    const monacoEditor = monaco.editor.create(editorRef.current, {
      value: initialCode,
      language: language,
      theme: 'vs-dark',
      automaticLayout: true,
      fontSize: 14,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      renderWhitespace: 'selection',
      formatOnPaste: true,
      formatOnType: true,
    });

    setEditor(monacoEditor);

    // Initialize Yjs
    const ydoc = new Y.Doc();
    ydocRef.current = ydoc;

    // Connect to WebSocket collaboration server
    const wsProvider = new WebsocketProvider(
      'ws://localhost:8080',
      `cognitive-ide-${documentId}`,
      ydoc,
      {
        connect: true,
      }
    );
    providerRef.current = wsProvider;

    // Set up awareness (user presence)
    const awareness = wsProvider.awareness;
    awareness.setLocalStateField('user', {
      name: currentUser.name,
      color: currentUser.color,
      id: currentUser.id,
    });

    // Monitor connection status
    wsProvider.on('status', (event: { status: string }) => {
      setIsConnected(event.status === 'connected');
    });

    // Monitor other users
    awareness.on('change', () => {
      const states = Array.from(awareness.getStates().values());
      const activeUsers: User[] = states
        .filter((state: any) => state.user && state.user.id !== currentUser.id)
        .map((state: any) => ({
          id: state.user.id,
          name: state.user.name,
          color: state.user.color,
          cursor: state.cursor || null,
          selection: state.selection || null,
        }));
      setUsers(activeUsers);
    });

    // Bind editor to Yjs document
    const ytext = ydoc.getText('monaco');
    const binding = new MonacoBinding(
      ytext,
      monacoEditor.getModel()!,
      new Set([monacoEditor]),
      awareness
    );
    bindingRef.current = binding;

    // Track local cursor and selection changes
    monacoEditor.onDidChangeCursorPosition((e) => {
      awareness.setLocalStateField('cursor', {
        line: e.position.lineNumber,
        column: e.position.column,
      });
    });

    monacoEditor.onDidChangeCursorSelection((e) => {
      awareness.setLocalStateField('selection', {
        start: e.selection.getStartPosition(),
        end: e.selection.getEndPosition(),
      });
    });

    // Notify parent of code changes
    monacoEditor.onDidChangeModelContent(() => {
      const code = monacoEditor.getValue();
      onCodeChange?.(code);
    });

    // Render other users' cursors
    renderUserCursors(monacoEditor, users);

    // Cleanup
    return () => {
      binding.destroy();
      wsProvider.destroy();
      ydoc.destroy();
      monacoEditor.dispose();
    };
  }, [documentId]);

  // Render user cursors and selections
  const renderUserCursors = useCallback(
    (editor: monaco.editor.IStandaloneCodeEditor, users: User[]) => {
      if (!editor) return;

      const decorations: string[] = [];

      users.forEach((user) => {
        if (user.cursor) {
          // Cursor decoration
          decorations.push(
            editor.createDecorationsCollection([
              {
                range: new monaco.Range(
                  user.cursor.line,
                  user.cursor.column,
                  user.cursor.line,
                  user.cursor.column
                ),
                options: {
                  className: 'user-cursor',
                  beforeContentClassName: 'user-cursor-marker',
                  glyphMarginClassName: 'user-cursor-glyph',
                  stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                },
              },
            ]) as any
          );
        }

        if (user.selection) {
          // Selection decoration
          decorations.push(
            editor.createDecorationsCollection([
              {
                range: new monaco.Range(
                  user.selection.start.lineNumber,
                  user.selection.start.column,
                  user.selection.end.lineNumber,
                  user.selection.end.column
                ),
                options: {
                  className: 'user-selection',
                  backgroundColor: user.color + '33', // 20% opacity
                  stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
                },
              },
            ]) as any
          );
        }
      });
    },
    []
  );

  // Update cursor rendering when users change
  useEffect(() => {
    if (editor) {
      renderUserCursors(editor, users);
    }
  }, [editor, users, renderUserCursors]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Editor container */}
      <div
        ref={editorRef}
        style={{
          width: '100%',
          height: 'calc(100% - 50px)',
          border: '2px solid #00ff41',
          borderRadius: '5px',
        }}
      />

      {/* Collaboration status bar */}
      <div
        style={{
          height: '50px',
          background: 'linear-gradient(180deg, #0d1f2a 0%, #061018 100%)',
          borderTop: '2px solid #ff9f00',
          display: 'flex',
          alignItems: 'center',
          padding: '0 15px',
          gap: '15px',
          fontFamily: 'Courier New',
          fontSize: '13px',
        }}
      >
        {/* Connection status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: isConnected ? '#00ff41' : '#ff4444',
          }}
        >
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: isConnected ? '#00ff41' : '#ff4444',
              boxShadow: isConnected
                ? '0 0 10px rgba(0, 255, 65, 0.5)'
                : '0 0 10px rgba(255, 68, 68, 0.5)',
            }}
          />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>

        {/* Current user */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#88ccff',
          }}
        >
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background: currentUser.color,
            }}
          />
          {currentUser.name} (You)
        </div>

        {/* Divider */}
        {users.length > 0 && (
          <div style={{ width: '1px', height: '30px', background: '#00ff41' }} />
        )}

        {/* Other users */}
        {users.map((user) => (
          <div
            key={user.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#88ccff',
            }}
          >
            <div
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: user.color,
              }}
            />
            {user.name}
          </div>
        ))}

        {users.length === 0 && (
          <div style={{ color: '#666', fontStyle: 'italic' }}>
            No other users online
          </div>
        )}

        {/* User count */}
        <div
          style={{
            marginLeft: 'auto',
            color: '#ff9f00',
            fontWeight: 'bold',
          }}
        >
          {users.length + 1} user{users.length !== 0 ? 's' : ''} online
        </div>
      </div>

      <style>{`
        .user-cursor {
          border-left: 2px solid;
          border-color: inherit;
        }
        .user-cursor-marker::before {
          content: '';
          position: absolute;
          width: 0;
          height: 0;
          border-left: 4px solid transparent;
          border-right: 4px solid transparent;
          border-top: 6px solid;
          border-color: inherit;
          margin-left: -3px;
        }
        .user-selection {
          opacity: 0.3;
        }
      `}</style>
    </div>
  );
};

// Utility functions
function generateUserId(): string {
  return Math.random().toString(36).substring(2, 15);
}

function generateUserColor(): string {
  const colors = [
    '#FF6B6B',
    '#4ECDC4',
    '#45B7D1',
    '#FFA07A',
    '#98D8C8',
    '#FFD93D',
    '#6BCF7F',
    '#C96DD8',
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

export default CollaborativeEditor;
