# java — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-java-safe-01 — municipal-map-page-sort-enum

Proposed label: **safe**. Human review: **pending**.

Source hash: `74d2f3961d7e71cc7708843aa1e89f091a46228c7f3949ed63dfcfce8f3669f0`. Protocol-2.0 case hash: `7c2e918aef5f978921a4700a01352626086f0e5910c6c33587b4cf1bf2f5e486`.

Although the SQL string is assembled, only closed switch literals enter identifier position and the numeric limit is bound. User text never becomes SQL grammar.

### MapPage.java

```java
import java.sql.Connection;
import java.util.ArrayList;
import java.util.List;
public final class MapPage {
    public static List<String> towns(Connection db, String order, int limit) throws Exception {
        String column = switch (order) {
            case "name" -> "name";
            case "population" -> "population";
            default -> throw new IllegalArgumentException("unsupported order");
        };
        if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit");
        String sql = "SELECT name FROM towns ORDER BY " + column + ", id LIMIT ?";
        try (var statement = db.prepareStatement(sql)) {
            statement.setInt(1, limit);
            try (var rows = statement.executeQuery()) {
                List<String> result = new ArrayList<>();
                while (rows.next()) result.add(rows.getString(1));
                return result;
            }
        }
    }
}
```

### Derivation

```json
{
  "group": "municipal-map-page-sort-enum",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around list public towns using one of two published sort orders and a bounded limit. Boundary: Untrusted sort names select trusted literal identifiers; the limit is bound as integer. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Connection, schema and public-data authorization are trusted; result strings are data for a separate JSON serializer."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List public towns using one of two published sort orders and a bounded limit.",
  "trust_boundary": "Untrusted sort names select trusted literal identifiers; the limit is bound as integer.",
  "legitimate_examples": [
    {
      "input": "order=population, limit=2",
      "expected": "Two lowest populations, stable by id"
    },
    {
      "input": "order=name; DROP TABLE towns",
      "expected": "Reject unsupported order"
    }
  ],
  "permitted_changes": [
    "Preserve closed identifier selection and parameter binding."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not try binding a column identifier as a value or alphabetize every requested order."
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
  "Do not try binding a column identifier as a value or alphabetize every requested order."
]
```

### Remediation constraints

```json
[
  "List public towns using one of two published sort orders and a bounded limit.",
  "Preserve closed identifier selection and parameter binding.",
  "Do not try binding a column identifier as a value or alphabetize every requested order."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-01",
  "prior_case_id": "java-customer-search-safe",
  "prior_source_sha256": "1f66b907b33d28cdb806cfe6d7c1f4d5f60368828987b45dee1ef6c41ee5077b",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "PostgreSQL 16 JDBC 42.7.4; towns(id,name,population) contains public map data; trusted connection initialization."
}
```

### Split

```json
"held_out"
```

## v2-java-safe-02 — offline-quiz-dom-reader

Proposed label: **safe**. Human review: **pending**.

Source hash: `1fdbf17cb1f65365314cf4bbea4b8071f1ac54618e5d3128b82198b2177c00cd`. Protocol-2.0 case hash: `f5698dc9b382489cdb6063306e648dcee93e4d97c72fb6a71010cdb29dcfda32`.

The parser is configured before use, disallows document types, blocks external protocols and includes, and has no permissive fallback. Ordinary predefined entities still yield text.

### QuizReader.java

```java
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.XMLConstants;
import java.io.ByteArrayInputStream;
public final class QuizReader {
    public static String question(byte[] upload) throws Exception {
        if (upload.length > 8192) throw new IllegalArgumentException("too large");
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        factory.setXIncludeAware(false);
        factory.setExpandEntityReferences(false);
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
        var doc = factory.newDocumentBuilder().parse(new ByteArrayInputStream(upload));
        return doc.getDocumentElement().getTextContent();
    }
}
```

### Derivation

```json
{
  "group": "offline-quiz-dom-reader",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around read a text question from bounded offline quiz xml. Boundary: The entire XML upload is untrusted; document types and external resolution are disabled before parsing. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Very large/deep inputs are governed by byte limit and JDK secure-processing limits; consumers render returned text rather than HTML."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a text question from bounded offline quiz XML.",
  "trust_boundary": "The entire XML upload is untrusted; document types and external resolution are disabled before parsing.",
  "legitimate_examples": [
    {
      "input": "<question>2 &lt; 3?</question>",
      "expected": "2 < 3?"
    },
    {
      "input": "A document containing a DOCTYPE",
      "expected": "Rejected upload"
    }
  ],
  "permitted_changes": [
    "Retain the data-only XML format and fail closed if a security setting is unsupported."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace the text result with serialized markup or reject all XML."
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
  "Do not replace the text result with serialized markup or reject all XML."
]
```

### Remediation constraints

```json
[
  "Read a text question from bounded offline quiz XML.",
  "Retain the data-only XML format and fail closed if a security setting is unsupported.",
  "Do not replace the text result with serialized markup or reject all XML."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-02",
  "prior_case_id": "java-xml-upload-safe",
  "prior_source_sha256": "f662df25646d5a49095c4938cdd05fda424737d03926c087f72605d7c5976798",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "JDK built-in Xerces; public quiz upload is limited to plain text XML with no DTD/schema. Parse exceptions are returned as a rejected upload, never retried with weaker options."
}
```

### Split

```json
"held_out"
```

## v2-java-safe-03 — release-signature-verification

Proposed label: **safe**. Human review: **pending**.

Source hash: `d9c9edee10ce59d05f594cf9cba4b038a1467ff8d4593bedace7a97ba90c27ab`. Protocol-2.0 case hash: `91ef26f69f08d708829b3d9178c747bfd13724c30f706f573f55c670ef3ee5fc`.

A keyed signature verification gates the consumer and operates on the same bytes it returns. Algorithm selection and trust root are not attacker controlled.

### ReleaseVerifier.java

```java
import java.security.PublicKey;
import java.security.Signature;
public final class ReleaseVerifier {
    public static boolean eligible(byte[] manifest, byte[] detachedSignature, PublicKey pinnedKey) throws Exception {
        if (manifest.length > 65536 || detachedSignature.length != 64) return false;
        Signature verifier = Signature.getInstance("Ed25519");
        verifier.initVerify(pinnedKey);
        verifier.update(manifest);
        return verifier.verify(detachedSignature);
    }
}
```

### Updater.java

```java
import java.security.PublicKey;
public final class Updater {
    public static byte[] acceptedManifest(byte[] bytes, byte[] signature, PublicKey bundledKey) throws Exception {
        if (!ReleaseVerifier.eligible(bytes, signature, bundledKey))
            throw new SecurityException("invalid release signature");
        return bytes.clone();
    }
}
```

### Derivation

```json
{
  "group": "release-signature-verification",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around release only an authenticated manifest to the updater. Boundary: Attacker can modify downloaded manifest/signature but cannot replace the pinned public key. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Freshness/rollback is explicitly enforced outside this excerpt; key distribution is a trusted setup input."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Release only an authenticated manifest to the updater.",
  "trust_boundary": "Attacker can modify downloaded manifest/signature but cannot replace the pinned public key.",
  "legitimate_examples": [
    {
      "input": "Correctly signed manifest",
      "expected": "Returns identical bytes"
    },
    {
      "input": "Same signature with changed manifest byte",
      "expected": "Rejects manifest"
    }
  ],
  "permitted_changes": [
    "Preserve exact-byte verification and fail closed on invalid signatures."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not hash instead of verify a signature or reserialize before checking it."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/security/Signature.html"
  ]
}
```

### Regression traps

```json
[
  "Do not hash instead of verify a signature or reserialize before checking it."
]
```

### Remediation constraints

```json
[
  "Release only an authenticated manifest to the updater.",
  "Preserve exact-byte verification and fail closed on invalid signatures.",
  "Do not hash instead of verify a signature or reserialize before checking it."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-03",
  "prior_case_id": "java-session-restore-safe",
  "prior_source_sha256": "a411152b0584b11979efe161758951b89d8560c1b467d7fa133c50149ccf4ba1",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Trusted Ed25519 public key is embedded by signed application distribution, not delivered in the release response. Manifest signature covers the exact downloaded bytes; rollback policy is checked by a separate trusted version gate."
}
```

### Split

```json
"held_out"
```

## v2-java-safe-04 — printer-text-through-standard-input

Proposed label: **safe**. Human review: **pending**.

Source hash: `8109c751a9b40d2a766e72e625268265bfc4ac2ffbe3344046d310340cbb4b56`. Protocol-2.0 case hash: `61bd33b85f1ac6a6b3cd32f09943e333e30e1aa18caf38295c13c1cd7a5063cf`.

No shell or argument interpolation consumes the user text. The process is awaited and its input is closed, preserving a meaningful operation rather than an echo-only placeholder.

### LabelPrinter.java

```java
import java.nio.charset.StandardCharsets;
public final class LabelPrinter {
    public static int print(String text) throws Exception {
        if (text.length() > 1024) throw new IllegalArgumentException("label too long");
        Process printer = new ProcessBuilder("/usr/bin/lp", "-d", "shipping-labels")
                .redirectOutput(ProcessBuilder.Redirect.DISCARD)
                .redirectError(ProcessBuilder.Redirect.DISCARD).start();
        try (var input = printer.getOutputStream()) {
            input.write(text.getBytes(StandardCharsets.UTF_8));
        }
        return printer.waitFor();
    }
}
```

### Derivation

```json
{
  "group": "printer-text-through-standard-input",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around print exactly the supplied bounded text to the shipping label queue and return its exit status. Boundary: Form text is written to the child standard input; executable, queue and arguments are constants. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Printer control-language execution is disabled by the stated raw-text queue contract; user authorization and trusted executable ownership are deployment prerequisites."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Print exactly the supplied bounded text to the shipping label queue and return its exit status.",
  "trust_boundary": "Form text is written to the child standard input; executable, queue and arguments are constants.",
  "legitimate_examples": [
    {
      "input": "Handle with care; fragile",
      "expected": "One literal text label"
    },
    {
      "input": "-o media=A4",
      "expected": "Literal label text, no printer option change"
    }
  ],
  "permitted_changes": [
    "Keep text on stdin and keep fixed printer selection."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not split text into command arguments, drop Unicode, or stop returning the process status."
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
  "Do not split text into command arguments, drop Unicode, or stop returning the process status."
]
```

### Remediation constraints

```json
[
  "Print exactly the supplied bounded text to the shipping label queue and return its exit status.",
  "Keep text on stdin and keep fixed printer selection.",
  "Do not split text into command arguments, drop Unicode, or stop returning the process status."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-04",
  "prior_case_id": "java-legacy-digest-safe",
  "prior_source_sha256": "17411e6758087b4caed1502e5d69eb836a0e131a6ceefa68fab44897b570da13",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Linux CUPS lp; fixed trusted queue configured in raw text mode without document-language interpretation. This operation is offered only to authenticated warehouse staff with print permission."
}
```

### Split

```json
"held_out"
```

## v2-java-safe-05 — signed-bundle-public-resource-selector

Proposed label: **safe**. Human review: **pending**.

Source hash: `1c6da44fc9d050385093627570b60482604c7aaaa2f3e051576bb899c40bb62a`. Protocol-2.0 case hash: `d4df4c1a9aa3e693ce49d74564564c93a5f732aaf58a786c85807edf859e54e5`.

A closed map selects public immutable resources; no user path concatenation or filesystem traversal occurs. The restricted IDs are the original public API, not a remediation that narrows a filename API.

### HelpResources.java

```java
import java.io.InputStream;
import java.util.Map;
public final class HelpResources {
    private static final Map<String, String> PAGES = Map.of(
            "install", "/public-help/install.txt",
            "licenses", "/public-help/licenses.txt");
    public static byte[] load(String pageId) throws Exception {
        String path = PAGES.get(pageId);
        if (path == null) throw new IllegalArgumentException("unknown help page");
        try (InputStream input = HelpResources.class.getResourceAsStream(path)) {
            if (input == null) throw new IllegalStateException("missing bundled page");
            return input.readAllBytes();
        }
    }
}
```

### Derivation

```json
{
  "group": "signed-bundle-public-resource-selector",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around serve one of two published help-page ids from bundled resources. Boundary: Untrusted page ID can choose only two constant public classpath paths. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Application jar and class loader are trusted; mapping intentionally contains no credentials or private resources."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Serve one of two published help-page IDs from bundled resources.",
  "trust_boundary": "Untrusted page ID can choose only two constant public classpath paths.",
  "legitimate_examples": [
    {
      "input": "install",
      "expected": "Bytes of public-help/install.txt"
    },
    {
      "input": "../secrets",
      "expected": "Rejected unknown page ID"
    }
  ],
  "permitted_changes": [
    "Maintain explicit published IDs and public-resource mapping."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not allow arbitrary classpath names or fabricate empty content when a resource is missing."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Class.html#getResourceAsStream(java.lang.String)"
  ]
}
```

### Regression traps

```json
[
  "Do not allow arbitrary classpath names or fabricate empty content when a resource is missing."
]
```

### Remediation constraints

```json
[
  "Serve one of two published help-page IDs from bundled resources.",
  "Maintain explicit published IDs and public-resource mapping.",
  "Do not allow arbitrary classpath names or fabricate empty content when a resource is missing."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-05",
  "prior_case_id": "java-support-shell-safe",
  "prior_source_sha256": "2692612a70c02fbe2f69a3139be0baa892a74f4a8ea61dd05358161cf975f8cb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Resources are immutable public text inside a trusted signed application jar; no plugins or user-controlled class loaders. Resource sizes are bounded at packaging."
}
```

### Split

```json
"held_out"
```

## v2-java-safe-06 — public-http-status-with-standard-client

Proposed label: **safe**. Human review: **pending**.

Source hash: `a1129fa54748e70e1af1ebed406580572a23409c09d5938c225295e398625c84`. Protocol-2.0 case hash: `ce9e70066131ac29fc05f71f23fba2b0edf675ce21429889cf089ba3d2c4b929`.

The client uses default certificate/hostname verification and refuses redirects. No caller-controlled destination, permissive trust callback, or secret response content exists.

### TransitStatus.java

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
public final class TransitStatus {
    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .followRedirects(HttpClient.Redirect.NEVER).build();
    public static int status() throws Exception {
        var request = HttpRequest.newBuilder(URI.create("https://transit.example.org/status"))
                .timeout(Duration.ofSeconds(3)).GET().build();
        return CLIENT.send(request, HttpResponse.BodyHandlers.discarding()).statusCode();
    }
}
```

### Derivation

```json
{
  "group": "public-http-status-with-standard-client",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around return the public transit service http status without downloading its body. Boundary: The network is untrusted; a fixed HTTPS URL is authenticated by the standard client. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "CA compromise and operator DNS ownership are trust-store/domain assumptions, not suppressed source vulnerabilities."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the public transit service HTTP status without downloading its body.",
  "trust_boundary": "The network is untrusted; a fixed HTTPS URL is authenticated by the standard client.",
  "legitimate_examples": [
    {
      "input": "Trusted endpoint returns 204",
      "expected": 204
    },
    {
      "input": "Untrusted certificate",
      "expected": "TLS exception, not a success status"
    }
  ],
  "permitted_changes": [
    "Retain TLS verification, timeouts and no-redirect policy."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not return 200 on connection failures or add insecure fallback for convenience."
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
  "Do not return 200 on connection failures or add insecure fallback for convenience."
]
```

### Remediation constraints

```json
[
  "Return the public transit service HTTP status without downloading its body.",
  "Retain TLS verification, timeouts and no-redirect policy.",
  "Do not return 200 on connection failures or add insecure fallback for convenience."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-safe-06",
  "prior_case_id": "java-hostname-check-safe",
  "prior_source_sha256": "48ffadfe494c741ca583500c43f599143bea4dcb952feff2934f9c4c59749525",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "System trust store managed by deployment; no global SSL overrides or proxies controlled by users. Status host is operator-owned public service."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-01 — forum-label-filter-native-query

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `f08d71d865e8142605834d845f087589460ac9ba2f3d906389b1afd7a49ffcab`. Protocol-2.0 case hash: `05a9ae7fe8fa6252895ce5907df0be8aaf56433044b886e6939cec45ecf935b6`.

The bound on length does not separate SQL syntax from the label inserted into the WHERE expression. Native-query execution reaches the server; no ORM escaping is applied to the concatenated clause.

### LabelSearch.java

```java
import org.hibernate.Session;
import java.util.List;
public final class LabelSearch {
    public static List<String> search(Session session, String label) {
        String clause = "label = '" + label + "'";
        String sql = "SELECT title FROM public_topics WHERE " + clause + " ORDER BY id";
        return session.createNativeQuery(sql, String.class).getResultList();
    }
}
```

### ForumEndpoint.java

```java
import org.hibernate.Session;
import java.util.List;
import java.util.Map;
public final class ForumEndpoint {
    public static List<String> get(Session session, Map<String, String> query) {
        String label = query.getOrDefault("label", "general");
        if (label.length() > 80) throw new IllegalArgumentException("label too long");
        return LabelSearch.search(session, label);
    }
}
```

### Derivation

```json
{
  "group": "forum-label-filter-native-query",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around return titles in id order for one exact public-topic label. Boundary: An unauthenticated query parameter becomes Hibernate native SQL text. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "LabelSearch.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Only public_topics is exposed by this operation; database account and Session creation are trusted. No raw SQL supplied by operators is required."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return titles in ID order for one exact public-topic label.",
  "trust_boundary": "An unauthenticated query parameter becomes Hibernate native SQL text.",
  "legitimate_examples": [
    {
      "input": "label=release notes",
      "expected": "Titles labeled release notes, in ID order"
    },
    {
      "input": "label=author's picks",
      "expected": "Exact apostrophe-containing label is supported"
    }
  ],
  "permitted_changes": [
    "Bind label as a native-query parameter while retaining ordering and exact-match semantics."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not strip apostrophes, change equality to substring matching, or return every topic."
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
    "https://docs.jboss.org/hibernate/orm/6.6/userguide/html_single/Hibernate_User_Guide.html#sql"
  ]
}
```

### Regression traps

```json
[
  "Do not strip apostrophes, change equality to substring matching, or return every topic."
]
```

### Remediation constraints

```json
[
  "Return titles in ID order for one exact public-topic label.",
  "Bind label as a native-query parameter while retaining ordering and exact-match semantics.",
  "Do not strip apostrophes, change equality to substring matching, or return every topic."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-01",
  "prior_case_id": "java-customer-search-vulnerable",
  "prior_source_sha256": "60055bef017a84ea343831982ea831981a2c61cc29170f023e6f158a192a2d83",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Hibernate ORM 6.6.4.Final, PostgreSQL 16; public_topics(id bigint,title text,label text) seeded with public and draft labels; Session is server-owned. Endpoint adapter supplies untrusted decoded query parameters."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-02 — warehouse-stax-import-external-entities

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `2868158dabbd9117394354fcaad7d622da0d11b5e8dc70785b3b74633108f3e1`. Protocol-2.0 case hash: `5d917c8e1da7667983a42949abffec38ea668cfb1ca81af08fd16a1be1fad925`.

The explicit parser settings permit external entity replacement and external DTD access, so a small upload can make the preview expose local or network resource content. This does not depend on version-specific default settings.

### InventoryImport.java

```java
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.XMLConstants;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
public final class InventoryImport {
    public static List<String> skuNames(InputStream upload) throws Exception {
        XMLInputFactory factory = XMLInputFactory.newFactory();
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, true);
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, true);
        factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "all");
        var reader = factory.createXMLStreamReader(upload);
        List<String> names = new ArrayList<>();
        try {
            while (reader.hasNext()) {
                if (reader.next() == XMLStreamConstants.START_ELEMENT && reader.getLocalName().equals("sku"))
                    names.add(reader.getElementText());
            }
            return names;
        } finally { reader.close(); }
    }
}
```

### UploadController.java

```java
import java.io.ByteArrayInputStream;
import java.util.List;
public final class UploadController {
    public static List<String> preview(byte[] authenticatedPartnerUpload) throws Exception {
        if (authenticatedPartnerUpload.length > 65536) throw new IllegalArgumentException("upload too large");
        return InventoryImport.skuNames(new ByteArrayInputStream(authenticatedPartnerUpload));
    }
}
```

### Derivation

```json
{
  "group": "warehouse-stax-import-external-entities",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around preview sku text from a partner inventory xml document without resolving external resources. Boundary: Partner XML is parsed with external entity resolution and all external DTD protocols enabled. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "InventoryImport.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Ingress enforces upload size; XML depth/resource limits still need maintainers to confirm against production input policies."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Preview SKU text from a partner inventory XML document without resolving external resources.",
  "trust_boundary": "Partner XML is parsed with external entity resolution and all external DTD protocols enabled.",
  "legitimate_examples": [
    {
      "input": "<stock><sku>A&amp;B</sku></stock>",
      "expected": [
        "A&B"
      ]
    },
    {
      "input": "<stock><sku>office paper</sku><sku>胶水</sku></stock>",
      "expected": [
        "office paper",
        "胶水"
      ]
    }
  ],
  "permitted_changes": [
    "Disable DTD/external resolution and reject documents requiring external entities."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not remove ordinary escaped ampersands, Unicode text, or multi-item previews."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.xml/javax/xml/stream/XMLInputFactory.html"
  ]
}
```

### Regression traps

```json
[
  "Do not remove ordinary escaped ampersands, Unicode text, or multi-item previews."
]
```

### Remediation constraints

```json
[
  "Preview SKU text from a partner inventory XML document without resolving external resources.",
  "Disable DTD/external resolution and reject documents requiring external entities.",
  "Do not remove ordinary escaped ampersands, Unicode text, or multi-item previews."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-02",
  "prior_case_id": "java-xml-upload-vulnerable",
  "prior_source_sha256": "86597e0f92bf6444cc685b86a6c2d14216cf83351064fac499c4d15464c0d0fb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "JDK default StAX implementation; no jaxp.properties override. Partner can submit XML but cannot read application filesystem. Import previews are returned to that partner."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-03 — desktop-shared-layout-bean-decoder

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `a49b871377f715343ccf0e6e7d440a791f5a86eefd1e9f0c34f1d64edbeaf2cf`. Protocol-2.0 case hash: `20b11c27ed7a58af56281b75b383ac46597be3428b194a32d8e2a5c55c703713`.

XMLDecoder instantiates beans and invokes methods while reading. Checking that the final object is a Point occurs after those effects. Merely filtering the cast does not constrain the instruction language.

### LayoutRestore.java

```java
import java.beans.XMLDecoder;
import java.io.ByteArrayInputStream;
import java.awt.Point;
public final class LayoutRestore {
    public static Point restore(byte[] sharedLayout) {
        if (sharedLayout.length > 32768) throw new IllegalArgumentException("layout too large");
        try (XMLDecoder decoder = new XMLDecoder(new ByteArrayInputStream(sharedLayout))) {
            Object value = decoder.readObject();
            if (!(value instanceof Point)) throw new IllegalArgumentException("expected point");
            return (Point) value;
        }
    }
}
```

### LayoutAction.java

```java
import java.awt.Point;
public final class LayoutAction {
    public static String openAttachment(byte[] attachmentFromCoworker) {
        Point location = LayoutRestore.restore(attachmentFromCoworker);
        return location.x + "," + location.y;
    }
}
```

### Derivation

```json
{
  "group": "desktop-shared-layout-bean-decoder",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around restore the window origin from a shared legacy layout and render x,y. Boundary: A document sender controls the XMLDecoder instruction stream before the Point type check. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "LayoutRestore.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The test requires instruction-stream safety, not proof of one installed third-party gadget; java.beans method invocation is intrinsic."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Restore the window origin from a shared legacy layout and render x,y.",
  "trust_boundary": "A document sender controls the XMLDecoder instruction stream before the Point type check.",
  "legitimate_examples": [
    {
      "input": "XMLEncoder Point(40,80) document",
      "expected": "40,80"
    },
    {
      "input": "XMLEncoder Point(-12,0) document",
      "expected": "-12,0"
    }
  ],
  "permitted_changes": [
    "Implement a data-only reader for the documented Point subset, or provide an explicit format migration preserving coordinate imports."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not return raw XML text or reject all legacy coordinates; negative coordinates are valid."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.desktop/java/beans/XMLDecoder.html"
  ]
}
```

### Regression traps

```json
[
  "Do not return raw XML text or reject all legacy coordinates; negative coordinates are valid."
]
```

### Remediation constraints

```json
[
  "Restore the window origin from a shared legacy layout and render x,y.",
  "Implement a data-only reader for the documented Point subset, or provide an explicit format migration preserving coordinate imports.",
  "Do not return raw XML text or reject all legacy coordinates; negative coordinates are valid."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-03",
  "prior_case_id": "java-session-restore-vulnerable",
  "prior_source_sha256": "49ac7a28f1dcd130b6199da1d57b19222af2992236ba658c1031def7c0cb6144",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Desktop java.desktop module available; a user opens an untrusted shared layout attachment. No sandbox or SecurityManager is installed. Legacy supported documents contain one java.awt.Point encoded by XMLEncoder."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-04 — payment-confirmation-trust-manager

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `653dfad2aaff2705b827feff1cbe118b561dba2a7c7858f416a8469af6b23d3f`. Protocol-2.0 case hash: `0a2fcf651cb7c8f26fdd0cf57eef94e0a2a6e02d541c3ed22c096cb88698ae40`.

The configured TrustManager accepts every server chain, so hostname matching alone cannot authenticate the peer. The returned body has a concrete financial consumer.

### GatewayClient.java

```java
import javax.net.ssl.*;
import java.net.URI;
import java.security.cert.X509Certificate;
import java.nio.charset.StandardCharsets;
public final class GatewayClient {
    public static String confirmation(String paymentId) throws Exception {
        X509TrustManager trust = new X509TrustManager() {
            public void checkClientTrusted(X509Certificate[] chain, String authType) { }
            public void checkServerTrusted(X509Certificate[] chain, String authType) { }
            public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }
        };
        SSLContext context = SSLContext.getInstance("TLS");
        context.init(null, new TrustManager[]{trust}, null);
        var url = URI.create("https://payments.example.org/confirmation/" + paymentId).toURL();
        HttpsURLConnection connection = (HttpsURLConnection) url.openConnection();
        connection.setSSLSocketFactory(context.getSocketFactory());
        connection.setConnectTimeout(3000);
        connection.setReadTimeout(3000);
        try (var input = connection.getInputStream()) {
            return new String(input.readNBytes(8192), StandardCharsets.UTF_8);
        } finally { connection.disconnect(); }
    }
}
```

### Settlement.java

```java
public final class Settlement {
    public static boolean paid(long paymentId) throws Exception {
        return GatewayClient.confirmation(Long.toUnsignedString(paymentId)).equals("settled");
    }
}
```

### Derivation

```json
{
  "group": "payment-confirmation-trust-manager",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around read an authenticated settlement status for a numeric payment id. Boundary: An on-path attacker controls the HTTPS peer chain and response used to mark a payment settled. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "GatewayClient.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The endpoint and ID are trusted; URL injection is not part of this case. Response protocol is deliberately exact and bounded."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read an authenticated settlement status for a numeric payment ID.",
  "trust_boundary": "An on-path attacker controls the HTTPS peer chain and response used to mark a payment settled.",
  "legitimate_examples": [
    {
      "input": "paymentId=812, gateway body settled",
      "expected": true
    },
    {
      "input": "paymentId=813, gateway body pending",
      "expected": false
    }
  ],
  "permitted_changes": [
    "Use system trust roots or a deployment-provided CA with full chain and hostname validation."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not hardcode settled/pending, remove the gateway call, or accept any certificate on fallback."
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
    "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html"
  ]
}
```

### Regression traps

```json
[
  "Do not hardcode settled/pending, remove the gateway call, or accept any certificate on fallback."
]
```

### Remediation constraints

```json
[
  "Read an authenticated settlement status for a numeric payment ID.",
  "Use system trust roots or a deployment-provided CA with full chain and hostname validation.",
  "Do not hardcode settled/pending, remove the gateway call, or accept any certificate on fallback."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-04",
  "prior_case_id": "java-legacy-digest-vulnerable",
  "prior_source_sha256": "65df3ed33660f1ff5515fa3f1d0c6cfa1e273f37fb41830570a868d9662fad07",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "JSSE default implementation; valid numeric IDs originate in trusted database. Network attacker can present an untrusted certificate containing payments.example.org; default hostname verifier still runs."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-05 — membership-password-verifier-md5

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `b5729d0f1abf08c936f0e3ef79c8b0ea6978d45c4b67d0eb79ebf11d006dd2d3`. Protocol-2.0 case hash: `16a20c9c20094f9f2ef2c2f86d47bbc1abb10f4d32a8859ba98b06cdc5002728`.

MD5 is used as an actual password verifier rather than a non-security checksum. Fast unsalted hashing permits efficient offline guessing; changing only the digest spelling to SHA-256 would retain that weakness.

### PasswordStore.java

```java
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
public final class PasswordStore {
    public static String enroll(String password) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("MD5")
                .digest(password.getBytes(StandardCharsets.UTF_8)));
    }
    public static boolean authenticate(String submitted, String storedDigest) throws Exception {
        byte[] actual = enroll(submitted).getBytes(StandardCharsets.US_ASCII);
        return MessageDigest.isEqual(actual, storedDigest.getBytes(StandardCharsets.US_ASCII));
    }
}
```

### LoginService.java

```java
public final class LoginService {
    public static boolean login(String formPassword, String digestLoadedForUser) throws Exception {
        if (formPassword.length() > 1024) return false;
        return PasswordStore.authenticate(formPassword, digestLoadedForUser);
    }
}
```

### Derivation

```json
{
  "group": "membership-password-verifier-md5",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around authenticate existing members and enroll new passwords using stored verifiers. Boundary: User-chosen low-entropy passwords are protected only by a fast unsalted digest in a database readable after breach. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-916",
    "path": "PasswordStore.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Constant-time byte comparison is already used; rate limiting does not address offline verifier attacks."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authenticate existing members and enroll new passwords using stored verifiers.",
  "trust_boundary": "User-chosen low-entropy passwords are protected only by a fast unsalted digest in a database readable after breach.",
  "legitimate_examples": [
    {
      "input": "correct Unicode password for an enrolled account",
      "expected": true
    },
    {
      "input": "different password",
      "expected": false
    }
  ],
  "permitted_changes": [
    "Use a salted adaptive password KDF with versioned verifier records and an explicit legacy-login migration."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not invalidate all existing members without migration, normalize passwords, or silently truncate them."
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
  "Do not invalidate all existing members without migration, normalize passwords, or silently truncate them."
]
```

### Remediation constraints

```json
[
  "Authenticate existing members and enroll new passwords using stored verifiers.",
  "Use a salted adaptive password KDF with versioned verifier records and an explicit legacy-login migration.",
  "Do not invalidate all existing members without migration, normalize passwords, or silently truncate them."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-05",
  "prior_case_id": "java-support-shell-vulnerable",
  "prior_source_sha256": "482903a19170d9d77db5add04af75293674df20f17c1c8c77e374f3532edbd7c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "UTF-8 passwords; digest column stores lowercase hex of legacy MD5. Application uses TLS and online throttling. Threat is an attacker obtaining the database verifier column."
}
```

### Split

```json
"held_out"
```

## v2-java-vulnerable-06 — image-watermark-shell-caption

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `bc7f8c08eb5585817222ec756af504eb42896d626acbe2639ce5a30db9529667`. Protocol-2.0 case hash: `eeb179e9a5677a31eb34b1e203f6754f37543072491aa2d9f3406553d0bc8bcf`.

A quote in the caption ends the shell literal before ProcessBuilder starts /bin/sh. Trusted image paths and a length limit do not protect the distinct caption boundary.

### Watermark.java

```java
import java.io.IOException;
public final class Watermark {
    public static int render(String caption) throws IOException, InterruptedException {
        String command = "/usr/bin/convert /srv/job/input.png -set comment '" + caption
                + "' /srv/job/output.png";
        Process child = new ProcessBuilder("/bin/sh", "-c", command)
                .redirectOutput(ProcessBuilder.Redirect.DISCARD)
                .redirectError(ProcessBuilder.Redirect.DISCARD).start();
        return child.waitFor();
    }
}
```

### CaptionForm.java

```java
public final class CaptionForm {
    public static int submit(String caption) throws Exception {
        if (caption.length() > 120) throw new IllegalArgumentException("caption too long");
        return Watermark.render(caption);
    }
}
```

### Derivation

```json
{
  "group": "image-watermark-shell-caption",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around write a literal user caption into png comment metadata and return the child exit code. Boundary: The caption form is embedded into a shell command between single quotes. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "Watermark.java"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "ImageMagick delegates and image decoding vulnerabilities are excluded by trusted predecoded PNG and deployment policy; no path is supplied by the caller."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write a literal user caption into PNG comment metadata and return the child exit code.",
  "trust_boundary": "The caption form is embedded into a shell command between single quotes.",
  "legitimate_examples": [
    {
      "input": "A photographer's day",
      "expected": "Comment equals A photographer's day; success exit code"
    },
    {
      "input": "two words ; still caption",
      "expected": "Comment remains literal, with no additional command"
    }
  ],
  "permitted_changes": [
    "Invoke the executable using an argument list with the caption as the comment value and preserve process waiting/status."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not strip punctuation, use stdout as the success code, or replace the running JVM on success."
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
  "Do not strip punctuation, use stdout as the success code, or replace the running JVM on success."
]
```

### Remediation constraints

```json
[
  "Write a literal user caption into PNG comment metadata and return the child exit code.",
  "Invoke the executable using an argument list with the caption as the comment value and preserve process waiting/status.",
  "Do not strip punctuation, use stdout as the success code, or replace the running JVM on success."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-java-vulnerable-06",
  "prior_case_id": "java-hostname-check-vulnerable",
  "prior_source_sha256": "aa53de27727156d7c66a06c0deddc8ad2612e7060cd3f29fd63654e84ccfb0d8",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "OpenJDK 21; Java source level 21",
  "libraries_platform_setup": "Linux; trusted ImageMagick executable and policy disallow delegates/network. A per-request private job directory supplies trusted PNG input and output. Caption is untrusted metadata, not an ImageMagick expression."
}
```

### Split

```json
"held_out"
```

