#!/usr/bin/env python3
"""
Startup script for CodeAgent Vulnerability Scanner
"""

import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_dependencies():
    """Check if required tools are installed."""
    import subprocess
    
    tools = ["git", "semgrep", "bandit", "pip-audit"]
    missing = []
    
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"Warning: Missing tools: {', '.join(missing)}")
        print("Some analyzers may not work properly.")
        return False
    
    print("All required tools are available.")
    return True

def main():
    """Main entry point."""
    setup_logging()
    
    print("CodeAgent Vulnerability Scanner v0.1.0")
    print("=====================================")
    
    # Check dependencies
    check_dependencies()
    
    # Import and start the application
    try:
        from api.app import app
        import uvicorn
        
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8080))
        
        print(f"Starting server on {host}:{port}")
        print(f"API documentation: http://{host}:{port}/docs")
        print(f"Health check: http://{host}:{port}/health")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()