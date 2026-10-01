# Security rulepack 1.0.0

This repository owns the rules; scans do not fetch registry packs, need a license,
execute source files, invoke package managers, or build uploaded projects. Versions
are recorded in `tool-versions.json`; the separate tool environment and .NET NuGet
lockfiles pin the engines. Source support means the security checks below have
positive and safe-negative fixtures run through the actual engine. It does not
mean every vulnerability in a supported language is detectable.

| Source language | Baseline check in this rulepack | Engine |
|---|---|---|
| Python | `subprocess.run(..., shell=True)`; additional Bandit checks | Semgrep + Bandit |
| JavaScript, TypeScript | `eval` invocation | Semgrep |
| Java, Kotlin, Scala | MD5 MessageDigest selection | Semgrep |
| Go | shell interpreter invoked with `-c` | Semgrep |
| C, C++ | unbounded `strcpy` | Semgrep |
| Ruby, PHP | `eval` invocation | Semgrep |
| Swift | CommonCrypto MD5 invocation | Semgrep |
| Rust | shell interpreter command chained with `-c` | Semgrep |
| Bash | downloaded script piped into Bash | Semgrep |
| C#, Visual Basic .NET, F# | weak cryptography; BinaryFormatter deserialization; always-true certificate callback; explicit XML DTD parsing | .NET adapter |

Config checks cover YAML privileged containers, JSON disabled TLS validation,
XML insecure cookie transport, HTML risky iframe sandbox tokens, and Dockerfile
root users. These are syntactic security review findings, not proof of exploitation.
The current Semgrep pack has one rule per listed Semgrep language/config group;
Bandit supplies its upstream Python rule suite. JavaScript rules also apply to
TypeScript in Semgrep, so related findings can overlap.

`fixtures/security-v1` is the release gate for all 17 source languages and five
config types. .NET fixtures exercise all four rules in each language, aliases,
and identifiers shadowing framework types. `CODEAGENT_REQUIRE_REAL_TOOLS=1 pytest
-q tests/test_analyzers_v2.py` fails when any required engine or DB is absent.

The .NET adapter parses C#/VB with Roslyn and binds only trusted runtime metadata.
F# uses FSharp.Compiler.Service syntax trees and conservative local name/alias
resolution. It does not typecheck external project references or perform
interprocedural dataflow. The F# checks cover direct imported/qualified framework
calls, type aliases, locally bound constructor receivers, and explicit property
assignments; complex computed aliases may not match. Files with syntax errors
or exhausted analysis budgets are incomplete. No MSBuild tasks, restore,
source generators, repository assemblies, script `#load`, or user code run.
Physical source line numbers are retained.

The scanner inventories regular files without following symlinks. It excludes
`.git`, dependency/build output folders listed in `analyzers/common.py`, and
AppleDouble metadata. Tool parse errors, timeouts, missing executables, and
engine skips produce failed/partial coverage, never an empty successful fallback.
Semgrep's bundled native parser is explicitly run on every target before matching;
the CLI otherwise counts prefiltered but unparsed targets as scanned. A finished scan with zero findings is still
limited to this documented rule set and inventory.

Coverage is deliberately conservative about untranslated generic-AST nodes, even
when the language parser reports valid syntax. For example, pinned Semgrep
1.178.0 represents a JavaScript `export function` directive as an untranslated
node: findings can still appear, but that file is incomplete for automatic
resolution and proposal validation. This candidate does not equate successful
syntax parsing with full rule-engine coverage.

## Dependency coverage

Trivy is the only dependency advisory engine. It runs with `--offline-scan`, DB,
Java DB, check and version updates disabled, telemetry disabled, and trusted
configuration/ignore files outside the repository. Provision the vulnerability
DB separately into `TRIVY_CACHE_DIR` (or `CODEAGENT_TRIVY_CACHE_DIR`); the adapter
reports its update time. A missing DB makes the tool unavailable.

Inputs include exact pinned Python requirements and Pipfile/Poetry/uv locks;
npm/yarn/pnpm/Bun locks; Gradle/SBT locks; NuGet locks, packages.config and deps.json;
go.mod; Cargo.lock; Gemfile.lock; composer.lock; conan.lock; Package.resolved;
and Podfile.lock. The twenty formats have real vulnerable/patched fixture gates
in `fixtures/dependencies-v1`, attributed to pinned Trivy upstream testdata.
Binary bun.lockb and npm-shrinkwrap.json are recognized as unresolved inputs;
use the supported text bun.lock/package-lock.json formats. Language is not a package ecosystem: C#/F#/VB share NuGet;
Java/Kotlin/Scala share JVM ecosystems; Bash has no universal dependency manifest.

Manifest-only inputs without a supported resolved file are explicitly incomplete.
Requirements containing VCS/path/editable references or version ranges are
incomplete even when some exact versions were audited. Any input for which Trivy
returns no package inventory is incomplete, including empty/unsupported locks.
No dependencies are installed, resolved, downloaded, or built. Offline JVM
parent/property resolution and local Go replacements are not reconstructed;
a checked-in supported lock is required for resolved dependency evidence.

## Candidate profile: security-v2

`security-v1` remains the default. Select `security-v2` explicitly to retain the
baseline and add the following 38 language/family combinations. The candidate
is not promoted by fixture success; the independently reviewed evaluation gate
must pass before changing the production default.

| Languages | Additional checks | Analysis |
|---|---|---|
| Python | SQL injection, path traversal, SSRF from Flask and Django request values | Function-local taint |
| JavaScript, TypeScript | Shell injection, path traversal, SSRF from Express-style request properties | Function-local taint |
| Java, Kotlin, Scala | Constructed JDBC SQL; unsafe XML parser features | Structural API patterns |
| Go | SQL injection and SSRF from HTTP request values; disabled TLS verification | Function-local taint / structural configuration |
| C, C++ | Nonliteral printf/fprintf format strings; nonliteral system/popen commands | Structural API patterns |
| Ruby | Rails SQL injection; Marshal/unsafe YAML deserialization from params | Function-local taint |
| PHP | mysqli/PDO SQL injection; filesystem access from request values | Function-local taint |
| Swift | Alamofire disabled trust / unconditional trust credentials; legacy Foundation deserialization | Structural API patterns |
| Rust | sqlx/rusqlite formatted SQL; reqwest disabled certificate/hostname validation | Structural API patterns |
| Bash | eval; curl/wget disabled certificate validation | Structural API patterns |
| C#, VB, F# | Constructed DbCommand.CommandText; constructed shell-interpreter arguments | Roslyn semantic API binding / F# lexical AST tracking |

`fixtures/security-v2/manifest.json` lists 228 separate rule regression files:
three vulnerable variants and three safe/counterexample variants for each cell.
These are development fixtures and must never be presented as held-out quality
evaluation data. Run `CODEAGENT_REQUIRE_REAL_TOOLS=1 pytest -q
tests/test_scanners_vnext.py` with the pinned tools available.

Taint sinks focus the actual URL/path/command/SQL argument. Tainted HTTP headers
and bound SQL arguments must not contaminate a fixed destination or parameterized
query. JavaScript candidate rules exclude TypeScript extensions to avoid the
engine's cross-language duplicate matches. Neither profile claims general
cross-file dataflow, complete framework support, or detection of all injection
forms. Structural concatenation patterns identify review candidates even when
trust cannot be established locally. Swift trust credentials are review
candidates: external challenge validation may make a particular use safe.

F# local binding resolution uses enclosing lexical ranges and typed parameter
contexts; sibling functions do not overwrite each other's local receiver aliases.
It remains an AST analysis, not semantic compilation of a repository.

Reports include per-file completed/not-assessed outcomes, source inventory,
source profile and advisory profile digests, finding family/CWE/end location,
rule revision, and available source evidence. Digests include trusted rules,
analyzer source, and actual engine versions; changing advisory metadata leaves
the source digest unchanged. Dependency findings include ecosystem, manifest,
package identifier/PURL, advisory, installed version and known fixed versions.
Capabilities expose advisory update time and age without downloading a database.

## Proposal validation

The scanner-only `/validate` endpoint accepts a snapshot ID, validation ID, exact
source-hash anchored edits, target evidence, profile, and a deadline capped at
120 seconds. It reserves one validation workspace per service process, verifies
the immutable snapshot, copies at most 10,000 files / 500 MiB, and applies edits
only to its temporary copy. Conflicting edits, stale hashes, ambiguous originals,
invalid offsets, path traversal and symlinks are rejected. UTF-8 decoding is
required for edits; source bytes and original line endings are preserved.

Trusted source parsers and relevant source/dependency scanners run before and
after editing. Missing baseline targets, missing tools, parser failures, timeout,
or changed profiles yield incomplete results. Remaining target rules in the same
file and new findings prevent a pass. Matching target findings is conservative
when multiple occurrences share a rule and file; a proposal may need to cover
all occurrences before that file can pass. This avoids incorrectly claiming a
fix after line shifts. The original snapshot never changes. No package manager,
repository build, plugin or test runs. A passed result means only that these
static checks passed; proposals remain unapplied and runtime-untested.
