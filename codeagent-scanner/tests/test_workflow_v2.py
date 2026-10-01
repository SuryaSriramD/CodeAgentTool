"""No-network checks for proposal workflow, durable replay, and provider adapters."""

import asyncio
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integration.context import ContextError, SourceContext, source_hash
from integration.models import (
    AnalystOutput, AuthorOutput, ProviderError, ProviderResult,
    ReviewCancelled, ReviewInterrupted,
)
from integration.providers import OllamaProvider, OpenAIProvider
from integration.workflow import run_review


SOURCE = "import subprocess\nsubprocess.run(command, shell=True)\n"
TRIAGE = {"disposition": "confirmed", "explanation": "Untrusted command reaches a shell",
          "evidence": [{"file": "app.py", "line_start": 2, "line_end": 2}], "context_requests": []}
AUTHOR = {"edits": [{"file": "app.py", "original": "subprocess.run(command, shell=True)",
                     "replacement": "subprocess.run(command, shell=False)"}],
          "explanation": "Avoid shell interpretation; caller must supply an argument list.",
          "checks": ["Confirm command is an argument list and run project tests"]}
APPROVE = {"decision": "approve", "comments": ["Proposal is suitable for human review"]}


class FakeProvider:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    async def generate(self, messages, schema, **kwargs):
        self.calls.append({"messages": copy.deepcopy(messages), "schema": schema.__name__})
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        if callable(output):
            output = output()
        return ProviderResult(output, {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20})


@pytest.fixture
def review_case(tmp_path):
    (tmp_path / "app.py").write_text(SOURCE)
    report = {"files": [{"path": "app.py", "source_hash": source_hash(SOURCE), "issues": [{
        "id": "finding1", "severity": "high", "type": "shell_injection", "line": 2,
        "message": "Possible shell injection", "tool": "example"}]}]}
    steps, events = {}, []

    def save(key, data):
        steps[key] = copy.deepcopy(data)
        events.append((key, copy.deepcopy(data)))

    async def validated(payload, *, is_cancelled):
        return {"status": "passed", "syntax": {"status": "passed", "errors": []},
                "target_findings_remaining": [], "introduced_findings": [], "errors": [],
                "coverage_after": [{"tool": "fixture", "status": "completed"}]}

    async def run(outputs, **config):
        fake = outputs if isinstance(outputs, FakeProvider) else FakeProvider(outputs)
        result = await run_review(report, str(tmp_path), {
            "provider": "ollama", "model": "test", "_provider": fake, "_validator": validated, **config,
        }, on_step=save, load_step=steps.get, is_cancelled=lambda: False)
        return result, fake

    return SimpleNamespace(path=tmp_path, report=report, steps=steps, events=events, save=save, run=run)


@pytest.mark.asyncio
async def test_reviewed_proposal_is_anchored_unapplied_and_untested(review_case):
    result, fake = await review_case.run([TRIAGE, AUTHOR, APPROVE])
    assert result["status"] == "complete"
    proposal = result["proposals"][0]
    assert proposal["status"] == "reviewed"
    assert proposal["edits"][0]["source_hash"] == source_hash(SOURCE)
    assert "--- a/app.py\n+++ b/app.py" in proposal["diff"]
    assert not proposal["applied"] and not proposal["tested"]
    assert (review_case.path / "app.py").read_text() == SOURCE
    assert len(fake.calls) == 3
    reviewer_input = json.loads(fake.calls[2]["messages"][1]["content"])
    assert "triage" not in reviewer_input
    assert "source" in reviewer_input and "proposal" in reviewer_input
    assert [data["status"] for _, data in review_case.events if data["role"] != "validator"] == ["running", "completed"] * 3
    assert result["usage"]["model_calls"] == 3


@pytest.mark.asyncio
async def test_completed_matching_checkpoints_make_no_new_calls(review_case):
    first, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE])
    second, fake = await review_case.run([])
    assert fake.calls == []
    assert first["proposals"] == second["proposals"]
    assert second["usage"]["cached_steps"] == 3
    assert second["usage"]["total_tokens"] == 60


@pytest.mark.asyncio
async def test_changed_model_does_not_reuse_checkpoint(review_case):
    await review_case.run([TRIAGE, AUTHOR, APPROVE])
    _, fake = await review_case.run([TRIAGE, AUTHOR, APPROVE], model="other-model")
    assert len(fake.calls) == 3


@pytest.mark.asyncio
async def test_reviewer_rejection_is_visible(review_case):
    result, _ = await review_case.run([TRIAGE, AUTHOR, {"decision": "reject", "comments": ["Input type is unsupported"]}])
    assert result["proposals"][0]["status"] == "rejected"
    assert result["proposals"][0]["review"]["comments"] == ["Input type is unsupported"]


@pytest.mark.asyncio
async def test_revision_is_bounded_and_unresolved_result_is_kept(review_case):
    request = {"decision": "request_revision", "comments": ["Explain input type migration"]}
    result, fake = await review_case.run([TRIAGE, AUTHOR, request, AUTHOR, request])
    assert len(fake.calls) == 5
    assert result["status"] == "partial"
    assert result["proposals"][0]["status"] == "unresolved"
    assert result["proposals"][0]["revision"] == 1


@pytest.mark.asyncio
async def test_false_positive_has_evidence_and_no_author(review_case):
    result, fake = await review_case.run([{**TRIAGE, "disposition": "false_positive"}])
    assert len(fake.calls) == 1 and not result["proposals"]
    assert result["triage"][0]["evidence"][0]["excerpt"] == SOURCE.splitlines(keepends=True)[1]


@pytest.mark.asyncio
async def test_invalid_provider_output_never_manufactures_fix(review_case):
    result, _ = await review_case.run([{"fixes": "not the triage contract"}])
    assert result["status"] == "failed" and result["proposals"] == []
    assert review_case.steps["finding:finding1:analyst:0"]["status"] == "failed"
    again, fake = await review_case.run([])
    assert again["status"] == "failed" and not fake.calls


@pytest.mark.asyncio
async def test_ambiguous_edit_is_rejected_before_reviewer(review_case):
    author = copy.deepcopy(AUTHOR)
    author["edits"][0]["original"] = "s"
    result, fake = await review_case.run([TRIAGE, author])
    assert result["status"] == "partial" and not result["proposals"]
    assert "exactly once" in result["errors"][0]["message"]
    assert len(fake.calls) == 2
    key = "finding:finding1:author:0"
    assert review_case.steps[key]["status"] == "failed"
    review_case.steps[key]["status"] = "retry_requested"
    repaired, fake = await review_case.run([AUTHOR, APPROVE])
    assert repaired["status"] == "complete"
    assert len(fake.calls) == 2 and repaired["usage"]["model_calls"] == 4


@pytest.mark.asyncio
async def test_source_hash_mismatch_prevents_paid_call(review_case):
    (review_case.path / "app.py").write_text(SOURCE + "# changed\n")
    result, fake = await review_case.run([])
    assert result["status"] == "failed" and not fake.calls
    assert "changed since the scan" in result["errors"][0]["message"]


@pytest.mark.asyncio
async def test_source_mutated_during_triage_cannot_get_false_positive_status(review_case):
    def change_source():
        (review_case.path / "app.py").write_text(SOURCE + "# modified during call\n")
        return {**TRIAGE, "disposition": "false_positive"}

    result, _ = await review_case.run([change_source])
    assert result["status"] == "failed"
    assert not result["triage"] and not result["proposals"]


@pytest.mark.asyncio
async def test_model_budget_stops_before_next_call_and_preserves_proposal(review_case):
    result, fake = await review_case.run([TRIAGE, AUTHOR], max_model_calls=2)
    assert len(fake.calls) == 2 and result["status"] == "partial"
    assert result["errors"][0]["code"] == "budget_exhausted"
    assert result["proposals"][0]["status"] == "unresolved"


@pytest.mark.asyncio
async def test_token_reservation_stops_before_first_call(review_case):
    result, fake = await review_case.run([], max_total_tokens=1)
    assert result["status"] == "failed" and not fake.calls


@pytest.mark.asyncio
async def test_uncertain_provider_call_requires_explicit_retry(review_case):
    with pytest.raises(ReviewInterrupted):
        await review_case.run([ProviderError("connection lost", uncertain=True)])
    key = "finding:finding1:analyst:0"
    assert review_case.steps[key]["status"] == "interrupted"
    with pytest.raises(ReviewInterrupted):
        await review_case.run([])
    review_case.steps[key]["status"] = "retry_requested"
    result, _ = await review_case.run([TRIAGE, AUTHOR, APPROVE])
    assert result["status"] == "complete"
    assert result["usage"]["model_calls"] == 4
    assert not result["usage"]["usage_complete"]
    assert review_case.steps[key]["attempt"] == 2


@pytest.mark.asyncio
async def test_cancel_before_any_call(review_case):
    fake = FakeProvider([])
    with pytest.raises(ReviewCancelled):
        await run_review(review_case.report, str(review_case.path), {"_provider": fake},
                         on_step=review_case.save, load_step=review_case.steps.get,
                         is_cancelled=lambda: True)
    assert not fake.calls


@pytest.mark.asyncio
async def test_cancellation_during_call_marks_checkpoint(review_case):
    cancelled = False

    class SlowProvider:
        async def generate(self, *args, **kwargs):
            nonlocal cancelled
            cancelled = True
            await asyncio.Event().wait()

    with pytest.raises(ReviewCancelled):
        await run_review(review_case.report, str(review_case.path), {"_provider": SlowProvider()},
                         on_step=review_case.save, load_step=review_case.steps.get,
                         is_cancelled=lambda: cancelled)
    assert review_case.steps["finding:finding1:analyst:0"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_bounded_context_tools_and_replay(review_case):
    (review_case.path / "helper.go").write_text("package helper\nfunc Safe() {}\n")
    request = {"disposition": "needs_context", "explanation": "Need helper context", "evidence": [],
               "context_requests": [{"kind": "search", "query": "func Safe"}]}
    result, fake = await review_case.run([request, TRIAGE, AUTHOR, APPROVE])
    assert result["status"] == "complete" and len(fake.calls) == 4
    analyst_second = json.loads(fake.calls[1]["messages"][1]["content"])
    assert analyst_second["context_results"][0]["result"][0]["file"] == "helper.go"
    replay, fake = await review_case.run([])
    assert replay["status"] == "complete" and not fake.calls


@pytest.mark.asyncio
async def test_author_and_independent_reviewer_can_read_and_search_with_durable_replay(review_case):
    (review_case.path / "caller.py").write_text("command = ['echo', user_input]\n")
    author_request = {"edits": [], "explanation": "Need the caller's argument type", "checks": [],
                      "context_requests": [{"kind": "read", "file": "caller.py", "line_start": 1, "line_end": 1}]}
    reviewer_request = {"decision": "needs_context", "comments": ["Check all callers"],
                        "context_requests": [{"kind": "search", "query": "user_input"}]}
    result, fake = await review_case.run([TRIAGE, author_request, AUTHOR, reviewer_request, APPROVE])
    assert result["status"] == "complete" and len(fake.calls) == 5
    author_input = json.loads(fake.calls[2]["messages"][1]["content"])
    assert author_input["context_results"][0]["result"]["file"] == "caller.py"
    reviewer_input = json.loads(fake.calls[4]["messages"][1]["content"])
    assert "triage" not in reviewer_input and "previous_proposal" not in reviewer_input
    assert reviewer_input["context_results"][-1]["result"][0]["file"] == "caller.py"
    assert all(len(call["messages"]) == 2 for call in fake.calls)
    assert "finding:finding1:author:0:context:1" in review_case.steps
    assert "finding:finding1:reviewer:0:context:1" in review_case.steps
    replay, fake = await review_case.run([])
    assert not fake.calls and replay["proposals"] == result["proposals"]
    assert replay["usage"]["cached_steps"] == 5


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["author", "reviewer"])
async def test_each_proposal_role_has_at_most_two_retrieval_rounds(review_case, role):
    requests = [{"kind": "read", "file": ".env", "line_start": 1, "line_end": 1}]
    if role == "author":
        request = {"edits": [], "explanation": "Need context", "context_requests": requests}
        outputs = [TRIAGE, request, request, request]
    else:
        request = {"decision": "needs_context", "comments": ["Need context"], "context_requests": requests}
        outputs = [TRIAGE, AUTHOR, request, request, request]
    result, fake = await review_case.run(outputs)
    assert result["status"] == "partial" and len(fake.calls) == len(outputs)
    last_input = json.loads(fake.calls[-1]["messages"][1]["content"])
    assert len(last_input["context_results"]) == 2
    assert all("error" in action for action in last_input["context_results"])
    if role == "author":
        assert not result["proposals"] and "retrieval was exhausted" in result["errors"][0]["message"]
    else:
        assert result["proposals"][0]["status"] == "unresolved"
        assert result["proposals"][0]["review"]["decision"] == "needs_context"
    replay, fake = await review_case.run([])
    assert not fake.calls and replay["status"] == "partial"


@pytest.mark.asyncio
async def test_retrieval_calls_obey_shared_model_budget(review_case):
    request = {"edits": [], "explanation": "Need caller", "context_requests": [{"kind": "search", "query": "command"}]}
    result, fake = await review_case.run([TRIAGE, request], max_model_calls=2)
    assert len(fake.calls) == 2 and result["status"] == "partial"
    assert result["errors"][0]["code"] == "budget_exhausted" and not result["proposals"]


@pytest.mark.asyncio
async def test_related_group_preserves_individual_provenance_and_bounded_context(review_case):
    issues = review_case.report["files"][0]["issues"]
    issues.extend({**issues[0], "id": f"finding{index}"} for index in range(2, 12))
    result, fake = await review_case.run([{ "findings": [{**TRIAGE, "finding_id": f"finding{index}"} for index in [1, 10, 11, 2, 3]]}], max_model_calls=1)
    group = result["finding_groups"][0]
    assert [len(item["finding_ids"]) for item in result["finding_groups"]] == [5, 5, 1]
    model_input = json.loads(fake.calls[0]["messages"][1]["content"])
    assert model_input["findings"][0]["id"] == "finding1"
    assert len(model_input["findings"]) == 5 and "finding" not in model_input
    assert result["triage"][0]["group_id"] == group["id"]


@pytest.mark.asyncio
async def test_interruption_preserves_completed_and_current_proposals_for_explicit_resume(review_case):
    issues = review_case.report["files"][0]["issues"]
    issues.append({**issues[0], "id": "finding2"})
    with pytest.raises(ReviewInterrupted) as caught:
        await review_case.run([{ "findings": [{**TRIAGE, "finding_id": value} for value in ["finding1", "finding2"]]}, AUTHOR, APPROVE, AUTHOR,
                               ProviderError("connection lost", uncertain=True)])
    partial = caught.value.partial_result
    assert partial["status"] == "interrupted"
    assert len(partial["triage"]) == 2 and len(partial["proposals"]) == 2
    assert [proposal["status"] for proposal in partial["proposals"]] == ["reviewed", "unresolved"]
    assert partial["usage"]["model_calls"] == 5 and not partial["usage"]["usage_complete"]
    with pytest.raises(ReviewInterrupted) as replayed:
        await review_case.run([])
    assert replayed.value.partial_result["proposals"] == partial["proposals"]
    assert replayed.value.partial_result["usage"]["model_calls"] == 5
    review_case.steps["finding:finding2:reviewer:0"]["status"] = "retry_requested"
    resumed, fake = await review_case.run([APPROVE])
    assert len(fake.calls) == 1 and resumed["status"] == "complete"
    assert len(resumed["proposals"]) == 2 and resumed["usage"]["model_calls"] == 6
    assert resumed["proposals"][0]["finding_ids"] == ["finding1"]
    assert resumed["proposals"][0]["related_finding_ids"] == ["finding2"]


@pytest.mark.asyncio
async def test_stage_records_effective_provider_model(review_case):
    class ActualModelProvider(FakeProvider):
        async def generate(self, *args, **kwargs):
            response = await super().generate(*args, **kwargs)
            response.usage["effective_model"] = "local-resolved-model"
            return response

    await review_case.run(ActualModelProvider([TRIAGE, AUTHOR, APPROVE]))
    assert all(step["provider"] == "ollama" and step["model"] == "local-resolved-model"
               for step in review_case.steps.values() if step["role"] != "validator")
    assert all(step["model"] == "test" for _, step in review_case.events if step["status"] == "running")


@pytest.mark.asyncio
async def test_configured_credentials_are_masked_before_all_model_calls(review_case):
    secret = "configured-private-token-CANARY-9274"
    source = SOURCE + f"# accidental credential: {secret}\n"
    (review_case.path / "app.py").write_text(source)
    review_case.report["files"][0]["source_hash"] = source_hash(source)
    review_case.report["files"][0]["issues"][0]["message"] += f" {secret}"
    result, fake = await review_case.run([TRIAGE, AUTHOR, APPROVE], _sensitive_values=[secret])
    assert result["status"] == "complete" and len(fake.calls) == 3
    assert secret not in json.dumps(fake.calls)
    assert "[REDACTED]" in fake.calls[0]["messages"][1]["content"]
    assert (review_case.path / "app.py").read_text() == source
    assert result["proposals"][0]["edits"][0]["source_hash"] == source_hash(source)


@pytest.mark.asyncio
async def test_edit_based_on_masked_credential_is_rejected_against_original_source(review_case):
    secret = "configured-secret-CANARY-2732"
    source = SOURCE + f"token = '{secret}'\n"
    (review_case.path / "app.py").write_text(source)
    review_case.report["files"][0]["source_hash"] = source_hash(source)
    authored = {**AUTHOR, "edits": [{"file": "app.py", "original": "token = '[REDACTED]'", "replacement": "token = ''"}]}
    result, fake = await review_case.run([TRIAGE, authored], _sensitive_values=[secret])
    assert result["status"] == "partial" and not result["proposals"] and len(fake.calls) == 2
    assert "exactly once" in result["errors"][0]["message"]


@pytest.mark.asyncio
async def test_known_failed_response_preserves_actual_usage_and_model_across_replay(review_case):
    failure = ProviderError("Structured result is invalid", code="invalid_output", usage={
        "input_tokens": 40, "output_tokens": 30, "total_tokens": 70, "effective_model": "resolved-model"})
    result, _ = await review_case.run([TRIAGE, AUTHOR, failure])
    assert result["status"] == "partial" and result["usage"]["usage_complete"]
    assert result["usage"]["total_tokens"] == result["usage"]["accounted_tokens"] == 110
    step = review_case.steps["finding:finding1:reviewer:0"]
    assert step["model"] == "resolved-model" and step["usage"]["total_tokens"] == 70
    assert step["status"] == "failed"
    replay, fake = await review_case.run([])
    assert not fake.calls and replay["usage"]["total_tokens"] == 110
    review_case.steps["finding:finding1:reviewer:0"]["status"] = "retry_requested"
    retried, fake = await review_case.run([APPROVE])
    assert len(fake.calls) == 1 and retried["usage"]["total_tokens"] == 130
    assert retried["usage"]["model_calls"] == 4 and retried["usage"]["usage_complete"]


@pytest.mark.asyncio
async def test_runner_validation_failure_keeps_usage_when_adapter_returned_a_result(review_case):
    result, _ = await review_case.run([{"invalid": "triage"}])
    assert result["status"] == "failed"
    assert result["usage"]["total_tokens"] == 20 and result["usage"]["usage_complete"]
    assert review_case.steps["finding:finding1:analyst:0"]["usage"]["accounted_tokens"] == 20


@pytest.mark.parametrize("filename", ["sample.py", "sample.js", "sample.ts", "sample.tsx", "sample.java",
                                     "sample.go", "sample.rb", "sample.php", "sample.c", "sample.cpp",
                                     "sample.cs", "sample.fs", "sample.vb", "sample.rs", "sample.kt", "sample.swift"])
def test_context_is_language_neutral(tmp_path, filename):
    (tmp_path / filename).write_text("first\nsecond\n")
    context = SourceContext(str(tmp_path))
    assert context.read(filename, 2, 2)["content"] == "second\n"


def test_context_rejects_secrets_traversal_symlinks_binary(tmp_path):
    (tmp_path / ".env").write_text("secret")
    (tmp_path / "app.py").write_text(SOURCE)
    (tmp_path / "alias.py").symlink_to(tmp_path / "app.py")
    (tmp_path / "binary.dat").write_bytes(b"a\x00b")
    context = SourceContext(str(tmp_path))
    for path in ("../app.py", str(tmp_path / "app.py"), ".env", "alias.py", "binary.dat"):
        with pytest.raises(ContextError):
            context.read(path)


def test_overlapping_edits_and_unseen_evidence_are_rejected(tmp_path):
    (tmp_path / "app.py").write_text(SOURCE)
    context = SourceContext(str(tmp_path))
    context.read("app.py")
    edits = [AUTHOR["edits"][0], {"file": "app.py", "original": "shell=True", "replacement": "shell=False"}]
    with pytest.raises(ContextError, match="overlap"):
        context.proposal(AuthorOutput(edits=edits, explanation="example", checks=[]), "id")


@pytest.mark.asyncio
async def test_ollama_uses_native_json_schema_without_cloud_fallback():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"done": True, "done_reason": "stop",
            "message": {"content": json.dumps(TRIAGE)}, "prompt_eval_count": 4, "eval_count": 8})

    provider = OllamaProvider({"model": "local-test", "base_url": "http://local.invalid"})
    await provider.client.aclose()
    provider.client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    try:
        response = await provider.generate([], AnalystOutput, max_output_tokens=100, timeout_sec=1)
    finally:
        await provider.aclose()
    body = json.loads(requests[0].content)
    assert requests[0].url.path == "/api/chat" and isinstance(body["format"], dict)
    assert body["stream"] is False and body["model"] == "local-test"
    assert response.usage["total_tokens"] == 12


@pytest.mark.asyncio
async def test_ollama_incomplete_response_is_a_failure():
    provider = OllamaProvider({"model": "local-test"})
    await provider.client.aclose()
    provider.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
        json={"done": True, "done_reason": "length", "message": {"content": json.dumps(TRIAGE)},
              "model": "local-resolved", "prompt_eval_count": 4, "eval_count": 8})))
    try:
        with pytest.raises(ProviderError, match="incomplete") as caught:
            await provider.generate([], AnalystOutput, max_output_tokens=10, timeout_sec=1)
        assert caught.value.usage["total_tokens"] == 12
        assert caught.value.usage["effective_model"] == "local-resolved"
    finally:
        await provider.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ['{"unexpected":"shape"}', 'not-json'])
async def test_ollama_schema_failures_keep_reported_token_usage(content):
    provider = OllamaProvider({"model": "local-test"})
    await provider.client.aclose()
    provider.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200,
        json={"done": True, "done_reason": "stop", "message": {"content": content},
              "model": "resolved-local", "prompt_eval_count": 11, "eval_count": 13})))
    try:
        with pytest.raises(ProviderError, match="required schema") as caught:
            await provider.generate([], AnalystOutput, max_output_tokens=100, timeout_sec=1)
        assert caught.value.usage["total_tokens"] == 24 and not caught.value.uncertain
        assert caught.value.usage["effective_model"] == "resolved-local"
    finally:
        await provider.aclose()


@pytest.mark.asyncio
async def test_openai_uses_responses_structured_contract(monkeypatch):
    captured = {}

    class Responses:
        async def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(status="completed", output_parsed=AnalystOutput.model_validate(TRIAGE),
                                   usage=SimpleNamespace(input_tokens=4, output_tokens=8, total_tokens=12), id="test-response")

    def client(**kwargs):
        captured["client"] = kwargs
        return SimpleNamespace(responses=Responses())

    monkeypatch.setattr("openai.AsyncOpenAI", client)
    provider = OpenAIProvider({"model": "cloud-test", "api_key": "fake-key"})
    result = await provider.generate([], AnalystOutput, max_output_tokens=100, timeout_sec=1)
    assert captured["client"]["max_retries"] == 0
    assert captured["text_format"] is AnalystOutput and captured["store"] is False
    assert result.output["disposition"] == "confirmed"


@pytest.mark.asyncio
@pytest.mark.parametrize("status,parsed", [("incomplete", None), ("completed", None), ("completed", {"bad": "output"})])
async def test_openai_known_unsuccessful_response_keeps_usage(monkeypatch, status, parsed):
    class Responses:
        async def parse(self, **kwargs):
            return SimpleNamespace(status=status, output_parsed=parsed,
                usage=SimpleNamespace(input_tokens=7, output_tokens=9, total_tokens=16),
                id="test-response", model="actual-cloud-model")

    monkeypatch.setattr("openai.AsyncOpenAI", lambda **kwargs: SimpleNamespace(responses=Responses()))
    provider = OpenAIProvider({"model": "cloud-test", "api_key": "fake-key"})
    with pytest.raises(ProviderError) as caught:
        await provider.generate([], AnalystOutput, max_output_tokens=100, timeout_sec=1)
    assert caught.value.usage["total_tokens"] == 16 and not caught.value.uncertain
    assert caught.value.usage["effective_model"] == "actual-cloud-model"


def test_evaluation_is_explicitly_synthetic_and_requires_complete_observations():
    from evaluation.compare import compare, synthetic_records

    corpus = {"cases": [{"id": "unsafe", "vulnerable": True}, {"id": "safe", "vulnerable": False}]}
    observations = synthetic_records(corpus["cases"])
    result = compare(corpus, observations)
    assert result["synthetic_not_model_quality"] is True
    assert result["patches_applied_or_tested"] is False
    for mode in result["modes"].values():
        assert mode["true_positives"] == 1 and mode["false_positives"] == 1
    observations["records"].pop()
    with pytest.raises(ValueError, match="one observation"):
        compare(corpus, observations)
