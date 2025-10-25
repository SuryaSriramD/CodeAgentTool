"""
CodeAgent Vulnerability Scanner

A comprehensive security vulnerability scanner API for source code repositories.
"""

__version__ = "0.1.0"
__author__ = "CodeAgent Team"
__email__ = "team@codeagent.dev"

from api.app import app
from pipeline.orchestrator import get_orchestrator
from analyzers.base import analyzer_registry