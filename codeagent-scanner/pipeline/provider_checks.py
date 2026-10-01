"""Explicit, queued provider checks using synthetic content only."""
import asyncio
import hashlib
import json
import time
from typing import Literal
from pydantic import BaseModel, ConfigDict, ValidationError
from integration.models import ProviderError, ReviewCancelled, ReviewInterrupted
from integration.providers import get_provider
from pipeline.store import now


class CheckResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ok: Literal[True]


def connection_fingerprint(settings, provider, model):
    destination = settings.ollama_url if provider == 'ollama' else hashlib.sha256(settings.openai_key.encode()).hexdigest()
    return hashlib.sha256(json.dumps([provider, model, destination]).encode()).hexdigest()


async def check_provider(config, cancel):
    provider = get_provider(config)
    task = asyncio.create_task(provider.generate([
        {'role': 'system', 'content': 'This is a synthetic connection test. Return the schema object with ok true.'},
        {'role': 'user', 'content': 'Confirm the structured-output connection test.'}],
        CheckResult, max_output_tokens=256, timeout_sec=60))
    started = time.monotonic()
    try:
        while not task.done():
            if cancel():
                raise ReviewCancelled('Provider check canceled')
            if time.monotonic() - started >= 60:
                raise ReviewInterrupted('Provider check timed out; retry explicitly')
            await asyncio.sleep(0.1)
        response = await task
        try:
            CheckResult.model_validate(response.output)
        except ValidationError as exc:
            raise ProviderError('Provider connection test returned an invalid structured response',
                                code='invalid_output', usage=response.usage) from exc
        return response
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        close = getattr(provider, 'aclose', None)
        if close:
            await close()


def execute_check(orchestrator, job, cancel):
    settings, store = orchestrator.settings, orchestrator.store
    config = job['config']
    signature = connection_fingerprint(settings, config['provider'], config['model'])
    if signature != config.get('_connection_fingerprint'):
        raise ValueError('Provider configuration changed after submission; start a new connection test')
    owner, identifier = job.get('_lease_owner'), job['job_id']
    started = time.monotonic()
    output = {'configured': True, 'reachable': False, 'schema_test_passed': False,
        'provider': config['provider'], 'model': config['model'], 'checked_at': now(),
        'model_digest': config.get('_model_digest'), 'usage': {}, 'error': None}
    record = {'role': 'provider_check', 'status': 'running', 'started_at': now(), 'input_hash': signature}
    if not store.save_step(identifier, 'provider_check', record, owner):
        raise ReviewCancelled('Provider check lease lost')
    store.progress(identifier, 'provider_check', 25, owner=owner)
    error, result_status = None, 'completed'
    try:
        result = asyncio.run(check_provider({**config, 'api_key': settings.openai_key,
            'base_url': settings.ollama_url if config['provider'] == 'ollama' else None}, cancel))
        output.update(reachable=True, schema_test_passed=True, usage=result.usage)
    except (ProviderError, ReviewInterrupted) as exc:
        error = exc
        uncertain = isinstance(exc, ReviewInterrupted) or getattr(exc, 'uncertain', False)
        unreachable = getattr(exc, 'code', None) in ('model_unavailable', 'not_configured')
        output.update(reachable=not uncertain and not unreachable, error=settings.redact(str(exc)), usage=getattr(exc, 'usage', {}))
        result_status = 'interrupted' if uncertain else 'failed'
    output['elapsed_ms'] = round((time.monotonic() - started) * 1000)
    from pipeline.orchestrator import redact
    output = redact(output, settings)
    record.update(status=result_status, output=output, finished_at=now(), duration_ms=output['elapsed_ms'])
    if not store.save_step(identifier, 'provider_check', record, owner):
        raise ReviewCancelled('Provider check lease lost')
    with store.connect(write=True) as db:
        if owner and not store._owns(db, identifier, owner):
            raise ReviewCancelled('Provider check lease lost')
        if cancel():
            raise ReviewCancelled('Provider check canceled')
        db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',
            ('provider_test:' + config['provider'] + ':' + config['model'],
             json.dumps({**output, 'configuration_hash': signature, 'run_id': identifier})))
    store.progress(identifier, 'provider_check', 100, owner=owner)
    store.finish(identifier, result_status, output['error'], owner=owner)
