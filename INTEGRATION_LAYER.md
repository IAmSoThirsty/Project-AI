# Integration Layer Specification

**Version:** 1.0  
**Last Updated:** 2026-01-23  
**Status:** Specification

---

## Overview

The Integration Layer provides standardized interfaces for connecting the PACE Engine to external systems, services, and communication protocols. It handles I/O routing, protocol translation, and integration with Project-AI's existing systems.

## Core Concepts

### Integration Points

1. **I/O Channels**: CLI, API, GUI, H.323, MCP servers
2. **External Services**: OpenAI, external APIs, databases
3. **Internal Systems**: Existing Project-AI modules (Triumvirate, Temporal workflows)
4. **Communication Protocols**: REST, gRPC, WebSocket, H.323

## Architecture

```
┌────────────────────────────────────────────────────┐
│               Integration Layer                     │
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │    IO    │  │ Protocol │  │  Service │         │
│  │  Router  │  │ Adapters │  │ Connectors│        │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Event   │  │  Message │  │   Data   │         │
│  │  Bus     │  │ Transform│  │ Mappers  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└────────────────────────────────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────┐
│            External Systems & Services              │
├────────────────────────────────────────────────────┤
│  • CLI/Terminal    • REST APIs    • Databases      │
│  • GUI (PyQt6)     • H.323        • OpenAI         │
│  • Web Frontend    • gRPC         • Temporal       │
│  • MCP Servers     • WebSocket    • Triumvirate    │
└────────────────────────────────────────────────────┘
```

## I/O Router

### IORouter Implementation

```python
class IORouter:
    """
    Handles IO channels and routes input/output to and from PACE.
    
    The IORouter is the main integration point for external systems,
    providing a unified interface for input/output across multiple channels.
    """
    
    def __init__(self, engine: 'PACEEngine'):
        """
        Initialize the IO router.
        
        Args:
            engine: Reference to the PACE engine
        """
        self.engine = engine
        self.channels: Dict[str, 'Channel'] = {}
        self.event_bus = EventBus()
        self.message_transform = MessageTransform()
        
        # Register default channels
        self._register_default_channels()
    
    def receive_input(self, channel: str, payload: dict) -> dict:
        """
        Receive input from a channel.
        
        Args:
            channel: Channel identifier (cli, api, gui, h323, etc.)
            payload: Input payload
            
        Returns:
            Response from engine
        """
        # Validate channel
        if channel not in self.channels:
            raise ValueError(f"Unknown channel: {channel}")
        
        # Transform input
        transformed = self.message_transform.transform_input(channel, payload)
        
        # Route to engine
        response = self.engine.handle_input(channel, transformed)
        
        # Transform output
        output = self.message_transform.transform_output(channel, response)
        
        # Emit event
        self.event_bus.emit("input_processed", {
            "channel": channel,
            "payload": payload,
            "response": output
        })
        
        return output
    
    def send_output(self, channel: str, data: dict) -> None:
        """
        Send output to a channel.
        
        Args:
            channel: Destination channel
            data: Output data
        """
        if channel not in self.channels:
            raise ValueError(f"Unknown channel: {channel}")
        
        channel_obj = self.channels[channel]
        channel_obj.send(data)
    
    def register_channel(self, channel: 'Channel') -> None:
        """
        Register a new I/O channel.
        
        Args:
            channel: Channel to register
        """
        self.channels[channel.name] = channel
        logger.info(f"Registered channel: {channel.name}")
    
    def unregister_channel(self, channel_name: str) -> None:
        """
        Unregister a channel.
        
        Args:
            channel_name: Channel name
        """
        if channel_name in self.channels:
            del self.channels[channel_name]
            logger.info(f"Unregistered channel: {channel_name}")
    
    def list_channels(self) -> List[str]:
        """
        List all registered channels.
        
        Returns:
            List of channel names
        """
        return list(self.channels.keys())
    
    def _register_default_channels(self) -> None:
        """Register default channels."""
        self.register_channel(CLIChannel("cli"))
        self.register_channel(APIChannel("api"))
        # Additional channels registered as needed
```

## Channel Implementations

### Base Channel Interface

```python
class Channel(ABC):
    """Base interface for I/O channels."""
    
    def __init__(self, name: str):
        """
        Initialize channel.
        
        Args:
            name: Channel name
        """
        self.name = name
    
    @abstractmethod
    def send(self, data: dict) -> None:
        """
        Send data through the channel.
        
        Args:
            data: Data to send
        """
        pass
    
    @abstractmethod
    def receive(self) -> Optional[dict]:
        """
        Receive data from the channel.
        
        Returns:
            Received data or None
        """
        pass
```

### CLI Channel

```python
class CLIChannel(Channel):
    """Command-line interface channel."""
    
    def send(self, data: dict) -> None:
        """Print data to console."""
        print(f"[{self.name}] {json.dumps(data, indent=2)}")
    
    def receive(self) -> Optional[dict]:
        """Read input from console."""
        try:
            line = input(f"[{self.name}] > ")
            return {"message": line}
        except EOFError:
            return None
```

### API Channel

```python
class APIChannel(Channel):
    """REST API channel."""
    
    def __init__(self, name: str, host: str = "0.0.0.0", port: int = 8000):
        """
        Initialize API channel.
        
        Args:
            name: Channel name
            host: API host
            port: API port
        """
        super().__init__(name)
        self.host = host
        self.port = port
        self.app = self._create_app()
        self.output_queue = []
    
    def send(self, data: dict) -> None:
        """Queue data for API response."""
        self.output_queue.append(data)
    
    def receive(self) -> Optional[dict]:
        """Handled by Flask/FastAPI routes."""
        return None
    
    def _create_app(self):
        """Create Flask/FastAPI application."""
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route("/api/v1/input", methods=["POST"])
        def handle_input():
            payload = request.json
            # Route through IORouter
            # response = io_router.receive_input("api", payload)
            return jsonify({"status": "received"})
        
        return app
    
    def start(self):
        """Start API server."""
        self.app.run(host=self.host, port=self.port)
```

### H.323 Channel

```python
class H323Channel(Channel):
    """H.323 communication protocol channel."""
    
    def __init__(self, name: str, config: dict):
        """
        Initialize H.323 channel.
        
        Args:
            name: Channel name
            config: H.323 configuration
        """
        super().__init__(name)
        self.config = config
        self.connection = None
    
    def send(self, data: dict) -> None:
        """Send data via H.323."""
        if self.connection:
            # Implementation depends on H.323 library
            # self.connection.send(self._encode_h323(data))
            pass
    
    def receive(self) -> Optional[dict]:
        """Receive data via H.323."""
        if self.connection:
            # data = self.connection.receive()
            # return self._decode_h323(data)
            pass
        return None
    
    def connect(self, endpoint: str) -> None:
        """Connect to H.323 endpoint."""
        # Implementation depends on H.323 library
        pass
    
    def disconnect(self) -> None:
        """Disconnect from H.323 endpoint."""
        if self.connection:
            # self.connection.close()
            self.connection = None
```

## Integration with Existing Project-AI Systems

### Triumvirate Integration

```python
class TriumvirateIntegration:
    """
    Integration with Project-AI's Triumvirate system
    (Galahad/Ethics, Cerberus/Security, Codex Deus Maximus/Logic).
    """
    
    def __init__(self, pace_engine: 'PACEEngine'):
        """
        Initialize Triumvirate integration.
        
        Args:
            pace_engine: PACE engine instance
        """
        self.pace_engine = pace_engine
        self.galahad = None  # Ethics agent
        self.cerberus = None  # Security agent
        self.codex = None     # Logic agent
    
    def initialize_triumvirate(self) -> None:
        """Initialize Triumvirate agents."""
        from src.cognition.galahad.engine import GalahadEngine
        from src.cognition.cerberus.engine import CerberusEngine
        from src.cognition.codex.engine import CodexEngine
        
        self.galahad = GalahadEngine()
        self.cerberus = CerberusEngine()
        self.codex = CodexEngine()
    
    def consult_ethics(self, action: dict) -> dict:
        """
        Consult Galahad for ethical review.
        
        Args:
            action: Action to review
            
        Returns:
            Ethics assessment
        """
        if self.galahad:
            return self.galahad.assess_ethics(action)
        return {"status": "unavailable"}
    
    def consult_security(self, action: dict) -> dict:
        """
        Consult Cerberus for security review.
        
        Args:
            action: Action to review
            
        Returns:
            Security assessment
        """
        if self.cerberus:
            return self.cerberus.assess_security(action)
        return {"status": "unavailable"}
    
    def consult_logic(self, reasoning: dict) -> dict:
        """
        Consult Codex for logical validation.
        
        Args:
            reasoning: Reasoning to validate
            
        Returns:
            Logic assessment
        """
        if self.codex:
            return self.codex.validate_logic(reasoning)
        return {"status": "unavailable"}
```

### Temporal Integration

```python
class TemporalIntegration:
    """
    Integration with Temporal.io workflows.
    """
    
    def __init__(self, pace_engine: 'PACEEngine'):
        """
        Initialize Temporal integration.
        
        Args:
            pace_engine: PACE engine instance
        """
        self.pace_engine = pace_engine
        self.client = None
    
    def initialize_temporal(self, config: dict) -> None:
        """
        Initialize Temporal client.
        
        Args:
            config: Temporal configuration
        """
        # from temporalio.client import Client
        # self.client = await Client.connect(config["namespace"])
        pass
    
    def execute_workflow_via_temporal(self, workflow_name: str, params: dict) -> Any:
        """
        Execute a PACE workflow via Temporal.
        
        Args:
            workflow_name: Workflow name
            params: Workflow parameters
            
        Returns:
            Workflow result
        """
        if self.client:
            # handle = await self.client.start_workflow(workflow_name, params)
            # return await handle.result()
            pass
        return None
```

### OpenAI Integration

```python
class OpenAIIntegration:
    """
    Integration with OpenAI API for LLM capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI integration.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            # from openai import OpenAI
            # self.client = OpenAI(api_key=self.api_key)
            pass
    
    def generate_completion(self, prompt: str, model: str = "gpt-4") -> str:
        """
        Generate text completion.
        
        Args:
            prompt: Input prompt
            model: Model to use
            
        Returns:
            Generated text
        """
        if self.client:
            # response = self.client.chat.completions.create(
            #     model=model,
            #     messages=[{"role": "user", "content": prompt}]
            # )
            # return response.choices[0].message.content
            pass
        return ""
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate text embedding.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if self.client:
            # response = self.client.embeddings.create(
            #     model="text-embedding-ada-002",
            #     input=text
            # )
            # return response.data[0].embedding
            pass
        return []
```

## Message Transform

### MessageTransform Class

```python
class MessageTransform:
    """
    Transforms messages between channel formats and internal format.
    """
    
    def transform_input(self, channel: str, payload: dict) -> dict:
        """
        Transform input from channel format to internal format.
        
        Args:
            channel: Source channel
            payload: Raw payload
            
        Returns:
            Transformed payload
        """
        # Channel-specific transformations
        if channel == "cli":
            return self._transform_cli_input(payload)
        elif channel == "api":
            return self._transform_api_input(payload)
        elif channel == "h323":
            return self._transform_h323_input(payload)
        else:
            return payload
    
    def transform_output(self, channel: str, response: dict) -> dict:
        """
        Transform output from internal format to channel format.
        
        Args:
            channel: Destination channel
            response: Internal response
            
        Returns:
            Transformed response
        """
        # Channel-specific transformations
        if channel == "cli":
            return self._transform_cli_output(response)
        elif channel == "api":
            return self._transform_api_output(response)
        elif channel == "h323":
            return self._transform_h323_output(response)
        else:
            return response
    
    def _transform_cli_input(self, payload: dict) -> dict:
        """Transform CLI input."""
        return {
            "type": "cli_command",
            "content": payload
        }
    
    def _transform_cli_output(self, response: dict) -> dict:
        """Transform CLI output."""
        return {
            "result": response.get("result"),
            "explanation": response.get("explanation")
        }
    
    def _transform_api_input(self, payload: dict) -> dict:
        """Transform API input."""
        return payload
    
    def _transform_api_output(self, response: dict) -> dict:
        """Transform API output."""
        return response
    
    def _transform_h323_input(self, payload: dict) -> dict:
        """Transform H.323 input."""
        return payload
    
    def _transform_h323_output(self, response: dict) -> dict:
        """Transform H.323 output."""
        return response
```

## Event Bus

### EventBus Class

```python
class EventBus:
    """
    Event bus for inter-component communication.
    """
    
    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Handler function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Event type
            handler: Handler function to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
    
    def emit(self, event_type: str, data: dict) -> None:
        """
        Emit an event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
```

## Configuration

```yaml
integration:
  io_router:
    channels:
      - name: "cli"
        type: "CLIChannel"
        enabled: true
      - name: "api"
        type: "APIChannel"
        enabled: true
        config:
          host: "0.0.0.0"
          port: 8000
      - name: "h323"
        type: "H323Channel"
        enabled: false
        config:
          endpoint: "h323://example.com"
  
  triumvirate:
    enabled: true
    ethics_agent: "galahad"
    security_agent: "cerberus"
    logic_agent: "codex"
  
  temporal:
    enabled: true
    namespace: "project-ai"
    address: "localhost:7233"
  
  openai:
    enabled: true
    api_key_env: "OPENAI_API_KEY"
    default_model: "gpt-4"
```

## Usage Examples

### CLI Integration

```python
# Initialize PACE engine
from project_ai.engine import PACEEngine

engine = PACEEngine()

# CLI loop
while True:
    user_input = input("> ")
    if user_input == "exit":
        break
    
    response = engine.io_router.receive_input("cli", {"message": user_input})
    print(response)
```

### API Integration

```python
from flask import Flask, request, jsonify
from project_ai.engine import PACEEngine

app = Flask(__name__)
engine = PACEEngine()

@app.route("/api/v1/query", methods=["POST"])
def handle_query():
    payload = request.json
    response = engine.io_router.receive_input("api", payload)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### Triumvirate Integration

```python
from project_ai.engine import PACEEngine

engine = PACEEngine()

# Initialize Triumvirate
triumvirate = TriumvirateIntegration(engine)
triumvirate.initialize_triumvirate()

# Consult ethics before action
action = {"type": "file_delete", "path": "/important/file"}
ethics_result = triumvirate.consult_ethics(action)

if ethics_result.get("approved"):
    # Proceed with action
    pass
```

## See Also

- [ENGINE_SPEC.md](ENGINE_SPEC.md) - Engine specification
- [PACE_ARCHITECTURE.md](PACE_ARCHITECTURE.md) - Overall architecture
- [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) - Module interfaces
