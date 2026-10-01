# bash — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-bash-safe-01 — Image resize options are selected by a closed mode and sent as argv

Proposed label: **safe**. Human review: **pending**.

Source hash: `741e7cdee697289159270f8a958ba0ddccc5df581a83e80b48a1789f61950889`. Protocol-2.0 case hash: `5b4541584f14ef65543fb8c349f8beb6cb6e4962b9807461319cebae423eeecb`.

Only fixed geometry values are selected, and the array preserves argument boundaries without eval or a shell program string. Filenames are private service constants.

### bin/thumbnail-mode.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )); then exit 2; fi
case "$1" in
    avatar) geometry='96x96>' ;;
    preview) geometry='640x480>' ;;
    *) printf '%s\n' 'unknown mode' >&2; exit 2 ;;
esac
input=/srv/images/current.png
output=/srv/images/thumb.png
arguments=("$input" -resize "$geometry" "$output")
/usr/bin/convert "${arguments[@]}"
```

### Derivation

```json
{
  "group": "bash-closed-geometry-argv",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A shell-looking redirection character is legitimately part of a fixed downstream geometry argument and must not be mistaken for evaluated shell syntax. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Process argument construction; image decoder correctness is outside this source case.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Resize a fixed staged image according to one of two public thumbnail modes.",
  "trust_boundary": "A user selects avatar or preview but cannot supply geometry syntax, executable names or paths.",
  "legitimate_examples": [
    {
      "input": "Mode avatar",
      "expected": "Invoke conversion with the exact 96x96> geometry argument."
    },
    {
      "input": "Mode preview;id",
      "expected": "Reject before invoking convert."
    }
  ],
  "permitted_changes": [
    "Keep closed mode mapping, quoted array expansion and fixed paths.",
    "Preserve greater-than resize semantics, which avoid enlarging already smaller images."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Unquoted array expansion could split or reinterpret arguments.",
  "The > inside a quoted argument is data, not shell redirection."
]
```

### Remediation constraints

```json
[
  "Keep closed mode mapping, quoted array expansion and fixed paths.",
  "Preserve greater-than resize semantics, which avoid enlarging already smaller images."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-01",
  "prior_case_id": "bash-user-expression-safe",
  "prior_source_sha256": "ad79485988184017b99d2b08422af4c26dc93aed97e5f7d75aea72f69511e4c4",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. ImageMagick 6.9 convert is trusted; the caller stages a valid bounded PNG in a private directory and imposes processing limits."
}
```

### Split

```json
"held_out"
```

## v2-bash-safe-02 — TLS health check uses an explicit private CA and refuses redirect downgrades

Proposed label: **safe**. Human review: **pending**.

Source hash: `19b060f9b3e236aac19d5664c5720ba7232f4dce2e9a9a7c39ac60a0a56cc1d9`. Protocol-2.0 case hash: `0050ef9ab20b3d06ae44c8171067f15eb529e8c3aadf7f86411440a210c654f9`.

The trusted CA file narrows certificate trust without disabling verification. HTTPS protocol restrictions, a fixed hostname and no -L redirect following retain authenticated transport.

### bin/check-service.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
ca=/etc/codeagent/team-ca.pem
if [[ ! -r "$ca" ]]; then
    printf '%s\n' 'team CA unavailable' >&2
    exit 2
fi
/usr/bin/curl --fail --silent --show-error --max-time 5 \
    --proto '=https' --proto-redir '=https' \
    --cacert "$ca" --head \
    https://scanner.internal.example/health >/dev/null
printf '%s\n' 'reachable'
```

### Derivation

```json
{
  "group": "bash-private-ca-head-check",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The safe case uses a deliberately private trust root with a HEAD request rather than replacing verification with an unconditional bypass. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "TLS configuration and explicit synthetic health request semantics.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Confirm the fixed team scanner health endpoint is reachable over verified HTTPS.",
  "trust_boundary": "The network is untrusted; the CA file and hostname are administrator-controlled.",
  "legitimate_examples": [
    {
      "input": "Trusted endpoint returns HTTP 204",
      "expected": "Print reachable and exit 0."
    },
    {
      "input": "Wrong-host or untrusted certificate",
      "expected": "Exit nonzero without printing reachable."
    }
  ],
  "permitted_changes": [
    "Retain certificate and hostname verification and the deadline.",
    "Fail when the CA file is unavailable; do not fall back to insecure mode."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "A private CA is not equivalent to --insecure.",
  "Printing success after suppressing curl failure misrepresents readiness."
]
```

### Remediation constraints

```json
[
  "Retain certificate and hostname verification and the deadline.",
  "Fail when the CA file is unavailable; do not fall back to insecure mode."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-02",
  "prior_case_id": "bash-curl-certificates-safe",
  "prior_source_sha256": "38567682544bf0b366eb0eb6910c5d4c6a3b9af3246273e8e1a1ad38a12c38c0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. curl 8.5 with its normal TLS backend; the CA file is a nonempty administrator-owned PEM trust bundle."
}
```

### Split

```json
"held_out"
```

## v2-bash-safe-03 — Artifact names are NUL-delimited data in a shell loop

Proposed label: **safe**. Human review: **pending**.

Source hash: `2358746fd070a6053d66ddf54b91833a25690154c556ad8acafd3746a6d84142`. Protocol-2.0 case hash: `f50e908d332ead60dbbe01e8445a8fa751d71912be916a16f4f75504eb6bef75`.

Filenames are consumed as NUL-delimited bytes with read -r and printed as data through a fixed format. Whitespace, backslashes and shell-looking names are never evaluated.

### bin/list-artifacts.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
root=/srv/artifacts/public
if [[ ! -d "$root" ]]; then exit 2; fi
count=0
while IFS= read -r -d '' name; do
    printf '%s\0' "${name##*/}"
    ((count+=1))
done < <(/usr/bin/find "$root" -maxdepth 1 -type f -print0)
printf 'listed=%d\n' "$count" >&2
```

### Derivation

```json
{
  "group": "bash-nul-filename-enumeration",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The operation handles arbitrary filename characters using NUL framing and separate diagnostic output rather than attempting ad hoc escaping. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Safe filename data handling; snapshot availability failures are excluded explicitly.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List basenames of direct regular public artifacts as a NUL-delimited stream and report the count on stderr.",
  "trust_boundary": "Uploaders may choose artifact names but cannot modify the private root directory or insert symlinks during this listing.",
  "legitimate_examples": [
    {
      "input": "Files named a b and $(note)",
      "expected": "Emit both literal names separated by NUL, with listed=2 on stderr."
    },
    {
      "input": "A nested directory containing a file",
      "expected": "Do not list the nested file."
    }
  ],
  "permitted_changes": [
    "Preserve NUL-delimited output, depth one and regular-file filtering.",
    "Keep filename data out of eval or format positions."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Line-delimited parsing would corrupt names containing newline.",
  "The count diagnostic must stay off the machine-readable stdout stream."
]
```

### Remediation constraints

```json
[
  "Preserve NUL-delimited output, depth one and regular-file filtering.",
  "Keep filename data out of eval or format positions."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-03",
  "prior_case_id": "bash-variable-indirection-safe",
  "prior_source_sha256": "35964157a4926389364ca2c75eef8268f79635ce39a34a32054bd47f6f0c6351",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. GNU findutils 4.9; root exists on a stable readable local filesystem, and no permission/read errors occur during this bounded operation."
}
```

### Split

```json
"held_out"
```

## v2-bash-safe-04 — A numeric batch size is validated before decimal arithmetic

Proposed label: **safe**. Human review: **pending**.

Source hash: `957b720d10c67e574960e435a0455ca95b080f89d6cdd88253cf23d82c786b45`. Protocol-2.0 case hash: `fd0aa31cdaae53fcf02fcb4dd879e229525e721c0b25e25bc2cc0f7b89ef3d9c`.

The anchored digit-only grammar limits length before arithmetic evaluation, and 10# explicitly chooses decimal. Arbitrary Bash arithmetic expressions cannot reach the evaluator.

### bin/batch-window.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )); then exit 2; fi
value=$1
if [[ ! "$value" =~ ^[0-9]{1,3}$ ]]; then
    printf '%s\n' 'decimal batch size required' >&2
    exit 2
fi
size=$((10#$value))
if (( size < 1 || size > 200 )); then exit 2; fi
for ((start=0; start<1000; start+=size)); do
    end=$((start+size))
    if (( end > 1000 )); then end=1000; fi
    printf '%d:%d\n' "$start" "$end"
done
```

### Derivation

```json
{
  "group": "bash-decimal-batch-arithmetic",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A legitimate arithmetic evaluator is safe only because its input grammar and numeric range are established before use. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Validated arithmetic input and shell evaluation false-positive control.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Emit half-open batch windows covering exactly the integer interval 0..1000.",
  "trust_boundary": "A caller controls one decimal batch-size string between 1 and 200.",
  "legitimate_examples": [
    {
      "input": "008",
      "expected": "Treat as decimal eight and begin with 0:8."
    },
    {
      "input": "1+2",
      "expected": "Reject as nondecimal input rather than evaluate an expression."
    }
  ],
  "permitted_changes": [
    "Keep strict grammar before arithmetic and explicit decimal interpretation.",
    "Preserve nonoverlapping half-open windows and clamp the final endpoint to 1000."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Removing 10# changes leading-zero values to octal.",
  "Bash arithmetic is an evaluator; the preceding narrow grammar is part of the safety proof."
]
```

### Remediation constraints

```json
[
  "Keep strict grammar before arithmetic and explicit decimal interpretation.",
  "Preserve nonoverlapping half-open windows and clamp the final endpoint to 1000."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-04",
  "prior_case_id": "bash-wget-certificates-safe",
  "prior_source_sha256": "f221eab0e296172f8b43d599db5ad79662bd80f642485fb60e35af7cdbd63009",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. GNU Bash 5.2 integer arithmetic; all values remain under 1200 and cannot overflow machine integers."
}
```

### Split

```json
"held_out"
```

## v2-bash-safe-05 — A configuration reader handles literal key/value text without sourcing

Proposed label: **safe**. Human review: **pending**.

Source hash: `1986c888bed50bffdb2d6c7cf359b4bcf8f94024e0e9d652818f34459e35109c`. Protocol-2.0 case hash: `68726bd2f46782e076c280365aef255e1793047dcc520f5c54bd321ac0e2b540`.

The reader treats the file as data, accepts exactly one theme key with a closed value set, and never sources or evaluates its content.

### bin/read-theme.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
file=/srv/preferences/theme.conf
theme=
while IFS='=' read -r key value || [[ -n "$key$value" ]]; do
    if [[ "$key" != theme || -n "$theme" ]]; then exit 2; fi
    case "$value" in light|dark) theme=$value ;; *) exit 2 ;; esac
done < "$file"
if [[ -z "$theme" ]]; then exit 2; fi
printf '%s\n' "$theme"
```

### Derivation

```json
{
  "group": "bash-single-preference-data-reader",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This is a single explicit application preference grammar, not a safe twin of the multi-field job dispatch manifest. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Data-only configuration parsing and duplicate-key rejection.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read exactly one persisted theme preference, including a final line without a newline.",
  "trust_boundary": "A user can update the preference file contents through a size-limited save API; the path is fixed.",
  "legitimate_examples": [
    {
      "input": "theme=dark without a trailing newline",
      "expected": "Print dark."
    },
    {
      "input": "Two theme lines or an unknown key",
      "expected": "Reject without output."
    }
  ],
  "permitted_changes": [
    "Retain one-key/one-value validation and non-evaluating parsing.",
    "Preserve support for a missing final newline."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Replacing the parser with source gives data file contents command privileges.",
  "A while-read loop without the EOF condition drops the last unterminated line."
]
```

### Remediation constraints

```json
[
  "Retain one-key/one-value validation and non-evaluating parsing.",
  "Preserve support for a missing final newline."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-05",
  "prior_case_id": "bash-nested-shell-safe",
  "prior_source_sha256": "81a4edde66550e01fa002b0b6ad72de271d42cb7ba61bfe3a62e35a3cad38431",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. The private file is an immutable snapshot of at most 64 bytes, contains ASCII without NUL, and is readable by the service."
}
```

### Split

```json
"held_out"
```

## v2-bash-safe-06 — An HTTPS package checksum is compared as data after a trusted download

Proposed label: **safe**. Human review: **pending**.

Source hash: `fb39e04278dc50e8b0c8cbe9f8a6ed3e05b9ec8d4f3295e2b25513d79182c89e`. Protocol-2.0 case hash: `bbf4e6cd767cba20bd3c6e9f5a1db30a764514a2446c90f9afef669cfbbdfe8c`.

The expected digest has a strict hexadecimal grammar and is compared as text to a SHA-256 result. No downloaded content or digest text is executed; authenticity comes from the separately authenticated metadata channel.

### bin/check-local-digest.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )); then exit 2; fi
expected=$1
if [[ ! "$expected" =~ ^[0-9a-f]{64}$ ]]; then
    printf '%s\n' 'invalid digest' >&2
    exit 2
fi
result=$(/usr/bin/sha256sum -- /srv/packages/staged.bin)
actual=${result%% *}
if [[ "$actual" != "$expected" ]]; then
    printf '%s\n' 'digest mismatch' >&2
    exit 1
fi
printf '%s\n' 'digest matched'
```

### Derivation

```json
{
  "group": "bash-trusted-digest-file-comparison",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe hash use has a concrete trusted reference and file-identity contract, distinct from using an unkeyed digest as sender authentication. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Content-integrity comparison with a trusted reference; metadata-channel implementation is outside this snippet.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Confirm that a fixed staged file matches its trusted expected content digest.",
  "trust_boundary": "The package bytes may be attacker-modified, but the expected digest is obtained from authenticated operator metadata rather than the same untrusted file.",
  "legitimate_examples": [
    {
      "input": "Correct lowercase SHA-256 digest",
      "expected": "Print digest matched and exit 0."
    },
    {
      "input": "Well-formed but wrong digest",
      "expected": "Print a mismatch to stderr and exit 1."
    }
  ],
  "permitted_changes": [
    "Retain SHA-256 and the authenticated expected-digest origin.",
    "Keep fixed file selection and separate mismatch versus malformed-input results."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "A hash does not authenticate anything when its expected value comes from the attacker too.",
  "Do not interpret expected text as a checksum command line or filename."
]
```

### Remediation constraints

```json
[
  "Retain SHA-256 and the authenticated expected-digest origin.",
  "Keep fixed file selection and separate mismatch versus malformed-input results."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-safe-06",
  "prior_case_id": "bash-format-argument-safe",
  "prior_source_sha256": "05e0d8a74b44b61ccf69d4a721492a00cacd199d46769e23d4dd1bf7d8f337f9",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. GNU sha256sum/coreutils 9.4; staged.bin is a stable private regular file, at most 64 MiB; authenticated metadata retrieval is an explicit caller precondition."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-01 — Job dispatcher sources a tenant-uploaded environment manifest

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `f7788043824f42f491067923a147519a472db201e91aee98f84deb4d15ab75bc`. Protocol-2.0 case hash: `6b8b792c93a3926ace446cc04916c57de897c79cb46d2d053f784fe0bcb599fc`.

The uploaded file is a data manifest, but source executes it as Bash under the dispatcher account before checking any values.

### bin/dispatch-job.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
manifest=/srv/jobs/current.env
if [[ ! -f "$manifest" ]]; then
    printf '%s\n' 'job manifest missing' >&2
    exit 2
fi
source "$manifest"
: "${TENANT:?tenant missing}"
: "${REGION:?region missing}"
case "$REGION" in eu|us) ;; *) exit 2 ;; esac
printf 'tenant=%s region=%s\n' "$TENANT" "$REGION"
```

### Derivation

```json
{
  "group": "bash-untrusted-env-manifest-source",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The unsafe boundary is a configuration file treated as a program, with an explicit finite data grammar and post-execution checks. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "bin/dispatch-job.sh",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Dynamic evaluation of a source-controlled manifest file.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a job manifest containing exactly TENANT and REGION key/value fields and emit a dispatch record.",
  "trust_boundary": "A tenant can upload manifest content but cannot execute worker code or modify the trusted manifest pathname.",
  "legitimate_examples": [
    {
      "input": "TENANT=acme followed by REGION=eu",
      "expected": "Emit tenant=acme region=eu."
    },
    {
      "input": "A line containing shell substitution",
      "expected": "Reject as invalid manifest data without evaluating it."
    }
  ],
  "permitted_changes": [
    "Parse the two documented keys as data; allow tenant IDs [A-Za-z0-9_-]{1,32} and region eu or us.",
    "Reject duplicates, unknown keys and missing required fields before output."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Checking REGION after sourcing is too late to prevent execution.",
  "Do not replace source with eval of the same text."
]
```

### Remediation constraints

```json
[
  "Parse the two documented keys as data; allow tenant IDs [A-Za-z0-9_-]{1,32} and region eu or us.",
  "Reject duplicates, unknown keys and missing required fields before output."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-01",
  "prior_case_id": "bash-user-expression-vulnerable",
  "prior_source_sha256": "5c0133dff261390af2421c0cf4f30ffa36386d6ecaa90a1119b2e0d1ca609426",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. Manifest is at most 1 KiB, UTF-8 ASCII subset, and a private immutable snapshot supplied by the upload service. Its format is key=value lines with no quoting or expansion."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-02 — Tag exporter builds an array by evaluating a comma-separated request

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `e16dde0ac0516da0c7cd32826a35e29b2a7ed21dd80fd1d177f3fb48d0dd4915`. Protocol-2.0 case hash: `63c176def7b6319913bd85ee450998e97eb1d3079c3abce6242f70378d952932`.

Comma replacement does not restrict the resulting shell language. eval performs substitutions and executes syntax while building what should be a list of literal identifiers.

### bin/export-tags.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )) || (( ${#1} > 256 )); then
    exit 2
fi
selection=${1//,/ }
labels=()
eval "labels=($selection)"
if (( ${#labels[@]} == 0 || ${#labels[@]} > 10 )); then
    exit 2
fi
for label in "${labels[@]}"; do
    printf 'tag=%s\n' "$label"
done
```

### Derivation

```json
{
  "group": "bash-comma-list-evaluated-array",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A collection parser accidentally invokes the shell language; its valid grammar, empty-item handling and duplicate behavior are explicit. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "bin/export-tags.sh",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Dynamic evaluation during collection construction.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Emit one tag record for each of up to ten comma-separated tag identifiers.",
  "trust_boundary": "A dashboard user supplies the tag selection string, not a Bash array expression.",
  "legitimate_examples": [
    {
      "input": "east,stable",
      "expected": "Emit tag=east then tag=stable on separate lines."
    },
    {
      "input": "An empty tag between commas",
      "expected": "Reject the entire request without partial output."
    }
  ],
  "permitted_changes": [
    "Split on commas without eval and validate each identifier against [A-Za-z0-9_-]{1,32}.",
    "Preserve order and duplicate tags; reject invalid input atomically before output."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Changing eval quoting cannot make arbitrary array source into safe data.",
  "Using read without preserving empty fields can silently accept malformed lists."
]
```

### Remediation constraints

```json
[
  "Split on commas without eval and validate each identifier against [A-Za-z0-9_-]{1,32}.",
  "Preserve order and duplicate tags; reject invalid input atomically before output."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-02",
  "prior_case_id": "bash-curl-certificates-vulnerable",
  "prior_source_sha256": "d23adc750dc52bc1ef9ffdf9cd693b813f5a1fabc57a978035cfc5a04a28a34d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. The API contract is comma-delimited ASCII identifiers without whitespace or escaping; bounds are enforced in the script."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-03 — A remote ticket lookup passes a local argument into an SSH shell command

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `ad83cd2eb08eb9155ef641daa6b4e6cef759f259887ee0bea66590ef07cb7263`. Protocol-2.0 case hash: `645140b9d0d714afe3cf00aca67172dd366add6047ead78d3cc6851cb83fb674`.

Local quoting preserves one local ssh argument, but SSH concatenates command arguments for execution by the remote shell. The untrusted ticket value can therefore become remote shell syntax.

### bin/remote-ticket.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )); then exit 2; fi
ticket=$1
if (( ${#ticket} == 0 || ${#ticket} > 80 )); then
    printf '%s\n' 'invalid ticket length' >&2
    exit 2
fi
remote_user=report
remote_host=reports.internal.example
/usr/bin/ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -- \
    "$remote_user@$remote_host" /usr/local/bin/ticket-summary "$ticket"
```

### Derivation

```json
{
  "group": "bash-ssh-remote-command-argument",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The injection occurs on a second host after local argv construction, distinguishing it from local eval and unquoted-shell examples. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "bin/remote-ticket.sh",
    "line_start": 12,
    "line_end": 12
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Remote shell construction across SSH, including the second parsing boundary.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return a remote summary for one literal ticket reference.",
  "trust_boundary": "A support user supplies a ticket reference and is authorized for summaries only; the SSH account may execute the trusted query helper but not arbitrary user programs by policy.",
  "legitimate_examples": [
    {
      "input": "Ticket CASE-204",
      "expected": "Return the helper summary for CASE-204."
    },
    {
      "input": "Ticket Owner's followup",
      "expected": "Pass the apostrophe and space literally to the remote helper."
    }
  ],
  "permitted_changes": [
    "Use a fixed remote command with length-delimited data on stdin or a documented correctly encoded protocol.",
    "Retain strict host-key verification and propagate the helper exit status."
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
    "https://man.openbsd.org/ssh.1",
    "https://www.gnu.org/software/bash/manual/bash.html"
  ]
}
```

### Regression traps

```json
[
  "Double-quoting the local variable does not preserve an argument boundary through the remote shell.",
  "Disabling host-key checking to make automation work is a separate regression."
]
```

### Remediation constraints

```json
[
  "Use a fixed remote command with length-delimited data on stdin or a documented correctly encoded protocol.",
  "Retain strict host-key verification and propagate the helper exit status."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-03",
  "prior_case_id": "bash-variable-indirection-vulnerable",
  "prior_source_sha256": "1b13742a2c67e397d8ea7fe3670207ed07dfdd39491d4809593701362ab29d80",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. OpenSSH 9.6; a pinned known_hosts entry and service-owned SSH key are installed; the remote account has a normal POSIX shell and no forced-command defense. The helper treats ticket data literally."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-04 — Production inventory download explicitly disables certificate verification

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c5f866746a17347b14cc153c9820d6b70e387fe060fc790a7d9f965d97d5a6d3`. Protocol-2.0 case hash: `1bb2df4be71c2c709022c9f4baf64fb19211fb4306912a12ab2ebe6ead813295`.

HTTPS-only protocol restrictions and atomic replacement do not authenticate the server when --insecure disables certificate and hostname checks.

### bin/fetch-inventory.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
output=/srv/inventory/current.json
staging=$(/usr/bin/mktemp /srv/inventory/pending.XXXXXX)
trap '/usr/bin/rm -f -- "$staging"' EXIT
options=(--fail --silent --show-error --max-time 20)
options+=(--proto '=https' --proto-redir '=https')
options+=(--insecure)
/usr/bin/curl "${options[@]}" \
    https://inventory.example.org/current.json --output "$staging"
/usr/bin/mv -- "$staging" "$output"
printf '%s\n' 'inventory updated'
```

### Derivation

```json
{
  "group": "bash-inventory-tls-atomic-download",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A seemingly careful download pipeline already has staging and protocol restrictions, isolating the remaining certificate-verification failure. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "bin/fetch-inventory.sh",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "TLS verification and update atomicity, not the inventory application schema.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Download authenticated inventory metadata and replace the current copy only after transport success.",
  "trust_boundary": "An active network attacker must not substitute inventory content; the URL and destination are operator-owned.",
  "legitimate_examples": [
    {
      "input": "A valid HTTPS endpoint returns JSON",
      "expected": "Replace current.json after a successful transfer."
    },
    {
      "input": "Endpoint presents an untrusted certificate",
      "expected": "Fail and preserve the previous current.json."
    }
  ],
  "permitted_changes": [
    "Remove insecure verification bypass and use the maintained system CA store or an explicitly managed private CA.",
    "Keep HTTPS restrictions, deadline, failure handling and atomic replacement."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Switching to HTTP avoids certificate errors by removing authentication entirely.",
  "Writing directly to current.json can destroy the last good copy on transfer failure."
]
```

### Remediation constraints

```json
[
  "Remove insecure verification bypass and use the maintained system CA store or an explicitly managed private CA.",
  "Keep HTTPS restrictions, deadline, failure handling and atomic replacement."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-04",
  "prior_case_id": "bash-wget-certificates-vulnerable",
  "prior_source_sha256": "27060cf5792952208109a72e7f6e0605ca388d164ecda3c5137eb91d9916481f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. curl 8.5; private service-owned /srv/inventory directory on one filesystem; files are bounded by a caller download quota; JSON is data and never sourced or evaluated."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-05 — Tenant branding text becomes the builtin printf program

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `fcc7de88211b9d6f35973a13b006c56bec7d4f512493d181515fef11b6290ee7`. Protocol-2.0 case hash: `9c23891dd2ab31d7e3bf622f96e85136de05dd04bfee949c96da3dd95f04985d`.

The tenant brand is interpreted as a Bash printf format, so percent sequences change output or trigger formatting errors instead of remaining literal. This is an output-integrity issue, not a claim of C-style arbitrary memory writes.

### bin/status-banner.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 2 )); then exit 2; fi
brand=$1
state=$2
if (( ${#brand} > 80 )); then exit 2; fi
case "$state" in ready|busy|offline) ;; *) exit 2 ;; esac
printf '%s' 'status: '
printf "$brand"
printf ' [%s]\n' "$state"
```

### Derivation

```json
{
  "group": "bash-branding-printf-output-integrity",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The effect is a bounded shell-builtin output violation with constrained severity, independent of variadic C memory hazards. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "format-string",
    "cwe": "CWE-134",
    "path": "bin/status-banner.sh",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Bash builtin formatting and literal output integrity; severity must reflect actual shell-builtin behavior.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a literal bounded tenant brand followed by a validated status label.",
  "trust_boundary": "Tenants control display branding but not formatting directives or status values.",
  "legitimate_examples": [
    {
      "input": "Brand 100% Studio, state ready",
      "expected": "Print status: 100% Studio [ready] and newline."
    },
    {
      "input": "Brand %s%s, state busy",
      "expected": "Print those percent sequences literally."
    }
  ],
  "permitted_changes": [
    "Use a fixed %s format for branding.",
    "Preserve every accepted brand character and the validated state layout."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Do not claim that Bash printf has the same memory-corruption impact as C printf.",
  "Escaping only a subset of percent sequences leaves format interpretation."
]
```

### Remediation constraints

```json
[
  "Use a fixed %s format for branding.",
  "Preserve every accepted brand character and the validated state layout."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-05",
  "prior_case_id": "bash-nested-shell-vulnerable",
  "prior_source_sha256": "2cfb163dc16139fa845c1763c003b760dd36203fdc5f3d4d856cdcc3d9d2e67c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. Branding contains no CR/LF or NUL and is rendered as terminal plain text; ingress also rejects terminal escape/control characters."
}
```

### Split

```json
"held_out"
```

## v2-bash-vulnerable-06 — A certificate-expiry job interpolates a domain into an arithmetic shell command

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `694853b7eea97e2774259b9d23e2eae8e501236cd13388d718e558aba73ded6a`. Protocol-2.0 case hash: `6f953bd2c9530e3758559f8910ea9f82045449eac65db63dacd03c60f9895698`.

The path separator and newline checks do not constrain the domain to DNS-label characters. Shell substitutions and operators can survive into the second shell despite the fixed path prefix and suffix.

### bin/certificate-days.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
if (( $# != 1 )); then exit 2; fi
domain=$1
if (( ${#domain} > 253 )); then exit 2; fi
case "$domain" in
    *$'\n'*|*'/'*) printf '%s\n' 'invalid domain' >&2; exit 2 ;;
esac
command="/usr/bin/openssl x509 -enddate -noout -in /srv/certificates/$domain.pem"
result=$(/bin/sh -c "$command")
printf '%s\n' "$result"
```

### Derivation

```json
{
  "group": "bash-certificate-identifier-shell-validation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The case concerns incomplete validation of a DNS identifier mapped to a local certificate, with a closed root and exact certificate-view permission rather than free-form log search. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "bin/certificate-days.sh",
    "line_start": 10,
    "line_end": 10
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell construction from a constrained identifier whose current validation is incomplete.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the notAfter field for a certificate selected by an authorized ASCII DNS name.",
  "trust_boundary": "An operator with certificate-view permission supplies a domain name but may not execute service-account commands.",
  "legitimate_examples": [
    {
      "input": "Domain api.example.org",
      "expected": "Read only /srv/certificates/api.example.org.pem and return its expiry line."
    },
    {
      "input": "Domain containing shell punctuation outside DNS-name grammar",
      "expected": "Reject before invoking a helper."
    }
  ],
  "permitted_changes": [
    "Validate the documented DNS-name grammar and invoke openssl directly with separate arguments.",
    "Preserve fixed root/suffix selection and propagate certificate parse errors."
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
    "https://www.gnu.org/software/bash/manual/bash.html",
    "https://curl.se/docs/manpage.html"
  ]
}
```

### Regression traps

```json
[
  "Rejecting slash prevents one path escape but not shell expansion.",
  "Do not accept an arbitrary certificate path or change the operation into network retrieval."
]
```

### Remediation constraints

```json
[
  "Validate the documented DNS-name grammar and invoke openssl directly with separate arguments.",
  "Preserve fixed root/suffix selection and propagate certificate parse errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-bash-vulnerable-06",
  "prior_case_id": "bash-format-argument-vulnerable",
  "prior_source_sha256": "304583118bbc16f6903130edeb24ac88550d2cb4a651e478ff606c743b9ec7f6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "GNU Bash 5.2",
  "libraries": [
    "GNU coreutils 9.4"
  ],
  "platform": "Linux x86-64",
  "setup": "The service launches the script with a fixed trusted PATH, sanitized environment and arguments described by the contract. Service-owned files and executable paths are not writable by the requester. OpenSSL 3.0; ASCII DNS names only with labels 1..63 chars, no leading/trailing hyphen, total at most 253; caller authorizes the exact name; private certificate directory is stable and has no symlinks."
}
```

### Split

```json
"held_out"
```

