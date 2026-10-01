"""Pure audit checks using small generic-AST controls, never held-out source."""
from copy import deepcopy

import pytest

from analyzers.parser_evidence import audit_ast, parse_statistics, from_statistics


def wrapped(text):
    return [text, "()"]


def typ(name):
    return {"T": {"t_attrs": [], "t": {"TyN": {"Id": [wrapped(name), {}]}}}}


CONTROLS = [
    ("javascript", {"OtherDirective": [wrapped("Export"), [{"I": wrapped("f")}]]}, "OtherDirective:Export"),
    ("typescript", {"OtherDirective": [wrapped("Export"), [{"I": wrapped("f")}]]}, "OtherDirective:Export"),
    ("c", {"OtherType": [wrapped("TSized"), [typ("unsigned"), typ("int")]]}, "OtherType:TSized"),
    ("cpp", {"OtherType": [wrapped("TSized"), [typ("unsigned"), typ("char")]]}, "OtherType:TSized"),
    ("java", {"OtherAttribute": [wrapped("Throw"), [typ("Exception")]]}, "OtherAttribute:Throw"),
    ("go", {"OtherAttribute": [wrapped("GoTag"), [{"E": {"L": {"String": wrapped('json:"message"')}}}]]}, "OtherAttribute:GoTag"),
]


@pytest.mark.parametrize("language,node,label", CONTROLS)
def test_exact_metadata_is_audited_without_persisting_source(language, node, label):
    counts, unsupported, errors = audit_ast({"Pr": [node]}, language, 1, "1.178.0")
    assert counts == {label: 1}
    assert unsupported == {} and errors == []


@pytest.mark.parametrize("language,node,label", CONTROLS)
def test_metadata_requires_pinned_version_and_correct_language(language, node, label):
    assert audit_ast({"Pr": [node]}, language, 1, "1.179.0")[2]
    assert audit_ast({"Pr": [node]}, "python", 1, "1.178.0")[2]


@pytest.mark.parametrize("constructor", ["OtherExpr", "OtherStmt", "RawExpr", "RawStmt", "TodoK", "OSWS_Block"])
def test_unhandled_or_raw_nodes_stay_incomplete(constructor):
    counts, unsupported, errors = audit_ast({"Pr": [{constructor: [wrapped("Send"), []]}]}, "go", 1, "1.178.0")
    assert counts == {} and unsupported == {constructor: 1} and errors


def test_allowed_metadata_does_not_hide_nested_executable_extension():
    node = {"OtherAttribute": [wrapped("Throw"), [
        {"T": {"t_attrs": [], "t": {"OtherExpr": [wrapped("SecretExpression"), []]}}}]]}
    counts, unsupported, errors = audit_ast({"Pr": [node]}, "java", 2, "1.178.0")
    assert counts == {"OtherAttribute:Throw": 1}
    assert unsupported == {"OtherExpr": 1}
    assert errors and "SecretExpression" not in str((counts, unsupported, errors))


@pytest.mark.parametrize("payload", [None, {}, {"results": []}, {"Pr": {}}, {"Pr": [], "Other": []}])
def test_invalid_ast_cannot_satisfy_metadata_audit(payload):
    assert audit_ast(payload, "javascript", 1, "1.178.0")[2]


def test_unknown_metadata_and_count_mismatches_fail_closed():
    node = deepcopy(CONTROLS[0][1])
    assert audit_ast({"Pr": [node]}, "javascript", 2, "1.178.0")[2]
    node["OtherDirective"][0] = wrapped("UnknownExport")
    assert audit_ast({"Pr": [node]}, "javascript", 1, "1.178.0")[2]


@pytest.mark.parametrize("language,node,label", CONTROLS)
def test_known_label_does_not_authorize_arbitrary_payload(language, node, label):
    node = deepcopy(node)
    node[next(iter(node))][1] = [{"E": {"Call": []}}]
    assert audit_ast({"Pr": [node]}, language, 1, "1.178.0")[2]


def stats():
    return {"projects": [{"name": "main.js", "file_count": 1, "error_file_count": 0,
                          "line_count": 2, "error_line_count": 0, "total_node_count": 12,
                          "untranslated_node_count": 0, "parsing_rate": 1.0}]}


@pytest.mark.parametrize("field", ["file_count", "error_file_count", "line_count", "error_line_count", "total_node_count", "untranslated_node_count"])
@pytest.mark.parametrize("bad", [None, True, 0.0, -1, "0"])
def test_all_native_counters_have_strict_integer_types(field, bad):
    data = stats()
    data["projects"][0][field] = bad
    with pytest.raises(ValueError):
        parse_statistics(data, ["main.js"], lambda path: path)


@pytest.mark.parametrize("rate", [None, True, "1", float("nan"), float("inf"), -1, 0.5])
def test_parsing_rate_must_be_finite_and_agree_with_line_counts(rate):
    data = stats()
    data["projects"][0]["parsing_rate"] = rate
    with pytest.raises(ValueError):
        parse_statistics(data, ["main.js"], lambda path: path)


def test_optional_aggregate_must_agree_and_no_missing_group_path_is_accepted():
    data = stats()
    data["global"] = dict(data["projects"][0], name="*", total_node_count=13)
    with pytest.raises(ValueError):
        parse_statistics(data, ["main.js"], lambda path: path)
    with pytest.raises(ValueError):
        parse_statistics(stats(), ["main.js", "other.js"], lambda path: path)


def test_native_syntax_failure_is_distinct_from_auditable_metadata():
    entry = stats()["projects"][0]
    assert from_statistics(entry)["status"] == "completed"
    entry.update(untranslated_node_count=1)
    assert from_statistics(entry)["status"] == "incomplete"
    entry.update(error_file_count=1, error_line_count=1, parsing_rate=0.5)
    assert from_statistics(entry)["errors"] == ["Native parser reported a syntax error"]
