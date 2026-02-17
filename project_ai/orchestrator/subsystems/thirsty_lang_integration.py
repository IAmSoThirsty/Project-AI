"""
Thirsty-Lang Compiler & Runtime Integration
Provides code compilation and execution capabilities
"""
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class ThirstyLangIntegration:
    """Integrates Thirsty-Lang programming language"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Path to Thirsty-Lang installation
        self.thirsty_root = Path(__file__).parent.parent.parent.parent / "external" / "Thirsty-Lang"
        self.cli_path = self.thirsty_root / "src" / "cli.js"
        
        self.active = False
        self.node_version = None
        self.logger.info("Thirsty-Lang integration initialized")
    
    def start(self) -> None:
        """Start Thirsty-Lang runtime"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING THIRSTY-LANG COMPILER & RUNTIME")
        self.logger.info("=" * 60)
        
        # Verify Node.js installation
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.node_version = result.stdout.strip()
            self.logger.info(f"Node.js version: {self.node_version}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"Node.js not found or not responding: {e}")
            raise RuntimeError(f"Node.js not found: {e}")
        
        # Verify Thirsty-Lang CLI exists
        if not self.cli_path.exists():
            self.logger.error(f"Thirsty-Lang CLI not found at {self.cli_path}")
            raise RuntimeError(f"Thirsty-Lang CLI not found at {self.cli_path}")
        
        # Test compilation capability
        test_code = 'drink x = 42\npour x'
        self.logger.info("Testing compilation with sample code...")
        
        if self.compile_and_run(test_code):
            self.active = True
            self.logger.info("✓ Thirsty-Lang READY - Can compile and execute code")
        else:
            raise RuntimeError("Failed to compile test code")
    
    def stop(self) -> None:
        """Stop Thirsty-Lang runtime"""
        self.logger.info("Stopping Thirsty-Lang...")
        self.active = False
    
    def compile_and_run(self, code: str, timeout: int = 10) -> bool:
        """
        Compile and run Thirsty code
        
        Args:
            code: Thirsty-lang source code
            timeout: Execution timeout in seconds
            
        Returns:
            True if compilation/execution succeeded
        """
        # Create temp file
        temp_file = Path('temp_thirsty_test.thirsty')
        
        try:
            temp_file.write_text(code, encoding='utf-8')
            
            result = subprocess.run(
                ['node', str(self.cli_path), str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.logger.debug(f"Compilation successful. Output: {result.stdout}")
                return True
            else:
                self.logger.error(f"Compilation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Execution timed out after {timeout}s")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Thirsty-Lang status"""
        return {
            'active': self.active,
            'node_version': self.node_version,
            'cli_path': str(self.cli_path),
            'cli_exists': self.cli_path.exists()
        }
