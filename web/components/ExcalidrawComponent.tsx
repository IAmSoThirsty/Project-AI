"use client";

import React, { useState, useEffect, useRef } from 'react';

/**
 * Excalidraw Integration Component for Project-AI
 * 
 * Provides visual diagramming capabilities using Excalidraw's embed mode.
 * Supports diagram creation, editing, saving, and exporting.
 * 
 * Features:
 * - Hand-drawn style diagrams
 * - Architecture visualization
 * - Real-time editing
 * - Export to PNG, SVG, JSON
 * - Local storage persistence
 */

interface ExcalidrawDiagram {
  id: string;
  name: string;
  description: string;
  created_at: string;
  modified_at: string;
  content?: string;
}

interface ExcalidrawComponentProps {
  /** Initial diagram to load */
  initialDiagram?: ExcalidrawDiagram;
  /** Callback when diagram is saved */
  onSave?: (diagram: ExcalidrawDiagram, content: string) => void;
  /** Callback when diagram is exported */
  onExport?: (format: string, data: Blob) => void;
  /** Height of the editor */
  height?: string;
  /** Enable dark mode */
  darkMode?: boolean;
}

export default function ExcalidrawComponent({
  initialDiagram,
  onSave,
  onExport,
  height = "600px",
  darkMode = false,
}: ExcalidrawComponentProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [currentDiagram, setCurrentDiagram] = useState<ExcalidrawDiagram | null>(
    initialDiagram || null
  );
  const [diagrams, setDiagrams] = useState<ExcalidrawDiagram[]>([]);
  const [showNewDiagramModal, setShowNewDiagramModal] = useState(false);
  const [newDiagramName, setNewDiagramName] = useState("");
  const [newDiagramDescription, setNewDiagramDescription] = useState("");
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Load diagrams from localStorage on mount
  useEffect(() => {
    const storedDiagrams = localStorage.getItem("excalidraw_diagrams");
    if (storedDiagrams) {
      try {
        setDiagrams(JSON.parse(storedDiagrams));
      } catch (e) {
        console.error("Failed to load diagrams:", e);
      }
    }
    setIsLoading(false);
  }, []);

  // Save diagrams to localStorage whenever they change
  useEffect(() => {
    if (diagrams.length > 0) {
      localStorage.setItem("excalidraw_diagrams", JSON.stringify(diagrams));
    }
  }, [diagrams]);

  const createNewDiagram = () => {
    if (!newDiagramName.trim()) {
      alert("Please enter a diagram name");
      return;
    }

    const newDiagram: ExcalidrawDiagram = {
      id: `diagram_${Date.now()}`,
      name: newDiagramName,
      description: newDiagramDescription,
      created_at: new Date().toISOString(),
      modified_at: new Date().toISOString(),
    };

    setDiagrams([...diagrams, newDiagram]);
    setCurrentDiagram(newDiagram);
    setShowNewDiagramModal(false);
    setNewDiagramName("");
    setNewDiagramDescription("");
  };

  const loadDiagram = (diagram: ExcalidrawDiagram) => {
    setCurrentDiagram(diagram);
    
    // Send diagram data to iframe if it has content
    if (diagram.content && iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: "excalidraw:load",
          data: JSON.parse(diagram.content),
        },
        "*"
      );
    }
  };

  const saveDiagram = () => {
    if (!currentDiagram) {
      alert("No diagram selected");
      return;
    }

    // Request diagram data from iframe
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        { type: "excalidraw:export" },
        "*"
      );
    }
  };

  // Handle messages from Excalidraw iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "excalidraw:export-data" && currentDiagram) {
        const content = JSON.stringify(event.data.data);
        const updatedDiagram = {
          ...currentDiagram,
          content,
          modified_at: new Date().toISOString(),
        };

        setDiagrams(diagrams.map(d => 
          d.id === currentDiagram.id ? updatedDiagram : d
        ));
        setCurrentDiagram(updatedDiagram);

        if (onSave) {
          onSave(updatedDiagram, content);
        }

        alert("Diagram saved successfully!");
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [currentDiagram, diagrams, onSave]);

  const exportDiagram = async (format: "png" | "svg" | "json") => {
    if (!currentDiagram) {
      alert("No diagram selected");
      return;
    }

    // Request export from iframe
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: "excalidraw:export",
          format,
        },
        "*"
      );
    }
  };

  const excalidrawUrl = `https://excalidraw.com${darkMode ? "?theme=dark" : ""}`;

  return (
    <div className="excalidraw-container" style={{ height: "100%" }}>
      {/* Toolbar */}
      <div className="excalidraw-toolbar" style={{
        padding: "1rem",
        backgroundColor: darkMode ? "#1a1a1a" : "#f5f5f5",
        borderBottom: "1px solid " + (darkMode ? "#333" : "#ddd"),
        display: "flex",
        gap: "1rem",
        alignItems: "center",
        flexWrap: "wrap",
      }}>
        <button
          onClick={() => setShowNewDiagramModal(true)}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          + New Diagram
        </button>

        <select
          value={currentDiagram?.id || ""}
          onChange={(e) => {
            const diagram = diagrams.find(d => d.id === e.target.value);
            if (diagram) loadDiagram(diagram);
          }}
          style={{
            padding: "0.5rem",
            borderRadius: "4px",
            border: "1px solid " + (darkMode ? "#444" : "#ccc"),
            backgroundColor: darkMode ? "#2a2a2a" : "white",
            color: darkMode ? "white" : "black",
          }}
        >
          <option value="">Select a diagram...</option>
          {diagrams.map(d => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>

        {currentDiagram && (
          <>
            <button
              onClick={saveDiagram}
              style={{
                padding: "0.5rem 1rem",
                backgroundColor: "#2196F3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              💾 Save
            </button>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                onClick={() => exportDiagram("png")}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: "#FF9800",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Export PNG
              </button>
              <button
                onClick={() => exportDiagram("svg")}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: "#9C27B0",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Export SVG
              </button>
              <button
                onClick={() => exportDiagram("json")}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: "#607D8B",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Export JSON
              </button>
            </div>

            <span style={{
              marginLeft: "auto",
              color: darkMode ? "#aaa" : "#666",
              fontSize: "0.9rem",
            }}>
              {currentDiagram.name}
            </span>
          </>
        )}
      </div>

      {/* Excalidraw iframe */}
      <div style={{ height: `calc(100% - 70px)` }}>
        {isLoading ? (
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            color: darkMode ? "white" : "black",
          }}>
            Loading Excalidraw...
          </div>
        ) : (
          <iframe
            ref={iframeRef}
            src={excalidrawUrl}
            style={{
              width: "100%",
              height: "100%",
              border: "none",
            }}
            allow="clipboard-read; clipboard-write"
            title="Excalidraw Drawing Canvas"
          />
        )}
      </div>

      {/* New Diagram Modal */}
      {showNewDiagramModal && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: darkMode ? "#2a2a2a" : "white",
            padding: "2rem",
            borderRadius: "8px",
            maxWidth: "500px",
            width: "90%",
          }}>
            <h2 style={{
              margin: "0 0 1rem 0",
              color: darkMode ? "white" : "black",
            }}>
              Create New Diagram
            </h2>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{
                display: "block",
                marginBottom: "0.5rem",
                color: darkMode ? "#ddd" : "#333",
              }}>
                Diagram Name *
              </label>
              <input
                type="text"
                value={newDiagramName}
                onChange={(e) => setNewDiagramName(e.target.value)}
                placeholder="e.g., System Architecture"
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid " + (darkMode ? "#444" : "#ccc"),
                  backgroundColor: darkMode ? "#1a1a1a" : "white",
                  color: darkMode ? "white" : "black",
                }}
              />
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{
                display: "block",
                marginBottom: "0.5rem",
                color: darkMode ? "#ddd" : "#333",
              }}>
                Description (optional)
              </label>
              <textarea
                value={newDiagramDescription}
                onChange={(e) => setNewDiagramDescription(e.target.value)}
                placeholder="Brief description of the diagram..."
                rows={3}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid " + (darkMode ? "#444" : "#ccc"),
                  backgroundColor: darkMode ? "#1a1a1a" : "white",
                  color: darkMode ? "white" : "black",
                  resize: "vertical",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
              <button
                onClick={() => {
                  setShowNewDiagramModal(false);
                  setNewDiagramName("");
                  setNewDiagramDescription("");
                }}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: darkMode ? "#444" : "#ccc",
                  color: darkMode ? "white" : "black",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              <button
                onClick={createNewDiagram}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor: "#4CAF50",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
