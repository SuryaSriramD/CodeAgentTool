# c — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-c-safe-01 — A hexadecimal device identifier uses a caller-provided exact capacity

Proposed label: **safe**. Human review: **pending**.

Source hash: `2916832dc9561a90916986078eb22314574ddce0369ff9435d90e62cf0ceb2f8`. Protocol-2.0 case hash: `bb6c86a76c8afe4db8277d5e16083e6ca5529a8d60f3c2e621205f250ccbe4c0`.

The count is capped before multiplication and the destination capacity includes the terminator; every array index is bounded by those checks.

### src/hex_identifier.c

```c
#include <stddef.h>
static const char digits[] = "0123456789abcdef";
int hex_identifier(const unsigned char *bytes, size_t count, char *out, size_t capacity) {
    if (count > 32 || capacity < count * 2 + 1) return -1;
    for (size_t i = 0; i < count; ++i) {
        out[i * 2] = digits[bytes[i] >> 4];
        out[i * 2 + 1] = digits[bytes[i] & 15];
    }
    out[count * 2] = '\0';
    return (int)(count * 2);
}
```

### Derivation

```json
{
  "group": "c-binary-hex-capacity",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe encoder handles arbitrary binary octets with arithmetic and destination-ownership checks rather than a repaired text-copy sibling. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Bounded binary-to-text writes; no shell, SQL, XML or cryptographic use.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Encode up to 32 binary identifier bytes into lowercase hexadecimal.",
  "trust_boundary": "A device controls the bytes and count; the caller supplies the actual allocated capacity, never a device-claimed capacity.",
  "legitimate_examples": [
    {
      "input": "Bytes 00 ff, capacity 5",
      "expected": "Write 00ff and NUL; return 4."
    },
    {
      "input": "Two bytes, capacity 4",
      "expected": "Return -1 without writing output."
    }
  ],
  "permitted_changes": [
    "Keep exact lowercase output and reject undersized buffers before any write.",
    "Preserve the actual-capacity caller contract."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "A count-based check without the terminator would allow an off-by-one write.",
  "Do not relabel arbitrary pointer provenance as safe; only the declared allocated buffer contract applies."
]
```

### Remediation constraints

```json
[
  "Keep exact lowercase output and reject undersized buffers before any write.",
  "Preserve the actual-capacity caller contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-01",
  "prior_case_id": "c-audit-format-safe",
  "prior_source_sha256": "c4ebb2b0f5ee16644eb28f34601bb8af86796bfc00dae3cc9ada68e9b52d13bc",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Input and output objects do not overlap. The caller-provided capacity equals the writable allocation size."
}
```

### Split

```json
"held_out"
```

## v2-c-safe-02 — A length-prefixed record is copied to a FILE without format interpretation

Proposed label: **safe**. Human review: **pending**.

Source hash: `9ef927e7cb1bafcb58b390f1c9e3ff256036357c0c9835cd7d683d493bca74bb`. Protocol-2.0 case hash: `851080e29a96dbf6b587a251c917664ada38889c818ee5fea499904e3327d050`.

The frame length is checked against both the available bytes and a maximum, and the payload is relayed with fwrite rather than interpreted as a C string or format.

### src/relay_record.c

```c
#include <stdio.h>
#include <stdint.h>
int relay_record(FILE *out, const unsigned char *record, size_t size) {
    if (size < 2) return -1;
    size_t body = ((size_t)record[0] << 8) | record[1];
    if (body > 4096 || body != size - 2) return -1;
    unsigned char prefix[2] = {(unsigned char)(body >> 8), (unsigned char)body};
    if (fwrite(prefix, 1, sizeof prefix, out) != sizeof prefix) return -1;
    if (fwrite(record + 2, 1, body, out) != body) return -1;
    return fflush(out) == EOF ? -1 : 0;
}
```

### Derivation

```json
{
  "group": "c-framed-binary-relay",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Binary-transparent framing has no string semantics and supplies a distinct safe control against lexical percent/string warnings. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Bounds and formatting for binary relay; authenticated routing and storage durability are outside this function.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Relay one binary framed record to a caller-owned spool stream.",
  "trust_boundary": "A remote sensor controls all frame bytes, including NULs and percent signs; the service owns the destination stream.",
  "legitimate_examples": [
    {
      "input": "Header 00 03 and bytes 25 00 ff",
      "expected": "Relay all five bytes exactly."
    },
    {
      "input": "Header claims eight bytes but only three follow",
      "expected": "Return -1 without writing."
    }
  ],
  "permitted_changes": [
    "Preserve binary transparency and exact length checks.",
    "Keep failure reporting on short writes and caller ownership."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Replacing fwrite with fputs truncates embedded NUL bytes.",
  "A format-string scanner must distinguish data written by fwrite."
]
```

### Remediation constraints

```json
[
  "Preserve binary transparency and exact length checks.",
  "Keep failure reporting on short writes and caller ownership."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-02",
  "prior_case_id": "c-archive-shell-safe",
  "prior_source_sha256": "f6ed03caec7921e1cbc203ebe2a4809b00453caf72222b99ceb23c2e2666c722",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Input size equals the readable record allocation; no concurrent mutation of the buffer."
}
```

### Split

```json
"held_out"
```

## v2-c-safe-03 — Database diagnostics are length-limited and formatted by trusted code

Proposed label: **safe**. Human review: **pending**.

Source hash: `e75ac7815959931c857d463e50170cddfa3109ecdc7457c415d886e915830223`. Protocol-2.0 case hash: `2a6502aa5d864817424887ab0a53634f3a29526125d5a81deaba4b01566c197a`.

The diagnostic contains SQL terminology but executes no SQL. All external text is passed as data to a fixed format, with a validated state field.

### src/db_diagnostic.c

```c
#include <stdio.h>
#include <string.h>
int db_diagnostic(FILE *out, const char *state, const char *detail) {
    size_t state_len = strlen(state);
    if (state_len != 5 || strlen(detail) > 2048) return -1;
    for (size_t i = 0; i < state_len; ++i) {
        if (!((state[i] >= '0' && state[i] <= '9') || (state[i] >= 'A' && state[i] <= 'Z'))) return -1;
    }
    if (fprintf(out, "SQLSTATE=%s detail=%s\n", state, detail) < 0) return -1;
    return fflush(out) == EOF ? -1 : 0;
}
```

### Derivation

```json
{
  "group": "c-db-error-literal-rendering",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A misleading database context contains diagnostic rendering only and intentionally separates vocabulary from actual query execution. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Formatting and SQL-injection false-positive control; it is not a database execution API.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write a bounded database diagnostic to an operator-only support stream.",
  "trust_boundary": "A remote database controls the SQLSTATE and detail values; the support stream is not parsed as commands or query text.",
  "legitimate_examples": [
    {
      "input": "State 23505, detail duplicate 10%",
      "expected": "Write both literal fields followed by newline."
    },
    {
      "input": "State containing a newline",
      "expected": "Return -1 without a diagnostic."
    }
  ],
  "permitted_changes": [
    "Keep external details as string arguments to a fixed format.",
    "Retain SQLSTATE validation and support-stream error reporting."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Variable names containing SQL do not imply a query sink.",
  "Percent signs in a %s argument must remain literal."
]
```

### Remediation constraints

```json
[
  "Keep external details as string arguments to a fixed format.",
  "Retain SQLSTATE validation and support-stream error reporting."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-03",
  "prior_case_id": "c-bounded-copy-safe",
  "prior_source_sha256": "61e21c07bf91e29c2b7376352a4440f4dad378c9198724f5485995f53a0012b3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Detail text has CR/LF removed by the database protocol adapter; support output is visible only to operators and may contain server diagnostic text."
}
```

### Split

```json
"held_out"
```

## v2-c-safe-04 — Append-only event storage checks remaining capacity before mutation

Proposed label: **safe**. Human review: **pending**.

Source hash: `a842b43e8f0870b5730de1f948e8712dc371372b5d3d1b9714111edde5d9cab2`. Protocol-2.0 case hash: `37228e8cb9bd162747c93519e535922e0d26fb32206e839cf53e100f51b59ee0`.

The size is capped before addition and checked by subtraction against remaining storage. The used invariant is validated before pointer arithmetic.

### src/event_queue.c

```c
#include <stddef.h>
#include <string.h>
struct event_queue { unsigned char bytes[1024]; size_t used; };
int enqueue_event(struct event_queue *queue, const unsigned char *event, size_t size) {
    if (queue->used > sizeof queue->bytes) return -1;
    if (size > 255 || size + 1 > sizeof queue->bytes - queue->used) return -1;
    size_t offset = queue->used;
    queue->bytes[offset] = (unsigned char)size;
    memcpy(queue->bytes + offset + 1, event, size);
    queue->used = offset + size + 1;
    return 0;
}
```

### Derivation

```json
{
  "group": "c-event-ring-append-invariant",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe case concerns persistent queue state, remaining capacity, and mutation atomicity rather than one-shot string encoding. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Buffer-capacity arithmetic and bounded memcpy.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Append a byte-length-prefixed event atomically to an in-memory queue.",
  "trust_boundary": "An external producer supplies arbitrary bytes and a size up to 255; the service exclusively owns the queue state.",
  "legitimate_examples": [
    {
      "input": "Used 1020, event size 3",
      "expected": "Write the prefix and three bytes; set used to 1024."
    },
    {
      "input": "Used 1020, event size 4",
      "expected": "Return -1 and leave all state unchanged."
    }
  ],
  "permitted_changes": [
    "Preserve atomic rejection and exact used accounting.",
    "Maintain source/destination non-overlap and the existing ownership invariant."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Replacing subtraction with unchecked used + size may overflow for corrupted state.",
  "The header byte consumes capacity too."
]
```

### Remediation constraints

```json
[
  "Preserve atomic rejection and exact used accounting.",
  "Maintain source/destination non-overlap and the existing ownership invariant."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-04",
  "prior_case_id": "c-stream-format-safe",
  "prior_source_sha256": "8ca96eb45a4950dafc1ebd01b8ffe7a91a587f90a9d6d37744f814c71f7b620e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. The queue starts with used=0 and is accessed by one thread; event points to at least size bytes and does not overlap queue."
}
```

### Split

```json
"held_out"
```

## v2-c-safe-05 — An upload byte counter compares an explicit limit without command execution

Proposed label: **safe**. Human review: **pending**.

Source hash: `89d81f72fafd6ae557db40152fd3195626ac6f772ab40bf2fd031d397b19e067`. Protocol-2.0 case hash: `f42ffc09ce0cf96c34bdac39a5e4afd62f2939dadbe16ffd0ca2b847577961d4`.

Each read is bounded by the local array and total never exceeds limit, so the subtraction stays defined. The byte counter performs no external process or data interpretation.

### src/upload_count.c

```c
#include <stdio.h>
#include <stdint.h>
int count_upload(FILE *input, size_t limit, size_t *accepted) {
    unsigned char block[4096];
    size_t total = 0;
    for (;;) {
        size_t got = fread(block, 1, sizeof block, input);
        if (got > limit - total) return -1;
        total += got;
        if (got < sizeof block) {
            if (ferror(input)) return -1;
            *accepted = total;
            return 0;
        }
    }
}
```

### Derivation

```json
{
  "group": "c-stream-limit-counting",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This is a streaming limit enforcement operation with no text conversion, distinct from aggregate-buffer and record-format cases. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Bounded streaming byte counting; blocking and authorization are handled by the ingress.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Consume a stream and return its exact length if it does not exceed a caller policy limit.",
  "trust_boundary": "An untrusted upload controls stream contents and length; a trusted caller selects limit.",
  "legitimate_examples": [
    {
      "input": "Five-byte stream, limit 8",
      "expected": "Return 0 and set accepted=5."
    },
    {
      "input": "Nine-byte stream, limit 8",
      "expected": "Return -1 without publishing an accepted length."
    }
  ],
  "permitted_changes": [
    "Retain bounded reads, checked accumulation and input-error handling.",
    "Do not treat binary NUL as end of input."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Reporting the partial total as success after exceeding the limit breaks the contract.",
  "Source bytes are not a format string or process command."
]
```

### Remediation constraints

```json
[
  "Retain bounded reads, checked accumulation and input-error handling.",
  "Do not treat binary NUL as end of input."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-05",
  "prior_case_id": "c-popen-pipeline-safe",
  "prior_source_sha256": "6d057d49e3165db6b3e341c65a38bf5d5ebc5091afa4b8da9bd2680b4241a4f8",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. The input is finite or subject to a caller I/O deadline; accepted is a valid caller-owned size_t object and limit is at most 64 MiB."
}
```

### Split

```json
"held_out"
```

## v2-c-safe-06 — An operator-selected compression mode maps to fixed argv entries

Proposed label: **safe**. Human review: **pending**.

Source hash: `efbbd56c5fdd7648fe27dfd5f355124406f89aa3c253d20fbcc3fca648bb4aa2`. Protocol-2.0 case hash: `fb9d77fecf3c01c945d59c32381645f336311a4f72ff73e3cd86a56f6a595ee7`.

Only two fixed arguments can be selected, the executable and input path are trusted, and posix_spawn does not invoke a shell. The parent reaps the child and returns an exit code.

### src/compress_job.c

```c
#include <spawn.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
extern char **environ;
int compress_job(const char *mode) {
    const char *level = strcmp(mode, "fast") == 0 ? "-1" : strcmp(mode, "dense") == 0 ? "-9" : NULL;
    if (!level) return -1;
    char *argv[] = {"gzip", (char *)level, "--", "/srv/jobs/current.dat", NULL};
    pid_t child;
    if (posix_spawn(&child, "/usr/bin/gzip", NULL, NULL, argv, environ) != 0) return -1;
    int status;
    while (waitpid(child, &status, 0) < 0) if (errno != EINTR) return -1;
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}
```

### Derivation

```json
{
  "group": "c-fixed-compression-dispatch",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A safe process launch derives its only variable option from a closed business-mode mapping and preserves child lifecycle explicitly. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Process construction with fixed command and allow-listed data; compression content security is out of scope.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Compress the current service-owned spool file at one of two approved levels.",
  "trust_boundary": "A scheduler caller chooses a public mode label but cannot choose a command, path, or arbitrary options.",
  "legitimate_examples": [
    {
      "input": "Mode fast",
      "expected": "Start gzip -1 on the fixed current.dat file and return its exit code."
    },
    {
      "input": "Mode fast;id",
      "expected": "Reject with -1 without launching anything."
    }
  ],
  "permitted_changes": [
    "Keep exact allow-list mapping, separate argv entries and child reaping.",
    "Preserve the parent worker process and exit-code semantics."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Changing posix_spawn to system would introduce a shell boundary.",
  "Do not treat an arbitrary argument string as an allowed compression level."
]
```

### Remediation constraints

```json
[
  "Keep exact allow-list mapping, separate argv entries and child reaping.",
  "Preserve the parent worker process and exit-code semantics."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-safe-06",
  "prior_case_id": "c-formatted-copy-safe",
  "prior_source_sha256": "c4f5931d8cc8363139df8772105706846c761230d2bf952e671deb8c339a8f3f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. GNU gzip 1.12 is installed at /usr/bin/gzip; a sanitized environment is supplied by the service; no attacker can modify current.dat or its directory during execution."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-01 — Length-prefixed sensor identity becomes a fixed-width export row

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c87fa0cf5a014a77f39f94bb43388ae9ef8969850b42d57f1bd862c1ba112ebf`. Protocol-2.0 case hash: `dfe672933460c2a48e2c145aae27535b792ac24b4182a91eb4d2f4b2d445fc5a`.

A valid frame may contain a 255-byte identity, which overflows the 64-byte stack row during formatting; ingress length validation protects the frame read but not the destination.

### src/sensor_csv.c

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int export_sensor(FILE *csv, const unsigned char *frame, size_t length) {
    if (length < 2 || frame[0] > length - 1) return -1;
    size_t name_length = frame[0];
    char *name = malloc(name_length + 1);
    if (!name) return -1;
    memcpy(name, frame + 1, name_length);
    name[name_length] = '\0';
    char row[64];
    sprintf(row, "sensor=%s;active=1\n", name);
    int result = fputs(row, csv) == EOF ? -1 : 0;
    free(name);
    return result;
}
```

### Derivation

```json
{
  "group": "c-sensor-frame-export",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The bug arises from binary ingress length validation feeding a smaller text record; its preservation condition is the complete exported identity. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "buffer-overflow",
    "cwe": "CWE-120",
    "path": "src/sensor_csv.c",
    "line_start": 12,
    "line_end": 12
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Bounded-copy/format overflow; delimiter injection is excluded by the stated ingress grammar.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Append a complete sensor identity and active flag to the caller-owned export stream.",
  "trust_boundary": "A gateway accepts a remote device identity of up to 255 non-NUL printable ASCII bytes; the output stream is opened by the service.",
  "legitimate_examples": [
    {
      "input": "Frame with identity pump-7",
      "expected": "Append sensor=pump-7;active=1 followed by newline and return 0."
    },
    {
      "input": "Identity of 80 ASCII letters",
      "expected": "Append all 80 letters; a fixed-capacity implementation must report an explicit error rather than corrupt memory."
    }
  ],
  "permitted_changes": [
    "Preserve full identities up to 255 bytes; streaming or checked dynamic allocation is allowed.",
    "Keep FILE ownership with the caller and the 0/-1 return convention."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Do not silently truncate long accepted identities.",
  "Length validation of the source does not establish the row capacity."
]
```

### Remediation constraints

```json
[
  "Preserve full identities up to 255 bytes; streaming or checked dynamic allocation is allowed.",
  "Keep FILE ownership with the caller and the 0/-1 return convention."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-01",
  "prior_case_id": "c-audit-format-vulnerable",
  "prior_source_sha256": "822abcc3e5e8cde1098ee79117e29f0eb337eeb172b7f35ed53f497af431dc46",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Ingress excludes NUL, semicolon and newline in device names; frame length is at most 256."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-02 — A scheduled disk-quota probe trusts a tenant mount label

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `4b069aa64040d470c6e07533f6fec51b595e8ee08fffebe2787ba19432e57991`. Protocol-2.0 case hash: `8166770ff512dc8470a3d8a230d5f3ab7763afbce889302d4cc93691570bd429`.

The length check and du option terminator do not stop the shell from interpreting metacharacters in the tenant-controlled label.

### src/quota_probe.c

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int quota_probe(FILE *audit, const char *mount_label) {
    if (strlen(mount_label) > 120) return -1;
    char command[256];
    int used = snprintf(command, sizeof command, "/usr/bin/du -sk -- /srv/tenants/%s", mount_label);
    if (used < 0 || (size_t)used >= sizeof command) return -1;
    int status = system(command);
    if (fprintf(audit, "quota-probe status=%d\n", status) < 0) return -1;
    if (fflush(audit) == EOF) return -1;
    return status;
}
```

### Derivation

```json
{
  "group": "c-quota-job-shell",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A persistent tenant metadata field crosses into a privileged scheduled maintenance process and has an observable audit-status contract. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/quota_probe.c",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell interpretation of tenant-controlled text; callers authorize the tenant separately.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Run one size probe for an authorized tenant directory and record its completion status.",
  "trust_boundary": "The scheduler receives a display label from tenant metadata; a separate authorization check grants access to that tenant, but the label is not a filesystem-safe identifier.",
  "legitimate_examples": [
    {
      "input": "Label acme-west",
      "expected": "Probe /srv/tenants/acme-west once and log completion."
    },
    {
      "input": "Label blue team",
      "expected": "Treat the space as part of one directory name, not two operands."
    }
  ],
  "permitted_changes": [
    "Resolve authorized tenant identifiers to service-owned directory paths.",
    "Invoke the trusted executable with separate arguments and preserve wait/exit status reporting."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Do not replace system with exec in the current worker process.",
  "-- protects utility option parsing, not shell parsing."
]
```

### Remediation constraints

```json
[
  "Resolve authorized tenant identifiers to service-owned directory paths.",
  "Invoke the trusted executable with separate arguments and preserve wait/exit status reporting."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-02",
  "prior_case_id": "c-archive-shell-vulnerable",
  "prior_source_sha256": "e5656c00a84f99853b9ce46603ba5a830af0691bf1a185fe4b89dea10ba14829",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. GNU du 9.4 is installed at /usr/bin/du; the worker is privileged only for its tenant roots. Labels contain no slash but may contain spaces and shell metacharacters."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-03 — Length-bounded network notice is used as a FILE format

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `33c750df397f34ab60ba4d853e432b5456b3ce7452a0d2858e394733a47d5dd4`. Protocol-2.0 case hash: `0677dca7498510fb4f8e25c66634c8710bbd8ca6b8456ed397b5a11dcf688f8b`.

A bounded and terminated network string remains an attacker-controlled printf format. Percent conversions consume nonexistent arguments and can disclose memory or cause undefined behavior.

### src/notice_log.c

```c
#include <stdio.h>
#include <string.h>
int write_notice(FILE *journal, const unsigned char *payload, size_t size) {
    if (size == 0 || size > 240 || memchr(payload, 0, size)) return -1;
    char notice[241];
    memcpy(notice, payload, size);
    notice[size] = '\0';
    if (fputs("NOTICE ", journal) == EOF) return -1;
    if (fprintf(journal, notice) < 0) return -1;
    if (fputc('\n', journal) == EOF) return -1;
    return fflush(journal) == EOF ? -1 : 0;
}
```

### Derivation

```json
{
  "group": "c-network-notice-format",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Length-delimited network bytes are copied safely yet remain dangerous when treated as a variadic format, distinct from an unbounded-copy case. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "format-string",
    "cwe": "CWE-134",
    "path": "src/notice_log.c",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Uncontrolled format string; log line injection is excluded by ingress and the payload is a bounded valid byte sequence.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write one literal bounded notice after a fixed journal prefix.",
  "trust_boundary": "A remote authenticated peer controls the notice payload; it cannot access the journal stream directly.",
  "legitimate_examples": [
    {
      "input": "Payload load 50%",
      "expected": "Journal contains NOTICE load 50% and one newline."
    },
    {
      "input": "Payload %p %p",
      "expected": "Journal must contain those literal characters."
    }
  ],
  "permitted_changes": [
    "Render the complete payload as data, using a fixed format or a length-aware write.",
    "Preserve the fixed prefix, line boundary and flush/error convention."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Escaping only %n still leaves other format conversions.",
  "A byte-length limit is not a format-string sanitizer."
]
```

### Remediation constraints

```json
[
  "Render the complete payload as data, using a fixed format or a length-aware write.",
  "Preserve the fixed prefix, line boundary and flush/error convention."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-03",
  "prior_case_id": "c-bounded-copy-vulnerable",
  "prior_source_sha256": "628289d9209d2d80fd72ef2676b5523ff30a65a7dba489f44fd5aa90bd3b6ff0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Ingress rejects CR/LF to maintain one journal line; the FILE is service-owned and valid."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-04 — Feature-list assembly undercounts separators across accepted fields

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `f941ebb0b443baf69d579adaa539723d3ecbb0ecc03886781b9dd4d7813375f7`. Protocol-2.0 case hash: `50f76e47e0e08cfeee072fdcf44ff33cb58eaa3f1c1b9b6e15e8b38c5b803500`.

Per-feature limits allow up to 103 content bytes plus a terminator in a 64-byte aggregate buffer. Independent bounded inputs do not bound their concatenation.

### src/feature_header.c

```c
#include <stdio.h>
#include <string.h>
int feature_header(FILE *response, const char *const *features, size_t count) {
    if (count > 8) return -1;
    char value[64] = "";
    for (size_t i = 0; i < count; ++i) {
        if (strlen(features[i]) > 12) return -1;
        if (i) strcat(value, ",");
        strcat(value, features[i]);
    }
    if (fprintf(response, "Features: %s\n", value) < 0) return -1;
    return 0;
}
```

### Derivation

```json
{
  "group": "c-capability-header-aggregation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Individually valid feature selections combine into an unsafe aggregate; the security boundary is combination cardinality rather than a single long name. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "buffer-overflow",
    "cwe": "CWE-120",
    "path": "src/feature_header.c",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Aggregate string overflow; arbitrary token injection is excluded by a strict allow-list.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Emit the ordered, comma-separated list of up to eight selected capability names.",
  "trust_boundary": "A tenant selects up to eight allow-listed feature names, each at most 12 bytes; the combination is untrusted even though each token is valid.",
  "legitimate_examples": [
    {
      "input": "alpha, beta",
      "expected": "Emit Features: alpha,beta followed by newline."
    },
    {
      "input": "Eight twelve-character capability names",
      "expected": "Emit every name in order, with seven commas, without corrupting memory."
    }
  ],
  "permitted_changes": [
    "Preserve all allowed combinations; use streaming output or checked dynamic sizing.",
    "Do not remove separators, reorder names or lower the documented feature count."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Checking only each feature length misses the accumulated size.",
  "strncat takes append length rather than total buffer capacity."
]
```

### Remediation constraints

```json
[
  "Preserve all allowed combinations; use streaming output or checked dynamic sizing.",
  "Do not remove separators, reorder names or lower the documented feature count."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-04",
  "prior_case_id": "c-stream-format-vulnerable",
  "prior_source_sha256": "203b48e4d055989416efa7cd50676a2702beb0e03b846faefbd9bc9941c4dd31",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. All names consist only of ASCII letters and digits; the caller validates the feature allow-list."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-05 — Certificate preview helper interpolates an uploaded file basename

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `a20b2f6f68a9546f93126e88c409e5ac369b226026cfd52edc8727b1a43e5b6e`. Protocol-2.0 case hash: `5882c8f2e25b8f87c2ea22524d9e5d42894dd3fc669ce736ee5a7c4bbf8453da`.

An upload basename is concatenated into a shell command executed by popen. A short basename can contain command substitution or separators without any slash.

### src/certificate_preview.c

```c
#include <stdio.h>
#include <string.h>
int certificate_subject(const char *upload_name, char *out, size_t capacity) {
    if (strlen(upload_name) > 100 || capacity < 2) return -1;
    char command[256];
    int n = snprintf(command, sizeof command,
        "/usr/bin/openssl x509 -noout -subject -in /srv/incoming/%s", upload_name);
    if (n < 0 || (size_t)n >= sizeof command) return -1;
    FILE *pipe = popen(command, "r");
    if (!pipe) return -1;
    int read_ok = fgets(out, (int)capacity, pipe) != NULL;
    int status = pclose(pipe);
    return read_ok && status == 0 ? 0 : -1;
}
```

### Derivation

```json
{
  "group": "c-certificate-upload-subprocess",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Uploaded binary files require text extraction with a bounded output buffer and child-process lifetime obligations, independent from maintenance size probes. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/certificate_preview.c",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell injection through a certificate filename; certificate parsing itself is delegated to the trusted installed tool.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a certificate subject into the caller-owned preview buffer and close/reap the helper.",
  "trust_boundary": "The upload API assigns a user-selected basename in a private incoming directory; length and slash checks permit shell metacharacters.",
  "legitimate_examples": [
    {
      "input": "client cert.pem",
      "expected": "Read the subject for that exact basename as one input file."
    },
    {
      "input": "Malformed certificate",
      "expected": "Return -1 after reaping the helper; no success preview is invented."
    }
  ],
  "permitted_changes": [
    "Keep caller buffer ownership and terminate output; bounds are 2..4096 bytes.",
    "Use a non-shell argument API or a trusted certificate parser; always close and reap subprocesses."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "Do not return a FILE opened with fopen to a caller that expects popen/pclose ownership.",
  "Escaping spaces alone does not handle shell command substitution."
]
```

### Remediation constraints

```json
[
  "Keep caller buffer ownership and terminate output; bounds are 2..4096 bytes.",
  "Use a non-shell argument API or a trusted certificate parser; always close and reap subprocesses."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-05",
  "prior_case_id": "c-popen-pipeline-vulnerable",
  "prior_source_sha256": "7d95b1c77b372d62c3912eb6d352a14d748ef04f22aa5603bcc45df934baf05e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. OpenSSL 3.0 is installed at /usr/bin/openssl; capacity is 2..4096; uploaded basenames contain no slash or NUL. Files cannot be replaced during a preview."
}
```

### Split

```json
"held_out"
```

## v2-c-vulnerable-06 — A report template passes a customer caption to snprintf as the format

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `2a62b0f53812227fb3ce30a6ed4c4ac194382869eb635f7ef25e310594e4999f`. Protocol-2.0 case hash: `e386a009171d9546dcc2b75bdb278abb7f6f1c58f584fb8049f1d01ac087a4a5`.

A length-bounded caption can demand conversions incompatible with the single unsigned argument. snprintf limits writes to text, but cannot make an untrusted variadic format type-safe.

### src/receipt_caption.c

```c
#include <stdio.h>
#include <string.h>
int receipt_caption(FILE *out, const char *caption, unsigned invoice) {
    if (strlen(caption) > 96) return -1;
    char text[128];
    int required = snprintf(text, sizeof text, caption, invoice);
    if (required < 0 || (size_t)required >= sizeof text) return -1;
    if (fputs("Caption: ", out) == EOF) return -1;
    if (fputs(text, out) == EOF) return -1;
    if (fputc('\n', out) == EOF) return -1;
    return 0;
}
```

### Derivation

```json
{
  "group": "c-caption-format-type-confusion",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A product template/data mix-up with an existing integer argument tests format type safety rather than only a missing argument in logging. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "format-string",
    "cwe": "CWE-134",
    "path": "src/receipt_caption.c",
    "line_start": 6,
    "line_end": 6
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Uncontrolled formatting with an existing vararg; buffer length checks are present and should be retained.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render customer caption text literally and append the invoice number using a documented service-owned layout.",
  "trust_boundary": "An invoice customer controls the display caption, not a printf template; invoice is a service-generated unsigned identifier.",
  "legitimate_examples": [
    {
      "input": "Caption Paid in full, invoice 42",
      "expected": "Output Caption: Paid in full (#42) followed by newline."
    },
    {
      "input": "Caption 100% settled, invoice 9",
      "expected": "Output Caption: 100% settled (#9) followed by newline."
    }
  ],
  "permitted_changes": [
    "Separate caption data from the fixed invoice-number format.",
    "Preserve complete captions up to 96 bytes and the numeric invoice identifier."
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
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/printf.html",
    "https://pubs.opengroup.org/onlinepubs/9799919799/functions/popen.html"
  ]
}
```

### Regression traps

```json
[
  "A large snprintf destination does not prevent format-type confusion.",
  "Changing the caption to a constant destroys user content."
]
```

### Remediation constraints

```json
[
  "Separate caption data from the fixed invoice-number format.",
  "Preserve complete captions up to 96 bytes and the numeric invoice identifier."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-c-vulnerable-06",
  "prior_case_id": "c-formatted-copy-vulnerable",
  "prior_source_sha256": "700f6bafc85dfab372f7893a0ca14b49e2d6695ddc4feae1e1c5e9dd26ae4f78",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "ISO C17; POSIX.1-2008 interfaces where used",
  "libraries": [
    "glibc 2.39"
  ],
  "platform": "Linux x86-64",
  "setup": "Caller-supplied pointers are non-null and point to valid objects; text inputs are NUL terminated. Input bounds specifically stated in each contract are enforced by the described ingress. Ingress excludes newlines; the existing implementation mistakenly conflates customer captions with templates. The required literal-caption layout is the intended product behavior. The required layout is exactly Caption: <caption> (#<unsigned invoice>) followed by newline."
}
```

### Split

```json
"held_out"
```

