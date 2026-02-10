/**
 * Main dashboard component with all AI features
 */

'use client';

import { useState } from 'react';
import { User } from '@/lib/store';

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

type TabType = 'overview' | 'persona' | 'image-gen' | 'data-analysis' | 'learning' | 'security' | 'emergency';

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'persona', label: 'AI Persona', icon: '🤖' },
    { id: 'image-gen', label: 'Image Generation', icon: '🎨' },
    { id: 'data-analysis', label: 'Data Analysis', icon: '📈' },
    { id: 'learning', label: 'Learning Paths', icon: '📚' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'emergency', label: 'Emergency', icon: '🚨' },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gray-900/50 border-b border-gray-800 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--primary)' }}>
                Project-AI Dashboard
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Welcome, <span className="font-semibold">{user.username}</span> ({user.role})
              </p>
            </div>
            <button
              onClick={onLogout}
              className="button button-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-900/30 border-b border-gray-800">
        <div className="container mx-auto px-4">
          <div className="flex gap-2 overflow-x-auto py-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white font-semibold'
                    : 'bg-gray-800/50 text-gray-300 hover:bg-gray-800'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'overview' && <OverviewTab user={user} />}
        {activeTab === 'persona' && <PersonaTab />}
        {activeTab === 'image-gen' && <ImageGenerationTab />}
        {activeTab === 'data-analysis' && <DataAnalysisTab />}
        {activeTab === 'learning' && <LearningTab />}
        {activeTab === 'security' && <SecurityTab />}
        {activeTab === 'emergency' && <EmergencyTab />}
      </main>
    </div>
  );
}

function OverviewTab({ user }: { user: User }) {
  const features = [
    {
      title: 'Four Laws Ethics Engine',
      description: 'Immutable ethics framework validating actions against hierarchical rules (Asimov\'s Laws)',
      status: 'Active',
      icon: '⚖️',
    },
    {
      title: 'AI Persona System',
      description: '8 personality traits with mood tracking and persistent state management',
      status: 'Active',
      icon: '🧠',
    },
    {
      title: 'Memory Expansion',
      description: 'Conversation logging with categorized knowledge base (6 categories)',
      status: 'Active',
      icon: '💾',
    },
    {
      title: 'Learning Manager',
      description: 'Human-in-the-loop approval workflow with Black Vault for denied content',
      status: 'Active',
      icon: '🎓',
    },
    {
      title: 'Image Generation',
      description: 'Dual backend support (HF Stable Diffusion, OpenAI DALL-E 3) with content filtering',
      status: 'Available',
      icon: '🎨',
    },
    {
      title: 'Data Analysis',
      description: 'CSV/XLSX/JSON analysis with K-means clustering and ML capabilities',
      status: 'Available',
      icon: '📊',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Welcome to Project-AI</h2>
        <p className="text-gray-300 mb-4">
          A sophisticated AI assistant with ethical decision-making, autonomous learning, and
          comprehensive security features.
        </p>
        <div className="flex gap-4 flex-wrap">
          <div className="badge badge-success">Production Ready</div>
          <div className="badge badge-info">Next.js 14</div>
          <div className="badge badge-info">TypeScript</div>
          <div className="badge badge-info">Zustand State Management</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <div key={index} className="card hover:border-purple-500/50 transition-all">
            <div className="text-4xl mb-3">{feature.icon}</div>
            <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-400 mb-3">{feature.description}</p>
            <div className={`badge ${feature.status === 'Active' ? 'badge-success' : 'badge-info'}`}>
              {feature.status}
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="text-xl font-bold mb-4">System Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-400">User:</p>
            <p className="font-mono">{user.username}</p>
          </div>
          <div>
            <p className="text-gray-400">Role:</p>
            <p className="font-mono">{user.role}</p>
          </div>
          <div>
            <p className="text-gray-400">Backend:</p>
            <p className="font-mono">Flask API (Python)</p>
          </div>
          <div>
            <p className="text-gray-400">Frontend:</p>
            <p className="font-mono">Next.js 14 (React)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function PersonaTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">🤖 AI Persona Configuration</h2>
      <p className="text-gray-300 mb-6">
        Configure the AI personality traits, mood tracking, and interaction preferences.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Personality Traits</h3>
          <p className="text-sm text-gray-400">
            8 configurable traits including creativity, empathy, humor, and more.
          </p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Mood Tracking</h3>
          <p className="text-sm text-gray-400">
            Real-time mood analysis based on interactions and context.
          </p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">State Persistence</h3>
          <p className="text-sm text-gray-400">
            Persistent storage in data/ai_persona/state.json for continuity.
          </p>
        </div>
      </div>
    </div>
  );
}

function ImageGenerationTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">🎨 Image Generation</h2>
      <p className="text-gray-300 mb-6">
        Generate images using AI with dual backend support and content filtering.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Backends Available</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>Hugging Face Stable Diffusion 2.1</li>
            <li>OpenAI DALL-E 3</li>
          </ul>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Features</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>10 style presets (photorealistic, anime, abstract, etc.)</li>
            <li>Content filtering with 15+ blocked keywords</li>
            <li>Generation history tracking</li>
            <li>Automatic safety negative prompts</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function DataAnalysisTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">📈 Data Analysis</h2>
      <p className="text-gray-300 mb-6">
        Analyze CSV, XLSX, and JSON files with machine learning capabilities.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Supported Formats</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>CSV files with automatic delimiter detection</li>
            <li>Excel (XLSX) workbooks</li>
            <li>JSON structured data</li>
          </ul>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Analysis Features</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>K-means clustering</li>
            <li>Statistical summaries</li>
            <li>Data visualization</li>
            <li>Correlation analysis</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function LearningTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">📚 Learning Paths</h2>
      <p className="text-gray-300 mb-6">
        AI-powered learning path generation with human-in-the-loop approval.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Request System</h3>
          <p className="text-sm text-gray-400">
            Submit learning requests that require human approval before integration.
          </p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Black Vault</h3>
          <p className="text-sm text-gray-400">
            SHA-256 fingerprinting system to prevent re-submission of denied content.
          </p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Knowledge Base</h3>
          <p className="text-sm text-gray-400">
            6 categorized knowledge areas with JSON persistence.
          </p>
        </div>
      </div>
    </div>
  );
}

function SecurityTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">🔒 Security Resources</h2>
      <p className="text-gray-300 mb-6">
        Security tools, CTF challenges, and vulnerability research resources.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">GitHub Integration</h3>
          <p className="text-sm text-gray-400">
            Access to security repositories, CTF challenges, and penetration testing tools.
          </p>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Security Features</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>Input validation on all forms</li>
            <li>XSS prevention with output encoding</li>
            <li>CSRF protection with tokens</li>
            <li>Rate limiting on API endpoints</li>
            <li>Security headers (CSP, X-Frame-Options, etc.)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function EmergencyTab() {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4">🚨 Emergency Alerts</h2>
      <p className="text-gray-300 mb-6">
        Emergency contact system with email alert capabilities.
      </p>
      <div className="space-y-4">
        <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
          <h3 className="font-semibold mb-2 text-red-400">⚠️ Emergency Features</h3>
          <ul className="text-sm text-gray-400 list-disc list-inside space-y-1">
            <li>Immediate email notifications</li>
            <li>Contact management system</li>
            <li>Alert history tracking</li>
            <li>Multiple recipient support</li>
          </ul>
        </div>
        <div className="p-4 bg-gray-800/50 rounded-lg">
          <h3 className="font-semibold mb-2">Configuration Required</h3>
          <p className="text-sm text-gray-400">
            Set SMTP_USERNAME and SMTP_PASSWORD in environment variables to enable email alerts.
          </p>
        </div>
      </div>
    </div>
  );
}
