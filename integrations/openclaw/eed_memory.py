#!/usr/bin/env python3
"""
EED Memory Adapter - Legion Phase 2
Handles persistent memory storage via Project-AI EED system
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class ConversationEntry(BaseModel):
    """Single conversation turn"""
    user_id: str
    message: str
    response: str
    timestamp: datetime
    context: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class ContextWindow(BaseModel):
    """EED context window"""
    user_id: str
    conversations: List[ConversationEntry]
    total_tokens: int
    max_tokens: int = 200000
    created_at: datetime
    updated_at: datetime


class EEDMemoryAdapter:
    """
    Adapter for Project-AI EED (Episodic Experience Database) memory system
    
    Features:
    - 200k+ token context window support
    - Persistent conversation storage
    - Cross-session memory retrieval
    - Automatic context pruning
    """
    
    def __init__(self, api_url: str = "http://localhost:8001"):
        """
        Initialize EED memory adapter
        
        Args:
            api_url: Base URL for Project-AI API
        """
        self.api_url = api_url.rstrip('/')
        self.memory_endpoint = f"{self.api_url}/memory"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def store_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store conversation in EED with 200k token context
        
        Args:
            user_id: User identifier
            message: User's message
            response: Agent's response
            context: Additional context
            metadata: Additional metadata
            
        Returns:
            str: Memory ID
            
        Raises:
            EEDError: If storage fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        entry = ConversationEntry(
            user_id=user_id,
            message=message,
            response=response,
            timestamp=datetime.now(),
            context=context or {},
            metadata=metadata or {}
        )
        
        payload = {
            "user_id": user_id,
            "type": "conversation",
            "data": {
                "message": message,
                "response": response,
                "timestamp": entry.timestamp.isoformat(),
                "context": entry.context,
                "metadata": entry.metadata
            }
        }
        
        try:
            async with self.session.post(
                f"{self.memory_endpoint}/store",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise EEDError(f"Failed to store conversation: {error_text}")
                
                data = await response.json()
                return data.get("memory_id", "")
                
        except aiohttp.ClientError as e:
            raise EEDError(f"Network error storing conversation: {str(e)}")
    
    async def retrieve_context(
        self,
        user_id: str,
        max_tokens: int = 200000,
        since: Optional[datetime] = None
    ) -> ContextWindow:
        """
        Retrieve full conversation history and context
        
        Args:
            user_id: User identifier
            max_tokens: Maximum context window size (tokens)
            since: Only retrieve conversations after this time
            
        Returns:
            ContextWindow: Full context with conversation history
            
        Raises:
            EEDError: If retrieval fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        params = {
            "user_id": user_id,
            "max_tokens": max_tokens
        }
        
        if since:
            params["since"] = since.isoformat()
        
        try:
            async with self.session.get(
                f"{self.memory_endpoint}/retrieve",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise EEDError(f"Failed to retrieve context: {error_text}")
                
                data = await response.json()
                return self._parse_context_window(data)
                
        except aiohttp.ClientError as e:
            raise EEDError(f"Network error retrieving context: {str(e)}")
    
    def _parse_context_window(self, data: Dict[str, Any]) -> ContextWindow:
        """Parse EED context window response"""
        conversations = []
        
        for conv_data in data.get("conversations", []):
            conversations.append(ConversationEntry(
                user_id=conv_data.get("user_id", ""),
                message=conv_data.get("message", ""),
                response=conv_data.get("response", ""),
                timestamp=datetime.fromisoformat(conv_data.get("timestamp", datetime.now().isoformat())),
                context=conv_data.get("context", {}),
                metadata=conv_data.get("metadata", {})
            ))
        
        return ContextWindow(
            user_id=data.get("user_id", ""),
            conversations=conversations,
            total_tokens=data.get("total_tokens", 0),
            max_tokens=data.get("max_tokens", 200000),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
    
    async def search_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[ConversationEntry]:
        """
        Search conversation memory
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching conversation entries
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        payload = {
            "user_id": user_id,
            "query": query,
            "limit": limit
        }
        
        try:
            async with self.session.post(
                f"{self.memory_endpoint}/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                results = []
                
                for conv_data in data.get("results", []):
                    results.append(ConversationEntry(
                        user_id=conv_data.get("user_id", ""),
                        message=conv_data.get("message", ""),
                        response=conv_data.get("response", ""),
                        timestamp=datetime.fromisoformat(conv_data.get("timestamp", datetime.now().isoformat())),
                        context=conv_data.get("context", {}),
                        metadata=conv_data.get("metadata", {})
                    ))
                
                return results
                
        except:
            return []
    
    async def forget_conversation(
        self,
        user_id: str,
        memory_id: str
    ) -> bool:
        """
        Remove specific conversation from memory
        
        Args:
            user_id: User identifier
            memory_id: Memory entry ID
            
        Returns:
            bool: True if successful
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.delete(
                f"{self.memory_endpoint}/{memory_id}",
                params={"user_id": user_id},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except:
            return False
    
    async def clear_user_memory(
        self,
        user_id: str,
        confirm: bool = False
    ) -> bool:
        """
        Clear all memory for a user (requires confirmation)
        
        Args:
            user_id: User identifier
            confirm: Must be True to proceed
            
        Returns:
            bool: True if successful
            
        Raises:
            EEDError: If confirmation not provided
        """
        if not confirm:
            raise EEDError("Memory clear requires explicit confirmation")
            
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.delete(
                f"{self.memory_endpoint}/user/{user_id}",
                params={"confirm": "true"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except:
            return False
    
    async def get_statistics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get memory statistics for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Statistics dictionary
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.get(
                f"{self.memory_endpoint}/stats/{user_id}",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status != 200:
                    return {}
                
                return await response.json()
        except:
            return {}


class EEDError(Exception):
    """Exception raised for EED memory errors"""
    pass


# CLI test interface
async def test_eed_memory():
    """Test EED memory adapter"""
    print("\n" + "=" * 60)
    print("EED Memory Adapter - Test Mode")
    print("=" * 60 + "\n")
    
    async with EEDMemoryAdapter() as eed:
        test_user = "test_user_legion"
        
        # Store test conversation
        print("Storing test conversation...")
        try:
            memory_id = await eed.store_conversation(
                user_id=test_user,
                message="Hello, Legion!",
                response="Greetings. How may I assist you today?",
                context={"test": True},
                metadata={"source": "test_script"}
            )
            print(f"  Stored with ID: {memory_id}\n")
        except EEDError as e:
            print(f"  Error: {str(e)}")
            print("  Note: Start Project-AI API with 'python start_api.py'\n")
            return
        
        # Retrieve context
        print("Retrieving conversation context...")
        try:
            context = await eed.retrieve_context(test_user)
            print(f"  Total conversations: {len(context.conversations)}")
            print(f"  Total tokens: {context.total_tokens}")
            print(f"  Max tokens: {context.max_tokens}\n")
            
            if context.conversations:
                latest = context.conversations[-1]
                print("  Latest conversation:")
                print(f"    User: {latest.message}")
                print(f"    Legion: {latest.response}\n")
        except EEDError as e:
            print(f"  Error: {str(e)}\n")
        
        # Get statistics
        print("Memory statistics:")
        stats = await eed.get_statistics(test_user)
        if stats:
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print("  No statistics available")


if __name__ == "__main__":
    asyncio.run(test_eed_memory())
