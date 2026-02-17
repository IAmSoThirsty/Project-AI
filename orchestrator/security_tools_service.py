"""
Security Tools Service Integration
Provides access to mgeeky's Penetration Testing Tools collection

Categories:
- Networks: Network security and analysis tools
- Web: Web application security
- Windows: Windows security testing
- Linux: Linux security testing  
- Red-teaming: Offensive security tools
- OSINT: Open Source Intelligence
- Social Engineering: SE tools and frameworks
"""

import os
import subprocess
from typing import Dict, List, Optional
from pathlib import Path


class SecurityToolsService:
    """Central service for accessing penetration testing tools"""
    
    def __init__(self, tools_path: str = None):
        if tools_path is None:
            base = Path(__file__).parent.parent
            tools_path = base / "security" / "penetration-testing-tools"
        
        self.tools_path = Path(tools_path)
        self.categories = self._discover_categories()
    
    def _discover_categories(self) -> Dict[str, Path]:
        """Discover available tool categories"""
        categories = {}
        
        if not self.tools_path.exists():
            return categories
        
        for item in self.tools_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories[item.name] = item
        
        return categories
    
    def list_categories(self) -> List[str]:
        """List all available tool categories"""
        return list(self.categories.keys())
    
    def list_tools(self, category: str) -> List[Dict[str, str]]:
        """List tools in a specific category"""
        if category not in self.categories:
            return []
        
        category_path = self.categories[category]
        tools = []
        
        for item in category_path.iterdir():
            if item.is_file() and item.suffix in ['.py', '.sh', '.ps1', '.rb']:
                tools.append({
                    'name': item.stem,
                    'path': str(item),
                    'type': item.suffix[1:],
                    'category': category
                })
        
        return tools
    
    def get_tool_info(self, category: str, tool_name: str) -> Optional[Dict]:
        """Get detailed information about a specific tool"""
        tools = self.list_tools(category)
        
        for tool in tools:
            if tool['name'] == tool_name:
                # Try to extract description from file
                tool_path = Path(tool['path'])
                description = self._extract_description(tool_path)
                tool['description'] = description
                return tool
        
        return None
    
    def _extract_description(self, tool_path: Path) -> str:
        """Extract description from tool file"""
        try:
            with open(tool_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:20]  # Read first 20 lines
                
                for line in lines:
                    line = line.strip()
                    # Look for description patterns
                    if any(marker in line.lower() for marker in ['description:', 'desc:', 'purpose:']):
                        return line.split(':', 1)[-1].strip()
                    # Look for comments with descriptive text
                    if line.startswith(('#', '//', '"""', "'''")):
                        cleaned = line.lstrip('#/ \'"').strip()
                        if len(cleaned) > 20:  # Likely a description
                            return cleaned
                
                return "No description available"
        except Exception:
            return "Unable to read description"
    
    def execute_tool(self, category: str, tool_name: str, args: List[str] = None, 
                     session_token: str = None) -> Dict:
        """
        Execute a security tool (use with caution!)
        
        SECURITY: Requires valid session token from vault authentication
        
        WARNING: Only execute tools you understand and trust
        """
        # SECURITY CHECK: Require vault authorization
        if session_token is None:
            return {
                'success': False, 
                'error': 'SECURITY: Session token required. Must authenticate via SecurityVault first.'
            }
        
        # Import vault here to avoid circular dependency
        try:
            from security.vault_access_control import vault, AccessDeniedError
            
            # Validate session
            if not vault.validate_session(session_token):
                return {
                    'success': False,
                    'error': 'SECURITY: Invalid or expired session token'
                }
            
            # Validate vault is active (not dormant)
            if vault.DORMANT:
                return {
                    'success': False,
                    'error': 'SECURITY: Vault is dormant. Requires admin activation.'
                }
            
            # Access tool through vault (logs access)
            tool_path = vault.access_tool(session_token, category, tool_name)
            
        except AccessDeniedError as e:
            return {'success': False, 'error': f'SECURITY: {str(e)}'}
        except ImportError:
            return {
                'success': False,
                'error': 'SECURITY: Vault access control not available'
            }
        
        # Original execution logic
        tool = self.get_tool_info(category, tool_name)
        
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        tool_type = tool['type']
        
        # Determine executor
        executor = {
            'py': ['python'],
            'sh': ['bash'],
            'ps1': ['powershell', '-File'],
            'rb': ['ruby']
        }.get(tool_type)
        
        if not executor:
            return {'success': False, 'error': f'Unsupported tool type: {tool_type}'}
        
        # Build command
        cmd = executor + [str(tool_path)] + (args or [])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'executed_by': session_token[:8] + '...'  # Audit trail
            }
        
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Tool execution timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class SecurityToolsAPI:
    """FastAPI integration for security tools"""
    
    def __init__(self):
        self.service = SecurityToolsService()
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories and their tools"""
        result = {}
        
        for category in self.service.list_categories():
            tools = self.service.list_tools(category)
            result[category] = [t['name'] for t in tools]
        
        return result
    
    def search_tools(self, query: str) -> List[Dict]:
        """Search for tools by name or category"""
        results = []
        query_lower = query.lower()
        
        for category in self.service.list_categories():
            if query_lower in category.lower():
                # Category matches
                results.extend(self.service.list_tools(category))
            else:
                # Search tool names
                tools = self.service.list_tools(category)
                for tool in tools:
                    if query_lower in tool['name'].lower():
                        results.append(tool)
        
        return results


# Export service
__all__ = ['SecurityToolsService', 'SecurityToolsAPI']
