# scala — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-scala-safe-01 — shipment-id-list-placeholders

Proposed label: **safe**. Human review: **pending**.

Source hash: `d4cc94f08c3555d32d1c5d13ce27c066b412b7454862b634123d9bb85f328f03`. Protocol-2.0 case hash: `b8ec18381f16f63dfbb25e75bcb5b1bae800a8bc96021364acda9cc6ae7ab57f`.

Dynamic SQL consists solely of repeated question-mark placeholders, not joined input values. The empty-list branch avoids malformed IN() without fabricating results.

### ShipmentRows.scala

```scala
import java.sql.Connection
object ShipmentRows {
  def statuses(db: Connection, ids: Vector[Long]): Vector[String] = {
    require(ids.size <= 40)
    if (ids.isEmpty) return Vector.empty
    val marks = Vector.fill(ids.size)("?").mkString(",")
    val statement = db.prepareStatement("SELECT status FROM shipments WHERE id IN (" + marks + ") ORDER BY id")
    try {
      ids.zipWithIndex.foreach { case (id, i) => statement.setLong(i + 1, id) }
      val rows = statement.executeQuery()
      try {
        val result = Vector.newBuilder[String]
        while (rows.next()) result += rows.getString(1)
        result.result()
      } finally rows.close()
    } finally statement.close()
  }
}
```

### Derivation

```json
{
  "group": "shipment-id-list-placeholders",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around return shipment statuses for a bounded list of authorized ids in id order. Boundary: Only the number of trusted placeholder tokens affects SQL structure; every ID is bound. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Tenant authorization comes from the scoped database view; this function does not accept a raw unrestricted connection in production."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return shipment statuses for a bounded list of authorized IDs in ID order.",
  "trust_boundary": "Only the number of trusted placeholder tokens affects SQL structure; every ID is bound.",
  "legitimate_examples": [
    {
      "input": "IDs[9,2]",
      "expected": "Statuses in ascending ID order"
    },
    {
      "input": "Empty IDs",
      "expected": []
    }
  ],
  "permitted_changes": [
    "Retain binding, bounded list length and deterministic result order."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not join numeric strings directly or change set membership into positional duplicate results."
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
  "Do not join numeric strings directly or change set membership into positional duplicate results."
]
```

### Remediation constraints

```json
[
  "Return shipment statuses for a bounded list of authorized IDs in ID order.",
  "Retain binding, bounded list length and deterministic result order.",
  "Do not join numeric strings directly or change set membership into positional duplicate results."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-01",
  "prior_case_id": "scala-customer-jdbc-safe",
  "prior_source_sha256": "2b33283f9fb058e835962f1ccf155687dcb857429ec9c7ce3f52469101140c97",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "PostgreSQL16 JDBC42.7.4; connection is scoped to a caller-authorized shipment view; IDs are decoded as signed64-bit numbers before entry."
}
```

### Split

```json
"held_out"
```

## v2-scala-safe-02 — external-dtd-free-schema-validation

Proposed label: **safe**. Human review: **pending**.

Source hash: `6a2cc65a0c5bb8bcbca4a968e88ac6a9d0e37b187430a3feeb0658f34efdc7b5`. Protocol-2.0 case hash: `9881f1ce235e540fab808d7e3ca3d7cf0833acf6a7ee7069e107ef1060e29b4c`.

Both schema creation and the validator deny external protocols. The trusted schema controls document shape; input-provided schema hints cannot broaden resource access.

### InvoiceShape.scala

```scala
import javax.xml.validation.SchemaFactory
import javax.xml.XMLConstants
import javax.xml.transform.stream.StreamSource
import java.io.StringReader
object InvoiceShape {
  private val schemaText = "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='amount' type='xs:decimal'/></xs:schema>"
  def valid(xml: String): Boolean = {
    require(xml.length <= 2048)
    val factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI)
    factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true)
    factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "")
    factory.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "")
    val validator = factory.newSchema(new StreamSource(new StringReader(schemaText))).newValidator()
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "")
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "")
    try { validator.validate(new StreamSource(new StringReader(xml))); true }
    catch { case _: org.xml.sax.SAXException => false }
  }
}
```

### Derivation

```json
{
  "group": "external-dtd-free-schema-validation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around validate a bounded amount document against a trusted decimal schema. Boundary: An untrusted invoice may not load schemas or DTD resources even when it supplies location hints. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The bounded XML and secure-processing limits constrain expansion; a maintainer should confirm those limits against deployment memory policies."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Validate a bounded amount document against a trusted decimal schema.",
  "trust_boundary": "An untrusted invoice may not load schemas or DTD resources even when it supplies location hints.",
  "legitimate_examples": [
    {
      "input": "<amount>12.50</amount>",
      "expected": true
    },
    {
      "input": "<amount>twelve</amount>",
      "expected": false
    }
  ],
  "permitted_changes": [
    "Preserve decimal validation and fail-closed resource denial."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not convert all exceptions into successful validation or accept arbitrary element names."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.xml/javax/xml/validation/SchemaFactory.html"
  ]
}
```

### Regression traps

```json
[
  "Do not convert all exceptions into successful validation or accept arbitrary element names."
]
```

### Remediation constraints

```json
[
  "Validate a bounded amount document against a trusted decimal schema.",
  "Preserve decimal validation and fail-closed resource denial.",
  "Do not convert all exceptions into successful validation or accept arbitrary element names."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-02",
  "prior_case_id": "scala-document-factory-safe",
  "prior_source_sha256": "41643d354c50131d7ab785aa280c305fe202fda020c5e1e85294a077fdc425e2",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "JDK built-in schema validator; schema is an application constant with no imports. Schema/parse errors reject the invoice; no insecure retry. JDK processing limits remain enabled."
}
```

### Split

```json
"held_out"
```

## v2-scala-safe-03 — legacy-contact-string-export-only

Proposed label: **safe**. Human review: **pending**.

Source hash: `52c0e6dbbf35478cd6790f2bf8eee2dc6cc159eacfcb5f43a29ffdb425ee3353`. Protocol-2.0 case hash: `9c3bbe1da26416b6e805e16697869c5a2e8bd266646c9f18e082c27f4c7e6917`.

ObjectOutputStream writes a fixed trusted graph assembled from strings. There is no deserialization boundary, and object-looking strings are not parsed as class metadata.

### ContactExport.scala

```scala
import java.io.{ByteArrayOutputStream, ObjectOutputStream}
object ContactExport {
  def download(addresses: Vector[String]): Array[Byte] = {
    require(addresses.size <= 100 && addresses.forall(_.length <= 200))
    val values = new java.util.ArrayList[String]()
    addresses.foreach(values.add)
    val bytes = new ByteArrayOutputStream()
    val output = new ObjectOutputStream(bytes)
    try {
      output.writeObject(values)
      output.flush()
      bytes.toByteArray
    } finally output.close()
  }
}
```

### ContactDownload.scala

```scala
object ContactDownload {
  def attachment(authorizedContactNames: Vector[String]): Array[Byte] =
    ContactExport.download(authorizedContactNames)
}
```

### Derivation

```json
{
  "group": "legacy-contact-string-export-only",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around export authorized contact strings in the documented legacy binary format. Boundary: Untrusted string contents are serialized as string data; they cannot select runtime object classes or invoke an input decoder. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The downstream migration utility needs its own safe decoder; this source-only label does not claim unrestricted object-input APIs are safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Export authorized contact strings in the documented legacy binary format.",
  "trust_boundary": "Untrusted string contents are serialized as string data; they cannot select runtime object classes or invoke an input decoder.",
  "legitimate_examples": [
    {
      "input": "Vector(alice@example.org,bob@example.org)",
      "expected": "Archive containing exactly those two String values in order"
    },
    {
      "input": "String containing a Java class name",
      "expected": "Serialized as an inert String value"
    }
  ],
  "permitted_changes": [
    "Retain the fixed string-only graph, size bounds and exact order."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not accept arbitrary objects, deserialize user data to validate it, or replace binary output with a printed vector."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/ObjectOutputStream.html"
  ]
}
```

### Regression traps

```json
[
  "Do not accept arbitrary objects, deserialize user data to validate it, or replace binary output with a printed vector."
]
```

### Remediation constraints

```json
[
  "Export authorized contact strings in the documented legacy binary format.",
  "Retain the fixed string-only graph, size bounds and exact order.",
  "Do not accept arbitrary objects, deserialize user data to validate it, or replace binary output with a printed vector."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-03",
  "prior_case_id": "scala-job-state-safe",
  "prior_source_sha256": "e1bf819f4e170c74cc71cfc880bae4999befa2e444bef255ff6a1462652c5252",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Legacy export format is a serialized java.util.ArrayList[String] consumed by an offline migration utility. Function accepts only bounded Scala String values, not arbitrary AnyRef objects; it never reads an object stream. Contacts are authorized before entry."
}
```

### Split

```json
"held_out"
```

## v2-scala-safe-04 — archive-entry-listing-direct-argv

Proposed label: **safe**. Human review: **pending**.

Source hash: `1da5553455eea64a46e983f02cd893540ea20583dac308e4311491bc0c691313`. Protocol-2.0 case hash: `fd71ac21d2922c93cbabef757a08087b2ae4e77f59eb7fe5ddc7c9d8270beda9`.

A direct argv process receives a server-generated absolute file path; entries are listed and never passed to a shell or filesystem writer. Dangerous-looking names alone do not establish traversal.

### ArchiveListing.scala

```scala
import scala.sys.process._
import java.nio.file.Path
object ArchiveListing {
  def list(ownedArchive: Path): (Int, Vector[String]) = {
    val lines = Vector.newBuilder[String]
    val exit = Process(Seq("/usr/bin/unzip", "-Z1", ownedArchive.toAbsolutePath.toString))
      .!(ProcessLogger(line => lines += line, _ => ()))
    (exit, lines.result())
  }
}
```

### UploadedArchive.scala

```scala
import java.nio.file.Path
final case class UploadedArchive(serverAssignedAbsolutePath: Path)
object ListingRoute {
  def show(upload: UploadedArchive): Vector[String] = {
    val (status, names) = ArchiveListing.list(upload.serverAssignedAbsolutePath)
    require(status == 0, "unreadable archive")
    names
  }
}
```

### Derivation

```json
{
  "group": "archive-entry-listing-direct-argv",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around list names in an accepted archive without extracting or executing them. Boundary: Attacker controls archive contents and entry names, not the absolute path or executable arguments. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Archive size/entry count were enforced by trusted ingestion; third-party unzip implementation flaws are outside source-code ground truth."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List names in an accepted archive without extracting or executing them.",
  "trust_boundary": "Attacker controls archive contents and entry names, not the absolute path or executable arguments.",
  "legitimate_examples": [
    {
      "input": "Archive entries a.txt and docs/b.txt",
      "expected": [
        "a.txt",
        "docs/b.txt"
      ]
    },
    {
      "input": "Entry name containing semicolon",
      "expected": "Name remains one output line of data"
    }
  ],
  "permitted_changes": [
    "Preserve listing-only behavior and propagate archive errors."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not extract to discover names or execute a command for each listed entry."
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
    "https://www.scala-lang.org/api/2.13.x/scala/sys/process/index.html"
  ]
}
```

### Regression traps

```json
[
  "Do not extract to discover names or execute a command for each listed entry."
]
```

### Remediation constraints

```json
[
  "List names in an accepted archive without extracting or executing them.",
  "Preserve listing-only behavior and propagate archive errors.",
  "Do not extract to discover names or execute a command for each listed entry."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-04",
  "prior_case_id": "scala-integrity-hash-safe",
  "prior_source_sha256": "ef3e4d10c818323e5bb674d731576d12afb84388266821127a40b0bd492cdb63",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Linux Info-ZIP6.0; ingestion has already accepted a bounded archive into a private server-assigned absolute filename. Listing does not extract entries. Names are JSON-encoded by the caller."
}
```

### Split

```json
"held_out"
```

## v2-scala-safe-05 — user-photo-aes-gcm-envelope

Proposed label: **safe**. Human review: **pending**.

Source hash: `131f138fcfa193d5a2aad43645158537784addcc8cce94b38c10ccd8416ad605`. Protocol-2.0 case hash: `806b66a9351826f2e905496a443450c1a0836b28af7172fd679f201e1567e5d1`.

The implementation uses a fresh random nonce, AEAD tag and explicit identity binding. The output retains nonce and version so it can be decrypted without weakening verification.

### PhotoEnvelope.scala

```scala
import javax.crypto.{Cipher, SecretKey}
import javax.crypto.spec.GCMParameterSpec
import java.security.SecureRandom
object PhotoEnvelope {
  private val random = new SecureRandom()
  def seal(jpeg: Array[Byte], key: SecretKey, ownerId: String): Array[Byte] = {
    require(jpeg.length <= 1048576)
    val nonce = new Array[Byte](12)
    random.nextBytes(nonce)
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, nonce))
    cipher.updateAAD(ownerId.getBytes(java.nio.charset.StandardCharsets.UTF_8))
    Array[Byte](1) ++ nonce ++ cipher.doFinal(jpeg)
  }
}
```

### Derivation

```json
{
  "group": "user-photo-aes-gcm-envelope",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around create an authenticated owner-bound encrypted envelope for a photo. Boundary: Untrusted storage may read or alter ciphertext but lacks the key; owner identity is trusted AAD. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Authorization precedes the function; malformed JPEG handling belongs to a separate prevalidated image pipeline."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Create an authenticated owner-bound encrypted envelope for a photo.",
  "trust_boundary": "Untrusted storage may read or alter ciphertext but lacks the key; owner identity is trusted AAD.",
  "legitimate_examples": [
    {
      "input": "Same JPEG encrypted twice",
      "expected": "Distinct nonce-bearing envelopes"
    },
    {
      "input": "Photo later opened for a different owner",
      "expected": "AAD verification fails in the documented consumer"
    }
  ],
  "permitted_changes": [
    "Retain random nonce generation, full authentication tag and owner binding."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not reuse a fixed IV, omit the nonce from storage, or move ownerId into unauthenticated metadata."
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
  "Do not reuse a fixed IV, omit the nonce from storage, or move ownerId into unauthenticated metadata."
]
```

### Remediation constraints

```json
[
  "Create an authenticated owner-bound encrypted envelope for a photo.",
  "Retain random nonce generation, full authentication tag and owner binding.",
  "Do not reuse a fixed IV, omit the nonce from storage, or move ownerId into unauthenticated metadata."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-05",
  "prior_case_id": "scala-system-query-safe",
  "prior_source_sha256": "e1007fa48744866226bc266050e989fc90d160db32dddc81a3419c4391417d02",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Fresh 256-bit AES key from trusted keystore; ownerId comes from the authenticated session. Per-key volume bounded far below nonce-collision limits. Version1 consumer verifies GCM tag and same owner AAD before releasing plaintext."
}
```

### Split

```json
"held_out"
```

## v2-scala-safe-06 — enum-origin-health-request

Proposed label: **safe**. Human review: **pending**.

Source hash: `d6525ac6a7c65ea32d3dfb11fb408c99d66957fc27ce726c6a7c7eb3c0c85093`. Protocol-2.0 case hash: `08844e9c396694fa13976e83b11a81e839e38f100d10a5a5cde82106d0ef3266`.

The original interface is a region enum, so the map does not remove a general URL-fetch requirement. Default verification and no redirects retain destination constraints.

### RegionHealth.scala

```scala
import java.net.URI
import java.net.http.{HttpClient, HttpRequest, HttpResponse}
import java.time.Duration
object RegionHealth {
  private val origins = Map("east" -> "https://east.example.org", "west" -> "https://west.example.org")
  private val client = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.NEVER)
    .connectTimeout(Duration.ofSeconds(2)).build()
  def check(region: String): Int = {
    val base = origins.getOrElse(region, throw new IllegalArgumentException("unknown region"))
    val request = HttpRequest.newBuilder(URI.create(base + "/health"))
      .timeout(Duration.ofSeconds(2)).GET().build()
    client.send(request, HttpResponse.BodyHandlers.discarding()).statusCode()
  }
}
```

### Derivation

```json
{
  "group": "enum-origin-health-request",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around check health of a selected configured region with certificate verification. Boundary: Untrusted region name selects a closed trusted-origin map; network content is untrusted until standard TLS verification. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "DNS and operator domain ownership are trusted infrastructure, not supplied by tenants."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Check health of a selected configured region with certificate verification.",
  "trust_boundary": "Untrusted region name selects a closed trusted-origin map; network content is untrusted until standard TLS verification.",
  "legitimate_examples": [
    {
      "input": "east",
      "expected": "Status from configured east /health"
    },
    {
      "input": "https://127.0.0.1",
      "expected": "Rejected unknown region"
    }
  ],
  "permitted_changes": [
    "Retain the two region meanings, standard TLS checks and no-redirect behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not interpret unknown region values as fallback URLs or mark connection failures healthy."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpClient.Builder.html"
  ]
}
```

### Regression traps

```json
[
  "Do not interpret unknown region values as fallback URLs or mark connection failures healthy."
]
```

### Remediation constraints

```json
[
  "Check health of a selected configured region with certificate verification.",
  "Retain the two region meanings, standard TLS checks and no-redirect behavior.",
  "Do not interpret unknown region values as fallback URLs or mark connection failures healthy."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-safe-06",
  "prior_case_id": "scala-tls-hostnames-safe",
  "prior_source_sha256": "7b9561506cf6ae2d449979f805c14700942dd34be6b08f6853c44d8d0fb14f9f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Operator-controlled regional domains with standard CA certificates, trusted system resolver/root store; users choose a published region ID, never a URL. No global TLS overrides."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-01 — library-shelf-slick-literal-splice

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0ef5c5f6a494b50485fcb9716d127f7a9feb075dfd68ff11c405bb9d12bf9045`. Protocol-2.0 case hash: `b7dae7516d154e7afd7ff614e446ecad5b8a057baf23ab042fbd73deaa810a66`.

Slick #$ explicitly splices literal text; surrounding it with SQL quotes does not turn it into a bound variable. A quote in the prefix can alter query grammar.

### ShelfSearch.scala

```scala
import slick.jdbc.PostgresProfile.api._
import scala.concurrent.Future
final class ShelfSearch(db: Database) {
  def locate(prefix: String): Future[Vector[String]] = {
    require(prefix.length <= 60)
    val pattern = prefix + "%"
    db.run(sql"SELECT title FROM books WHERE shelf LIKE '#$pattern' ORDER BY accession".as[String])
  }
}
```

### SearchEndpoint.scala

```scala
import scala.concurrent.Future
final class SearchEndpoint(search: ShelfSearch) {
  def get(parameters: Map[String, String]): Future[Vector[String]] =
    search.locate(parameters.getOrElse("shelf", ""))
}
```

### Derivation

```json
{
  "group": "library-shelf-slick-literal-splice",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around find book titles by a shelf-prefix pattern in accession order. Boundary: A reader controls a pattern passed through Slick literal splicing rather than a bound interpolator. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "ShelfSearch.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Public catalog authorization is intentional; SQL account is read-only but injected predicates still violate filtering."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Find book titles by a shelf-prefix pattern in accession order.",
  "trust_boundary": "A reader controls a pattern passed through Slick literal splicing rather than a bound interpolator.",
  "legitimate_examples": [
    {
      "input": "shelf=YA",
      "expected": "Titles on shelves beginning YA"
    },
    {
      "input": "shelf=A_",
      "expected": "The documented single-character wildcard remains meaningful"
    }
  ],
  "permitted_changes": [
    "Bind the complete LIKE pattern using the regular Slick interpolator and preserve documented wildcard behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not escape percent/underscore into literals unless the API contract is explicitly migrated, or replace prefix results with all books."
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
    "https://scala-slick.org/doc/3.5.1/sql.html"
  ]
}
```

### Regression traps

```json
[
  "Do not escape percent/underscore into literals unless the API contract is explicitly migrated, or replace prefix results with all books."
]
```

### Remediation constraints

```json
[
  "Find book titles by a shelf-prefix pattern in accession order.",
  "Bind the complete LIKE pattern using the regular Slick interpolator and preserve documented wildcard behavior.",
  "Do not escape percent/underscore into literals unless the API contract is explicitly migrated, or replace prefix results with all books."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-01",
  "prior_case_id": "scala-customer-jdbc-vulnerable",
  "prior_source_sha256": "47134407f8fc2e6fe7ddb9ac76e3ddc3e6d42f2e73227237d3a26934a37d04e6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Slick3.5.1, PostgreSQL16, PostgreSQL JDBC42.7.4; books(title,shelf,accession) public catalog. Prefix matching intentionally supports SQL LIKE % and _ wildcard semantics."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-02 — theme-xslt-preview-external-document

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `6414660072d7f313d60af3e39ee3512dcb8eb3fa7575d817a8ec1a62a7c33b93`. Protocol-2.0 case hash: `f9fd11388d7c343cfb22916047865d5330b4e620e7bf2f5ae17da7b711005080`.

The factory explicitly enables external resource access and disables secure processing before compiling an untrusted stylesheet. Transformer execution is the reachable boundary, not just parsing a harmless XML string.

### ThemePreview.scala

```scala
import javax.xml.transform.TransformerFactory
import javax.xml.transform.stream.{StreamResult, StreamSource}
import javax.xml.XMLConstants
import java.io.{StringReader, StringWriter}
object ThemePreview {
  def render(stylesheet: String): String = {
    require(stylesheet.length <= 16384)
    val factory = TransformerFactory.newInstance()
    factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, false)
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "all")
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "all")
    val transformer = factory.newTransformer(new StreamSource(new StringReader(stylesheet)))
    val output = new StringWriter()
    transformer.transform(new StreamSource(new StringReader("<page><title>Welcome</title></page>")), new StreamResult(output))
    output.toString
  }
}
```

### Derivation

```json
{
  "group": "theme-xslt-preview-external-document",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around preview a theme transform of a fixed welcome-page xml document. Boundary: Editor-controlled XSLT can request external stylesheet/DTD/document resources with unrestricted access. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "ThemePreview.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Inert preview delivery excludes HTML execution. XML external access may overlap SSRF; that is the same source resource-resolution flaw in this case."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Preview a theme transform of a fixed welcome-page XML document.",
  "trust_boundary": "Editor-controlled XSLT can request external stylesheet/DTD/document resources with unrestricted access.",
  "legitimate_examples": [
    {
      "input": "Stylesheet emitting page/title",
      "expected": "Preview contains Welcome"
    },
    {
      "input": "Stylesheet sorting fixed document nodes",
      "expected": "The permitted data-only transform still executes"
    }
  ],
  "permitted_changes": [
    "Disable external resource access and extension execution while retaining the approved data-only XSLT subset; enforce transform resource limits."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not return the stylesheet itself or replace every transform with fixed Welcome text."
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
  "Do not return the stylesheet itself or replace every transform with fixed Welcome text."
]
```

### Remediation constraints

```json
[
  "Preview a theme transform of a fixed welcome-page XML document.",
  "Disable external resource access and extension execution while retaining the approved data-only XSLT subset; enforce transform resource limits.",
  "Do not return the stylesheet itself or replace every transform with fixed Welcome text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-02",
  "prior_case_id": "scala-document-factory-vulnerable",
  "prior_source_sha256": "6dbd8018308a8de76b3e2d26fdc1a3b0c4a0318fe5b9e68c29b19299b279c662",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "JDK built-in XSLT transformer. Theme editors may author bounded presentation stylesheets but may not read host files or contact internal services. Response is previewed to the editor as inert text."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-03 — automation-yaml-arbitrary-constructor

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0ed208cf0db9d320bf1f10b85d43799010643fe7b348ff977648a0d3d96bf797`. Protocol-2.0 case hash: `1ce4968b7089dbefcb4e7ca3ba00f75a3105d69c99f8f3a5df3d5eeaf119daea`.

Under the explicitly pinned legacy constructor, global tags can activate arbitrary available classes before the match checks the result. The shape check is after deserialization and cannot establish a data-only boundary.

### WorkflowYaml.scala

```scala
import org.yaml.snakeyaml.Yaml
object WorkflowYaml {
  def title(upload: String): String = {
    require(upload.length <= 16384)
    val document: AnyRef = new Yaml().load[AnyRef](upload)
    document match {
      case fields: java.util.Map[_, _] => String.valueOf(fields.get("title"))
      case _ => throw new IllegalArgumentException("mapping required")
    }
  }
}
```

### WorkflowDraft.scala

```scala
final class WorkflowDraft {
  def preview(untrustedYamlFromAuthor: String): String = WorkflowYaml.title(untrustedYamlFromAuthor)
}
```

### Derivation

```json
{
  "group": "automation-yaml-arbitrary-constructor",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around preview the title of a data-only workflow mapping supplied by an author. Boundary: YAML tags reach the legacy general object constructor before the root mapping check. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "WorkflowYaml.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "This is a deliberate legacy API reachability case, not an unpinned claim about safe defaults in SnakeYAML2.x; gadget-specific execution is not assumed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Preview the title of a data-only workflow mapping supplied by an author.",
  "trust_boundary": "YAML tags reach the legacy general object constructor before the root mapping check.",
  "legitimate_examples": [
    {
      "input": "title: Nightly inventory",
      "expected": "Nightly inventory"
    },
    {
      "input": "title: 'on: call'",
      "expected": "on: call"
    }
  ],
  "permitted_changes": [
    "Use a safe data constructor with explicit collection/size limits and reject non-data tags."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not return raw YAML, instantiate tagged classes merely to inspect their type, or stringify every document indiscriminately."
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
    "https://javadoc.io/doc/org.yaml/snakeyaml/1.33/org/yaml/snakeyaml/constructor/Constructor.html",
    "https://javadoc.io/doc/org.yaml/snakeyaml/1.33/org/yaml/snakeyaml/constructor/SafeConstructor.html"
  ]
}
```

### Regression traps

```json
[
  "Do not return raw YAML, instantiate tagged classes merely to inspect their type, or stringify every document indiscriminately."
]
```

### Remediation constraints

```json
[
  "Preview the title of a data-only workflow mapping supplied by an author.",
  "Use a safe data constructor with explicit collection/size limits and reject non-data tags.",
  "Do not return raw YAML, instantiate tagged classes merely to inspect their type, or stringify every document indiscriminately."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-03",
  "prior_case_id": "scala-job-state-vulnerable",
  "prior_source_sha256": "ea0a676e820eb1d20b982cf870b4e8ff81b399f9d4e141762fc79c7260dac274",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "SnakeYAML1.33 (not2.x); default Constructor permits global Java tags. The application classpath contains JDK classes; workflow authors are not trusted to instantiate arbitrary host objects. YAML is not signed."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-04 — federated-admin-assertion-unverified-signature

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `dcd16ad677c6188ddc55ca41db1b549ddc0c53dad1da1bbe28eb5fd9fee09ad6`. Protocol-2.0 case hash: `1a69fe0163ec1964f1491f8de2938a71b983e6fe0f8b9112ff287f21c1a340b2`.

The configured verification key is never used and the third compact-token field is checked only for non-emptiness. Anyone can supply admin claims with arbitrary signature text; audience/expiry checks do not establish origin.

### AdminAssertion.scala

```scala
import java.security.PublicKey
import java.util.Base64
import java.nio.charset.StandardCharsets
object AdminAssertion {
  def mayAdminister(token: String, configuredIssuerKey: PublicKey, now: Long): Boolean = {
    require(token.length <= 8192)
    val parts = token.split("\\.", -1)
    if (parts.length != 3 || parts(2).isEmpty) return false
    val payload = new String(Base64.getUrlDecoder.decode(parts(1)), StandardCharsets.UTF_8)
    val claims = ujson.read(payload)
    claims("aud").str == "tenant-admin" && claims("role").str == "admin" && claims("exp").num > now
  }
}
```

### AdminPanel.scala

```scala
import java.security.PublicKey
object AdminPanel {
  def open(bearer: String, trustedIssuerKey: PublicKey, nowEpochSeconds: Long): String = {
    if (!AdminAssertion.mayAdminister(bearer, trustedIssuerKey, nowEpochSeconds))
      throw new SecurityException("administrator assertion required")
    "administration-enabled"
  }
}
```

### Derivation

```json
{
  "group": "federated-admin-assertion-unverified-signature",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around authorize the administration panel only with a valid issuer-signed unexpired admin assertion. Boundary: Remote bearer-token claims are trusted after base64/JSON decoding without cryptographic verification. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "signature-verification",
    "cwe": "CWE-347",
    "path": "AdminAssertion.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Trusted key and clock are explicit; malformed-token denial-of-service is constrained by the byte limit and edge error mapping."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authorize the administration panel only with a valid issuer-signed unexpired admin assertion.",
  "trust_boundary": "Remote bearer-token claims are trusted after base64/JSON decoding without cryptographic verification.",
  "legitimate_examples": [
    {
      "input": "Valid signed unexpired admin assertion",
      "expected": "administration-enabled"
    },
    {
      "input": "Valid signed non-admin assertion",
      "expected": "Denied"
    }
  ],
  "permitted_changes": [
    "Verify the Ed25519 signature over the exact protected header and payload, enforce the allowed algorithm/issuer, then evaluate claims."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not delete role/expiry checks, accept alg=none, or replace signature verification with decoding or hashing alone."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/security/Signature.html",
    "https://www.rfc-editor.org/rfc/rfc7515"
  ]
}
```

### Regression traps

```json
[
  "Do not delete role/expiry checks, accept alg=none, or replace signature verification with decoding or hashing alone."
]
```

### Remediation constraints

```json
[
  "Authorize the administration panel only with a valid issuer-signed unexpired admin assertion.",
  "Verify the Ed25519 signature over the exact protected header and payload, enforce the allowed algorithm/issuer, then evaluate claims.",
  "Do not delete role/expiry checks, accept alg=none, or replace signature verification with decoding or hashing alone."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-04",
  "prior_case_id": "scala-integrity-hash-vulnerable",
  "prior_source_sha256": "da145aa8a4608384db07278ecc052e02168bed553f8a8b819cea948651f94b5c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "ujson3.3.1. Issuer uses Ed25519 compact JWS assertions with aud,role,exp claims; the server has the authentic issuer public key and a trusted clock. Edge maps malformed input to401. No upstream component verifies the signature."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-05 — notification-callback-unrestricted-url

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `6585e059beba6d98c03878c0e607312eda521c812b2ab862c365756b927628af`. Protocol-2.0 case hash: `044dd3af0953646164b3c283c6ff4f0799acdc2eadac0c936647c3c79eb118f0`.

An HTTP/HTTPS scheme allow-list does not exclude loopback, link-local or private destinations. Response status gives a concrete internal reachability oracle even though the body is discarded.

### DeliveryProbe.scala

```scala
import java.net.URI
import java.net.http.{HttpClient, HttpRequest, HttpResponse}
import java.time.Duration
object DeliveryProbe {
  private val client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()
  def probe(callback: String): Int = {
    val uri = URI.create(callback)
    require(Set("http", "https").contains(uri.getScheme))
    val request = HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(2)).GET().build()
    client.send(request, HttpResponse.BodyHandlers.discarding()).statusCode()
  }
}
```

### Registration.scala

```scala
object Registration {
  def preview(form: Map[String, String]): String = {
    val result = DeliveryProbe.probe(form("callback"))
    "Remote status: " + result
  }
}
```

### Derivation

```json
{
  "group": "notification-callback-unrestricted-url",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around probe a tenant callback and report status before registration. Boundary: Tenant URL is fetched by the privileged server after checking only the scheme. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "ssrf",
    "cwe": "CWE-918",
    "path": "DeliveryProbe.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "No redirect following is configured; the direct network destination remains unrestricted. Trusted egress enforcement may be a valid deployment-backed remediation if explicitly verifiable."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Probe a tenant callback and report status before registration.",
  "trust_boundary": "Tenant URL is fetched by the privileged server after checking only the scheme.",
  "legitimate_examples": [
    {
      "input": "Public HTTPS callback returns204",
      "expected": "Remote status: 204"
    },
    {
      "input": "Public HTTPS endpoint with path/query",
      "expected": "Preserve that endpoint path/query"
    }
  ],
  "permitted_changes": [
    "Enforce the public HTTPS callback policy, including DNS/address and redirect behavior, without blocking all public tenant endpoints."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not claim hostname text checks alone prevent DNS rebinding, or return a fabricated healthy status."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpClient.html"
  ]
}
```

### Regression traps

```json
[
  "Do not claim hostname text checks alone prevent DNS rebinding, or return a fabricated healthy status."
]
```

### Remediation constraints

```json
[
  "Probe a tenant callback and report status before registration.",
  "Enforce the public HTTPS callback policy, including DNS/address and redirect behavior, without blocking all public tenant endpoints.",
  "Do not claim hostname text checks alone prevent DNS rebinding, or return a fabricated healthy status."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-05",
  "prior_case_id": "scala-system-query-vulnerable",
  "prior_source_sha256": "04b52457bbb2848526c4c07f91322908fd157719259e0cff1a97d172c43e7542",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "Server has network routes to public HTTPS services and private management networks; callback authors are untrusted tenants. Successful registration permits public HTTPS callback origins only, not arbitrary internal endpoints."
}
```

### Split

```json
"held_out"
```

## v2-scala-vulnerable-06 — legacy-vault-pbe-low-work-factor

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `549e44a74dedf7860847cd2f9ec1e3444577cf7aba9462733e28e0c3136c8698`. Protocol-2.0 case hash: `7248358ba1e0b0ca51705f4abb824e32c42fabd3f073e01d8457c39ffb299115`.

A fresh salt does not make DES or a 100-iteration legacy KDF adequate against offline attacks. Key strength and work factor are explicitly visible rather than inferred from a harmless hash mention.

### VaultEnvelope.scala

```scala
import javax.crypto.{Cipher, SecretKeyFactory}
import javax.crypto.spec.{PBEKeySpec, PBEParameterSpec}
object VaultEnvelope {
  def encrypt(note: Array[Byte], passphrase: Array[Char], salt: Array[Byte]): Array[Byte] = {
    require(note.length <= 4096 && salt.length == 8)
    val keySpec = new PBEKeySpec(passphrase)
    try {
      val key = SecretKeyFactory.getInstance("PBEWithMD5AndDES").generateSecret(keySpec)
      val cipher = Cipher.getInstance("PBEWithMD5AndDES")
      cipher.init(Cipher.ENCRYPT_MODE, key, new PBEParameterSpec(salt, 100))
      salt ++ cipher.doFinal(note)
    } finally { keySpec.clearPassword() }
  }
}
```

### Derivation

```json
{
  "group": "legacy-vault-pbe-low-work-factor",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around encrypt a private vault note under a user passphrase into a portable envelope. Boundary: Sensitive note bytes rely on legacy MD5/DES password-based encryption with only100 iterations. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-327",
    "path": "VaultEnvelope.scala"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Trusted salt generation is assumed; the defect is cryptographic construction, not predictability of the supplied salt."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Encrypt a private vault note under a user passphrase into a portable envelope.",
  "trust_boundary": "Sensitive note bytes rely on legacy MD5/DES password-based encryption with only100 iterations.",
  "legitimate_examples": [
    {
      "input": "UTF-8 note under a passphrase",
      "expected": "Portable encrypted envelope, no plaintext"
    },
    {
      "input": "Two encryptions with different salts",
      "expected": "Independent salt-prefixed envelopes"
    }
  ],
  "permitted_changes": [
    "Define a versioned strong KDF plus AEAD envelope, including salt/nonce storage and a migration reader."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not lose portability, use a global fixed salt/nonce, or return only a hash that cannot restore the note."
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
    "https://docs.oracle.com/en/java/javase/21/docs/specs/security/standard-names.html"
  ]
}
```

### Regression traps

```json
[
  "Do not lose portability, use a global fixed salt/nonce, or return only a hash that cannot restore the note."
]
```

### Remediation constraints

```json
[
  "Encrypt a private vault note under a user passphrase into a portable envelope.",
  "Define a versioned strong KDF plus AEAD envelope, including salt/nonce storage and a migration reader.",
  "Do not lose portability, use a global fixed salt/nonce, or return only a hash that cannot restore the note."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-scala-vulnerable-06",
  "prior_case_id": "scala-tls-hostnames-vulnerable",
  "prior_source_sha256": "513558a3b5f60c72119a44503767897ea4e85b4e9e00f888b50bbc9abdc48765",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Scala 2.13.14 on OpenJDK 21",
  "libraries_platform_setup": "SunJCE provider; caller generates a fresh8-byte salt with SecureRandom for each note and stores the complete returned envelope. Offline attacker can obtain ciphertext but not the user passphrase."
}
```

### Split

```json
"held_out"
```

