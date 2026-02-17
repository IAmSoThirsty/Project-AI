"""
The_Triumvirate Integration
A documentation/manifesto website for the Sovereign Stack
"""
import logging
from typing import Dict, Any
from pathlib import Path


class TriumvirateIntegration:
    """Integrates The_Triumvirate documentation website"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.active = False
        
        # Path to Triumvirate
        self.triumvirate_root = Path(__file__).parent.parent.parent.parent / "external" / "The_Triumvirate"
        self.index_path = self.triumvirate_root / "index.html"
        
        self.logger.info("Triumvirate integration initialized")
    
    def start(self) -> None:
        """Start Triumvirate (documentation website)"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING THE_TRIUMVIRATE")
        self.logger.info("=" * 60)
        
        # Verify index.html exists
        if not self.index_path.exists():
            self.logger.error(f"Triumvirate index.html not found at {self.index_path}")
            self.active = False
            return
        
        # The Triumvirate is a static website - just verify it's there
        self.logger.info("The_Triumvirate: Documentation/Manifesto Website")
        self.logger.info("Purpose: Exploring the Trinity of AI, Humanity & Technology")
        self.logger.info(f"Location: {self.triumvirate_root}")
        self.logger.info("Components: Project AI, Cerberus, Codex Deus Maximus")
        self.logger.info("Pages: 11 HTML pages with manifesto and architecture docs")
        
        self.active = True
        self.logger.info("✓ Triumvirate documentation AVAILABLE")
    
    def stop(self) -> None:
        """Stop Triumvirate"""
        self.logger.info("Triumvirate documentation closed")
        self.active = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Triumvirate status"""
        return {
            'active': self.active,
            'type': 'documentation_website',
            'purpose': 'AGI-Human relations manifesto',
            'location': str(self.triumvirate_root),
            'index_exists': self.index_path.exists(),
            'pages': 11
        }
    
    def get_website_url(self) -> str:
        """Get the local file URL to the website"""
        if self.index_path.exists():
            return f"file:///{self.index_path.as_posix()}"
        return None
