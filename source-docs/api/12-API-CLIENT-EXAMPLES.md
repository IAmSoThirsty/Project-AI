---
title: API Client Examples
category: api
layer: integration-examples
audience: [integrator]
status: production
classification: tutorial
confidence: verified
requires: [01-API-OVERVIEW.md]
time_estimate: 30min
last_updated: 2025-06-09
version: 1.0.0
---

# API Client Examples

## Python Client

### Installation
```bash
pip install requests pyjwt
```

### Complete Client Class
```python
import requests
from typing import Any, Optional

class ProjectAIClient:
    """Python client for Project-AI API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, username: str, password: str) -> dict:
        """Authenticate and store token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.token = data["token"]
        return data
    
    def chat(self, prompt: str, model: str = "gpt-4", provider: str = "openai") -> str:
        """Send chat message to AI"""
        if not self.token:
            raise ValueError("Not authenticated. Call login() first")
        
        response = requests.post(
            f"{self.base_url}/api/ai/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"prompt": prompt, "model": model, "provider": provider}
        )
        response.raise_for_status()
        
        return response.json()["result"]
    
    def generate_image(self, prompt: str, size: str = "1024x1024") -> dict:
        """Generate AI image"""
        if not self.token:
            raise ValueError("Not authenticated")
        
        response = requests.post(
            f"{self.base_url}/api/ai/image",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"prompt": prompt, "size": size, "provider": "huggingface"}
        )
        response.raise_for_status()
        
        return response.json()["result"]
    
    def update_persona(self, trait: str, value: int) -> dict:
        """Update AI personality trait"""
        if not self.token:
            raise ValueError("Not authenticated")
        
        response = requests.post(
            f"{self.base_url}/api/persona/update",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"trait": trait, "value": value}
        )
        response.raise_for_status()
        
        return response.json()

# Usage
client = ProjectAIClient()
client.login("admin", "secure123")
response = client.chat("What is quantum computing?")
print(response)
```

---

## JavaScript Client

### Installation
```bash
npm install axios jwt-decode
```

### Complete Client Class
```javascript
import axios from 'axios';

class ProjectAIClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.api = axios.create({ baseURL });
    this.token = null;
  }

  async login(username, password) {
    const response = await this.api.post('/api/auth/login', {
      username,
      password
    });
    
    this.token = response.data.token;
    this.api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    
    return response.data;
  }

  async chat(prompt, model = 'gpt-4', provider = 'openai') {
    if (!this.token) throw new Error('Not authenticated');
    
    const response = await this.api.post('/api/ai/chat', {
      prompt,
      model,
      provider
    });
    
    return response.data.result;
  }

  async generateImage(prompt, size = '1024x1024') {
    if (!this.token) throw new Error('Not authenticated');
    
    const response = await this.api.post('/api/ai/image', {
      prompt,
      size,
      provider: 'huggingface'
    });
    
    return response.data.result;
  }

  async updatePersona(trait, value) {
    if (!this.token) throw new Error('Not authenticated');
    
    const response = await this.api.post('/api/persona/update', {
      trait,
      value
    });
    
    return response.data;
  }
}

// Usage
const client = new ProjectAIClient();
await client.login('admin', 'secure123');
const response = await client.chat('What is quantum computing?');
console.log(response);
```

---

## cURL Examples

### Authentication
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure123"}'

# Response: {"token": "eyJhbGc...", "user": {...}}

# Store token
TOKEN="eyJhbGc..."
```

### AI Chat
```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "What is quantum computing?",
    "model": "gpt-4",
    "provider": "openai"
  }'
```

### Image Generation
```bash
curl -X POST http://localhost:5000/api/ai/image \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "cyberpunk city at sunset",
    "size": "1024x1024",
    "provider": "huggingface"
  }'
```

### Update Persona
```bash
curl -X POST http://localhost:5000/api/persona/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "trait": "curiosity",
    "value": 8
  }'
```

---

## React Hook

```typescript
import { useState, useCallback } from 'react';
import axios from 'axios';

interface UseProjectAIResult {
  login: (username: string, password: string) => Promise<void>;
  chat: (prompt: string) => Promise<string>;
  generateImage: (prompt: string) => Promise<any>;
  updatePersona: (trait: string, value: number) => Promise<any>;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export function useProjectAI(baseURL = 'http://localhost:5000'): UseProjectAIResult {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const api = axios.create({ baseURL });

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/api/auth/login', { username, password });
      setToken(response.data.token);
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const chat = useCallback(async (prompt: string): Promise<string> => {
    if (!token) throw new Error('Not authenticated');
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/api/ai/chat', { prompt });
      return response.data.result;
    } catch (err: any) {
      setError(err.response?.data?.error || 'Chat failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const generateImage = useCallback(async (prompt: string) => {
    if (!token) throw new Error('Not authenticated');
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/api/ai/image', { prompt });
      return response.data.result;
    } catch (err: any) {
      setError(err.response?.data?.error || 'Image generation failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  const updatePersona = useCallback(async (trait: string, value: number) => {
    if (!token) throw new Error('Not authenticated');
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/api/persona/update', { trait, value });
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.error || 'Persona update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token]);

  return {
    login,
    chat,
    generateImage,
    updatePersona,
    isAuthenticated: !!token,
    loading,
    error
  };
}

// Usage in component
function ChatComponent() {
  const { login, chat, isAuthenticated, loading, error } = useProjectAI();
  const [response, setResponse] = useState('');

  useEffect(() => {
    login('admin', 'secure123');
  }, []);

  const handleChat = async () => {
    const result = await chat('What is quantum computing?');
    setResponse(result);
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {isAuthenticated && (
        <button onClick={handleChat}>Send Chat</button>
      )}
      <p>{response}</p>
    </div>
  );
}
```

---

## Error Handling

### Python
```python
try:
    response = client.chat("Hello AI")
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - token expired")
        client.login(username, password)
        response = client.chat("Hello AI")
    elif e.response.status_code == 403:
        print("Governance denied request")
    elif e.response.status_code == 429:
        print("Rate limit exceeded - wait before retrying")
    else:
        print(f"API error: {e.response.json()}")
```

### JavaScript
```javascript
try {
  const response = await client.chat('Hello AI');
} catch (error) {
  if (error.response?.status === 401) {
    console.log('Authentication failed - token expired');
    await client.login(username, password);
    const response = await client.chat('Hello AI');
  } else if (error.response?.status === 403) {
    console.log('Governance denied request');
  } else if (error.response?.status === 429) {
    console.log('Rate limit exceeded');
  } else {
    console.error('API error:', error.response?.data);
  }
}
```

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - API architecture
- **[06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md)** - Flask endpoints
- **[09-SECURITY-AUTH.md](./09-SECURITY-AUTH.md)** - Authentication details
