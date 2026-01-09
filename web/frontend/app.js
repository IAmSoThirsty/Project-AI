/**
 * Project-AI Web SPA - Main Application Entry Point
 * 
 * This file provides the foundation for a React-like SPA experience
 * with component-based architecture and state management.
 */

// Application state
const AppState = {
  user: null,
  token: null,
  components: {},
  isOnline: false,
};

// Component registry
class ComponentRegistry {
  constructor() {
    this.components = new Map();
  }

  register(name, component) {
    this.components.set(name, component);
  }

  get(name) {
    return this.components.get(name);
  }

  mount(name, target) {
    const component = this.get(name);
    if (component) {
      component.mount(target);
    }
  }
}

// Base Component class
class Component {
  constructor(props = {}) {
    this.props = props;
    this.state = {};
    this.element = null;
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.render();
  }

  mount(target) {
    this.element = target;
    this.render();
  }

  render() {
    // Override in subclasses
  }
}

// Status Component
class StatusComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      status: 'checking',
      message: 'Connecting to backend...',
    };
  }

  async checkStatus() {
    try {
      const response = await fetch('/api/status');
      if (!response.ok) throw new Error('network');
      const data = await response.json();
      this.setState({
        status: 'online',
        message: `${data.component} is ${data.status}`,
      });
      AppState.isOnline = true;
    } catch (error) {
      this.setState({
        status: 'offline',
        message: 'Backend unavailable (Flask not running)',
      });
      AppState.isOnline = false;
    }
  }

  mount(target) {
    super.mount(target);
    this.checkStatus();
    setInterval(() => this.checkStatus(), 5000);
  }

  render() {
    if (!this.element) return;
    
    const statusClass = this.state.status === 'online' ? 'status online' : 'status offline';
    this.element.className = statusClass;
    this.element.textContent = this.state.message;
  }
}

// Initialize application
const registry = new ComponentRegistry();

document.addEventListener('DOMContentLoaded', () => {
  // Register components
  const statusComponent = new StatusComponent();
  registry.register('status', statusComponent);
  
  // Mount components
  const statusEl = document.getElementById('status');
  if (statusEl) {
    registry.mount('status', statusEl);
  }

  // Update year in footer
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Component, ComponentRegistry, StatusComponent, AppState };
}
