#!/usr/bin/env python3
"""Start one runtime role; importing this module does not launch work."""
import argparse
import logging
import os
from pathlib import Path
import runpy
import sys


def main():
    from dotenv import load_dotenv
    load_dotenv(Path.cwd() / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", nargs="?", choices=("api", "worker", "scanner"), default="api")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
    if args.role == "worker":
        runpy.run_module("worker", run_name="__main__")
        return
    import uvicorn
    target = "api.app:app" if args.role == "api" else "api.scanner:app"
    uvicorn.run(target, host=args.host, port=args.port or (8080 if args.role == "api" else 8090))


if __name__ == "__main__":
    main()
