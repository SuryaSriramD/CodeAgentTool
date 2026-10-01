# kotlin — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-kotlin-safe-01 — event-audit-batched-bound-values

Proposed label: **safe**. Human review: **pending**.

Source hash: `70294c81d63efbdaa0499017ae48e352ab0efa84d28bb55ecb4746382a5ca193`. Protocol-2.0 case hash: `a8bf721685ff86936a598b7d9c69469c09fe8f6d2b2406278a6fb3b30dd341cf`.

SQL-looking words and quotes are values in a prepared batch. A list of messages does not become a list of SQL fragments.

### AuditBatch.kt

```kotlin
import java.sql.Connection
class AuditBatch(private val db: Connection) {
    fun record(messages: List<String>): IntArray {
        require(messages.size <= 100)
        require(messages.all { it.length <= 2048 })
        db.prepareStatement("INSERT INTO audit_events(message) VALUES (?)").use { statement ->
            messages.forEach { message ->
                statement.setString(1, message)
                statement.addBatch()
            }
            return statement.executeBatch()
        }
    }
}
```

### Derivation

```json
{
  "group": "event-audit-batched-bound-values",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around persist each bounded audit message literally and return batch update counts. Boundary: Untrusted message strings are bound as data for every batch entry. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The text may be rendered only with output escaping by consumers; this storage function does not claim to sanitize future HTML."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Persist each bounded audit message literally and return batch update counts.",
  "trust_boundary": "Untrusted message strings are bound as data for every batch entry.",
  "legitimate_examples": [
    {
      "input": "[can't open, SELECT * FROM users]",
      "expected": "Two unchanged message rows"
    },
    {
      "input": "Empty list",
      "expected": "No inserts and empty update-count array"
    }
  ],
  "permitted_changes": [
    "Retain one bound value per row and batch result ordering."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not escape or truncate text unnecessarily or combine messages into one row."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/PreparedStatement.html"
  ]
}
```

### Regression traps

```json
[
  "Do not escape or truncate text unnecessarily or combine messages into one row."
]
```

### Remediation constraints

```json
[
  "Persist each bounded audit message literally and return batch update counts.",
  "Retain one bound value per row and batch result ordering.",
  "Do not escape or truncate text unnecessarily or combine messages into one row."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-01",
  "prior_case_id": "kotlin-invoice-jdbc-safe",
  "prior_source_sha256": "d00c22ec7199e665415f7914be43da215589d192677e1cf86f644f58d1ff20a3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "PostgreSQL16 and JDBC42.7.4; audit_events(message text). Connection uses a trusted insert-only role; messages are arbitrary display text, and no downstream SQL/shell interprets them."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-safe-02 — webhook-hmac-envelope-consumer

Proposed label: **safe**. Human review: **pending**.

Source hash: `5e83d4db76f0ce1d32cf19750bab14b0a3ef959d76f88e34455df0513f79923a`. Protocol-2.0 case hash: `02090896fcff814cb8ff2b6347c624de2c6f0aef1bf9e9e8c5475bf184e874e6`.

A keyed SHA-256 MAC, exact-byte comparison and a fail-closed consumer preserve authentication. An unkeyed checksum is not substituted for a MAC.

### WebhookAuthenticator.kt

```kotlin
import javax.crypto.Mac
import javax.crypto.SecretKey
import java.security.MessageDigest
class WebhookAuthenticator(private val secret: SecretKey) {
    fun accept(body: ByteArray, suppliedTag: ByteArray): ByteArray {
        require(body.size <= 65536 && suppliedTag.size == 32)
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(secret)
        val expected = mac.doFinal(body)
        require(MessageDigest.isEqual(expected, suppliedTag)) { "invalid signature" }
        return body.copyOf()
    }
}
```

### Derivation

```json
{
  "group": "webhook-hmac-envelope-consumer",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around authenticate exact webhook bytes before exposing them to the event decoder. Boundary: Remote senders control body and tag but not the configured HMAC key. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Replay defense is an explicit downstream protocol prerequisite, not falsely attributed to HMAC alone."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authenticate exact webhook bytes before exposing them to the event decoder.",
  "trust_boundary": "Remote senders control body and tag but not the configured HMAC key.",
  "legitimate_examples": [
    {
      "input": "Valid tag over UTF-8 body",
      "expected": "Returns identical body bytes"
    },
    {
      "input": "Same tag with one changed body byte",
      "expected": "Rejects before decoder"
    }
  ],
  "permitted_changes": [
    "Keep key from trusted configuration and authenticate the bytes actually consumed."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not parse/reserialize before checking the tag or accept requests on crypto exceptions."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/Mac.html"
  ]
}
```

### Regression traps

```json
[
  "Do not parse/reserialize before checking the tag or accept requests on crypto exceptions."
]
```

### Remediation constraints

```json
[
  "Authenticate exact webhook bytes before exposing them to the event decoder.",
  "Keep key from trusted configuration and authenticate the bytes actually consumed.",
  "Do not parse/reserialize before checking the tag or accept requests on crypto exceptions."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-02",
  "prior_case_id": "kotlin-xml-dom-safe",
  "prior_source_sha256": "61f5923337b627995d85280a1bca665ee4586b13f0a35071875b498aac11f583",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "A 256-bit random HMAC key is provided from server configuration, never from the request. Replay IDs/timestamps are checked by the event consumer after authentication; only authenticated bytes are passed onward."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-safe-03 — fixed-format-telemetry-binary-reader

Proposed label: **safe**. Human review: **pending**.

Source hash: `4aa27ae92443fc7a396ce29a80371b3a347b3fde8e79343733799a8a97907e40`. Protocol-2.0 case hash: `aea3d20590e12dd81f5810082d9d39cd7b2a25817baf4de594c34d20642ec451`.

DataInputStream reads only explicitly selected primitives. Count and exact packet size are checked before list allocation; no arbitrary object deserialization occurs despite binary input.

### TelemetryReader.kt

```kotlin
import java.io.ByteArrayInputStream
import java.io.DataInputStream
object TelemetryReader {
    fun temperatures(packet: ByteArray): List<Short> {
        require(packet.size in 2..514)
        DataInputStream(ByteArrayInputStream(packet)).use { input ->
            val count = input.readUnsignedShort()
            require(count <= 256 && packet.size == 2 + count * 2)
            return List(count) { input.readShort() }
        }
    }
}
```

### Derivation

```json
{
  "group": "fixed-format-telemetry-binary-reader",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around decode a bounded counted temperature packet with signed values. Boundary: Bytes cross the network boundary into a fixed primitive reader without class metadata or object activation. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Sensor authenticity is outside this public display protocol; values do not authorize actions."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Decode a bounded counted temperature packet with signed values.",
  "trust_boundary": "Bytes cross the network boundary into a fixed primitive reader without class metadata or object activation.",
  "legitimate_examples": [
    {
      "input": "Count 2 followed by -125 and 2034",
      "expected": [
        -125,
        2034
      ]
    },
    {
      "input": "Count 0, no extra bytes",
      "expected": []
    }
  ],
  "permitted_changes": [
    "Retain exact length checks and signed temperature interpretation."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace signed values with unsigned values or silently ignore trailing bytes."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/DataInputStream.html"
  ]
}
```

### Regression traps

```json
[
  "Do not replace signed values with unsigned values or silently ignore trailing bytes."
]
```

### Remediation constraints

```json
[
  "Decode a bounded counted temperature packet with signed values.",
  "Retain exact length checks and signed temperature interpretation.",
  "Do not replace signed values with unsigned values or silently ignore trailing bytes."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-03",
  "prior_case_id": "kotlin-native-state-safe",
  "prior_source_sha256": "4434a7e165505b4aa2d0b3a91d2455770f5cdfeafa58e80c48ee2b8b837995f7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "Big-endian wire format: unsigned 16-bit count followed by that many signed 16-bit centidegrees. Public sensor packets are untrusted; parsed values are displayed as measurements, not security decisions."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-safe-04 — nonsecurity-cache-display-md5

Proposed label: **safe**. Human review: **pending**.

Source hash: `f38dac66ea730adf0878666faccf08ab4334a3fe9fecc94be1f9543278920174`. Protocol-2.0 case hash: `52bb1abb7fe5f4205c2633f47f7d1b8d9509ae5123c5b4c9e8559bc49fb8bc94`.

The use of MD5 does not protect passwords, integrity or authenticity; the consumer only decorates a public preview. The separate download path returns its actual argument and never resolves by badge.

### CacheBadge.kt

```kotlin
import java.security.MessageDigest
import java.util.HexFormat
object CacheBadge {
    fun displayId(publicThumbnail: ByteArray): String {
        require(publicThumbnail.size <= 65536)
        val digest = MessageDigest.getInstance("MD5").digest(publicThumbnail)
        return HexFormat.of().formatHex(digest).take(8)
    }
}
```

### GalleryCell.kt

```kotlin
class GalleryCell {
    fun caption(publicBytes: ByteArray): String = "Preview #" + CacheBadge.displayId(publicBytes)
    fun bytesForDownload(originalBytes: ByteArray): ByteArray = originalBytes.copyOf()
}
```

### Derivation

```json
{
  "group": "nonsecurity-cache-display-md5",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around display a short deterministic cosmetic badge for a public thumbnail. Boundary: Untrusted thumbnail bytes affect only a label; no security-sensitive consumer trusts digest uniqueness. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Collision resistance is not a requirement of this operation; dependency/runtime vulnerabilities are not part of the source label."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Display a short deterministic cosmetic badge for a public thumbnail.",
  "trust_boundary": "Untrusted thumbnail bytes affect only a label; no security-sensitive consumer trusts digest uniqueness.",
  "legitimate_examples": [
    {
      "input": "Same public image bytes twice",
      "expected": "Same 8-character badge"
    },
    {
      "input": "Two colliding badges",
      "expected": "Both thumbnails remain independently downloadable"
    }
  ],
  "permitted_changes": [
    "Keep the label explicitly non-authoritative; algorithm changes may update cosmetic badges."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not start using the truncated badge as an authorization token or unique storage identity."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/security/MessageDigest.html"
  ]
}
```

### Regression traps

```json
[
  "Do not start using the truncated badge as an authorization token or unique storage identity."
]
```

### Remediation constraints

```json
[
  "Display a short deterministic cosmetic badge for a public thumbnail.",
  "Keep the label explicitly non-authoritative; algorithm changes may update cosmetic badges.",
  "Do not start using the truncated badge as an authorization token or unique storage identity."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-04",
  "prior_case_id": "kotlin-digest-choice-safe",
  "prior_source_sha256": "064293eae65a1883f73d6c6a2b6f0a7c9b036806d974678bb49c59cbd978f290",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "The short badge is explicitly cosmetic and may collide. Storage identity, downloads, signatures, access control and cache lookup do not use it. Thumbnails are public and size-bounded."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-safe-05 — line-locator-literal-grep-pattern

Proposed label: **safe**. Human review: **pending**.

Source hash: `b56c3d38a385f1032a739468dd6d324b062825d42639c887e6a36cbf729aaa16`. Protocol-2.0 case hash: `ce5bded18519f18fb1d92e1bf37e9a3fdcb93be8581fe4a5854cfc59e3b8ee14`.

No shell executes the pattern; -F and -- also prevent regex and option interpretation. Output and child status have a visible consumer contract.

### LineLocator.kt

```kotlin
import java.nio.charset.StandardCharsets
class LineLocator {
    fun locate(pattern: String): Pair<Int, String> {
        require(pattern.length <= 80 && !pattern.contains('\n') && !pattern.contains('\u0000'))
        val process = ProcessBuilder("/usr/bin/grep", "-n", "-F", "--", pattern, "/srv/public/manual.txt")
            .redirectError(ProcessBuilder.Redirect.DISCARD).start()
        val output = process.inputStream.use { String(it.readAllBytes(), StandardCharsets.UTF_8) }
        return process.waitFor() to output
    }
}
```

### Derivation

```json
{
  "group": "line-locator-literal-grep-pattern",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around find literal single-line text in the public manual with line numbers. Boundary: Untrusted text occupies one grep argument after option termination and fixed-string selection. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Bounded public manual prevents unbounded output; trusted filesystem excludes attacker replacement of executable or manual."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Find literal single-line text in the public manual with line numbers.",
  "trust_boundary": "Untrusted text occupies one grep argument after option termination and fixed-string selection.",
  "legitimate_examples": [
    {
      "input": "pattern=-v",
      "expected": "Find literal -v, not an option"
    },
    {
      "input": "pattern=a.*b",
      "expected": "Find literal punctuation, not a regular expression"
    }
  ],
  "permitted_changes": [
    "Preserve literal matching, option termination and exit-code distinctions."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not switch to regular expressions or report a no-match exit as success with arbitrary lines."
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
    "https://www.gnu.org/software/grep/manual/grep.html"
  ]
}
```

### Regression traps

```json
[
  "Do not switch to regular expressions or report a no-match exit as success with arbitrary lines."
]
```

### Remediation constraints

```json
[
  "Find literal single-line text in the public manual with line numbers.",
  "Preserve literal matching, option termination and exit-code distinctions.",
  "Do not switch to regular expressions or report a no-match exit as success with arbitrary lines."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-05",
  "prior_case_id": "kotlin-maintenance-shell-safe",
  "prior_source_sha256": "b60747fded701a5c01b5f8cb90eddf138b2c6ea74d30c5d7182b14ec2de6f2f6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "GNU grep3.11 on Linux; immutable bounded public manual, trusted absolute executable path. grep exit1 means no match and is retained rather than treated as a crash."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-safe-06 — calendar-xml-text-writer

Proposed label: **safe**. Human review: **pending**.

Source hash: `d221b78e45f259815ed5cd7b510699722156a7330498341452fbccea896ca5b6`. Protocol-2.0 case hash: `c426d0cc3e62a2757263472c06262cb1c055f06e2f79be131303b82cfc7e8a73`.

The standard writer escapes markup-significant characters as text. Strings that resemble XML attack syntax do not change the document structure.

### CalendarXml.kt

```kotlin
import java.io.StringWriter
import javax.xml.stream.XMLOutputFactory
object CalendarXml {
    fun event(title: String): String {
        require(title.length <= 200)
        val output = StringWriter()
        val writer = XMLOutputFactory.newFactory().createXMLStreamWriter(output)
        writer.writeStartDocument("UTF-8", "1.0")
        writer.writeStartElement("event")
        writer.writeStartElement("title")
        writer.writeCharacters(title)
        writer.writeEndElement()
        writer.writeEndElement()
        writer.writeEndDocument()
        writer.close()
        return output.toString()
    }
}
```

### Derivation

```json
{
  "group": "calendar-xml-text-writer",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around encode a calendar title as text in one xml event element. Boundary: Untrusted title reaches XMLStreamWriter.writeCharacters rather than markup concatenation. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Invalid XML character policy is enforced at the documented edge; ordinary Unicode is preserved."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Encode a calendar title as text in one XML event element.",
  "trust_boundary": "Untrusted title reaches XMLStreamWriter.writeCharacters rather than markup concatenation.",
  "legitimate_examples": [
    {
      "input": "R&D <planning>",
      "expected": "One title text node containing R&D <planning>"
    },
    {
      "input": "A title containing <!DOCTYPE",
      "expected": "Literal title text, not a declaration"
    }
  ],
  "permitted_changes": [
    "Retain a text node and valid XML escaping."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not pre-escape and double-encode titles or reinterpret title text as an XML fragment."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.xml/javax/xml/stream/XMLStreamWriter.html"
  ]
}
```

### Regression traps

```json
[
  "Do not pre-escape and double-encode titles or reinterpret title text as an XML fragment."
]
```

### Remediation constraints

```json
[
  "Encode a calendar title as text in one XML event element.",
  "Retain a text node and valid XML escaping.",
  "Do not pre-escape and double-encode titles or reinterpret title text as an XML fragment."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-safe-06",
  "prior_case_id": "kotlin-host-verifier-safe",
  "prior_source_sha256": "cd0d872c73c7062ebe2ca262c1ca7c1551c4fd5d23de13c226d54065c062331a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "Titles contain valid XML1.0 Unicode characters; HTTP edge rejects invalid control characters. Output is served as application/xml, not HTML. No parser or stylesheet is invoked."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-01 — expense-dashboard-exposed-status-filter

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c3da320f5311c0c064749a866d4f7a43bea0382729050c6eed7202a99d781bf2`. Protocol-2.0 case hash: `8ee88c7e910ce100949aab3431d668a02743968502bfcb8d05a14deacfe3c1c7`.

The raw exec API receives interpolated SQL syntax. A transaction and a read-only database account do not preserve intended row filtering.

### ExpenseReport.kt

```kotlin
import org.jetbrains.exposed.sql.transactions.transaction
import java.math.BigDecimal
class ExpenseReport {
    fun total(statusFromForm: String): BigDecimal = transaction {
        var result = BigDecimal.ZERO
        val query = "SELECT COALESCE(sum(amount),0) FROM expenses WHERE status = '$statusFromForm'"
        exec(query) { rows -> if (rows.next()) result = rows.getBigDecimal(1) }
        result
    }
}
```

### ReportController.kt

```kotlin
class ReportController(private val report: ExpenseReport) {
    fun show(parameters: Map<String, String>): String {
        val status = parameters["status"] ?: "submitted"
        require(status.length <= 40)
        return report.total(status).toPlainString()
    }
}
```

### Derivation

```json
{
  "group": "expense-dashboard-exposed-status-filter",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around calculate the decimal total of expenses having an exact workflow status. Boundary: An authenticated employee controls a report filter inserted into Exposed raw SQL. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "ExpenseReport.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Organization isolation is database-enforced; the expected injection affects permitted report rows, not cross-tenant authorization."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Calculate the decimal total of expenses having an exact workflow status.",
  "trust_boundary": "An authenticated employee controls a report filter inserted into Exposed raw SQL.",
  "legitimate_examples": [
    {
      "input": "status=awaiting manager",
      "expected": "Exact decimal total for awaiting manager"
    },
    {
      "input": "status=director's review",
      "expected": "Apostrophe-containing custom status works"
    }
  ],
  "permitted_changes": [
    "Use Exposed typed expressions or supported bound arguments without converting decimal amounts to floating point."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not restrict legitimate organization-defined status labels or round the total to an integer."
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
    "https://www.jetbrains.com/help/exposed/working-with-sql-strings.html"
  ]
}
```

### Regression traps

```json
[
  "Do not restrict legitimate organization-defined status labels or round the total to an integer."
]
```

### Remediation constraints

```json
[
  "Calculate the decimal total of expenses having an exact workflow status.",
  "Use Exposed typed expressions or supported bound arguments without converting decimal amounts to floating point.",
  "Do not restrict legitimate organization-defined status labels or round the total to an integer."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-01",
  "prior_case_id": "kotlin-invoice-jdbc-vulnerable",
  "prior_source_sha256": "a00547465c4ab146a51c1f80bbb0b10ec921c638eba37209a405961485de2cae",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "Exposed 0.55.0 initialized with PostgreSQL JDBC 42.7.4 and PostgreSQL16. expenses(status text,amount numeric); read-only reporting role can view this organization only."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-02 — payroll-sax-worker-name-preview

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `96084134fa93c786cc4b8430d825bbc2509d84d6c2932b0dc055e1c67cea6512`. Protocol-2.0 case hash: `d03e23d91d0c1e0a0bf02a0d550bb1be433e83f78b70c907737a357053ed41c0`.

General/parameter external entities and external DTD protocols are enabled before parsing. SAX character callbacks expose resolved external content to the preview consumer.

### PayrollPreview.kt

```kotlin
import javax.xml.parsers.SAXParserFactory
import javax.xml.XMLConstants
import org.xml.sax.helpers.DefaultHandler
import java.io.ByteArrayInputStream
object PayrollPreview {
    fun preview(bytes: ByteArray): String {
        require(bytes.size <= 32768)
        val factory = SAXParserFactory.newInstance()
        factory.setFeature("http://xml.org/sax/features/external-general-entities", true)
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", true)
        val parser = factory.newSAXParser()
        parser.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "all")
        val text = StringBuilder()
        parser.parse(ByteArrayInputStream(bytes), object : DefaultHandler() {
            override fun characters(chars: CharArray, start: Int, length: Int) {
                text.append(chars, start, length)
            }
        })
        return text.toString()
    }
}
```

### Derivation

```json
{
  "group": "payroll-sax-worker-name-preview",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around show text content from a payroll xml upload before accepting its rows. Boundary: A payroll partner controls XML declarations and entities consumed by an explicitly permissive SAX parser. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "PayrollPreview.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Byte limits do not bound external-resource reads. Internal expansion/depth must also be addressed by a repaired parser policy."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Show text content from a payroll XML upload before accepting its rows.",
  "trust_boundary": "A payroll partner controls XML declarations and entities consumed by an explicitly permissive SAX parser.",
  "legitimate_examples": [
    {
      "input": "<payroll><name>Zoë</name></payroll>",
      "expected": "Zoë"
    },
    {
      "input": "<payroll><name>A&amp;B</name></payroll>",
      "expected": "A&B"
    }
  ],
  "permitted_changes": [
    "Reject external entities and DTD use while preserving ordinary XML text extraction."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not treat the upload as plain UTF-8 text; entity-decoded names and document text are required."
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
    "https://docs.oracle.com/en/java/javase/21/security/java-api-xml-processing-jaxp-security-guide.html"
  ]
}
```

### Regression traps

```json
[
  "Do not treat the upload as plain UTF-8 text; entity-decoded names and document text are required."
]
```

### Remediation constraints

```json
[
  "Show text content from a payroll XML upload before accepting its rows.",
  "Reject external entities and DTD use while preserving ordinary XML text extraction.",
  "Do not treat the upload as plain UTF-8 text; entity-decoded names and document text are required."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-02",
  "prior_case_id": "kotlin-xml-dom-vulnerable",
  "prior_source_sha256": "be498e4a38de7b6e22208003452ca69627b6581061ab43971d7649c9864b71e9",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "JDK SAX implementation, no external JAXP overrides. An authenticated outsourced payroll processor submits the XML; returned text is shown to that processor. Application files are not otherwise accessible to it."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-03 — device-provisioning-okhttp-hostname-policy

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `1a6fd91ed8d8c9b75d9a857af63c1f6d485e5144488afaa2b892c53abf7cb7b8`. Protocol-2.0 case hash: `e07f5747ef414d7c49cba734023923e44b362c2611c0191a1b4400b02471e774`.

An always-true hostname verifier accepts an unrelated valid certificate. The fixed URL and standard trust roots do not compensate for skipped peer identity.

### Provisioning.kt

```kotlin
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit
class Provisioning {
    private val client = OkHttpClient.Builder()
        .hostnameVerifier { _, _ -> true }
        .followRedirects(false)
        .callTimeout(4, TimeUnit.SECONDS)
        .build()
    fun enrollmentCode(): String {
        val request = Request.Builder().url("https://enroll.example.org/device-code").build()
        return client.newCall(request).execute().use { response ->
            check(response.isSuccessful)
            require((response.body?.contentLength() ?: 0) <= 4096)
            response.body!!.string()
        }
    }
}
```

### DeviceScreen.kt

```kotlin
class DeviceScreen(private val provisioning: Provisioning) {
    fun displayedCode(): String = provisioning.enrollmentCode().trim()
}
```

### Derivation

```json
{
  "group": "device-provisioning-okhttp-hostname-policy",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around retrieve the enrollment code only from the configured enrollment origin. Boundary: The peer certificate remains chain-validated, but its identity is not checked against enroll.example.org. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "Provisioning.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Response length relies partly on the stated upstream protocol; transport authenticity is the expected defect, not attacker-chosen URL fetching."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Retrieve the enrollment code only from the configured enrollment origin.",
  "trust_boundary": "The peer certificate remains chain-validated, but its identity is not checked against enroll.example.org.",
  "legitimate_examples": [
    {
      "input": "Valid enrolled host returns Q7X9",
      "expected": "Displays Q7X9"
    },
    {
      "input": "Unrelated-domain certificate",
      "expected": "Must fail authentication after remediation"
    }
  ],
  "permitted_changes": [
    "Restore hostname verification while preserving configured origin and redirect refusal."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not accept a hostname mismatch merely because the certificate chains to a trusted CA."
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
    "https://square.github.io/okhttp/3.x/okhttp/okhttp3/OkHttpClient.Builder.html#hostnameVerifier-javax.net.ssl.HostnameVerifier-"
  ]
}
```

### Regression traps

```json
[
  "Do not accept a hostname mismatch merely because the certificate chains to a trusted CA."
]
```

### Remediation constraints

```json
[
  "Retrieve the enrollment code only from the configured enrollment origin.",
  "Restore hostname verification while preserving configured origin and redirect refusal.",
  "Do not accept a hostname mismatch merely because the certificate chains to a trusted CA."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-03",
  "prior_case_id": "kotlin-native-state-vulnerable",
  "prior_source_sha256": "1cf10c9ee6189ce19fd3183bbc22b285b23ec974f5f33f2645e8580ec8b3d3de",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "OkHttp4.12.0 with normal JVM CA roots. On-path attacker has a CA-valid certificate for an unrelated domain. Enrollment service promises fixed-length text bodies; code is displayed to bind a physical device."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-04 — clinic-export-des-encryption

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `10eaa50a9800983bc323f63977e3ee7b8ab4dc5878ba13e763d1003f907ba255`. Protocol-2.0 case hash: `8302dfed08d54c9af78bafe3283bbdc3ca06b12588e23cdaa1055edb9802edc1`.

DES has insufficient key strength and ECB lacks semantic security/authentication. This is a confidentiality boundary with actual encryption/decryption consumers, not a harmless algorithm-name string.

### ClinicalExport.kt

```kotlin
import javax.crypto.Cipher
import javax.crypto.SecretKey
import java.nio.charset.StandardCharsets
object ClinicalExport {
    fun protect(csv: String, exportKey: SecretKey): ByteArray {
        val cipher = Cipher.getInstance("DES/ECB/PKCS5Padding")
        cipher.init(Cipher.ENCRYPT_MODE, exportKey)
        return cipher.doFinal(csv.toByteArray(StandardCharsets.UTF_8))
    }
    fun restore(blob: ByteArray, exportKey: SecretKey): String {
        val cipher = Cipher.getInstance("DES/ECB/PKCS5Padding")
        cipher.init(Cipher.DECRYPT_MODE, exportKey)
        return String(cipher.doFinal(blob), StandardCharsets.UTF_8)
    }
}
```

### ExportRoute.kt

```kotlin
import javax.crypto.SecretKey
class ExportRoute(private val key: SecretKey) {
    fun download(authorizedRows: List<String>): ByteArray =
        ClinicalExport.protect(authorizedRows.joinToString("\n"), key)
}
```

### Derivation

```json
{
  "group": "clinic-export-des-encryption",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around export and restore clinical csv without exposing patient data to storage readers. Boundary: Storage attackers obtain ciphertext protected with 56-bit DES in deterministic ECB mode. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-327",
    "path": "ClinicalExport.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Both weak cipher and unauthenticated mode belong to the same cryptographic storage defect; importing arbitrary legacy ciphertext must not silently become a downgrade route."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Export and restore clinical CSV without exposing patient data to storage readers.",
  "trust_boundary": "Storage attackers obtain ciphertext protected with 56-bit DES in deterministic ECB mode.",
  "legitimate_examples": [
    {
      "input": "Two UTF-8 CSV rows",
      "expected": "Round trip returns identical CSV"
    },
    {
      "input": "Empty export",
      "expected": "A valid encrypted empty payload round trips"
    }
  ],
  "permitted_changes": [
    "Introduce a versioned AEAD envelope with fresh nonce and strong key, and an explicit authenticated migration path for trusted legacy archives."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not emit plaintext, silently change CSV encodings, or reuse one nonce across exports."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/Cipher.html"
  ]
}
```

### Regression traps

```json
[
  "Do not emit plaintext, silently change CSV encodings, or reuse one nonce across exports."
]
```

### Remediation constraints

```json
[
  "Export and restore clinical CSV without exposing patient data to storage readers.",
  "Introduce a versioned AEAD envelope with fresh nonce and strong key, and an explicit authenticated migration path for trusted legacy archives.",
  "Do not emit plaintext, silently change CSV encodings, or reuse one nonce across exports."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-04",
  "prior_case_id": "kotlin-digest-choice-vulnerable",
  "prior_source_sha256": "a0d717dd33cac01c453edbd3247b6781de0698cd53b4389d476313336eb7168d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "JCE SunJCE DES provider; a trusted keystore supplies a DES key. Authorized clinical CSV is encrypted before crossing an untrusted storage medium; confidentiality and tamper detection are requirements."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-05 — project-template-zip-install-path

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `3ebae2eb84faf3396eb390a5193072c77e99d839de9b5f02d65d26cb75869fc1`. Protocol-2.0 case hash: `c289163e1de210809a6d81dcc6167e7f0264f51aebb5ce66cafccc01dccbd044`.

Relative parent components and absolute archive names can escape projectRoot. Size/count bounds do not limit the filesystem destination.

### TemplateInstaller.kt

```kotlin
import java.nio.file.Files
import java.nio.file.Path
import java.util.zip.ZipInputStream
import java.io.ByteArrayInputStream
object TemplateInstaller {
    fun install(zipBytes: ByteArray, projectRoot: Path): Int {
        require(zipBytes.size <= 65536)
        var count = 0
        ZipInputStream(ByteArrayInputStream(zipBytes)).use { archive ->
            var entry = archive.nextEntry
            while (entry != null) {
                require(++count <= 20)
                val target = projectRoot.resolve(entry.name)
                if (entry.isDirectory) Files.createDirectories(target)
                else {
                    Files.createDirectories(target.parent)
                    val content = archive.readNBytes(65537)
                    require(content.size <= 65536)
                    Files.write(target, content)
                }
                entry = archive.nextEntry
            }
        }
        return count
    }
}
```

### Derivation

```json
{
  "group": "project-template-zip-install-path",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around install a bounded project-template archive while retaining its nested relative layout. Boundary: Archive entry names are joined with a trusted project root without containment validation. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "TemplateInstaller.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Fresh root has no pre-existing symlinks and is private; archive expansion limits are explicitly present. A fix still needs fail-safe cleanup of rejected imports."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Install a bounded project-template archive while retaining its nested relative layout.",
  "trust_boundary": "Archive entry names are joined with a trusted project root without containment validation.",
  "legitimate_examples": [
    {
      "input": "assets/logo.txt and README.txt",
      "expected": "Both appear inside the new project"
    },
    {
      "input": "docs/guide with spaces.txt",
      "expected": "Nested spaced filename is preserved"
    }
  ],
  "permitted_changes": [
    "Validate every entry as a contained relative path before writing; reject traversal and escaping links, and avoid partial installation on rejection."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not flatten directories, rename all files, or accept archives after merely removing ../ text."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Path.html#resolve(java.lang.String)"
  ]
}
```

### Regression traps

```json
[
  "Do not flatten directories, rename all files, or accept archives after merely removing ../ text."
]
```

### Remediation constraints

```json
[
  "Install a bounded project-template archive while retaining its nested relative layout.",
  "Validate every entry as a contained relative path before writing; reject traversal and escaping links, and avoid partial installation on rejection.",
  "Do not flatten directories, rename all files, or accept archives after merely removing ../ text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-05",
  "prior_case_id": "kotlin-maintenance-shell-vulnerable",
  "prior_source_sha256": "2763f094afcea3695525ec9ad70e09be878df0dc2bb4d13e19d972dcb69a23a7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "Linux; projectRoot is a new private directory created by server in a parent containing other projects. ZIP entries are regular files/directories only; untrusted publisher supplies the archive."
}
```

### Split

```json
"held_out"
```

## v2-kotlin-vulnerable-06 — nightly-backup-comment-shell-pipeline

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `348897a59ff0148c4336060b7d13a6d2f297a20fcd1573d035c0dfbb00af8970`. Protocol-2.0 case hash: `a0b4506391690a08c83ab5c451bfb89cebdcb5e36a82d13216453d12c0339299`.

Double quotes do not disable shell command substitution or variable expansion. The string is interpreted by /bin/sh before printf receives it.

### BackupAnnotation.kt

```kotlin
class BackupAnnotation {
    fun annotate(comment: String): Int {
        require(comment.length <= 80)
        val command = "printf '%s\\n' \"$comment\" >> /srv/backups/notes.txt"
        val process = ProcessBuilder("/bin/sh", "-c", command)
            .redirectError(ProcessBuilder.Redirect.DISCARD)
            .redirectOutput(ProcessBuilder.Redirect.DISCARD).start()
        return process.waitFor()
    }
}
```

### BackupForm.kt

```kotlin
class BackupForm(private val writer: BackupAnnotation) {
    fun addComment(fields: Map<String, String>): Boolean =
        writer.annotate(fields.getValue("comment")) == 0
}
```

### Derivation

```json
{
  "group": "nightly-backup-comment-shell-pipeline",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around append the exact backup comment and one newline to the notes file. Boundary: A comment is interpolated inside a shell double-quoted word, where command substitution remains active. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "BackupAnnotation.kt"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "File path and concurrency policy are trusted; comment authors lack host execution permission."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Append the exact backup comment and one newline to the notes file.",
  "trust_boundary": "A comment is interpolated inside a shell double-quoted word, where command substitution remains active.",
  "legitimate_examples": [
    {
      "input": "Friday's backup",
      "expected": "Append Friday's backup and newline"
    },
    {
      "input": "literal $HOME text",
      "expected": "Append dollar sign and HOME literally"
    }
  ],
  "permitted_changes": [
    "Append using a trusted file API with UTF-8 and append semantics, or pass data via stdin without shell evaluation."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not overwrite prior notes, omit the newline, or expand environment-variable text."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ProcessBuilder.html"
  ]
}
```

### Regression traps

```json
[
  "Do not overwrite prior notes, omit the newline, or expand environment-variable text."
]
```

### Remediation constraints

```json
[
  "Append the exact backup comment and one newline to the notes file.",
  "Append using a trusted file API with UTF-8 and append semantics, or pass data via stdin without shell evaluation.",
  "Do not overwrite prior notes, omit the newline, or expand environment-variable text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-kotlin-vulnerable-06",
  "prior_case_id": "kotlin-host-verifier-vulnerable",
  "prior_source_sha256": "399d49cefa16d49714b1ff74b2e2116b4d08694e9061ca821994116fc592a577",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Kotlin 2.0.21 on OpenJDK 21",
  "libraries_platform_setup": "Linux POSIX shell; notes file is trusted and fixed, requests are serialized, authenticated backup viewers may add bounded comments but may not execute host commands."
}
```

### Split

```json
"held_out"
```

