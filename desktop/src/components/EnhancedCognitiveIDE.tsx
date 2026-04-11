/**
 * Enhanced Miniature Office - Cognitive IDE
 * Integrates VR/AR, Collaborative Editing, AI Pair Programming, and Simulation Visualization
 */

import React, { useState, useRef, useEffect } from 'react';
import CognitiveIDE_VR from './CognitiveIDE_VR';
import CollaborativeEditor from './CollaborativeEditor';
import { AIPairProgrammer, AIPairProgrammerPanel } from './AIPairProgrammer';
import SimulationVisualizer from './SimulationVisualizer';
import * as monaco from 'monaco-editor';

type ViewMode = 'desktop' | 'vr' | 'ar';
type PanelType = 'editor' | 'simulation' | 'ai-assistant';

interface EnhancedCognitiveIDEProps {
  initialMode?: ViewMode;
}

export const EnhancedCognitiveIDE: React.FC<EnhancedCognitiveIDEProps> = ({
  initialMode = 'desktop',
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>(initialMode);
  const [activePanel, setActivePanel] = useState<PanelType>('editor');
  const [currentFile, setCurrentFile] = useState<string>('main.py');
  const [code, setCode] = useState<string>('# Welcome to Enhanced Cognitive IDE\n');
  const [aiProgrammer] = useState(() => new AIPairProgrammer());
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  // Initialize AI programmer when editor is ready
  useEffect(() => {
    if (editorRef.current) {
      aiProgrammer.initialize(editorRef.current, 'python');
    }

    return () => {
      aiProgrammer.dispose();
    };
  }, [aiProgrammer]);

  const renderDesktopMode = () => {
    return (
      <div style={{ display: 'flex', height: '100vh', flexDirection: 'column' }}>
        {/* Header */}
        <header
          style={{
            height: '60px',
            background: 'linear-gradient(180deg, #1a3a4a 0%, #0d1f2a 100%)',
            borderBottom: '3px solid #ff9f00',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 20px',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.5)',
          }}
        >
          <div
            style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: '#ff9f00',
              fontFamily: 'Courier New',
            }}
          >
            ⚙ ENHANCED COGNITIVE IDE
          </div>

          {/* View mode selector */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => setViewMode('desktop')}
              style={getButtonStyle(viewMode === 'desktop')}
            >
              🖥️ Desktop
            </button>
            <button
              onClick={() => setViewMode('vr')}
              style={getButtonStyle(viewMode === 'vr')}
            >
              🥽 VR Mode
            </button>
            <button
              onClick={() => setViewMode('ar')}
              style={getButtonStyle(viewMode === 'ar')}
            >
              🔍 AR Mode
            </button>
          </div>
        </header>

        {/* Main content */}
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Sidebar */}
          <aside
            style={{
              width: '250px',
              background: 'linear-gradient(180deg, #0d1f2a 0%, #061018 100%)',
              borderRight: '2px solid #00ff41',
              padding: '20px',
              overflowY: 'auto',
            }}
          >
            <h3
              style={{
                color: '#ff9f00',
                marginBottom: '15px',
                fontFamily: 'Courier New',
              }}
            >
              Panels
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button
                onClick={() => setActivePanel('editor')}
                style={getSidebarButtonStyle(activePanel === 'editor')}
              >
                📝 Code Editor
              </button>
              <button
                onClick={() => setActivePanel('simulation')}
                style={getSidebarButtonStyle(activePanel === 'simulation')}
              >
                🎬 Simulation
              </button>
              <button
                onClick={() => setActivePanel('ai-assistant')}
                style={getSidebarButtonStyle(activePanel === 'ai-assistant')}
              >
                🤖 AI Assistant
              </button>
            </div>

            <hr
              style={{
                margin: '20px 0',
                border: 'none',
                borderTop: '1px solid #00ff41',
              }}
            />

            <h3
              style={{
                color: '#ff9f00',
                marginBottom: '15px',
                fontFamily: 'Courier New',
              }}
            >
              Files
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              {['main.py', 'utils.ts', 'config.rs', 'server.go'].map((file) => (
                <button
                  key={file}
                  onClick={() => setCurrentFile(file)}
                  style={{
                    padding: '8px 12px',
                    background:
                      currentFile === file
                        ? 'rgba(0, 255, 65, 0.2)'
                        : 'transparent',
                    border: '1px solid',
                    borderColor: currentFile === file ? '#00ff41' : '#1a3a4a',
                    color: '#00ff41',
                    cursor: 'pointer',
                    fontFamily: 'Courier New',
                    fontSize: '12px',
                    textAlign: 'left',
                    borderRadius: '3px',
                  }}
                >
                  {file}
                </button>
              ))}
            </div>
          </aside>

          {/* Main panel area */}
          <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {activePanel === 'editor' && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <CollaborativeEditor
                  documentId={currentFile}
                  initialCode={code}
                  language={getLanguageFromFile(currentFile)}
                  onCodeChange={setCode}
                />
                <AIPairProgrammerPanel programmer={aiProgrammer} />
              </div>
            )}

            {activePanel === 'simulation' && (
              <SimulationVisualizer autoRotate={true} showStats={true} />
            )}

            {activePanel === 'ai-assistant' && (
              <div
                style={{
                  flex: 1,
                  padding: '20px',
                  background: '#0a0e1a',
                  color: '#00ff41',
                  fontFamily: 'Courier New',
                }}
              >
                <h2 style={{ color: '#ff9f00', marginBottom: '20px' }}>
                  🤖 AI Pair Programming Assistant
                </h2>
                <p>
                  The AI assistant is actively monitoring your code for:
                </p>
                <ul style={{ marginTop: '15px', lineHeight: '1.8' }}>
                  <li>🔒 Security vulnerabilities</li>
                  <li>⚡ Performance optimizations</li>
                  <li>🐛 Logic errors and bugs</li>
                  <li>✨ Code quality improvements</li>
                  <li>📚 Best practices compliance</li>
                </ul>

                <div
                  style={{
                    marginTop: '30px',
                    padding: '15px',
                    background: 'rgba(0, 255, 65, 0.1)',
                    border: '1px solid #00ff41',
                    borderRadius: '5px',
                  }}
                >
                  <h3 style={{ color: '#88ccff', marginBottom: '10px' }}>
                    Recent Suggestions
                  </h3>
                  <div style={{ fontSize: '13px' }}>
                    Switch to the Code Editor panel to see AI suggestions in
                    real-time.
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    );
  };

  const renderVRMode = () => {
    return (
      <div style={{ width: '100%', height: '100vh' }}>
        <CognitiveIDE_VR />
      </div>
    );
  };

  const renderARMode = () => {
    return (
      <div
        style={{
          width: '100%',
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0a0e1a',
          color: '#00ff41',
          fontFamily: 'Courier New',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ color: '#ff9f00', marginBottom: '20px' }}>
            AR Mode (Preview)
          </h1>
          <p>AR features are being initialized...</p>
          <p style={{ marginTop: '10px', color: '#88ccff' }}>
            AR mode will overlay code panels and simulation data in your
            physical environment.
          </p>
          <button
            onClick={() => setViewMode('desktop')}
            style={{
              marginTop: '30px',
              padding: '12px 24px',
              background: 'linear-gradient(180deg, #1a3a4a 0%, #0d1f2a 100%)',
              border: '2px solid #00ff41',
              color: '#00ff41',
              cursor: 'pointer',
              fontFamily: 'Courier New',
              fontSize: '14px',
              borderRadius: '5px',
            }}
          >
            Back to Desktop
          </button>
        </div>
      </div>
    );
  };

  return (
    <>
      {viewMode === 'desktop' && renderDesktopMode()}
      {viewMode === 'vr' && renderVRMode()}
      {viewMode === 'ar' && renderARMode()}
    </>
  );
};

// Helper functions
function getButtonStyle(isActive: boolean): React.CSSProperties {
  return {
    padding: '10px 20px',
    background: isActive
      ? 'linear-gradient(180deg, #2a5a6a 0%, #1a3a4a 100%)'
      : 'linear-gradient(180deg, #1a3a4a 0%, #0d1f2a 100%)',
    border: '2px solid',
    borderColor: isActive ? '#ff9f00' : '#00ff41',
    color: isActive ? '#ff9f00' : '#00ff41',
    cursor: 'pointer',
    fontFamily: 'Courier New',
    fontSize: '14px',
    borderRadius: '5px',
    transition: 'all 0.2s',
    boxShadow: isActive ? '0 0 10px rgba(255, 159, 0, 0.5)' : 'none',
  };
}

function getSidebarButtonStyle(isActive: boolean): React.CSSProperties {
  return {
    padding: '12px 15px',
    background: isActive ? 'rgba(0, 255, 65, 0.2)' : 'rgba(0, 0, 0, 0.3)',
    border: '2px solid',
    borderColor: isActive ? '#00ff41' : '#1a3a4a',
    color: isActive ? '#ff9f00' : '#00ff41',
    cursor: 'pointer',
    fontFamily: 'Courier New',
    fontSize: '13px',
    borderRadius: '5px',
    textAlign: 'left',
    transition: 'all 0.2s',
  };
}

function getLanguageFromFile(filename: string): string {
  const ext = filename.split('.').pop();
  const languageMap: Record<string, string> = {
    py: 'python',
    ts: 'typescript',
    js: 'javascript',
    rs: 'rust',
    go: 'go',
    cpp: 'cpp',
    c: 'c',
  };
  return languageMap[ext || ''] || 'plaintext';
}

export default EnhancedCognitiveIDE;
