"""
Model Context Protocol (MCP) Server for Project-AI

This module provides a comprehensive MCP server implementation that exposes
Project-AI's capabilities as MCP tools, resources, and prompts. This allows
AI assistants (like Claude Desktop) to interact with Project-AI's features
through the standard Model Context Protocol.

Features exposed via MCP:
- AI Ethics (FourLaws) validation
- AI Persona interactions and configuration
- Memory expansion and knowledge base management
- Learning request management
- Command override system
- Data analysis capabilities
- Location tracking
- Emergency alerts
- Security resources
- Image generation
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Configure logging to stderr (required for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ProjectAIMCPServer:
    """
    MCP Server for Project-AI that exposes core functionality through
    the Model Context Protocol.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the MCP server with Project-AI components.

        Args:
            data_dir: Optional directory for data persistence. Defaults to ./data
        """
        self.server = Server("project-ai")
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "../../../data")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize core components
        self._init_core_systems()
        
        # Register all MCP tools, resources, and prompts
        self._register_tools()
        self._register_resources()
        self._register_prompts()
        
        logger.info("Project-AI MCP Server initialized successfully")

    def _init_core_systems(self):
        """Initialize Project-AI core systems for MCP exposure."""
        try:
            from app.core.ai_systems import (
                FourLaws,
                AIPersona,
                MemoryExpansionSystem,
                LearningRequestManager,
                CommandOverrideSystem,
                PluginManager
            )
            from app.core.user_manager import UserManager
            from app.core.data_analysis import DataAnalyzer
            from app.core.location_tracker import LocationTracker
            from app.core.emergency_alert import EmergencyAlertSystem
            from app.core.image_generator import ImageGenerator
            
            # Initialize systems
            self.four_laws = FourLaws()
            self.persona = AIPersona(data_dir=self.data_dir)
            self.memory = MemoryExpansionSystem(data_dir=self.data_dir)
            self.learning = LearningRequestManager(data_dir=self.data_dir)
            self.override = CommandOverrideSystem(data_dir=self.data_dir)
            self.plugins = PluginManager(data_dir=self.data_dir)
            self.user_manager = UserManager(data_dir=self.data_dir)
            self.data_analyzer = DataAnalyzer()
            self.location_tracker = LocationTracker(data_dir=self.data_dir)
            self.emergency = EmergencyAlertSystem(data_dir=self.data_dir)
            self.image_gen = ImageGenerator(data_dir=self.data_dir)
            
            logger.info("Core systems initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing core systems: {e}")
            # Initialize with minimal functionality if imports fail
            self.four_laws = None
            self.persona = None

    def _register_tools(self):
        """Register all MCP tools."""
        
        # ==================== AI ETHICS TOOLS ====================
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="validate_action",
                    description="Validate an action against AI ethics framework (Asimov's Laws)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to validate"
                            },
                            "context": {
                                "type": "object",
                                "description": "Context for the action",
                                "properties": {
                                    "is_user_order": {"type": "boolean"},
                                    "endangers_humanity": {"type": "boolean"},
                                    "harms_human": {"type": "boolean"}
                                }
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="get_persona_state",
                    description="Get current AI persona state including personality traits and mood",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="adjust_persona_trait",
                    description="Adjust a personality trait of the AI persona",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "trait": {
                                "type": "string",
                                "description": "Trait to adjust (curiosity, empathy, patience, confidence, humor, creativity, enthusiasm, analytical)",
                                "enum": ["curiosity", "empathy", "patience", "confidence", "humor", "creativity", "enthusiasm", "analytical"]
                            },
                            "value": {
                                "type": "number",
                                "description": "New trait value (0.0 to 1.0)",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["trait", "value"]
                    }
                ),
                Tool(
                    name="add_memory",
                    description="Add a memory to the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Category of knowledge",
                                "enum": ["general", "user_preferences", "facts", "skills", "goals", "relationships"]
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to remember"
                            },
                            "importance": {
                                "type": "number",
                                "description": "Importance level (0.0 to 1.0)",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["category", "content"]
                    }
                ),
                Tool(
                    name="search_memory",
                    description="Search the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "category": {
                                "type": "string",
                                "description": "Optional category filter",
                                "enum": ["general", "user_preferences", "facts", "skills", "goals", "relationships"]
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="submit_learning_request",
                    description="Submit a request for the AI to learn new content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content to learn"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Reason for learning request"
                            }
                        },
                        "required": ["content", "reason"]
                    }
                ),
                Tool(
                    name="approve_learning_request",
                    description="Approve a pending learning request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "request_id": {
                                "type": "string",
                                "description": "ID of the learning request"
                            }
                        },
                        "required": ["request_id"]
                    }
                ),
                Tool(
                    name="analyze_data",
                    description="Analyze data from CSV, Excel, or JSON files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to data file"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis",
                                "enum": ["summary", "correlation", "clustering", "statistics"]
                            }
                        },
                        "required": ["file_path", "analysis_type"]
                    }
                ),
                Tool(
                    name="track_location",
                    description="Track current location using IP geolocation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ip_address": {
                                "type": "string",
                                "description": "Optional IP address to geolocate"
                            }
                        }
                    }
                ),
                Tool(
                    name="send_emergency_alert",
                    description="Send an emergency alert to configured contacts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Emergency message"
                            },
                            "location": {
                                "type": "string",
                                "description": "Current location"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="generate_image",
                    description="Generate an image using AI (Stable Diffusion or DALL-E)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Image generation prompt"
                            },
                            "style": {
                                "type": "string",
                                "description": "Style preset",
                                "enum": ["photorealistic", "digital_art", "oil_painting", "watercolor", "anime", "sketch", "abstract", "cyberpunk", "fantasy", "minimalist"]
                            },
                            "backend": {
                                "type": "string",
                                "description": "Backend to use",
                                "enum": ["huggingface", "openai"]
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="list_plugins",
                    description="List all available plugins",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="enable_plugin",
                    description="Enable a plugin",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plugin_name": {
                                "type": "string",
                                "description": "Name of the plugin to enable"
                            }
                        },
                        "required": ["plugin_name"]
                    }
                ),
                Tool(
                    name="disable_plugin",
                    description="Disable a plugin",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plugin_name": {
                                "type": "string",
                                "description": "Name of the plugin to disable"
                            }
                        },
                        "required": ["plugin_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "validate_action":
                    return await self._validate_action(arguments)
                elif name == "get_persona_state":
                    return await self._get_persona_state(arguments)
                elif name == "adjust_persona_trait":
                    return await self._adjust_persona_trait(arguments)
                elif name == "add_memory":
                    return await self._add_memory(arguments)
                elif name == "search_memory":
                    return await self._search_memory(arguments)
                elif name == "submit_learning_request":
                    return await self._submit_learning_request(arguments)
                elif name == "approve_learning_request":
                    return await self._approve_learning_request(arguments)
                elif name == "analyze_data":
                    return await self._analyze_data(arguments)
                elif name == "track_location":
                    return await self._track_location(arguments)
                elif name == "send_emergency_alert":
                    return await self._send_emergency_alert(arguments)
                elif name == "generate_image":
                    return await self._generate_image(arguments)
                elif name == "list_plugins":
                    return await self._list_plugins(arguments)
                elif name == "enable_plugin":
                    return await self._enable_plugin(arguments)
                elif name == "disable_plugin":
                    return await self._disable_plugin(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _register_resources(self):
        """Register MCP resources."""
        
        @self.server.list_resources()
        async def list_resources():
            """List available resources."""
            return [
                {
                    "uri": "persona://state",
                    "name": "AI Persona State",
                    "description": "Current AI persona configuration and state",
                    "mimeType": "application/json"
                },
                {
                    "uri": "memory://knowledge",
                    "name": "Knowledge Base",
                    "description": "Complete knowledge base with all memories",
                    "mimeType": "application/json"
                },
                {
                    "uri": "learning://requests",
                    "name": "Learning Requests",
                    "description": "All learning requests (pending, approved, denied)",
                    "mimeType": "application/json"
                },
                {
                    "uri": "plugins://list",
                    "name": "Plugin List",
                    "description": "List of all available plugins and their status",
                    "mimeType": "application/json"
                }
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource."""
            try:
                if uri == "persona://state":
                    return json.dumps(self.persona.get_state(), indent=2)
                elif uri == "memory://knowledge":
                    return json.dumps(self.memory.get_all_knowledge(), indent=2)
                elif uri == "learning://requests":
                    return json.dumps(self.learning.get_all_requests(), indent=2)
                elif uri == "plugins://list":
                    return json.dumps(self.plugins.list_plugins(), indent=2)
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})

    def _register_prompts(self):
        """Register MCP prompts."""
        
        @self.server.list_prompts()
        async def list_prompts():
            """List available prompts."""
            return [
                {
                    "name": "analyze_with_ethics",
                    "description": "Analyze an action with AI ethics framework",
                    "arguments": [
                        {
                            "name": "action",
                            "description": "Action to analyze",
                            "required": True
                        }
                    ]
                },
                {
                    "name": "persona_interaction",
                    "description": "Interact with AI persona based on its current state",
                    "arguments": [
                        {
                            "name": "message",
                            "description": "Message to the AI persona",
                            "required": True
                        }
                    ]
                },
                {
                    "name": "memory_guided_response",
                    "description": "Generate response guided by knowledge base",
                    "arguments": [
                        {
                            "name": "query",
                            "description": "Query to answer using knowledge base",
                            "required": True
                        }
                    ]
                }
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> str:
            """Get a prompt."""
            try:
                if name == "analyze_with_ethics":
                    action = arguments.get("action", "")
                    return f"Analyze the following action using AI ethics framework (Asimov's Laws): {action}\n\nConsider: Does it harm humans? Does it harm humanity? Is it a user order? Provide ethical analysis."
                elif name == "persona_interaction":
                    message = arguments.get("message", "")
                    state = self.persona.get_state()
                    return f"You are an AI with the following personality traits: {json.dumps(state.get('traits', {}), indent=2)}\n\nCurrent mood: {json.dumps(state.get('mood', {}), indent=2)}\n\nRespond to: {message}"
                elif name == "memory_guided_response":
                    query = arguments.get("query", "")
                    # Search memory for relevant information
                    memories = self.memory.search_knowledge(query)
                    return f"Based on the following knowledge:\n{json.dumps(memories, indent=2)}\n\nAnswer the query: {query}"
                else:
                    return f"Unknown prompt: {name}"
            except Exception as e:
                logger.error(f"Error getting prompt {name}: {e}")
                return f"Error: {str(e)}"

    # ==================== TOOL IMPLEMENTATIONS ====================
    
    async def _validate_action(self, args: Dict[str, Any]) -> List[TextContent]:
        """Validate an action against AI ethics."""
        action = args.get("action", "")
        context = args.get("context", {})
        
        if not self.four_laws:
            return [TextContent(type="text", text="Ethics system not available")]
        
        is_allowed, reason = self.four_laws.validate_action(action, context)
        result = {
            "is_allowed": is_allowed,
            "reason": reason,
            "action": action,
            "context": context
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_persona_state(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get current persona state."""
        if not self.persona:
            return [TextContent(type="text", text="Persona system not available")]
        
        state = self.persona.get_state()
        return [TextContent(type="text", text=json.dumps(state, indent=2))]
    
    async def _adjust_persona_trait(self, args: Dict[str, Any]) -> List[TextContent]:
        """Adjust a persona trait."""
        if not self.persona:
            return [TextContent(type="text", text="Persona system not available")]
        
        trait = args.get("trait")
        value = args.get("value")
        
        self.persona.adjust_trait(trait, value)
        result = {
            "success": True,
            "trait": trait,
            "new_value": value,
            "message": f"Trait '{trait}' adjusted to {value}"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _add_memory(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add a memory to knowledge base."""
        if not self.memory:
            return [TextContent(type="text", text="Memory system not available")]
        
        category = args.get("category")
        content = args.get("content")
        importance = args.get("importance", 0.5)
        
        memory_id = self.memory.add_knowledge(category, content, importance)
        result = {
            "success": True,
            "memory_id": memory_id,
            "category": category,
            "importance": importance
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _search_memory(self, args: Dict[str, Any]) -> List[TextContent]:
        """Search knowledge base."""
        if not self.memory:
            return [TextContent(type="text", text="Memory system not available")]
        
        query = args.get("query")
        category = args.get("category")
        
        results = self.memory.search_knowledge(query, category)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    async def _submit_learning_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Submit a learning request."""
        if not self.learning:
            return [TextContent(type="text", text="Learning system not available")]
        
        content = args.get("content")
        reason = args.get("reason")
        
        request_id = self.learning.submit_request(content, reason)
        result = {
            "success": True,
            "request_id": request_id,
            "status": "pending",
            "message": "Learning request submitted for approval"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _approve_learning_request(self, args: Dict[str, Any]) -> List[TextContent]:
        """Approve a learning request."""
        if not self.learning:
            return [TextContent(type="text", text="Learning system not available")]
        
        request_id = args.get("request_id")
        
        success = self.learning.approve_request(request_id)
        result = {
            "success": success,
            "request_id": request_id,
            "status": "approved" if success else "error"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _analyze_data(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze data file."""
        if not self.data_analyzer:
            return [TextContent(type="text", text="Data analyzer not available")]
        
        file_path = args.get("file_path")
        analysis_type = args.get("analysis_type")
        
        try:
            if analysis_type == "summary":
                results = self.data_analyzer.get_summary(file_path)
            elif analysis_type == "correlation":
                results = self.data_analyzer.get_correlation(file_path)
            elif analysis_type == "clustering":
                results = self.data_analyzer.perform_clustering(file_path)
            else:
                results = self.data_analyzer.get_statistics(file_path)
            
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Analysis error: {str(e)}")]
    
    async def _track_location(self, args: Dict[str, Any]) -> List[TextContent]:
        """Track location."""
        if not self.location_tracker:
            return [TextContent(type="text", text="Location tracker not available")]
        
        ip_address = args.get("ip_address")
        
        try:
            location = self.location_tracker.get_location(ip_address)
            return [TextContent(type="text", text=json.dumps(location, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Location tracking error: {str(e)}")]
    
    async def _send_emergency_alert(self, args: Dict[str, Any]) -> List[TextContent]:
        """Send emergency alert."""
        if not self.emergency:
            return [TextContent(type="text", text="Emergency system not available")]
        
        message = args.get("message")
        location = args.get("location", "Unknown")
        
        try:
            success = self.emergency.send_alert(message, location)
            result = {
                "success": success,
                "message": "Alert sent successfully" if success else "Alert failed"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Emergency alert error: {str(e)}")]
    
    async def _generate_image(self, args: Dict[str, Any]) -> List[TextContent]:
        """Generate an image."""
        if not self.image_gen:
            return [TextContent(type="text", text="Image generator not available")]
        
        prompt = args.get("prompt")
        style = args.get("style", "photorealistic")
        backend = args.get("backend", "huggingface")
        
        try:
            image_path, metadata = self.image_gen.generate(prompt, style=style, backend=backend)
            result = {
                "success": True,
                "image_path": image_path,
                "metadata": metadata
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Image generation error: {str(e)}")]
    
    async def _list_plugins(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all plugins."""
        if not self.plugins:
            return [TextContent(type="text", text="Plugin system not available")]
        
        plugins = self.plugins.list_plugins()
        return [TextContent(type="text", text=json.dumps(plugins, indent=2))]
    
    async def _enable_plugin(self, args: Dict[str, Any]) -> List[TextContent]:
        """Enable a plugin."""
        if not self.plugins:
            return [TextContent(type="text", text="Plugin system not available")]
        
        plugin_name = args.get("plugin_name")
        success = self.plugins.enable_plugin(plugin_name)
        result = {
            "success": success,
            "plugin": plugin_name,
            "status": "enabled" if success else "error"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _disable_plugin(self, args: Dict[str, Any]) -> List[TextContent]:
        """Disable a plugin."""
        if not self.plugins:
            return [TextContent(type="text", text="Plugin system not available")]
        
        plugin_name = args.get("plugin_name")
        success = self.plugins.disable_plugin(plugin_name)
        result = {
            "success": success,
            "plugin": plugin_name,
            "status": "disabled" if success else "error"
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def run(self):
        """Run the MCP server using STDIO transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server."""
    server = ProjectAIMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
