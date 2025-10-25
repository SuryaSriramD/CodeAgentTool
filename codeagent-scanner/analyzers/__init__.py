"""Initialize analyzers package and register all analyzers."""

# Import all analyzer implementations to register them
from .semgrep_runner import SemgrepAnalyzer
from .bandit_runner import BanditAnalyzer
from .depcheck_runner import DepCheckAnalyzer

# The analyzers are automatically registered when imported