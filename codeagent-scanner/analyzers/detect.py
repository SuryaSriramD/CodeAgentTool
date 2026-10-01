"""Selection is driven by the same inventory each analyzer actually consumes."""
from pathlib import Path
from .base import analyzer_registry
from .common import inventory, IGNORED_DIRS
from .depcheck_runner import dependency_inventory

def detect_applicable_analyzers(workspace_path, available_analyzers):
    return [name for name in available_analyzers if (tool := analyzer_registry.get_analyzer(name)) is not None and tool.is_applicable(workspace_path)]

def _scan_workspace(workspace_path):
    files = {p for p,_ in inventory(workspace_path)}
    return {'files': files, 'extensions': {Path(p).suffix.lower() for p in files}, 'total_files':len(files),
            'directories': {str(Path(p).parent) for p in files}}

def _is_analyzer_applicable(analyzer_name, file_info, workspace_path):
    analyzer = analyzer_registry.get_analyzer(analyzer_name)
    return bool(analyzer and analyzer.is_applicable(workspace_path))

def _find_dependency_files(workspace_path, file_info=None):
    return [p for p,_ in dependency_inventory(workspace_path)[0]]

def _is_ignored_directory(name): return name in IGNORED_DIRS

def _is_ignored_file(name): return name.startswith('._') or name == '.DS_Store'

def get_analyzer_defaults(): return ['semgrep', 'bandit', 'dotnet', 'depcheck']

def filter_analyzers_by_config(requested, allowed):
    return [name for name in requested if not allowed or name in allowed]
