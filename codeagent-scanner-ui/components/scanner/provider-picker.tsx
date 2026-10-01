"use client";
import { modelNames } from "@/lib/api-client";
import type { Capabilities, Provider } from "@/lib/types";

export function ProviderPicker({ capabilities, provider, model, onProvider, onModel, id = "analysis" }: {
  capabilities?: Capabilities; provider: Provider; model: string;
  onProvider: (provider: Provider) => void; onModel: (model: string) => void; id?: string;
}) {
  const models = modelNames(capabilities, provider);
  const ready = capabilities?.providers?.[provider]?.available;
  return <div className="provider-picker"><div className="field-grid"><div><label htmlFor={`${id}-provider`}>AI provider</label><select id={`${id}-provider`} value={provider} onChange={(event) => { const value = event.target.value as Provider; onProvider(value); onModel(modelNames(capabilities, value)[0] ?? ""); }}><option value="ollama">Local · Ollama</option><option value="openai">Cloud · OpenAI</option></select></div><div><label htmlFor={`${id}-model`}>Model</label>{provider === "openai" ? <input id={`${id}-model`} value={model} onChange={(event) => onModel(event.target.value)} placeholder="Exact OpenAI model ID" required spellCheck={false} autoComplete="off" /> : <select id={`${id}-model`} value={model} onChange={(event) => onModel(event.target.value)} required><option value="">Choose a model</option>{model && !models.includes(model) && <option value={model}>Unavailable: {model}</option>}{models.map((name) => <option key={name} value={name}>{name}</option>)}</select>}</div></div>
    <p className="field-help">{provider === "ollama" ? "Analysis stays with the configured Ollama server. No fallback to a cloud provider." : "Selected source snippets are sent to OpenAI. API usage may incur charges."}</p>
    {provider === "ollama" && model && !models.includes(model) && <p className="notice warning">The saved model is not installed. Select an installed completion model or install this model on the Ollama server.</p>}
    {!ready && <p className="notice warning">{provider === "ollama" ? "Ollama is not ready. Start the server and install a supported model before requesting review." : "OpenAI is not configured. Ask the administrator to configure the server API key."}</p>}
  </div>;
}
