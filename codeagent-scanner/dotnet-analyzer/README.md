# CodeAgent .NET security adapter

Build this trusted analyzer once; uploaded .NET projects are never built.

```sh
dotnet restore CodeAgent.DotNet.fsproj --locked-mode
dotnet publish CodeAgent.DotNet.fsproj -c Release --no-restore -o publish
```

Use the pinned SDK from `../rules/tool-versions.json`. Runtime configuration:

```sh
export CODEAGENT_DOTNET_ANALYZER=/opt/codeagent-dotnet-analyzer/CodeAgent.DotNet.dll
# Optional if dotnet is not on PATH:
export CODEAGENT_DOTNET_BIN=/usr/share/dotnet/dotnet
```

The CLI accepts one JSON manifest (`workspace`, `files` with relative `path` and
`language` csharp/vb/fsharp). It emits a JSON array of file reports; diagnostics
are separate from findings. `--version` reports the trusted analyzer version (independent of the selected rule profile). Keep this
process in the scanner isolation boundary with repository input read-only and
no credentials/network access. Rooted/outside-workspace paths are rejected.

Roslyn and FSharp.Compiler.Service are MIT licensed upstream dependencies. See
`../rules/README.md` for exact rule scope and `packages.lock.json` plus
`Roslyn/packages.lock.json` for dependency integrity pins.

The manifest optionally selects `profile` (`security-v1` by default,
`security-v2` for the candidate). Candidate checks add constructed
`DbCommand.CommandText` and dynamic shell-interpreter arguments. Roslyn binds
only trusted runtime APIs. F# uses lexical local scopes and typed parameter
contexts, with a bounded alias resolution chain. Baseline rules remain active
under either profile. Findings include family, CWE and end-line metadata.
