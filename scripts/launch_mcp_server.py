#!/usr/bin/env python3
"""
MCP Server Launcher for Project-AI

This script provides a convenient way to launch the Project-AI MCP server
with various configuration options.

Usage:
    python scripts/launch_mcp_server.py
    python scripts/launch_mcp_server.py --data-dir /custom/data
    python scripts/launch_mcp_server.py --log-level DEBUG
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app.core.mcp_server import ProjectAIMCPServer


def setup_logging(log_level: str):
    """Setup logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Launch Project-AI MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch with default settings
  python scripts/launch_mcp_server.py
  
  # Launch with custom data directory
  python scripts/launch_mcp_server.py --data-dir /path/to/data
  
  # Launch with debug logging
  python scripts/launch_mcp_server.py --log-level DEBUG
  
  # Launch with all options
  python scripts/launch_mcp_server.py --data-dir /path/to/data --log-level INFO
        """
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory for data persistence (default: ./data)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies and exit"
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    
    dependencies = {
        "mcp": "MCP SDK",
        "openai": "OpenAI SDK",
        "cryptography": "Cryptography",
        "PyQt6": "PyQt6 (optional, for GUI)",
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - MISSING")
            missing.append(module)
    
    if missing:
        print("\nMissing dependencies:")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("\n✓ All dependencies installed")
    return True


def check_environment():
    """Check if required environment variables are set."""
    print("\nChecking environment variables...")
    
    required = {
        "OPENAI_API_KEY": "OpenAI API key",
        "HUGGINGFACE_API_KEY": "Hugging Face API key"
    }
    
    optional = {
        "FERNET_KEY": "Encryption key",
        "SMTP_USERNAME": "Email username",
        "SMTP_PASSWORD": "Email password"
    }
    
    missing_required = []
    for var, desc in required.items():
        if os.getenv(var):
            print(f"✓ {desc} ({var})")
        else:
            print(f"✗ {desc} ({var}) - MISSING")
            missing_required.append(var)
    
    for var, desc in optional.items():
        if os.getenv(var):
            print(f"✓ {desc} ({var}) [optional]")
        else:
            print(f"○ {desc} ({var}) [optional] - not set")
    
    if missing_required:
        print("\n⚠ Warning: Missing required environment variables")
        print("Set them in .env file or environment")
        return False
    
    print("\n✓ All required environment variables set")
    return True


async def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Check dependencies if requested
    if args.check_deps:
        deps_ok = check_dependencies()
        env_ok = check_environment()
        sys.exit(0 if (deps_ok and env_ok) else 1)
    
    try:
        logger.info("Starting Project-AI MCP Server...")
        
        # Initialize and run server
        server = ProjectAIMCPServer(data_dir=args.data_dir)
        
        logger.info("MCP Server initialized successfully")
        logger.info("Listening for MCP protocol messages on STDIO...")
        
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
