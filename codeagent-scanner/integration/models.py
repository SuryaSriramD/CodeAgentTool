"""Validated contracts for the proposal-only security review workflow."""

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator, create_model


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceReference(Contract):
    file: str
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)

    @model_validator(mode="after")
    def ordered_lines(self):
        if self.line_end < self.line_start:
            raise ValueError("Evidence line_end must follow line_start")
        return self


class ContextAction(Contract):
    kind: Literal["read", "search"]
    file: str | None = None
    line_start: int = Field(default=1, ge=1)
    line_end: int = Field(default=100, ge=1)
    query: str | None = None

    @model_validator(mode="after")
    def valid_action(self):
        if self.kind == "read" and (not self.file or self.line_end < self.line_start):
            raise ValueError("Read needs a file and ordered line range")
        if self.kind == "search" and (not self.query or len(self.query) > 120):
            raise ValueError("Search needs a literal query of 1–120 characters")
        return self


class AnalystOutput(Contract):
    disposition: Literal["confirmed", "false_positive", "needs_context"]
    explanation: str = Field(min_length=1, max_length=12000)
    evidence: list[EvidenceReference] = Field(default_factory=list, max_length=12)
    context_requests: list[ContextAction] = Field(default_factory=list, max_length=4)


class FindingTriage(AnalystOutput):
    finding_id: str


class GroupAnalystOutput(Contract):
    findings: list[FindingTriage] = Field(min_length=1, max_length=5)
    context_requests: list[ContextAction] = Field(default_factory=list, max_length=4)


def group_analyst_schema(finding_ids: list[str]):
    """Constrain local/hosted decoding to exactly this group's known IDs."""
    if not 1 <= len(finding_ids) <= 5 or len(finding_ids) != len(set(finding_ids)):
        raise ValueError("A group must contain one to five unique IDs")
    entry = create_model("GroupedFindingTriage", __base__=FindingTriage,
                         finding_id=(Literal[tuple(sorted(finding_ids))], ...))
    return create_model("BoundedGroupAnalystOutput", __base__=GroupAnalystOutput,
                        findings=(list[entry], Field(min_length=len(finding_ids), max_length=len(finding_ids))))


class SuggestedEdit(Contract):
    file: str
    original: str = Field(min_length=1, max_length=60000)
    replacement: str = Field(max_length=60000)


class AuthorOutput(Contract):
    edits: list[SuggestedEdit] = Field(default_factory=list, max_length=12)
    explanation: str = Field(min_length=1, max_length=12000)
    checks: list[str] = Field(default_factory=list, max_length=12)
    context_requests: list[ContextAction] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def edits_or_context(self):
        if not self.edits and not self.context_requests:
            raise ValueError("Author must propose an edit or request source context")
        return self


class ReviewerOutput(Contract):
    decision: Literal["approve", "request_revision", "reject", "needs_context"]
    comments: list[str] = Field(min_length=1, max_length=20)
    context_requests: list[ContextAction] = Field(default_factory=list, max_length=4)


@dataclass
class ProviderResult:
    output: dict[str, Any]
    usage: dict[str, Any] = field(default_factory=dict)


class ModelProvider(Protocol):
    async def generate(
        self, messages: list[dict[str, str]], schema: type[BaseModel], *,
        max_output_tokens: int, timeout_sec: float,
    ) -> ProviderResult: ...


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, code: str = "provider_error", uncertain: bool = False,
                 usage: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.uncertain = uncertain
        self.usage = usage or {}


class ReviewCancelled(RuntimeError):
    """The user cancelled the workflow; do not report it as a model failure."""


class ReviewInterrupted(RuntimeError):
    """A call might have completed externally; an explicit retry is required."""

    partial_result: dict[str, Any] | None = None


class ReviewBudgetExceeded(RuntimeError):
    """The bounded run has no further model-call, token, or time budget."""
