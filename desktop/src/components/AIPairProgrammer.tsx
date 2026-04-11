/**
 * AI Pair Programming System
 * Context-aware code suggestions and bug detection
 */

import React, { useState, useEffect, useCallback } from 'react';
import * as monaco from 'monaco-editor';

interface CodeSuggestion {
  id: string;
  type: 'completion' | 'refactor' | 'bug-fix' | 'optimization';
  severity: 'info' | 'warning' | 'error';
  line: number;
  column: number;
  message: string;
  suggestion: string;
  confidence: number;
}

interface BugDetection {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'security' | 'performance' | 'logic' | 'style';
  line: number;
  column: number;
  description: string;
  fix?: string;
}

interface AIContext {
  currentFile: string;
  language: string;
  recentEdits: Array<{ timestamp: number; change: string }>;
  imports: string[];
  functions: string[];
  variables: string[];
}

export class AIPairProgrammer {
  private editor: monaco.editor.IStandaloneCodeEditor | null = null;
  private context: AIContext;
  private suggestions: CodeSuggestion[] = [];
  private bugs: BugDetection[] = [];
  private analysisInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.context = {
      currentFile: '',
      language: '',
      recentEdits: [],
      imports: [],
      functions: [],
      variables: [],
    };
  }

  // Initialize with Monaco editor instance
  public initialize(editor: monaco.editor.IStandaloneCodeEditor, language: string) {
    this.editor = editor;
    this.context.language = language;

    // Set up real-time analysis
    this.setupRealtimeAnalysis();

    // Register completion provider
    this.registerCompletionProvider();

    // Register code actions provider
    this.registerCodeActionsProvider();

    // Start continuous analysis
    this.startContinuousAnalysis();
  }

  // Set up real-time code analysis
  private setupRealtimeAnalysis() {
    if (!this.editor) return;

    this.editor.onDidChangeModelContent((e) => {
      // Track recent edits for context
      this.context.recentEdits.push({
        timestamp: Date.now(),
        change: e.changes.map((c) => c.text).join(''),
      });

      // Keep only last 50 edits
      if (this.context.recentEdits.length > 50) {
        this.context.recentEdits = this.context.recentEdits.slice(-50);
      }

      // Analyze code for bugs
      this.analyzeCode();

      // Update context
      this.updateContext();
    });
  }

  // Register AI-powered completion provider
  private registerCompletionProvider() {
    if (!this.editor) return;

    monaco.languages.registerCompletionItemProvider(this.context.language, {
      provideCompletionItems: async (model, position) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column,
        });

        const suggestions = await this.getAISuggestions(textUntilPosition, position);

        return {
          suggestions: suggestions.map((sug) => ({
            label: sug.message,
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: sug.suggestion,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: `AI Confidence: ${(sug.confidence * 100).toFixed(0)}%`,
            range: new monaco.Range(
              position.lineNumber,
              position.column,
              position.lineNumber,
              position.column
            ),
          })),
        };
      },
    });
  }

  // Register code actions provider (quick fixes)
  private registerCodeActionsProvider() {
    if (!this.editor) return;

    monaco.languages.registerCodeActionProvider(this.context.language, {
      provideCodeActions: (model, range, context) => {
        const actions: monaco.languages.CodeAction[] = [];

        // Get bugs in the current range
        const bugsInRange = this.bugs.filter(
          (bug) =>
            bug.line >= range.startLineNumber && bug.line <= range.endLineNumber
        );

        bugsInRange.forEach((bug) => {
          if (bug.fix) {
            actions.push({
              title: `🤖 AI Fix: ${bug.description}`,
              diagnostics: [],
              kind: 'quickfix',
              edit: {
                edits: [
                  {
                    resource: model.uri,
                    textEdit: {
                      range: new monaco.Range(bug.line, 1, bug.line, 1000),
                      text: bug.fix,
                    },
                    versionId: undefined,
                  },
                ],
              },
              isPreferred: true,
            });
          }
        });

        return { actions, dispose: () => {} };
      },
    });
  }

  // Get AI-powered code suggestions
  private async getAISuggestions(
    code: string,
    position: monaco.Position
  ): Promise<CodeSuggestion[]> {
    // Analyze current context
    const context = this.buildAnalysisContext(code);

    // Call AI model for suggestions
    const suggestions = await this.callAIModel(code, context, position);

    return suggestions;
  }

  // Build analysis context from code
  private buildAnalysisContext(code: string): any {
    const lines = code.split('\n');
    const imports: string[] = [];
    const functions: string[] = [];
    const variables: string[] = [];

    lines.forEach((line) => {
      // Extract imports
      if (line.includes('import ') || line.includes('from ')) {
        imports.push(line.trim());
      }

      // Extract function definitions
      const funcMatch = line.match(/(?:function|def|const|let|var)\s+(\w+)/);
      if (funcMatch) {
        functions.push(funcMatch[1]);
      }

      // Extract variable declarations
      const varMatch = line.match(/(?:const|let|var)\s+(\w+)/);
      if (varMatch) {
        variables.push(varMatch[1]);
      }
    });

    return {
      imports,
      functions,
      variables,
      language: this.context.language,
      recentEdits: this.context.recentEdits.slice(-10),
    };
  }

  // Call AI model for analysis
  private async callAIModel(
    code: string,
    context: any,
    position: monaco.Position
  ): Promise<CodeSuggestion[]> {
    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          context,
          position: { line: position.lineNumber, column: position.column },
          language: this.context.language,
        }),
      });

      const data = await response.json();
      return data.suggestions || [];
    } catch (error) {
      console.error('AI analysis failed:', error);
      return this.getFallbackSuggestions(code, position);
    }
  }

  // Fallback suggestions using heuristics
  private getFallbackSuggestions(
    code: string,
    position: monaco.Position
  ): CodeSuggestion[] {
    const suggestions: CodeSuggestion[] = [];
    const lines = code.split('\n');
    const currentLine = lines[position.lineNumber - 1] || '';

    // Common patterns
    if (currentLine.includes('console.log')) {
      suggestions.push({
        id: 'log-cleanup',
        type: 'optimization',
        severity: 'info',
        line: position.lineNumber,
        column: position.column,
        message: 'Consider removing console.log in production',
        suggestion: '// TODO: Remove debug logging',
        confidence: 0.8,
      });
    }

    if (currentLine.includes('var ')) {
      suggestions.push({
        id: 'var-to-const',
        type: 'refactor',
        severity: 'warning',
        line: position.lineNumber,
        column: position.column,
        message: 'Use const or let instead of var',
        suggestion: currentLine.replace('var ', 'const '),
        confidence: 0.95,
      });
    }

    return suggestions;
  }

  // Analyze code for bugs
  private async analyzeCode() {
    if (!this.editor) return;

    const code = this.editor.getValue();
    const bugs = await this.detectBugs(code);

    this.bugs = bugs;
    this.updateMarkers();
  }

  // Detect bugs in code
  private async detectBugs(code: string): Promise<BugDetection[]> {
    const bugs: BugDetection[] = [];
    const lines = code.split('\n');

    lines.forEach((line, index) => {
      // Security: SQL injection risk
      if (line.includes('execute(') && line.includes('+')) {
        bugs.push({
          id: `sql-injection-${index}`,
          severity: 'critical',
          category: 'security',
          line: index + 1,
          column: 1,
          description: 'Potential SQL injection vulnerability',
          fix: '// Use parameterized queries instead',
        });
      }

      // Performance: synchronous operations
      if (line.includes('readFileSync') || line.includes('execSync')) {
        bugs.push({
          id: `sync-op-${index}`,
          severity: 'medium',
          category: 'performance',
          line: index + 1,
          column: 1,
          description: 'Synchronous operation may block event loop',
          fix: line.replace('Sync', '').replace('(', 'Async('),
        });
      }

      // Logic: uninitialized variables
      if (line.match(/let\s+\w+;/) || line.match(/var\s+\w+;/)) {
        bugs.push({
          id: `uninit-var-${index}`,
          severity: 'low',
          category: 'logic',
          line: index + 1,
          column: 1,
          description: 'Variable declared but not initialized',
        });
      }

      // Style: long lines
      if (line.length > 120) {
        bugs.push({
          id: `long-line-${index}`,
          severity: 'low',
          category: 'style',
          line: index + 1,
          column: 1,
          description: 'Line exceeds 120 characters',
        });
      }
    });

    return bugs;
  }

  // Update editor markers with detected bugs
  private updateMarkers() {
    if (!this.editor) return;

    const model = this.editor.getModel();
    if (!model) return;

    const markers: monaco.editor.IMarkerData[] = this.bugs.map((bug) => ({
      severity:
        bug.severity === 'critical' || bug.severity === 'high'
          ? monaco.MarkerSeverity.Error
          : bug.severity === 'medium'
          ? monaco.MarkerSeverity.Warning
          : monaco.MarkerSeverity.Info,
      message: `[AI] ${bug.description}`,
      startLineNumber: bug.line,
      startColumn: bug.column,
      endLineNumber: bug.line,
      endColumn: 1000,
      tags:
        bug.category === 'security'
          ? [monaco.MarkerTag.Unnecessary]
          : undefined,
    }));

    monaco.editor.setModelMarkers(model, 'ai-pair-programmer', markers);
  }

  // Update context from current code
  private updateContext() {
    if (!this.editor) return;

    const code = this.editor.getValue();
    const context = this.buildAnalysisContext(code);

    this.context.imports = context.imports;
    this.context.functions = context.functions;
    this.context.variables = context.variables;
  }

  // Start continuous analysis
  private startContinuousAnalysis() {
    this.analysisInterval = setInterval(() => {
      this.analyzeCode();
    }, 2000); // Analyze every 2 seconds
  }

  // Get current suggestions
  public getSuggestions(): CodeSuggestion[] {
    return this.suggestions;
  }

  // Get detected bugs
  public getBugs(): BugDetection[] {
    return this.bugs;
  }

  // Cleanup
  public dispose() {
    if (this.analysisInterval) {
      clearInterval(this.analysisInterval);
    }
  }
}

// React component wrapper
interface AIPairProgrammerPanelProps {
  programmer: AIPairProgrammer;
}

export const AIPairProgrammerPanel: React.FC<AIPairProgrammerPanelProps> = ({
  programmer,
}) => {
  const [bugs, setBugs] = useState<BugDetection[]>([]);
  const [suggestions, setSuggestions] = useState<CodeSuggestion[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBugs(programmer.getBugs());
      setSuggestions(programmer.getSuggestions());
    }, 1000);

    return () => clearInterval(interval);
  }, [programmer]);

  const severityColors = {
    critical: '#ff0000',
    high: '#ff4444',
    medium: '#ff9f00',
    low: '#ffff00',
  };

  return (
    <div
      style={{
        width: '100%',
        padding: '15px',
        background: 'linear-gradient(180deg, #0d1f2a 0%, #061018 100%)',
        borderTop: '2px solid #00ff41',
        fontFamily: 'Courier New',
        fontSize: '13px',
        color: '#00ff41',
      }}
    >
      <h3 style={{ color: '#ff9f00', marginBottom: '10px' }}>
        🤖 AI Pair Programmer
      </h3>

      {/* Bugs section */}
      <div style={{ marginBottom: '15px' }}>
        <h4 style={{ color: '#88ccff', marginBottom: '8px' }}>
          Detected Issues ({bugs.length})
        </h4>
        {bugs.length === 0 ? (
          <div style={{ color: '#00ff41', fontStyle: 'italic' }}>
            ✓ No issues detected
          </div>
        ) : (
          <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {bugs.map((bug) => (
              <div
                key={bug.id}
                style={{
                  padding: '8px',
                  margin: '5px 0',
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderLeft: `3px solid ${severityColors[bug.severity]}`,
                  borderRadius: '2px',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: '4px',
                  }}
                >
                  <span style={{ color: severityColors[bug.severity] }}>
                    Line {bug.line} - {bug.category.toUpperCase()}
                  </span>
                  <span style={{ color: '#88ccff' }}>
                    {bug.severity.toUpperCase()}
                  </span>
                </div>
                <div style={{ color: '#fff' }}>{bug.description}</div>
                {bug.fix && (
                  <div
                    style={{
                      marginTop: '4px',
                      padding: '4px',
                      background: 'rgba(0, 255, 65, 0.1)',
                      color: '#00ff41',
                      fontSize: '11px',
                    }}
                  >
                    Fix: {bug.fix}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suggestions section */}
      <div>
        <h4 style={{ color: '#88ccff', marginBottom: '8px' }}>
          AI Suggestions ({suggestions.length})
        </h4>
        {suggestions.length === 0 ? (
          <div style={{ color: '#666', fontStyle: 'italic' }}>
            Type to get AI suggestions...
          </div>
        ) : (
          <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {suggestions.map((sug) => (
              <div
                key={sug.id}
                style={{
                  padding: '8px',
                  margin: '5px 0',
                  background: 'rgba(0, 255, 65, 0.1)',
                  border: '1px solid #00ff41',
                  borderRadius: '2px',
                }}
              >
                <div style={{ marginBottom: '4px' }}>
                  <span style={{ color: '#ff9f00' }}>
                    {sug.type.toUpperCase()}
                  </span>{' '}
                  - Confidence: {(sug.confidence * 100).toFixed(0)}%
                </div>
                <div style={{ color: '#fff' }}>{sug.message}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIPairProgrammer;
