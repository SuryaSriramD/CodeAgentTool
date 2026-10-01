# cpp — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-cpp-safe-01 — A fixed-size telemetry sample keeps indexes inside the owning vector

Proposed label: **safe**. Human review: **pending**.

Source hash: `0adfe684407639acbab687c940caf7c886c24feac76fb3cfdb73756cadc4e7c0`. Protocol-2.0 case hash: `6a259e8413455b556a8b20b870249edcade7c55166696526d214457f721d0d7c`.

The begin check precedes subtraction, and count is checked against remaining elements before index addition. The returned vector owns its copy and does not outlive a borrowed view.

### src/TelemetrySlice.cpp

```cpp
#include <vector>
#include <span>
#include <stdexcept>
#include <cstddef>
std::vector<double> sample_window(std::span<const double> samples,
                                  std::size_t begin, std::size_t count) {
    if (samples.size() > 4096) throw std::invalid_argument("samples");
    if (begin > samples.size() || count > samples.size() - begin) throw std::out_of_range("window");
    std::vector<double> selected;
    selected.reserve(count);
    for (std::size_t offset = 0; offset < count; ++offset) {
        selected.push_back(samples[begin + offset]);
    }
    return selected;
}
```

### Derivation

```json
{
  "group": "cpp-telemetry-owning-window",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The safe operation copies a requested numeric range with arithmetic and lifetime invariants; it is unrelated to binary-to-hex rendering. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Bounds arithmetic and object lifetime in a bounded C++ span operation.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return an owning copy of a requested contiguous telemetry window.",
  "trust_boundary": "A dashboard user controls begin and count; the service owns a stable bounded sample array.",
  "legitimate_examples": [
    {
      "input": "Samples [1.5,2.5,3.5], begin=1, count=2",
      "expected": "Return an owning [2.5,3.5] vector."
    },
    {
      "input": "begin at the sample count, count=0",
      "expected": "Return an empty vector; a larger count is rejected."
    }
  ],
  "permitted_changes": [
    "Keep checked subtraction before index addition and owning result storage.",
    "Preserve exact numeric values, order and the valid empty tail window."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Checking begin+count without guarding overflow can accept an invalid range.",
  "Returning a span instead of an owning vector changes the result lifetime contract."
]
```

### Remediation constraints

```json
[
  "Keep checked subtraction before index addition and owning result storage.",
  "Preserve exact numeric values, order and the valid empty tail window."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-01",
  "prior_case_id": "cpp-diagnostic-format-safe",
  "prior_source_sha256": "e9a327b83eabeb891e2a89346e4a27ebe57961505686bdb34db0504f32c12699",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. The source span remains stable during the call and contains initialized doubles; NaN values are data and copied without normalization."
}
```

### Split

```json
"held_out"
```

## v2-cpp-safe-02 — An approved report ID is resolved to a private immutable file

Proposed label: **safe**. Human review: **pending**.

Source hash: `b8627aad1dfb39400954f4830d182ad2449ef5bccddc4a1987073e159e704bd1`. Protocol-2.0 case hash: `20e241a7ae3ff6c51721ea00f569bae081b46486a53c9b0721655a1bd0956b14`.

The user value is only a key in a closed map, never a joined path. Both targets are immutable private regular files under service control.

### src/report_lookup.cpp

```cpp
#include <fstream>
#include <iterator>
#include <string>
#include <unordered_map>
#include <stdexcept>
std::string read_report(const std::string& public_id) {
    static const std::unordered_map<std::string, std::string> paths = {
        {"weekly", "/srv/reports/weekly.txt"}, {"billing", "/srv/reports/billing.txt"}
    };
    auto found = paths.find(public_id);
    if (found == paths.end()) throw std::invalid_argument("report");
    std::ifstream input(found->second, std::ios::binary);
    if (!input) throw std::runtime_error("open");
    return std::string(std::istreambuf_iterator<char>(input), {});
}
```

### Derivation

```json
{
  "group": "cpp-report-alias-file-selection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This is an intentionally alias-based read API with fixed small report inventory, distinct from retrofitting aliases onto a filename API. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Path-selection control and exact bounded-source reading; the caller authorizes report access.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the exact bytes of either public report identified by a documented stable alias.",
  "trust_boundary": "A user chooses weekly or billing after caller authorization; arbitrary filenames are not part of this API.",
  "legitimate_examples": [
    {
      "input": "ID weekly",
      "expected": "Return all bytes of weekly.txt, including embedded newline characters."
    },
    {
      "input": "ID ../secret",
      "expected": "Reject as an unknown report."
    }
  ],
  "permitted_changes": [
    "Keep the closed alias-to-path mapping and binary output.",
    "Retain caller authorization for the selected report."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Adding a fallback that joins unknown IDs to a directory breaks containment.",
  "Replacing the existing alias API with filename acceptance expands the trust boundary."
]
```

### Remediation constraints

```json
[
  "Keep the closed alias-to-path mapping and binary output.",
  "Retain caller authorization for the selected report."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-02",
  "prior_case_id": "cpp-cleanup-shell-safe",
  "prior_source_sha256": "245b489f03fd7941807190790522b42ceadd7c5d5f42052f5df2d7570ab70441",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. The private directory and both files are not attacker writable, contain no symlinks, and each is at most 1 MiB."
}
```

### Split

```json
"held_out"
```

## v2-cpp-safe-03 — Structured SQL evidence is displayed with iostream insertion

Proposed label: **safe**. Human review: **pending**.

Source hash: `4b8fec0f754d36e6b98eccae658a1641ac0a5404dfd70ed9ed0417aa4896dd37`. Protocol-2.0 case hash: `4e299b6b7f065d4b2ae27108aa4172125e0a81f0bf2cdf47f95ca7249543af7e`.

Operation text is streamed as data; no SQL execution or printf format sink exists. The term SQL and untrusted plan text are diagnostic evidence, not executable query assembly.

### src/query_plan_view.cpp

```cpp
#include <ostream>
#include <string>
#include <vector>
#include <stdexcept>
struct PlanRow { std::string operation; unsigned cost; };
void show_plan(std::ostream& out, const std::vector<PlanRow>& rows) {
    if (rows.size() > 100) throw std::invalid_argument("rows");
    for (const auto& row : rows) {
        if (row.operation.size() > 120) throw std::invalid_argument("operation");
        out << "SQL plan: " << row.operation << " cost=" << row.cost << '\n';
        if (!out) throw std::runtime_error("write");
    }
}
```

### Derivation

```json
{
  "group": "cpp-query-plan-nonexecuting-view",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This case distinguishes SQL-like vocabulary from executable query construction through an output-only type and interface. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL and format-string false-positive control for diagnostic-only flow.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List a bounded query execution plan for an authorized operator.",
  "trust_boundary": "A database response supplies plan operation names; the renderer cannot submit queries.",
  "legitimate_examples": [
    {
      "input": "Operation Index Scan, cost 12",
      "expected": "Write SQL plan: Index Scan cost=12 and newline."
    },
    {
      "input": "Operation containing %s",
      "expected": "Display %s literally."
    }
  ],
  "permitted_changes": [
    "Preserve row order, costs and stream error handling.",
    "Keep the plan renderer separate from query execution."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Flagging every SQL-bearing concatenation would be a false positive.",
  "Do not accidentally use an operation value as a printf format during refactoring."
]
```

### Remediation constraints

```json
[
  "Preserve row order, costs and stream error handling.",
  "Keep the plan renderer separate from query execution."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-03",
  "prior_case_id": "cpp-name-copy-safe",
  "prior_source_sha256": "3af35cc51c651465ef62a139eb70fb4f1cdf47f86bf692e267e9c6f5a591e7f9",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Operation names have CR/LF stripped by the protocol adapter; the supplied ostream is valid and operator-only."
}
```

### Split

```json
"held_out"
```

## v2-cpp-safe-04 — A ZIP central-directory name is rendered as escaped HTML text

Proposed label: **safe**. Human review: **pending**.

Source hash: `25321d819b2057f5b80ec33ce045660d85127575a8b20de84f82add0eb3e09b6`. Protocol-2.0 case hash: `1870734d862b8a850e2ec6f6a3cea9bd8372baeb53d3427fbaa8d43aa263273a`.

The name appears only in an HTML text node and escapes the three text-node metacharacters. This function never extracts the archive or opens a path.

### src/archive_listing.cpp

```cpp
#include <string>
#include <stdexcept>
std::string archive_name_html(const std::string& name) {
    if (name.size() > 512) throw std::invalid_argument("name");
    std::string output = "<li>";
    for (char ch : name) {
        switch (ch) {
            case '&': output += "&amp;"; break;
            case '<': output += "&lt;"; break;
            case '>': output += "&gt;"; break;
            default: output += ch;
        }
    }
    output += "</li>";
    return output;
}
```

### Derivation

```json
{
  "group": "cpp-archive-name-display-only",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "An archive-looking path remains display data; there is intentionally no extraction or path-joining sink. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Buffer, path and text-rendering boundaries in the declared text-node context.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a bounded archive entry name in a list item without interpreting it as markup or a filesystem path.",
  "trust_boundary": "An uploaded archive controls UTF-8 entry names; the caller inserts this result only as element content.",
  "legitimate_examples": [
    {
      "input": "Name <draft>&notes",
      "expected": "Return <li>&lt;draft&gt;&amp;notes</li>."
    },
    {
      "input": "Name ../src/main.cpp",
      "expected": "Display that literal path without opening or extracting it."
    }
  ],
  "permitted_changes": [
    "Keep text-node escaping and the fixed element wrapper.",
    "Do not reuse this escaping routine for attributes, script or style contexts."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "A ../ string is not path traversal without a filesystem operation.",
  "The output encoding contract is text-node-only, not universal HTML sanitization."
]
```

### Remediation constraints

```json
[
  "Keep text-node escaping and the fixed element wrapper.",
  "Do not reuse this escaping routine for attributes, script or style contexts."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-04",
  "prior_case_id": "cpp-buffer-format-safe",
  "prior_source_sha256": "8e072ec04044df507a5c5f9d93ca3f5265967a997c26bacc22d284508224dc4b",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Names are valid UTF-8 without NUL; output is inserted as HTML body content and never used as an attribute or script string."
}
```

### Split

```json
"held_out"
```

## v2-cpp-safe-05 — A monotonic sequence parser rejects overflow before multiplication

Proposed label: **safe**. Human review: **pending**.

Source hash: `10ef80a5fec20c7b941c49d43674ed438efc5f4a1be8b1da0d5820357f4472f6`. Protocol-2.0 case hash: `2394388e0636958b75769782008511d91339b6dd1fe365b4a838fec65423048d`.

The digit range and pre-multiplication bound prevent wraparound; no memory access depends on a parsed unchecked length.

### src/sequence_number.cpp

```cpp
#include <string_view>
#include <cstdint>
#include <limits>
#include <optional>
std::optional<std::uint32_t> sequence_number(std::string_view input) {
    if (input.empty() || input.size() > 10) return std::nullopt;
    std::uint32_t result = 0;
    for (char digit : input) {
        if (digit < '0' || digit > '9') return std::nullopt;
        unsigned value = static_cast<unsigned>(digit - '0');
        if (result > (std::numeric_limits<std::uint32_t>::max() - value) / 10) return std::nullopt;
        result = result * 10 + value;
    }
    return result;
}
```

### Derivation

```json
{
  "group": "cpp-sequence-decimal-overflow-control",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A protocol identity parser establishes a numeric invariant without string or shell sinks, providing a distinct safe input-handling operation. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Integer parsing and source bounds; downstream authorization does not depend on this function.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Parse a decimal protocol sequence into an unsigned 32-bit value or reject it.",
  "trust_boundary": "A peer controls the complete decimal field, including length and characters.",
  "legitimate_examples": [
    {
      "input": "4294967295",
      "expected": "Return the maximum uint32 value."
    },
    {
      "input": "4294967296",
      "expected": "Return nullopt without wrapping to zero."
    }
  ],
  "permitted_changes": [
    "Preserve decimal-only grammar and exact 32-bit range.",
    "Keep checked arithmetic before each multiplication."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Checking overflow only after arithmetic loses the original value.",
  "Replacing rejection with clamping changes sequence identity."
]
```

### Remediation constraints

```json
[
  "Preserve decimal-only grammar and exact 32-bit range.",
  "Keep checked arithmetic before each multiplication."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-05",
  "prior_case_id": "cpp-query-pipeline-safe",
  "prior_source_sha256": "08388d58dae5fa51ab774dfc2d91078056610c7c95c0dcac02d8688bc6796a15",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. The string_view references stable readable memory; leading zeros are legitimate decimal input."
}
```

### Split

```json
"held_out"
```

## v2-cpp-safe-06 — A user search token is matched literally against a fixed in-memory index

Proposed label: **safe**. Human review: **pending**.

Source hash: `395e8534f77d4def81a2658e33c7c8812d82024e19d6da916d55bf268ad166d9`. Protocol-2.0 case hash: `eea3337e23c00e17092dfb55daefa9122718088237ca33873bee9f92ace5e239`.

The token is used by literal substring search over bounded std::string values. Shell-looking and SQL-looking characters acquire no executable meaning.

### src/catalog_search.cpp

```cpp
#include <string>
#include <vector>
#include <stdexcept>
std::vector<std::string> catalog_search(const std::vector<std::string>& titles,
                                      const std::string& token) {
    if (token.empty() || token.size() > 80 || titles.size() > 1000) throw std::invalid_argument("search");
    std::vector<std::string> matches;
    for (const auto& title : titles) {
        if (title.size() > 200) throw std::invalid_argument("title");
        if (title.find(token) != std::string::npos) matches.push_back(title);
    }
    return matches;
}
```

### Derivation

```json
{
  "group": "cpp-literal-catalog-search",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The input deliberately resembles injection payloads but only a literal in-memory search consumes it; it has no repaired vulnerable sibling. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Injection false-positive control and bounded standard-library string operations.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return original catalog titles containing an exact, case-sensitive substring in original order.",
  "trust_boundary": "A user supplies the search token; the service provides an already authorized bounded list of titles.",
  "legitimate_examples": [
    {
      "input": "Token ' OR 1=1 --",
      "expected": "Match only titles containing those literal bytes."
    },
    {
      "input": "Token [a-z]",
      "expected": "Search the literal bracketed text; do not treat it as a regular expression."
    }
  ],
  "permitted_changes": [
    "Preserve exact substring semantics, duplicates and input order.",
    "Keep bounded input counts and lengths."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Changing find to a regular-expression API introduces a different input language.",
  "No database or process sink exists even when input resembles injected code."
]
```

### Remediation constraints

```json
[
  "Preserve exact substring semantics, duplicates and input order.",
  "Keep bounded input counts and lengths."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-safe-06",
  "prior_case_id": "cpp-joined-buffer-safe",
  "prior_source_sha256": "eead61f11b301044a73210fce9e4ce6d5b6b6b2cd738f6cbffc8a5b1f3b292c0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Titles and token are NUL-free UTF-8 byte strings; matching is intentionally bytewise and case-sensitive."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-01 — Localized build status treats a translator string as a variadic format

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `58fa8f257eafd575230dec9d2234608137f9c7a248e5ce66733fb2af65e0e893`. Protocol-2.0 case hash: `b17750cbaac8c985a1dd0110a21c12059ea9ea577af88ed4e82e1ac1d08ec60d`.

The locale key is found safely, but a tenant translator controls the selected format value. Conversions other than the intended integer substitution consume incompatible variadic arguments.

### src/build_status.cpp

```cpp
#include <cstdio>
#include <string>
#include <unordered_map>
int build_status(FILE *out, const std::unordered_map<std::string, std::string>& catalog,
                 const std::string& locale, unsigned completed) {
    auto entry = catalog.find(locale);
    if (entry == catalog.end() || entry->second.size() > 160) return -1;
    if (std::fputs("Build status: ", out) == EOF) return -1;
    if (std::fprintf(out, entry->second.c_str(), completed) < 0) return -1;
    if (std::fputc('\n', out) == EOF) return -1;
    return std::fflush(out) == EOF ? -1 : 0;
}
```

### Derivation

```json
{
  "group": "cpp-translation-placeholder-language",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A translator capability intentionally permits a small placeholder language, requiring a semantic repair rather than simply rendering every character verbatim. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "format-string",
    "cwe": "CWE-134",
    "path": "src/build_status.cpp",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Untrusted format interpretation; map lookup and translation authorization are defined by the caller.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a tenant translation with exactly one {count} placeholder into an operator build status line.",
  "trust_boundary": "Translators may edit bounded catalog values but are not trusted to supply printf programs; completed is a trusted integer.",
  "legitimate_examples": [
    {
      "input": "Catalog value Finished {count} files; completed=7",
      "expected": "Output Build status: Finished 7 files and newline."
    },
    {
      "input": "Catalog value 100% complete: {count}",
      "expected": "Render the percent sign literally and substitute the count."
    }
  ],
  "permitted_changes": [
    "Implement the documented literal {count} substitution or an equivalently constrained template parser.",
    "Reject zero or multiple placeholders explicitly; preserve other literal text."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Escaping the entire template and dropping the count breaks localization.",
  "Limiting length does not restrict format conversions."
]
```

### Remediation constraints

```json
[
  "Implement the documented literal {count} substitution or an equivalently constrained template parser.",
  "Reject zero or multiple placeholders explicitly; preserve other literal text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-01",
  "prior_case_id": "cpp-diagnostic-format-vulnerable",
  "prior_source_sha256": "f9ca171b7b32a519e3f4b8f79aa04d50a5f120049e6fe81af36528d0a7c18f44",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Catalog ingestion enforces exactly one literal {count} placeholder and rejects newlines; this renderer currently uses the wrong formatting API."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-02 — Export worker quotes a title but leaves shell command substitution active

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `bc125abcf29358aa1a364aa983f3a51bdf96c03984661f6ceebe446caf60fb23`. Protocol-2.0 case hash: `83625370374d948504be3be9ba31086b25a37be9a7fd1eaba081c84c2b74b0e1`.

Rejecting double quotes does not neutralize command substitution inside a double-quoted shell word. A user title reaches popen and executes with the export worker permissions.

### src/pdf_export.cpp

```cpp
#include <cstdio>
#include <string>
#include <stdexcept>
std::string render_pdf_summary(const std::string& title) {
    if (title.size() > 180 || title.find('"') != std::string::npos) throw std::invalid_argument("title");
    std::string command = "/usr/local/bin/render-pdf --title \"" + title + "\" --summary";
    FILE *child = popen(command.c_str(), "r");
    if (!child) throw std::runtime_error("spawn");
    char buffer[512];
    std::string output;
    while (std::fgets(buffer, sizeof buffer, child)) output += buffer;
    int status = pclose(child);
    if (status != 0) throw std::runtime_error("render failed");
    return output;
}
```

### Derivation

```json
{
  "group": "cpp-report-title-partial-shell-escaping",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "An attempted quote filter creates a different injection boundary from raw filename concatenation and requires preserving captured subprocess output. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/pdf_export.cpp",
    "line_start": 7,
    "line_end": 7
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell injection despite attempted quoting; renderer input semantics are explicitly literal.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a PDF with a literal user title and return the renderer summary after reaping the child.",
  "trust_boundary": "An authenticated editor controls a report title; the renderer executable and document input are service-owned.",
  "legitimate_examples": [
    {
      "input": "Title Quarterly revenue",
      "expected": "Pass that complete title as one argument and return the summary."
    },
    {
      "input": "Title Costs $5 and taxes",
      "expected": "Keep the dollar sign and spaces literally."
    }
  ],
  "permitted_changes": [
    "Launch the renderer directly with discrete arguments and capture stdout.",
    "Preserve the full title, child exit failures and process cleanup."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Rejecting only quote characters misses shell expansion.",
  "Replacing popen with exec discards the output-returning parent contract."
]
```

### Remediation constraints

```json
[
  "Launch the renderer directly with discrete arguments and capture stdout.",
  "Preserve the full title, child exit failures and process cleanup."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-02",
  "prior_case_id": "cpp-cleanup-shell-vulnerable",
  "prior_source_sha256": "ac77d062b31b2118ace9d3aa804625a4792969c89cc6e7fcfaeb4528ea6e0d9c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. The trusted renderer emits at most 16 KiB and has a caller-enforced deadline; it does not itself interpret title text as code. Input titles contain no newline or NUL."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-03 — A legacy binary response has a size-aware interface but ignores capacity

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `b62697a6d4a3a53bbc882884a628f6ddeb941bb0b4cd7faaa1bcef5a3bd7179a`. Protocol-2.0 case hash: `e9e52b72564858856e8896e81b3a93589625aceb1d25c394fda995b0404153f5`.

The output object carries a capacity but only checks space for the prefix. The string copy can exceed a small reply allocation even for valid bounded labels.

### src/session_reply.cpp

```cpp
#include <cstring>
#include <string>
#include <cstddef>
struct Reply { char *data; std::size_t capacity; std::size_t used; };
bool session_reply(Reply& out, const std::string& session_label) {
    if (session_label.size() > 256 || out.capacity < 4) return false;
    const char prefix[] = "OK ";
    std::memcpy(out.data, prefix, 3);
    std::strcpy(out.data + 3, session_label.c_str());
    out.used = 3 + session_label.size();
    return true;
}
```

### Derivation

```json
{
  "group": "cpp-reply-capacity-publication",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The consumer-facing protocol object includes capacity and used metadata, making repair correctness depend on atomic publication rather than a bare copy wrapper. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "buffer-overflow",
    "cwe": "CWE-120",
    "path": "src/session_reply.cpp",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Destination-capacity misuse; source std::string ownership is valid.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Populate a caller-owned wire reply and publish used only after a complete successful write.",
  "trust_boundary": "A remote session supplies the label; a connection pool provides reply buffers of varying capacities.",
  "legitimate_examples": [
    {
      "input": "Label east, capacity 8",
      "expected": "Write OK east plus NUL; set used=7 and return true."
    },
    {
      "input": "Label east, capacity 7",
      "expected": "Return false without changing data or used."
    }
  ],
  "permitted_changes": [
    "Check total required bytes including the terminator before any mutation.",
    "Preserve the struct ABI, caller buffer ownership and atomic-failure behavior."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Updating used after a truncated copy falsely advertises bytes not written.",
  "Changing the function to return a new std::string leaves existing connection buffers unchanged."
]
```

### Remediation constraints

```json
[
  "Check total required bytes including the terminator before any mutation.",
  "Preserve the struct ABI, caller buffer ownership and atomic-failure behavior."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-03",
  "prior_case_id": "cpp-name-copy-vulnerable",
  "prior_source_sha256": "fdcd2853b5eb0c8911f314dbac07653f6d6e0752e40fbfea7b6063b56732ae38",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Reply.data points to a writable capacity-byte allocation; session_label contains no NUL; used starts at zero and must remain unchanged on failure."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-04 — Two valid route fragments overflow a shared diagnostic scratch buffer

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `132ce11e8efa2bba155e7a61d41199b9ebe9d90c3a0aafca8a590100cdfc5a70`. Protocol-2.0 case hash: `ee245b378c4d345235b1570d16581f0f2d841af611ca26303338b06218f56248`.

The first copy fits, but the accepted pair can require 85 bytes including separator and terminator in a 64-byte scratch buffer.

### src/route_trace.cpp

```cpp
#include <cstdio>
#include <cstring>
#include <string>
int route_trace(FILE *out, const std::string& from, const std::string& to) {
    if (from.size() > 40 || to.size() > 40) return -1;
    char trace[64];
    std::strcpy(trace, from.c_str());
    std::strcat(trace, " -> ");
    std::strcat(trace, to.c_str());
    if (std::fprintf(out, "%s\n", trace) < 0) return -1;
    return std::fflush(out) == EOF ? -1 : 0;
}
```

### Derivation

```json
{
  "group": "cpp-two-endpoint-route-aggregation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Two independent protocol fields share one fixed scratch allocation; neither is an individually oversized source, unlike the variable-capacity reply scenario. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "buffer-overflow",
    "cwe": "CWE-120",
    "path": "src/route_trace.cpp",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "C-style string aggregate overflow within a C++ ownership boundary.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write a complete source-to-destination route trace in a fixed textual layout.",
  "trust_boundary": "Peers supply two separately bounded route identifiers; neither identifier alone violates its input contract.",
  "legitimate_examples": [
    {
      "input": "from=west, to=east",
      "expected": "Write west -> east followed by newline."
    },
    {
      "input": "Two 40-character identifiers",
      "expected": "Write all characters with the separator; never silently shorten a route."
    }
  ],
  "permitted_changes": [
    "Use size-aware composition or streaming while retaining the entire route.",
    "Keep the stream ownership and 0/-1 error result."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Reducing both limits to fit changes the declared accepted route space.",
  "Checking only the source of the final strcat misses the existing prefix length."
]
```

### Remediation constraints

```json
[
  "Use size-aware composition or streaming while retaining the entire route.",
  "Keep the stream ownership and 0/-1 error result."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-04",
  "prior_case_id": "cpp-buffer-format-vulnerable",
  "prior_source_sha256": "64e0b1cf2813217becb23bdb63ed878d2209f8c483ee32a290b4a16b69648f26",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Route identifiers contain only alphanumeric, dash and underscore characters and are NUL-free."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-05 — Maintenance queue interprets a requested retention suffix through a shell

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `591bc6eca67db043c630ee62067c5ddc4cdd223332537dfb46448908aed1fe2e`. Protocol-2.0 case hash: `ceaff1c2347af9525074a0f05f3f02b134520290c042cb917eb566c476165182`.

A tenant selects a filename suffix which is embedded inside single quotes. An apostrophe can end the quoting and introduce shell operators in a scheduled deletion job.

### src/retention_job.cpp

```cpp
#include <cstdlib>
#include <string>
#include <stdexcept>
struct RetentionJob { std::string suffix; unsigned tenant; };
int run_retention(const RetentionJob& job) {
    if (job.tenant == 0 || job.suffix.empty() || job.suffix.size() > 64) throw std::invalid_argument("job");
    std::string root = "/srv/retention/" + std::to_string(job.tenant);
    std::string command = "/usr/bin/find " + root + " -maxdepth 1 -type f -name '*" + job.suffix + "' -delete";
    int status = std::system(command.c_str());
    if (status == -1) throw std::runtime_error("start failed");
    return status;
}
```

### Derivation

```json
{
  "group": "cpp-retention-literal-suffix",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The repair must distinguish shell quoting from downstream glob semantics while preserving a scoped destructive operation. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/retention_job.cpp",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell injection plus literal-versus-glob contract; filesystem races are excluded by the stable private workspace.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Delete only direct regular files in the authorized tenant root whose names end in a literal suffix.",
  "trust_boundary": "The queue validates tenant identity independently but allows arbitrary non-NUL suffix text, including apostrophes.",
  "legitimate_examples": [
    {
      "input": "Tenant 17, suffix .tmp",
      "expected": "Delete direct regular files ending in .tmp in tenant 17 only."
    },
    {
      "input": "Suffix owner's draft",
      "expected": "Treat the apostrophe and space literally as suffix characters."
    }
  ],
  "permitted_changes": [
    "Use direct filesystem enumeration with literal suffix comparison or a non-shell argv API with explicit glob escaping.",
    "Preserve root containment, regular-file filtering and completion status."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://eel.is/c++draft/string.classes",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html"
  ]
}
```

### Regression traps

```json
[
  "Passing a suffix unchanged to find -name still interprets glob metacharacters.",
  "Do not delete directories or follow links while removing shell use."
]
```

### Remediation constraints

```json
[
  "Use direct filesystem enumeration with literal suffix comparison or a non-shell argv API with explicit glob escaping.",
  "Preserve root containment, regular-file filtering and completion status."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-05",
  "prior_case_id": "cpp-query-pipeline-vulnerable",
  "prior_source_sha256": "07ab3319d90eda1e6ea81648e5ed697e42eabf9cf60a0d5ee38929ed43c80d76",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Each tenant root is service-owned and stable during enumeration; tenant IDs are authorized unsigned integers. This case does not permit glob-pattern input."
}
```

### Split

```json
"held_out"
```

## v2-cpp-vulnerable-06 — A path-segment encoder budgets input bytes but not escape expansion

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c989ce648e84d687a8c6c27c80c516001cb507108fe729a57b669be6c61bada2`. Protocol-2.0 case hash: `0e5172587b77a18b19556c067ed97d325512cd74753d87ff25a9a4e074c1b975`.

The 96-byte input cap does not account for three-byte percent escapes. A valid segment with many reserved bytes requires up to 289 bytes including its terminator, overflowing the 128-byte array.

### src/PercentSegment.cpp

```cpp
#include <string>
#include <stdexcept>
#include <cstddef>
std::string percent_segment(const std::string& segment) {
    if (segment.size() > 96) throw std::invalid_argument("segment");
    constexpr char hex[] = "0123456789ABCDEF";
    char encoded[128];
    std::size_t used = 0;
    for (unsigned char ch : segment) {
        bool literal = (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') ||
                       (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' || ch == '.' || ch == '~';
        if (literal) {
            encoded[used++] = static_cast<char>(ch);
        } else {
            encoded[used++] = '%';
            encoded[used++] = hex[ch >> 4];
            encoded[used++] = hex[ch & 15];
        }
    }
    encoded[used] = '\0';
    return std::string(encoded);
}
```

### Derivation

```json
{
  "group": "cpp-uri-component-expansion-capacity",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The vulnerability comes from variable-width encoding expansion, not a raw string copy, variadic format or aggregation of separately bounded fields. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "buffer-overflow",
    "cwe": "CWE-787",
    "path": "src/PercentSegment.cpp",
    "line_start": 17,
    "line_end": 17
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Destination expansion overflow and exact URI-component identity preservation.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Encode every byte of a bounded opaque identifier as one URI path segment, leaving only ASCII unreserved bytes literal.",
  "trust_boundary": "A user controls identifier bytes; the service must not let slashes or other reserved characters become URI structure.",
  "legitimate_examples": [
    {
      "input": "Segment team/a b",
      "expected": "Return team%2Fa%20b."
    },
    {
      "input": "Ninety-six slash bytes",
      "expected": "Return exactly ninety-six %2F escapes, without truncation or memory corruption."
    }
  ],
  "permitted_changes": [
    "Use checked dynamic storage or budget the maximum expansion including the terminator.",
    "Preserve uppercase hexadecimal escapes and encode every reserved byte, including slash."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://www.rfc-editor.org/rfc/rfc3986#section-2.1",
    "https://eel.is/c++draft/expr.add"
  ]
}
```

### Regression traps

```json
[
  "Bounding input length alone does not bound encoded output to the same length.",
  "Dropping or double-encoding bytes changes resource identity."
]
```

### Remediation constraints

```json
[
  "Use checked dynamic storage or budget the maximum expansion including the terminator.",
  "Preserve uppercase hexadecimal escapes and encode every reserved byte, including slash."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-cpp-vulnerable-06",
  "prior_case_id": "cpp-joined-buffer-vulnerable",
  "prior_source_sha256": "c975d4eedd684e7491186d239f8f17d7d1107fca37fc74a793365274ff162b14",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "C++20 with POSIX.1-2008 interfaces where used",
  "libraries": [
    "libstdc++ 13",
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-owned streams and strings are valid. Executable paths and service-owned directories cannot be modified by the requester. Input is a stable byte string of length at most 96 and may contain non-ASCII bytes or NUL; the required encoding is bytewise RFC 3986 path-segment data."
}
```

### Split

```json
"held_out"
```

