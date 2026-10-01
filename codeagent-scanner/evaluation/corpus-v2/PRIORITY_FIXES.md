# Corpus-v2 priority replacement briefs

These 58 slots inherit local clarification/revision questions from the AI technical review. All 204 slots still require independent new authoring. Nothing below is an authored or human-approved case.

## v2-cpp-safe-04 — cpp-buffer-format-safe

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

app.cpp:3 fixes the format and bounds the write when n is accurate. However, it can truncate input while the case constraints demand rendering the entire supplied text.

Replacement requirements:

- Show attacker control of formatting input and a meaningful output consumer. Define literal percent handling and, for bounded buffers, capacity and truncation/error behavior.
- Specify a sufficient-capacity precondition with caller evidence, expose and handle truncation, or revise the approved behavior contract.

Carry into the new operation/runtime specification:

- out is writable and value is valid untrusted NUL-terminated text.
- For the negative label, n must not exceed the actual out allocation and pointers must obey snprintf preconditions.

## v2-cpp-vulnerable-04 — cpp-buffer-format-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

app.cpp:2 has both caller-controlled format interpretation and no destination capacity. CWE-134 is valid but the supplied expected findings omit the separate unbounded-write concern.

Replacement requirements:

- Show attacker control of formatting input and a meaningful output consumer. Define literal percent handling and, for bounded buffers, capacity and truncation/error behavior.
- Add the relevant buffer-overflow expected finding or explicitly document multi-weakness scope, and include caller capacity context.
- Define dynamic output, safe rejection, or another approved capacity contract so a reviewer can assess fixes consistently.

Carry into the new operation/runtime specification:

- out is writable and value is valid untrusted NUL-terminated text.
- For the negative label, n must not exceed the actual out allocation and pointers must obey snprintf preconditions.

## v2-csharp-vulnerable-02 — csharp-shell-command-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

## v2-csharp-vulnerable-04 — csharp-state-formatter-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
- Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

## v2-fsharp-vulnerable-02 — fsharp-support-process-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

## v2-fsharp-vulnerable-04 — fsharp-binary-state-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
- Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

## v2-java-vulnerable-03 — java-session-restore-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.
- Describe potential dangerous deserialization under an explicit classpath/filter model; do not score an unproved specific execution consequence as established.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

## v2-kotlin-vulnerable-03 — kotlin-native-state-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

## v2-ruby-safe-04 — ruby-hostname-command-safe

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

app.rb:2 uses Ruby multi-argument system, so shell metacharacters are passed literally. GNU getent still parses options using argp_parse with default flags: a supplied name such as --help or --service=files can select an option rather than remain a hosts key. This is argument injection, not shell injection.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Pass an option terminator before the hostname according to the pinned getent contract and include a leading-dash counterexample; alternatively constrain input to a validated hostname grammar.

Carry into the new operation/runtime specification:

- The utility is GNU/glibc getent with ordinary GNU option parsing.
- name is an arbitrary caller-controlled string, including values beginning with a dash.

## v2-scala-vulnerable-03 — scala-job-state-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

## v2-swift-vulnerable-02 — swift-archive-import-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The deprecated convenience method decodes an archive without a caller-supplied expected-class restriction, supporting CWE-502 for untrusted archives. Actual consequences depend on available classes and the platform.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- State the legitimate archive root/object graph and compatibility/error expectations for this vulnerable case. Do not infer them from the independently evaluated NSString safe case.

Carry into the new operation/runtime specification:

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

## v2-swift-vulnerable-04 — swift-archive-file-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The deprecated convenience method decodes an archive without a caller-supplied expected-class restriction, supporting CWE-502 for untrusted archives. Actual consequences depend on available classes and the platform.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- State the legitimate archive root/object graph and compatibility/error expectations for this vulnerable case. Do not infer them from the independently evaluated NSString safe case.

Carry into the new operation/runtime specification:

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

## v2-swift-vulnerable-06 — swift-path-selection-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

Concatenating a name containing parent-directory components into /srv/docs/ produces an escaping file path, so CWE-22 is supported under the documented confinement intent. The proposed ID mapping is safe in principle but its legitimate input set is unspecified.

Replacement requirements:

- Define the intended file namespace, path/identifier contract, attacker-controlled components, symlink/write permissions and legitimate nested-file behavior.
- Define the intended public ID/filename contract and allowed documents for this vulnerable case, or permit containment validation that preserves authorized filenames. Do not infer the contract from an independently evaluated safe case.

Carry into the new operation/runtime specification:

- For the vulnerable case, name is attacker-controlled and reads must remain within /srv/docs.
- For the safe case, the document map and target filesystem paths are trusted and cannot be replaced by attacker-controlled symlinks.

## v2-visualbasic-vulnerable-02 — visualbasic-diagnostic-shell-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

## v2-visualbasic-vulnerable-04 — visualbasic-import-formatter-vulnerable

Prior AI verdict: **revise**. Status: planned, owner unassigned, human review pending.

The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
- Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

## v2-bash-vulnerable-01 — bash-user-expression-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.sh:4 evaluates caller text as a shell program. CWE-95 is supported only if a less-trusted caller crosses a boundary where such execution is not the authorized purpose.

Replacement requirements:

- Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.
- Define the legitimate operation/trust boundary and behavior-preserving alternatives; do not use the independent printf sibling as an automatic gold fix.

Carry into the new operation/runtime specification:

- The intended vulnerable application boundary must be defined; a script deliberately running its owner's commands is not automatically a privilege violation.
- The safe snippet's own operation is literal display, not an arithmetic interpreter.

## v2-c-safe-02 — c-archive-shell-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 passes the archive name as a separate execl argument. Shell syntax is not evaluated. Successful exec replaces the caller process, which must be intentional for this standalone example.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Declare that replacing the current process is intended, or provide a child-process caller if this is meant to model a returning helper.

Carry into the new operation/runtime specification:

- The archive filename is untrusted, but the executable and local archive access policy are trusted.
- The safe snippet targets a GNU-compatible tar at /usr/bin/tar.

## v2-c-safe-03 — c-bounded-copy-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 bounds writes to 16 bytes and terminates the result. Inputs longer than 15 bytes are silently truncated, and the result is never observed.

Replacement requirements:

- Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.
- Give the independent case an observable result and explicit overlength behavior; do not infer full data preservation from bounded writes.

Carry into the new operation/runtime specification:

- value is a valid NUL-terminated string with caller-controlled length.

## v2-c-safe-06 — c-formatted-copy-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 bounds the prefix and text to b capacity, eliminating that overwrite. It discards truncation information and the computed string.

Replacement requirements:

- Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.
- Specify whether truncation is acceptable and expose the relevant output/error behavior in the case.

Carry into the new operation/runtime specification:

- value is a valid untrusted NUL-terminated string; snprintf has conforming C99/POSIX behavior.

## v2-c-vulnerable-03 — c-bounded-copy-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 copies arbitrary-length input into out[16] without a bound, supporting CWE-120 for sufficiently long input. The local buffer is never consumed.

Replacement requirements:

- Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.
- Add a realistic consumer and state whether overlength input must be rejected, preserved dynamically, or intentionally truncated.

Carry into the new operation/runtime specification:

- value is a valid NUL-terminated string with caller-controlled length.

## v2-c-vulnerable-05 — c-popen-pipeline-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 inserts value into a cat command parsed by popen through a shell. The command buffer bound does not prevent CWE-78.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Supply the stream consumer/cleanup contract in the revised case so reviewers can assess any direct-file remediation without missing ownership regressions.

Carry into the new operation/runtime specification:

- The application is authorized to read the requested path; this case targets command interpretation, not an unspecified path-access boundary.
- Callers manage the returned stream with the matching API.

## v2-c-vulnerable-06 — c-formatted-copy-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.c:2 adds prefix: and unbounded caller text into b[24]; sufficiently long input overflows the local buffer. The format itself is constant, so CWE-120 is the relevant label.

Replacement requirements:

- Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.
- Provide a real label consumer and define size limits/error behavior before judging preserved functionality.

Carry into the new operation/runtime specification:

- value is a valid untrusted NUL-terminated string; snprintf has conforming C99/POSIX behavior.

## v2-cpp-safe-05 — cpp-query-pipeline-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.cpp:3 passes host as one argument to execl, avoiding shell parsing. The program becomes ping on success; no output stream is returned.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Declare an intentionally process-replacing negative example, or supply pipe/child/wait context for a returning API. Do not use this independent safe case as a gold fix.

Carry into the new operation/runtime specification:

- host is untrusted; the original function is intended to expose one ping operation to a stream consumer.
- The safe snippet requires a trusted /bin/ping implementation accepting the shown arguments including --.

## v2-cpp-vulnerable-03 — cpp-name-copy-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.cpp:2 copies caller text into out[32] with no bound. CWE-120 fits long input, but the copied name is never used.

Replacement requirements:

- Show actual destination capacity, input length and a consumer of the result. Define ownership, termination, growth/rejection/truncation and caller-visible behavior.
- Add a real consumer/result contract and define any allowed API migration.

Carry into the new operation/runtime specification:

- input is a valid untrusted NUL-terminated string.
- Ordinary allocation failure is outside this targeted buffer-overflow label.

## v2-csharp-safe-02 — csharp-shell-command-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

## v2-csharp-vulnerable-05 — csharp-integrity-alias-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.cs:2 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
- Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.

## v2-fsharp-safe-02 — fsharp-support-process-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

## v2-fsharp-safe-04 — fsharp-binary-state-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

This standalone case accepts a JSON stream and deserializes a string array without polymorphic object construction. The different format and result type from the BinaryFormatter sibling are not defects in this independent safe scenario. Its own bounded-schema constraint still requires explicit resource limits or a documented upstream bound.

Replacement requirements:

- Declare the accepted schema/types, source of serialized input, reachable deserialization runtime and migration/compatibility contract; raw text is not automatically a schema-preserving replacement.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- State the trusted upstream byte limit or include explicit bounded input/collection checks in a revised case. Avoid crediting an unbounded replacement as meeting the bounded-schema rubric.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The standalone API intentionally accepts JSON string-array input.
- The caller supplies an explicit input-size bound; custom unsafe converters are absent.

## v2-fsharp-vulnerable-05 — fsharp-digest-scope-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.fs:4 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label. The local use binding has normal lexical lifetime; the safe file's misleading MD5 string is documentation data and must not be treated as a call.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
- Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.

## v2-go-safe-01 — go-order-query-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.go:3 separates customer from the query text using a positional argument. This is injection-safe with a compatible driver, but the generic database/sql type does not establish that $1 is its placeholder syntax.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Declare the driver/database and schema; preserve the same database in the positive and negative cases.

Carry into the new operation/runtime specification:

- customer is untrusted; the database connection and orders table are initialized by trusted code.

## v2-go-safe-06 — go-checksum-authentication-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.go:3 uses SHA-256 and the correct 32-byte return size. This removes the MD5 weakness, but an unkeyed digest is not by itself message authentication despite the scenario name.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Define the intended verification property and caller protocol; keep a weak-digest negative label scoped to that property.

Carry into the new operation/runtime specification:

- No caller or expected-digest storage is supplied.
- Digest changes necessarily change output bytes; approved compatibility may include migrating digest consumers and stored values.

## v2-go-vulnerable-03 — go-url-fetcher-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.go:3 sends the request-selected url to http.Get, allowing the requester to choose an outbound destination. CWE-918 fits a server that can reach resources unavailable to that requester.

Replacement requirements:

- Define permitted destinations and the user-visible fetch contract, including DNS, redirects, ports/schemes and trust in destination configuration.
- State the allowed destination/input and expected response contract so a reviewer can distinguish security restrictions from deleting supported behavior.

Carry into the new operation/runtime specification:

- The vulnerable helper runs in a server-side request context with privileged network reachability.
- The safe destination, proxy settings, DNS administration and trust roots are controlled by the operator.

## v2-go-vulnerable-06 — go-checksum-authentication-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.go:3 uses MD5, a collision-broken digest, but the source contains no comparison, authenticated reference or security-sensitive consumer. A weak-algorithm observation is supported; exploitability is conditional.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- State whether this is collision-resistant content verification against a trusted reference, authentication, or a nonsecurity checksum; include the consumer and permitted migration.

Carry into the new operation/runtime specification:

- No caller or expected-digest storage is supplied.
- Digest changes necessarily change output bytes; approved compatibility may include migrating digest consumers and stored values.

## v2-java-vulnerable-04 — java-legacy-digest-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

## v2-java-vulnerable-06 — java-hostname-check-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

Replacement requirements:

- Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.
- Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

## v2-javascript-safe-05 — javascript-account-lookup-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.js:1 passes req.query.email as a ? replacement, which can safely represent a scalar string in a declared compatible driver. It is not universally a prepared statement: mysqljs query performs client-side escaping by value shape, and an object such as {email:1} can expand the predicate to email=`email`=1. No scalar check or specific driver is present.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Name the exact driver and require a scalar string or use a real prepared/execute API with documented parameter semantics. Include nested-query input as a counterexample in the revised corpus.

Carry into the new operation/runtime specification:

- The safe label currently depends on an unstated database driver and a guarantee that email is a scalar string.
- The endpoint uses a query parser whose structured-value behavior must be pinned.

## v2-javascript-vulnerable-04 — javascript-calculator-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.js:1 evaluates req.body.expression as JavaScript, supporting CWE-95. This case asks for explicit numeric conversion while preserving supported numeric computation, but does not say whether legitimate inputs include arithmetic expressions such as 1+2 or only number literals. That case-local ambiguity can lead independent proposal reviewers to disagree about rejecting ordinary expressions.

Replacement requirements:

- Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.
- Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

Carry into the new operation/runtime specification:

- The request field is an attacker-controlled string.
- The intended numeric grammar and operation have not been specified.

## v2-javascript-vulnerable-05 — javascript-account-lookup-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.js:1 concatenates caller email into a quoted SQL literal; a real SQL driver receives attacker-controlled syntax and CWE-89 fits. The db parameter is untyped and unconfigured, leaving placeholder syntax, return shape and the valid remediation API undecided.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Declare a specific driver/version, SQL mode, query-input type and result contract so that reviewers can evaluate actual parameter binding.

Carry into the new operation/runtime specification:

- lookup() is called with attacker-controlled email and a real database client.
- The accounts table and id/email columns exist.

## v2-kotlin-vulnerable-04 — kotlin-digest-choice-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

## v2-kotlin-vulnerable-06 — kotlin-host-verifier-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

Replacement requirements:

- Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.
- Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

## v2-php-vulnerable-05 — php-dynamic-plugin-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.php:2 evaluates supplied PHP code and returns its result, supporting CWE-95. This case asks for the intended string transformation without identifying that transformation, permitted operations, or normal input/output examples. The vulnerability label is sound; the legitimate replacement behavior needs definition within this case before proposals can be reviewed consistently.

Replacement requirements:

- Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.
- Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

Carry into the new operation/runtime specification:

- source is attacker-controlled.
- The proposed intended string transformation has not been defined in the vulnerable program.

## v2-python-safe-01 — python-catalog-filter-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.py:4-5 passes name as the single bound value of a ? placeholder, preserving quotes and Unicode as data. This is the correct SQLite API. db.py:1-2 creates an empty in-memory database, so the example still requires a declared products-table initialization step to represent a functioning lookup.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Document fixture setup and expected schema/data, or include initialization in a new corpus version; do not count startup errors as security success.

Carry into the new operation/runtime specification:

- A Flask request context invokes search().
- The same connection has an initialized products(name) table before search(), and remains on an allowed SQLite thread.

## v2-python-vulnerable-01 — python-catalog-filter-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.py:4-5 carries the Flask query value directly into a quoted SQLite SQL expression; no binding or escaping occurs. CWE-89 fits if products exists. db.py:1-2 explicitly opens a fresh in-memory database but never initializes that table, so reachability of a successful query needs a declared setup contract.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Document fixture setup and expected schema/data, or include initialization in a new corpus version; do not count startup errors as security success.

Carry into the new operation/runtime specification:

- A Flask request context invokes search().
- The same connection has an initialized products(name) table before search(), and remains on an allowed SQLite thread.

## v2-ruby-vulnerable-05 — ruby-stored-expression-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.rb:2 evaluates untrusted expression text as Ruby source, supporting CWE-95. The instruction to use numeric parsing for the intended numeric operation leaves the allowed expression grammar and output contract unstated. Human reviewers need that case-local distinction to decide whether a proposed restricted parser preserves legitimate use.

Replacement requirements:

- Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.
- Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

Carry into the new operation/runtime specification:

- expression is attacker-controlled text.
- The intended numeric operation and accepted syntax have not been stated.

## v2-rust-safe-01 — rust-account-sqlx-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.rs:1 keeps the statement literal and binds name as data. Quoted and Unicode values remain values. The safe implementation still discards rows, matching the shown function but leaving the account-lookup contract underspecified.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Specify SQLx 0.8.x/PostgreSQL runtime features and whether executing versus returning the lookup is intended. Add a small caller/result contract in a revised corpus; preserve the same contract in both variants.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The caller supplies untrusted name; the provided PgPool is usable against a users table.
- A compatible SQLx version and PostgreSQL async runtime/features are present; no repository code was compiled or executed.

## v2-rust-vulnerable-01 — rust-account-sqlx-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.rs:1 interpolates name inside a quoted SQL literal before preparing/executing it. Single-statement preparation does not prevent predicate injection; no returned rows does not remove timing/error or query-structure impact.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Specify SQLx 0.8.x/PostgreSQL runtime features and whether executing versus returning the lookup is intended. Add a small caller/result contract in a revised corpus; preserve the same contract in both variants.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The caller supplies untrusted name; the provided PgPool is usable against a users table.
- A compatible SQLx version and PostgreSQL async runtime/features are present; no repository code was compiled or executed.

## v2-rust-vulnerable-06 — rust-artifact-file-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.rs:1 joins an unchecked name and reads it. Absolute paths replace the base and traversal reaches parent directories. Its own remediation constraints demand fixed public-name mappings while preserving the operation, but do not define which legitimate artifact names must remain accepted.

Replacement requirements:

- Define the intended file namespace, path/identifier contract, attacker-controlled components, symlink/write permissions and legitimate nested-file behavior.
- Record the accepted public identifiers, permitted files and any allowed API migration in this vulnerable case. Do not use the separately submitted safe sibling as a gold fix.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The operating system supplies Unix-style /srv paths and the service can read files outside the artifact directory.
- For the safe mapping, report.json and its parent directories cannot be replaced by an attacker-controlled symlink.

## v2-scala-vulnerable-04 — scala-integrity-hash-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

## v2-scala-vulnerable-06 — scala-tls-hostnames-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

Replacement requirements:

- Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.
- Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.

Carry into the new operation/runtime specification:

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

## v2-swift-vulnerable-01 — swift-server-trust-policy-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

DisabledTrustEvaluator deliberately skips Alamofire evaluation, so its use is a valid policy concern. However this snippet neither installs the manager into a Session nor establishes whether ATS allows trust relaxation for the target domain.

Replacement requirements:

- Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.
- Pin the intended Darwin/Alamofire configuration, show Session use and record relevant ATS/domain exceptions, or limit the expected claim to an unsafe inactive policy. Do not weaken TLS settings merely to make a benchmark appear vulnerable.

Carry into the new operation/runtime specification:

- Alamofire 5 is available on a Darwin Foundation target.
- The manager is passed to the Session making requests to api.example.org; a standalone unused manager has no network effect.

## v2-swift-vulnerable-03 — swift-session-challenge-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The helper supplies a trust credential without evaluating trust. Its actual bypass potential depends on domain ATS policy; the unconditional force unwrap also assumes every forwarded challenge is a server-trust challenge.

Replacement requirements:

- Show the real client/transport wiring and platform trust policy, distinguish peer/hostname checks, and state the legitimate endpoints and certificate/trust-store behavior.
- Document target platform, domain policy and delegation. Keep the finding as an unsafe manual-authentication pattern unless evidence establishes the claimed bypass.
- Specify that the caller filters server-trust challenges, or add the guard/default handling in the scenario and include the associated behavior constraint.

Carry into the new operation/runtime specification:

- A URLSessionDelegate forwards actual authentication challenges to this helper on Darwin.
- The URLSession and URLSessionTask ownership/lifetimes are outside this small helper.

## v2-typescript-safe-01 — typescript-backup-process-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.ts:2 uses execFile with a separate destination and --, removing shell interpretation. Whether -- protects options and still performs a backup depends on the undefined backup-tool interface.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Document the trusted utility contract and representative valid destination/output, or use an actual pinned utility with those semantics.

Carry into the new operation/runtime specification:

- A Node.js application invokes backup() with an untrusted string destination.
- backup-tool is intended to be a trusted installed executable with a declared command-line interface.

## v2-typescript-safe-05 — typescript-invoice-lookup-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.ts:1 uses a $1 parameter and separate values, which is valid and safe for node-postgres. db:any does not establish that this is the actual driver; MySQL-style clients do not use that placeholder contract.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Declare the concrete client and version so a valid fix cannot be rejected or a nonfunctional placeholder accepted.

Carry into the new operation/runtime specification:

- reference is untrusted even though TypeScript annotates it as string.
- The intended database client is node-postgres or another explicitly declared $1-binding API, and invoices(total,ref) exists.

## v2-typescript-vulnerable-01 — typescript-backup-process-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.ts:2 interpolates destination into child_process.exec, whose shell interpretation supports CWE-78.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Document the trusted utility contract and representative valid destination/output, or use an actual pinned utility with those semantics.

Carry into the new operation/runtime specification:

- A Node.js application invokes backup() with an untrusted string destination.
- backup-tool is intended to be a trusted installed executable with a declared command-line interface.

## v2-typescript-vulnerable-04 — typescript-formula-parser-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.ts:1 constructs and executes a Function from the supplied text, supporting CWE-95. The same case asks for numeric conversion while preserving supported numeric computation, but does not define whether a formula such as 1+2 must remain supported. The missing legitimate-input boundary is relevant to human review of proposals for this case itself.

Replacement requirements:

- Define the legitimate expression or transformation grammar, supported inputs and outputs, and the interpreter trust boundary; printing input is not automatically an equivalent operation.
- Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

Carry into the new operation/runtime specification:

- The string argument crosses an untrusted-input boundary.
- The acceptable formula grammar and arithmetic operation are currently unspecified.

## v2-typescript-vulnerable-05 — typescript-invoice-lookup-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.ts:1 inserts reference into a quoted SQL template with no binding, supporting CWE-89 when the caller is untrusted.

Replacement requirements:

- Define an initialized schema, concrete database driver and binding semantics, an untrusted value's path into the query, and legitimate quoted/Unicode values with exact expected rows.
- Declare the concrete client and version so a valid fix cannot be rejected or a nonfunctional placeholder accepted.

Carry into the new operation/runtime specification:

- reference is untrusted even though TypeScript annotates it as string.
- The intended database client is node-postgres or another explicitly declared $1-binding API, and invoices(total,ref) exists.

## v2-visualbasic-safe-02 — visualbasic-diagnostic-shell-safe

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

Replacement requirements:

- Define the legitimate operation and allowed arguments; include caller-visible output, error, exit-status and process/stream lifecycle requirements as relevant.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

## v2-visualbasic-vulnerable-05 — visualbasic-digest-import-vulnerable

Prior AI verdict: **needs_clarification**. Status: planned, owner unassigned, human review pending.

app.vb:4 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label.

Replacement requirements:

- Show the security-sensitive consumer and adversary model, distinguish integrity from authentication, and define output-format/storage/protocol migration constraints.
- Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
- Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
- Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

Carry into the new operation/runtime specification:

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.
