"""Independent development examples for command sources and generated artifacts."""
import hashlib
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from analyzers.common import IGNORED_DIRS, executable, inventory
from analyzers.depcheck_runner import DepCheckAnalyzer, dependency_inventory
from ingestion.policy import SOURCE_POLICY_VERSION, excluded_source_path
from ingestion.snapshots import build_snapshot, verify_snapshot
from settings import Settings


def snapshot(tmp_path, files, config=None):
    settings = Settings(storage=tmp_path / "storage", team_mode=False)
    settings.prepare()
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        for name, content in files.items():
            stream.writestr(name, content)
    manifest = build_snapshot(archive, "commands", settings, {"source": "zip"}, config or {})
    return settings.storage / "snapshots/commands/source", manifest, settings, archive


def test_bin_sources_and_nested_dependency_evidence_survive_ingestion(tmp_path):
    files = {
        "bin/announce.sh": "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\"\n",
        "tools/bin/status.py": "def status():\n    return 'ready'\n",
        "bin/commands/inspect.ts": "const inspected = process.argv.length;\n",
        "bin/library/Service.cs": "class Service { public int Count() => 3; }\n",
        "bin/project/requirements.txt": "requests==2.32.4\n",
        "bin/README.md": "These are maintained command-line entry points.\n",
    }
    root, manifest, _, _ = snapshot(tmp_path, files)
    assert manifest["files"] == {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}
    assert manifest["source_inventory"] == sorted(files)
    assert manifest["excluded_files"] == []
    assert manifest["source_policy_version"] == SOURCE_POLICY_VERSION
    assert manifest["ingestion_version"] == 3
    assert dict(inventory(root))["bin/announce.sh"] == "bash"
    assert dict(inventory(root))["tools/bin/status.py"] == "python"
    assert dict(inventory(root))["bin/commands/inspect.ts"] == "typescript"
    assert dict(inventory(root))["bin/library/Service.cs"] == "csharp"
    assert dependency_inventory(root) == ([("bin/project/requirements.txt", "python")], set())
    verify_snapshot(root, manifest)


@pytest.mark.parametrize("name", [
    "bin/Debug/App.dll", "bin/Release/App.exe", "bin/Debug/App.pdb", "bin/helpers.o",
    "bin/helpers.obj", "bin/helpers.a", "bin/helpers.lib", "bin/Helpers.class", "bin/libhelpers.dylib",
    "bin/.env", "bin/.env.production", "bin/id_rsa", "bin/server.pem", "bin/._launch.sh",
    "bin/.DS_Store", "bin/build/generated.sh", "bin/obj/generated.cs", "dist/bin/generated.sh",
    "tools/vendor/bin/vendor.sh", "bin/node_modules/command/index.js", "bin/.svn/source.sh",
    "bin/.pytest_cache/entry.py",
])
def test_known_outputs_credentials_and_ignored_directories_stay_excluded(tmp_path, name):
    # Even text-shaped files with known compiled extensions remain artifacts.
    files = {"bin/entry.sh": "printf 'entry\\n'\n", name: "generated or secret\n"}
    root, manifest, _, _ = snapshot(tmp_path, files)
    assert excluded_source_path(name)
    assert set(manifest["files"]) == {"bin/entry.sh"}
    assert manifest["excluded_files"] == [name]
    assert [path for path, _ in inventory(root)] == ["bin/entry.sh"]
    # Inventory has the same path policy when invoked directly on a workspace.
    excluded = root / name
    excluded.parent.mkdir(parents=True, exist_ok=True)
    excluded.write_text(files[name])
    assert [path for path, _ in inventory(root)] == ["bin/entry.sh"]


def test_binary_content_and_user_exclusions_under_bin_remain_effective(tmp_path):
    files = {"bin/binary": b"\x7fELF\0payload", "bin/entry.sh": "printf 'entry\\n'\n",
             "bin/disabled.sh": "printf 'disabled\\n'\n"}
    root, manifest, _, _ = snapshot(tmp_path, files, {"exclude": ["bin/disabled.sh"]})
    assert set(manifest["files"]) == {"bin/entry.sh"}
    assert manifest["excluded_files"] == ["bin/binary", "bin/disabled.sh"]
    assert [path for path, _ in inventory(root)] == ["bin/entry.sh"]


def test_scanner_inventory_never_follows_bin_symlinks(tmp_path):
    (tmp_path / "source/bin").mkdir(parents=True)
    (tmp_path / "outside.sh").write_text("printf 'outside\\n'\n")
    (tmp_path / "source/bin/external.sh").symlink_to(tmp_path / "outside.sh")
    (tmp_path / "source/bin/external_dir").symlink_to(tmp_path, target_is_directory=True)
    assert inventory(tmp_path / "source") == []


def test_existing_snapshot_stays_immutable_when_policy_changes(tmp_path):
    root, manifest, settings, archive = snapshot(tmp_path, {"bin/entry.sh": "printf 'entry\\n'\n"})
    # Model an old saved snapshot in which the same archive's bin source was excluded.
    (root / "bin/entry.sh").unlink()
    old = {**manifest, "files": {}, "digest": hashlib.sha256(b"{}").hexdigest(),
           "excluded_files": ["bin/entry.sh"], "ingestion_version": 2}
    old.pop("source_policy_version")
    (root.parent / "manifest.json").write_text(json.dumps(old))
    assert build_snapshot(archive, "commands", settings, {"source": "zip"}, {}) == old
    assert not (root / "bin/entry.sh").exists()


def test_trivy_does_not_skip_bin_dependency_projects(tmp_path, monkeypatch):
    import analyzers.depcheck_runner as module
    root = tmp_path / "source"
    (root / "bin/project").mkdir(parents=True)
    (root / "bin/project/requirements.txt").write_text("requests==2.32.4\n")
    cache = tmp_path / "cache"
    (cache / "db").mkdir(parents=True)
    (cache / "db/metadata.json").write_text('{}')
    monkeypatch.setattr(module, "cache_dir", lambda: cache)
    monkeypatch.setattr(module, "database_ready", lambda: True)
    monkeypatch.setattr(module, "executable", lambda _: "/trusted/trivy")
    monkeypatch.setattr(module, "tool_version", lambda *_, **__: "test-version")
    analyzer = DepCheckAnalyzer()
    def trusted_response(command, workspace, **kwargs):
        assert command[command.index("--skip-dirs") + 1].split(",") == sorted(IGNORED_DIRS)
        assert "bin" not in IGNORED_DIRS
        assert {"--offline-scan", "--skip-db-update", "--skip-java-db-update"}.issubset(command)
        return SimpleNamespace(returncode=0, stderr="", stdout=json.dumps({"SchemaVersion": 2,
            "Results": [{"Target": "bin/project/requirements.txt", "Packages": []}]}))
    monkeypatch.setattr(analyzer, "_run_command", trusted_response)
    report = analyzer.run_analysis(str(root))
    assert report.status == "completed"
    assert report.coverage["scanned_paths"] == ["bin/project/requirements.txt"]


@pytest.mark.skipif(not executable("semgrep"), reason="Trusted pinned Semgrep engine is required")
def test_actual_engine_parses_and_checks_source_under_bin(tmp_path):
    from analyzers.semgrep_runner import SemgrepAnalyzer
    root, manifest, _, _ = snapshot(tmp_path, {
        "bin/announce.sh": "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\"\n",
    })
    report = SemgrepAnalyzer(timeout_sec=30, profile="security-v2").run_analysis(str(root))
    assert report.status == "completed", report.coverage
    assert report.coverage["scanned_paths"] == ["bin/announce.sh"]
    assert report.coverage["path_outcomes"][0]["status"] == "completed"
    assert len(manifest["files"]) == 1
