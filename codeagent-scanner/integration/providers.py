"""Provider adapters. Neither adapter retries or switches providers implicitly."""

import os
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from integration.models import ModelProvider, ProviderError, ProviderResult


class OpenAIProvider:
    def __init__(self, config: dict[str, Any]):
        from openai import AsyncOpenAI

        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OpenAI API key is not configured", code="not_configured")
        self.model = config["model"]
        self.client = AsyncOpenAI(api_key=api_key, max_retries=0)

    async def generate(self, messages, schema, *, max_output_tokens, timeout_sec):
        try:
            response = await self.client.responses.parse(
                model=self.model, input=messages, text_format=schema,
                max_output_tokens=max_output_tokens, timeout=timeout_sec,
                store=False,
            )
        except Exception as exc:
            # Do not persist provider response bodies, credentials, or source text.
            name = type(exc).__name__
            uncertain = name in {"APITimeoutError", "APIConnectionError"}
            raise ProviderError(
                f"OpenAI request failed ({name})",
                code="interrupted" if uncertain else "provider_error", uncertain=uncertain,
            ) from exc
        usage = response.usage
        reported_usage = {
            "input_tokens": usage.input_tokens if usage else None,
            "output_tokens": usage.output_tokens if usage else None,
            "total_tokens": usage.total_tokens if usage else None,
            "response_id": response.id,
            "effective_model": getattr(response, "model", self.model),
            "model": getattr(response, "model", self.model),
        }
        if response.status != "completed":
            raise ProviderError(f"OpenAI response is {response.status}", code="incomplete", usage=reported_usage)
        if response.output_parsed is None:
            raise ProviderError("OpenAI returned a refusal or no structured result", code="invalid_output", usage=reported_usage)
        try:
            parsed = schema.model_validate(response.output_parsed)
        except ValidationError as exc:
            raise ProviderError("OpenAI response did not match the required schema", code="invalid_output", usage=reported_usage) from exc
        return ProviderResult(parsed.model_dump(), reported_usage)

    async def aclose(self):
        await self.client.close()


class OllamaProvider:
    def __init__(self, config: dict[str, Any]):
        self.model = config["model"]
        self.expected_digest = config.get("_model_digest")
        self.base_url = (config.get("base_url") or config.get("ollama_base_url")
                         or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.client = httpx.AsyncClient(follow_redirects=False, trust_env=False)

    async def generate(self, messages, schema: type[BaseModel], *, max_output_tokens, timeout_sec):
        if self.expected_digest:
            no_model_usage = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                              "effective_model": self.model, "model_digest": self.expected_digest}
            try:
                metadata = await self.client.get(self.base_url + "/api/tags", timeout=min(10, timeout_sec))
                metadata.raise_for_status()
                actual = next((item.get("digest") for item in metadata.json().get("models", [])
                               if item.get("name") == self.model), None)
            except (httpx.HTTPError, ValueError, TypeError, AttributeError) as exc:
                raise ProviderError("Unable to verify the pinned local model before dispatch", code="model_unavailable",
                                    usage=no_model_usage) from exc
            if actual != self.expected_digest:
                raise ProviderError("Installed model changed since submission; start a new review", code="model_changed",
                                    usage=no_model_usage)
        try:
            response = await self.client.post(
                self.base_url + "/api/chat", timeout=timeout_sec,
                json={"model": self.model, "messages": messages, "stream": False,
                      "format": schema.model_json_schema(),
                      "options": {"num_predict": max_output_tokens, "temperature": 0.1}},
            )
            response.raise_for_status()
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise ProviderError("Ollama connection was interrupted", code="interrupted", uncertain=True) from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Ollama returned HTTP {exc.response.status_code}", code="provider_error") from exc
        reported_usage = {}
        try:
            body = response.json()
            input_tokens, output_tokens = body.get("prompt_eval_count"), body.get("eval_count")
            total = (input_tokens + output_tokens
                     if isinstance(input_tokens, int) and isinstance(output_tokens, int) else None)
            reported_usage = {
                "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total,
                "effective_model": body.get("model", self.model), "model": body.get("model", self.model),
                "model_digest": self.expected_digest,
            }
            if not body.get("done") or body.get("done_reason") == "length":
                raise ProviderError("Ollama response was incomplete", code="incomplete", usage=reported_usage)
            if body.get("message", {}).get("tool_calls"):
                raise ProviderError("Unexpected tool calls in Ollama response", code="invalid_output", usage=reported_usage)
            parsed = schema.model_validate_json(body["message"]["content"])
        except (ValueError, KeyError, TypeError, AttributeError, ValidationError) as exc:
            raise ProviderError("Ollama response did not match the required schema", code="invalid_output", usage=reported_usage) from exc
        return ProviderResult(parsed.model_dump(), reported_usage)

    async def aclose(self):
        await self.client.aclose()


def get_provider(config: dict[str, Any]) -> ModelProvider:
    if config.get("_provider") is not None:
        return config["_provider"]
    if not config.get("model"):
        raise ProviderError("Choose a model before starting an AI review", code="not_configured")
    kind = config.get("provider", "openai")
    if kind == "openai":
        return OpenAIProvider(config)
    if kind == "ollama":
        return OllamaProvider(config)
    raise ProviderError(f"Unsupported provider: {kind}", code="not_configured")


def get_provider_capabilities(config: dict[str, Any]) -> dict[str, Any]:
    kind = config.get("provider", "openai")
    return {"provider": kind, "model": config.get("model"),
            "structured_output": kind in {"openai", "ollama"},
            "cloud": kind == "openai", "automatic_fallback": False,
            "proposal_only": True}
