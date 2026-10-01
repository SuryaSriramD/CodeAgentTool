"""Conservative, version-specific interpretation of Semgrep's native AST evidence.

Semgrep 1.178.0 counts every generic ``todo_kind`` as untranslated, including
metadata whose children remain ordinary generic AST nodes. Only the explicitly
audited metadata below is accepted. Executable extensions and raw trees are not.
See upstream src/parsing/tests/AST_stat.ml and src/analyzing/AST_to_IL.ml at
https://github.com/semgrep/semgrep/tree/v1.178.0 . Never persist the dumped AST.
"""
from collections import Counter
import math

POLICY = "native-parser-evidence/2"
AUDITED_VERSION = "1.178.0"
COUNTERS = ("file_count", "error_file_count", "line_count", "error_line_count",
            "total_node_count", "untranslated_node_count")


def evidence(error=None):
    return {"policy": POLICY, "status": "incomplete", "syntax_error_files": None,
            "error_lines": None, "untranslated_nodes": None,
            "untranslated_node_count": None, "audited_metadata_counts": {},
            "unsupported_node_counts": {}, "errors": [error] if error else []}


def _counts(entry):
    if not isinstance(entry, dict):
        raise ValueError("Native parser returned a non-object entry")
    for name in COUNTERS:
        if type(entry.get(name)) is not int or entry[name] < 0:
            raise ValueError(f"Native parser has invalid {name}")
    if (entry["error_file_count"] > entry["file_count"]
            or entry["error_line_count"] > entry["line_count"]
            or entry["untranslated_node_count"] > entry["total_node_count"]
            or bool(entry["error_file_count"]) != bool(entry["error_line_count"])):
        raise ValueError("Native parser returned inconsistent counters")
    rate = entry.get("parsing_rate")
    expected = 1 - entry["error_line_count"] / entry["line_count"] if entry["line_count"] else 1
    if (type(rate) not in (int, float) or not math.isfinite(rate)
            or not 0 <= rate <= 1 or not math.isclose(rate, expected, abs_tol=1e-9)):
        raise ValueError("Native parser returned an invalid parsing rate")


def parse_statistics(payload, targets, normalize):
    """Return validated per-path stats; an unreliable group invalidates all paths."""
    if not isinstance(payload, dict) or not isinstance(payload.get("projects"), list):
        raise ValueError("Native parser returned an invalid projects collection")
    wanted = set(targets)
    entries = {}
    for entry in payload["projects"]:
        _counts(entry)
        if not isinstance(entry.get("name"), str) or not entry["name"]:
            raise ValueError("Native parser returned a missing path")
        try:
            path = normalize(entry["name"])
        except (ValueError, OSError, TypeError):
            raise ValueError("Native parser returned a path outside the source inventory") from None
        if path not in wanted or path in entries:
            raise ValueError("Native parser returned an unknown or duplicate path")
        if entry["file_count"] != 1:
            raise ValueError("Native parser did not assess exactly one file per path")
        entries[path] = entry
    if set(entries) != wanted:
        raise ValueError("Native parser omitted source paths")
    if "global" in payload:
        _counts(payload["global"])
        if any(payload["global"][field] != sum(e[field] for e in entries.values()) for field in COUNTERS):
            raise ValueError("Native parser aggregate counters disagree with its paths")
    return entries


def _wrapped(value):
    return isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and value[1] == "()"


def _one(value, key):
    return isinstance(value, dict) and set(value) == {key}


def _type_payload(value):
    return (_one(value, "T") and isinstance(value["T"], dict)
            and set(value["T"]) == {"t_attrs", "t"}
            and isinstance(value["T"]["t_attrs"], list) and isinstance(value["T"]["t"], dict))


def _sized_type(value):
    if not _type_payload(value):
        return False
    typ = value["T"]
    if typ["t_attrs"] or not _one(typ["t"], "TyN") or not _one(typ["t"]["TyN"], "Id"):
        return False
    ident = typ["t"]["TyN"]["Id"]
    return (isinstance(ident, list) and len(ident) == 2 and _wrapped(ident[0])
            and ident[0][0] in {"signed", "unsigned", "short", "long", "int", "char", "float", "double"}
            and isinstance(ident[1], dict))


def _metadata(constructor, value, language):
    if not (isinstance(value, list) and len(value) == 2 and _wrapped(value[0])
            and isinstance(value[1], list)):
        return None
    label, children = value[0][0], value[1]
    if (language in {"javascript", "typescript"} and constructor == "OtherDirective"
            and label == "Export" and len(children) == 1 and _one(children[0], "I")
            and _wrapped(children[0]["I"]) and children[0]["I"][0]):
        return "OtherDirective:Export"
    if (language in {"c", "cpp"} and constructor == "OtherType" and label == "TSized"
            and children and all(_sized_type(child) for child in children)):
        return "OtherType:TSized"
    if (language == "java" and constructor == "OtherAttribute" and label == "Throw"
            and len(children) == 1 and _type_payload(children[0])):
        return "OtherAttribute:Throw"
    if language == "go" and constructor == "OtherAttribute" and label == "GoTag" and len(children) == 1:
        child = children[0]
        if (_one(child, "E") and _one(child["E"], "L") and _one(child["E"]["L"], "String")
                and _wrapped(child["E"]["L"]["String"])):
            return "OtherAttribute:GoTag"
    return None


def audit_ast(payload, language, untranslated_count, version):
    """Audit counted extensions without storing repository identifiers or source."""
    counts, unsupported, errors = Counter(), Counter(), []
    if version != AUDITED_VERSION:
        return {}, {}, ["AST metadata audit is unavailable for this Semgrep version"]
    if not _one(payload, "Pr") or not isinstance(payload["Pr"], list):
        return {}, {}, ["Native parser returned an invalid generic AST"]
    stack, extensions, visited = [payload], 0, 0
    while stack:
        node = stack.pop()
        visited += 1
        if visited > 2_000_000:
            return dict(counts), dict(unsupported), ["Generic AST audit exceeded its node limit"]
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            for constructor, child in node.items():
                if constructor.startswith(("Other", "Raw")) or constructor == "TodoK" or constructor == "OSWS_Block":
                    extensions += 1
                    audited = _metadata(constructor, child, language)
                    if audited:
                        counts[audited] += 1
                    else:
                        # Constructors are fixed engine variants. Never include raw
                        # payloads or unknown labels, which can contain source text.
                        unsupported[constructor if len(constructor) <= 64 else "UnknownExtension"] += 1
                stack.append(child)
    if unsupported:
        errors.append("Unsupported generic AST extensions: " + ", ".join(sorted(unsupported)))
    if extensions != untranslated_count:
        errors.append("Generic AST extension count disagrees with native parser statistics")
    return dict(counts), dict(unsupported), errors


def from_statistics(entry):
    item = evidence()
    item.update(syntax_error_files=entry["error_file_count"], error_lines=entry["error_line_count"],
                untranslated_nodes=entry["untranslated_node_count"],
                untranslated_node_count=entry["untranslated_node_count"])
    if entry["error_file_count"] or entry["error_line_count"]:
        item["errors"].append("Native parser reported a syntax error")
    elif not entry["untranslated_node_count"]:
        item["status"] = "completed"
    return item
