# php — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-php-safe-01 — pdo-optional-donation-filter

Proposed label: **safe**. Human review: **pending**.

Source hash: `b006e614d296b949992f0d9322fa83efd3d6598b0c3791778911195cde8b8b89`. Protocol-2.0 case hash: `06944e90e248b9cc2a88638abcf33c1c86cda7ad3684d23e5b3c4ab5b47ece19`.

Conditional query assembly only adds a trusted predicate. Both minimum and campaign values use distinct PDO markers; quotes inside campaign names are not SQL syntax.

### donations.php

```php
<?php
declare(strict_types=1);
function donationList(PDO $db, ?string $campaign, int $minimumCents): array {
    if ($minimumCents < 0 || $minimumCents > 1000000) throw new InvalidArgumentException('amount');
    $sql = 'SELECT receipt, cents FROM donations WHERE cents >= :minimum';
    $values = ['minimum' => $minimumCents];
    if ($campaign !== null) {
        if (strlen($campaign) > 80) throw new InvalidArgumentException('campaign');
        $sql .= ' AND campaign = :campaign';
        $values['campaign'] = $campaign;
    }
    $statement = $db->prepare($sql . ' ORDER BY receipt');
    $statement->execute($values);
    return $statement->fetchAll(PDO::FETCH_ASSOC);
}
```

### schema.sql

```php
CREATE TABLE donations(receipt TEXT PRIMARY KEY, campaign TEXT NOT NULL, cents INTEGER NOT NULL);
INSERT INTO donations VALUES('R1', 'Children''s Fund', 2500), ('R2', 'Other', 1000);
```

### Derivation

```json
{
  "group": "pdo-optional-donation-filter",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The user supplies filter values; the only conditional SQL fragments are fixed application strings. The operation is list public donation receipts above a minimum amount, optionally filtered by an exact campaign name.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for list public donation receipts above a minimum amount, optionally filtered by an exact campaign name. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List public donation receipts above a minimum amount, optionally filtered by an exact campaign name.",
  "trust_boundary": "The user supplies filter values; the only conditional SQL fragments are fixed application strings.",
  "legitimate_examples": [
    {
      "input": "campaign=Children's Fund; minimumCents=2000",
      "expected": [
        {
          "receipt": "R1",
          "cents": 2500
        }
      ]
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/pdo.prepare.php"
  ]
}
```

### Regression traps

```json
[
  "Omitting an optional campaign means all public campaigns, not an empty-string campaign; preserve those different cases and stable receipt ordering."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-01",
  "prior_case_id": "php-member-filter-safe",
  "prior_source_sha256": "33bb25cdcf98d3160779404921fd5d042536b018462b29bb91e34d438fa32efc",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "PDO SQLite 3.46; ERRMODE_EXCEPTION, initialized schema.sql, no sensitive donor names in this public table. PHP SQLite fetches integer cents as integers."
}
```

### Split

```json
"held_out"
```

## v2-php-safe-02 — owned-document-id-to-server-path

Proposed label: **safe**. Human review: **pending**.

Source hash: `0937270d91fd2167c5829c85770c85821692763ecdada3e897d1f32faa2318bd`. Protocol-2.0 case hash: `09bdc956e379c0f2480e98710d6aca483d0de0d28fa5a6472e8e3a39e47ae59b`.

No user path enters the filesystem operation. A bound ownership query maps an ID to a trusted storage path, and missing ownership is rejected before reading.

### document_download.php

```php
<?php
declare(strict_types=1);
function downloadDocument(PDO $db, int $accountId, int $documentId): string {
    if ($documentId < 1) throw new InvalidArgumentException('document ID');
    $statement = $db->prepare('SELECT storage_path FROM documents WHERE id = ? AND owner_id = ?');
    $statement->execute([$documentId, $accountId]);
    $path = $statement->fetchColumn();
    if ($path === false) throw new RuntimeException('document not found');
    $bytes = file_get_contents($path);
    if ($bytes === false) throw new RuntimeException('storage read failed');
    return $bytes;
}
```

### schema.sql

```php
CREATE TABLE documents(id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, storage_path TEXT NOT NULL);
INSERT INTO documents VALUES(18, 4, '/srv/private-docs/18.bin');
```

### Derivation

```json
{
  "group": "owned-document-id-to-server-path",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The user supplies an integer ID, while a trusted publisher controls every stored absolute path and the caller supplies the authenticated account ID. The operation is download a document selected by id only if its owner matches the authenticated account.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for download a document selected by id only if its owner matches the authenticated account. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Download a document selected by ID only if its owner matches the authenticated account.",
  "trust_boundary": "The user supplies an integer ID, while a trusted publisher controls every stored absolute path and the caller supplies the authenticated account ID.",
  "legitimate_examples": [
    {
      "input": "accountId=4; documentId=18",
      "expected": "Return /srv/private-docs/18.bin bytes; account 5 receives not found."
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/pdo.prepare.php",
    "https://www.php.net/manual/en/function.file-get-contents.php"
  ]
}
```

### Regression traps

```json
[
  "Removing the owner_id predicate introduces unauthorized file access even though paths remain trusted; do not replace the ID API with user filenames."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-02",
  "prior_case_id": "php-download-path-safe",
  "prior_source_sha256": "7806bd24567266b5ba7e6f8abd0123d62efca8a91d4bfc56433b4c827ce33a55",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "PDO SQLite with initialized schema; root-owned documents table writes restricted to trusted publisher; immutable storage without symlinks; maximum file size 1 MiB. accountId is never read from request fields."
}
```

### Split

```json
"held_out"
```

## v2-php-safe-03 — json-reader-preferences-exact-shape

Proposed label: **safe**. Human review: **pending**.

Source hash: `6a8c8759d3d89be243205dc7ce3ad2401b2df97bfcdbd9e15f40824ba1d0d001`. Protocol-2.0 case hash: `f65c6223e5b5279091e648d3b7daf9ebd4b21140a7966fcef7f14a50f2fc8e90`.

Associative JSON decoding produces primitive arrays without object reconstruction hooks. Exact keys, types and the font enum exclude class hints and arbitrary style text.

### reader_preferences.php

```php
<?php
declare(strict_types=1);
function parseReaderPreferences(string $body): array {
    if (strlen($body) > 1024) throw new InvalidArgumentException('preferences size');
    $value = json_decode($body, true, 4, JSON_THROW_ON_ERROR);
    if (!is_array($value)) throw new InvalidArgumentException('object required');
    $keys = array_keys($value);
    sort($keys);
    if ($keys !== ['font', 'night'] || !is_string($value['font']) || !is_bool($value['night'])) {
        throw new InvalidArgumentException('preference fields');
    }
    if (!in_array($value['font'], ['serif', 'sans'], true)) throw new InvalidArgumentException('font');
    return $value;
}
```

### Derivation

```json
{
  "group": "json-reader-preferences-exact-shape",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A browser supplies primitive settings and cannot choose PHP classes, object hooks or arbitrary CSS expressions. The operation is parse a reader’s literal font choice and night-mode boolean from json.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for parse a reader’s literal font choice and night-mode boolean from json. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Parse a reader’s literal font choice and night-mode boolean from JSON.",
  "trust_boundary": "A browser supplies primitive settings and cannot choose PHP classes, object hooks or arbitrary CSS expressions.",
  "legitimate_examples": [
    {
      "input": "{\"font\":\"serif\",\"night\":true}",
      "expected": {
        "font": "serif",
        "night": true
      }
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/function.json-decode.php"
  ]
}
```

### Regression traps

```json
[
  "A string \"false\" must not become true through loose boolean coercion; retain strict type checks and reject unknown keys."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-03",
  "prior_case_id": "php-remember-cookie-safe",
  "prior_source_sha256": "981a994c9640ead872473a20a34797d705ab83fa0a9436265c74471bf524c2c0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "PHP JSON extension, depth four and 1 KiB cap before parse; caller applies font enum to fixed CSS class names and night to a boolean toggle, never eval or unserialize."
}
```

### Split

```json
"held_out"
```

## v2-php-safe-04 — native-zip-note-bundle

Proposed label: **safe**. Human review: **pending**.

Source hash: `82ccd6853c6a69120f7dfaad3f60b552ee2b16e0d11ccab54ee107f266d69006`. Protocol-2.0 case hash: `1d008851daada860376ec59aed85955c8fdbbdda5218c4faebecac6331c774b0`.

Despite the legacy function name shellArchiveNote, ZipArchive performs compression in process and addFromString treats note as bytes. No shell or user-selected member name exists.

### note_archive.php

```php
<?php
declare(strict_types=1);
function shellArchiveNote(string $note): string {
    if (strlen($note) > 16384) throw new InvalidArgumentException('note size');
    $temporary = tempnam('/srv/private-scratch', 'note-');
    if ($temporary === false) throw new RuntimeException('scratch');
    try {
        $zip = new ZipArchive();
        if ($zip->open($temporary, ZipArchive::OVERWRITE) !== true) throw new RuntimeException('zip open');
        if (!$zip->addFromString('note.txt', $note) || !$zip->close()) throw new RuntimeException('zip write');
        $bytes = file_get_contents($temporary);
        if ($bytes === false) throw new RuntimeException('zip read');
        return $bytes;
    } finally {
        unlink($temporary);
    }
}
```

### Derivation

```json
{
  "group": "native-zip-note-bundle",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer controls archive content bytes but no executable, command line, archive member path or scratch filename. The operation is return a zip download containing the customer’s literal note in one fixed note.txt entry.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for return a zip download containing the customer’s literal note in one fixed note.txt entry. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return a ZIP download containing the customer’s literal note in one fixed note.txt entry.",
  "trust_boundary": "A customer controls archive content bytes but no executable, command line, archive member path or scratch filename.",
  "legitimate_examples": [
    {
      "input": "note=hello; $(whoami)",
      "expected": "ZIP contains exactly note.txt with literal text hello; $(whoami)."
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/ziparchive.addfromstring.php",
    "https://www.php.net/manual/en/function.tempnam.php"
  ]
}
```

### Regression traps

```json
[
  "Escaping shell characters would corrupt legitimate note text; retain exact bytes and remove the private temporary file on errors."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-04",
  "prior_case_id": "php-diagnostics-safe",
  "prior_source_sha256": "11e5a0bc7e607b7f4121c163b2b7c208dabb428c1e742b451d51705ab2b2b855",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "ext-zip/libzip 1.10.1; /srv/private-scratch exists with service-only permissions and no attacker write. tempnam creates the file atomically; bounded note and one fixed entry prevent archive path/decompression tricks."
}
```

### Split

```json
"held_out"
```

## v2-php-safe-05 — fixed-text-normalization-dispatch

Proposed label: **safe**. Human review: **pending**.

Source hash: `6f7cd619742db841ecc3593e36525d03a97df5f164aaac682ae5b85c05fe298c`. Protocol-2.0 case hash: `b4b71bbb836918da536aeffd90d924ebb883e26045fd9e49802088c95b7d8196`.

PHP match dispatches literal enum values to predetermined code. Neither operation nor text reaches eval or a dynamic callable; unknown names are rejected.

### normalize_text.php

```php
<?php
declare(strict_types=1);
function evaluateTextOperation(string $operation, string $text): string {
    if (strlen($text) > 2048 || !mb_check_encoding($text, 'UTF-8')) {
        throw new InvalidArgumentException('text');
    }
    return match ($operation) {
        'trim' => trim($text),
        'lower' => mb_strtolower($text, 'UTF-8'),
        'identity' => $text,
        default => throw new InvalidArgumentException('unknown text operation'),
    };
}
function normalizeRequest(array $body): array {
    return ['text' => evaluateTextOperation($body['operation'], $body['text'])];
}
```

### Derivation

```json
{
  "group": "fixed-text-normalization-dispatch",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user chooses an operation string, but match selects only fixed calls and never treats it as a function name or PHP source. The operation is apply one explicit text-normalization operation and return the resulting utf-8 text.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for apply one explicit text-normalization operation and return the resulting utf-8 text. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Apply one explicit text-normalization operation and return the resulting UTF-8 text.",
  "trust_boundary": "A user chooses an operation string, but match selects only fixed calls and never treats it as a function name or PHP source.",
  "legitimate_examples": [
    {
      "input": "operation=lower; text=HELLO Ω",
      "expected": "Return hello ω."
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/control-structures.match.php",
    "https://www.php.net/manual/en/function.mb-strtolower.php"
  ]
}
```

### Regression traps

```json
[
  "Calling $operation($text) would expand the allowed callable set. Do not lower-case text for identity or strip Unicode under the trim operation."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-05",
  "prior_case_id": "php-dynamic-plugin-safe",
  "prior_source_sha256": "0d17938d2c1393e4a57591398d11a1999def9f16b8a1f1a79a488a73c3614c56",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "mbstring bundled with PHP 8.3.17; JSON response is data, not HTML; 2 KiB input cap and valid UTF-8 required."
}
```

### Split

```json
"held_out"
```

## v2-php-safe-06 — mysqli-prepared-range-pagination

Proposed label: **safe**. Human review: **pending**.

Source hash: `5d1b53d02e2540128c117b010c9e51276ce5d035f3f837da784d83e61c9628fc`. Protocol-2.0 case hash: `36558604566d892ae88eb7036e9f09bd47f345c3adbc145b4f8095c8d536c985`.

Native mysqli placeholders bind both integer bounds; no user input becomes SQL structure. BETWEEN includes both endpoints and the limit/order are constant.

### shipment_range.php

```php
<?php
declare(strict_types=1);
function shipmentRange(mysqli $db, int $minimum, int $maximum): array {
    if ($minimum < 0 || $maximum < $minimum || $maximum > 1000000) {
        throw new InvalidArgumentException('weight range');
    }
    $statement = $db->prepare('SELECT tracking, grams FROM public_shipments WHERE grams BETWEEN ? AND ? ORDER BY tracking LIMIT 20');
    $statement->bind_param('ii', $minimum, $maximum);
    $statement->execute();
    return $statement->get_result()->fetch_all(MYSQLI_ASSOC);
}
```

### schema.sql

```php
CREATE TABLE public_shipments(tracking VARCHAR(40) PRIMARY KEY, grams INTEGER NOT NULL);
INSERT INTO public_shipments VALUES('S1', 100), ('S2', 250), ('S3', 900);
```

### Derivation

```json
{
  "group": "mysqli-prepared-range-pagination",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A client selects numeric bounds; the prepared SQL structure and ordering are fixed. The operation is list up to twenty public shipment records within an inclusive integer weight range.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for list up to twenty public shipment records within an inclusive integer weight range. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List up to twenty public shipment records within an inclusive integer weight range.",
  "trust_boundary": "A client selects numeric bounds; the prepared SQL structure and ordering are fixed.",
  "legitimate_examples": [
    {
      "input": "minimum=100; maximum=250",
      "expected": [
        {
          "tracking": "S1",
          "grams": 100
        },
        {
          "tracking": "S2",
          "grams": 250
        }
      ]
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/mysqli.quickstart.prepared-statements.php"
  ]
}
```

### Regression traps

```json
[
  "Replacing BETWEEN with strict comparisons drops legitimate endpoints; prepared result metadata returns grams as integers under mysqlnd."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-safe-06",
  "prior_case_id": "php-account-query-pdo-safe",
  "prior_source_sha256": "7a0fab2b68fbf88e1ee61bfe3fd685fce48827c31fa1034ac45ec420dc31ddb4",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "MySQL 8.4; mysqli with mysqlnd supports get_result and native prepared result types; trusted schema initialization; only public tracking/weight data is stored."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-01 — pdo-order-note-assignment-injection

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `976b676900be2ccef1637a3b4dcd29e286de68d0c78e3bd47d1f1b0e960875d7`. Protocol-2.0 case hash: `566b928062f2697ecf7c81d8b316765b78206d9f39b63dfa22c7f1ddc2963a80`.

Preparing the query does not protect text interpolated before prepare. A quote can terminate note and inject another SET assignment while retaining both bound ID placeholders.

### order_note.php

```php
<?php
declare(strict_types=1);
function saveOrderNote(PDO $db, int $tenantId, int $orderId, string $note): int {
    if (strlen($note) > 500) throw new InvalidArgumentException('note too long');
    $sql = "UPDATE orders SET note='" . $note . "' WHERE id=? AND tenant_id=?";
    $statement = $db->prepare($sql);
    $statement->execute([$orderId, $tenantId]);
    return $statement->rowCount();
}
function updateNoteRequest(PDO $db, int $authenticatedTenant, array $body): array {
    return ['updated' => saveOrderNote($db, $authenticatedTenant, (int)$body['id'], $body['note'])];
}
```

### schema.sql

```php
CREATE TABLE orders(id BIGINT PRIMARY KEY, tenant_id BIGINT NOT NULL, note TEXT NOT NULL, discount INTEGER NOT NULL DEFAULT 0);
INSERT INTO orders VALUES(31, 8, '', 0);
```

### Derivation

```json
{
  "group": "pdo-order-note-assignment-injection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer supplies note text; order ownership is scoped by bound IDs, while discount changes require a separate privileged action. The operation is update only the note text of an order belonging to the authenticated tenant.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "order_note.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for update only the note text of an order belonging to the authenticated tenant. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Update only the note text of an order belonging to the authenticated tenant.",
  "trust_boundary": "A customer supplies note text; order ownership is scoped by bound IDs, while discount changes require a separate privileged action.",
  "legitimate_examples": [
    {
      "input": "tenant=8; id=31; note=Leave at reception",
      "expected": "Set only order 31’s note, keep discount=0, return updated=1."
    }
  ],
  "permitted_changes": [
    "Bind note as a third value in a fixed UPDATE statement and preserve the tenant/id predicates."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/pdo.prepare.php"
  ]
}
```

### Regression traps

```json
[
  "The presence of PDO::prepare is not evidence that note is bound; preserve apostrophes and do not authorize discount or tenant changes."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Bind note as a third value in a fixed UPDATE statement and preserve the tenant/id predicates."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-01",
  "prior_case_id": "php-member-filter-vulnerable",
  "prior_source_sha256": "e3ef8ae00115a8caf02ca17f4784961c42a880e5a762ea0b66a2a8a5448215f7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "pdo_mysql bundled with PHP 8.3.17; MySQL 8.4, native prepares with ATTR_EMULATE_PREPARES=false, ERRMODE_EXCEPTION; trusted initialized schema; tenant ID authenticated."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-02 — invoice-preview-single-pass-dot-filter

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `d8a63ac5c511123b1fb324870180d4ae144164e2013770dc8c128a11b7b3bddd`. Protocol-2.0 case hash: `72b15348eb7f897d7b132f638cf453a41cbdbcdc3d7fcf471b91f51233a36ae2`.

Removing ../ once is not canonical containment: overlapping dot/slash sequences can leave new parent components after replacement and escape the account directory.

### invoice_preview.php

```php
<?php
declare(strict_types=1);
function previewInvoice(int $accountId, string $submittedName): string {
    if (strlen($submittedName) > 180 || str_contains($submittedName, "\0")) {
        throw new InvalidArgumentException('filename');
    }
    // Legacy upload code tried to remove traversal text in one pass.
    $name = str_replace('../', '', $submittedName);
    $path = '/srv/invoices/' . $accountId . '/' . $name;
    $bytes = file_get_contents($path);
    if ($bytes === false) throw new RuntimeException('missing invoice');
    return $bytes;
}
function downloadRequest(int $authenticatedAccount, array $query): string {
    return previewInvoice($authenticatedAccount, $query['name']);
}
```

### Derivation

```json
{
  "group": "invoice-preview-single-pass-dot-filter",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An account holder selects a filename while the account root is supplied by authentication. The operation is download an account invoice by a relative nested filename.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "invoice_preview.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for download an account invoice by a relative nested filename. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Download an account invoice by a relative nested filename.",
  "trust_boundary": "An account holder selects a filename while the account root is supplied by authentication.",
  "legitimate_examples": [
    {
      "input": "account=3; name=2025/April.pdf",
      "expected": "Return /srv/invoices/3/2025/April.pdf bytes."
    }
  ],
  "permitted_changes": [
    "Resolve and enforce path-component containment beneath the account directory, rejecting escapes instead of editing filenames."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/function.str-replace.php",
    "https://www.php.net/manual/en/function.realpath.php"
  ]
}
```

### Regression traps

```json
[
  "Repeated string filtering is fragile; preserve legitimate nested invoice paths and validate the final canonical path within the authenticated root."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Resolve and enforce path-component containment beneath the account directory, rejecting escapes instead of editing filenames."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-02",
  "prior_case_id": "php-download-path-vulnerable",
  "prior_source_sha256": "ffa920cbdc0e6c919375f4c0b9ad94c23fcd19eb0fd6c36b0c81acec535a898d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "Linux filesystem; read-only trusted invoice tree during requests, no untrusted symlink mutation; service also reads sibling account directories. Output is a binary attachment, not interpreted HTML."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-03 — serialized-view-cookie-publish-hook

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0433acfa8b52eb3de057907e07055cd2e0f956b6056e1aafe2d98e83b66fdb5b`. Protocol-2.0 case hash: `d50e65ec9371867c023c17fbb4d24eaac3e5bdaeab29712803692888d417d2fa`.

unserialize permits arbitrary loaded classes and invokes __wakeup before the array check. An attacker-controlled PublishDraftSnapshot can publish a draft through the trusted PDO handle.

### view_cookie.php

```php
<?php
declare(strict_types=1);
require_once __DIR__ . '/draft_restore.php';
function decodeViewCookie(string $cookie): array {
    if (strlen($cookie) > 4096) throw new InvalidArgumentException('cookie size');
    $bytes = base64_decode($cookie, true);
    if ($bytes === false) throw new InvalidArgumentException('encoding');
    $view = unserialize($bytes);
    if (!is_array($view) || !isset($view['page'])) throw new InvalidArgumentException('view');
    return ['page' => $view['page']];
}
```

### draft_restore.php

```php
<?php
// This class is also used by an authenticated internal draft-restoration job.
final class PublishDraftSnapshot {
    public int $draftId;
    public function __wakeup(): void {
        $db = $GLOBALS['draftDb'];
        $statement = $db->prepare('UPDATE drafts SET published = 1 WHERE id = ?');
        $statement->execute([$this->draftId]);
    }
}
```

### schema.sql

```php
CREATE TABLE drafts(id INTEGER PRIMARY KEY, title TEXT NOT NULL, published INTEGER NOT NULL);
INSERT INTO drafts VALUES(12, 'Embargoed launch', 0);
```

### Authoring notes

```json
[
  "Historical authoring relationship only: the retired initial drafts of v2-ruby-vulnerable-02 and v2-ruby-vulnerable-03 used privileged object-restoration hooks. Their current sources were replaced with calibration file-to-process dispatch and archive-symlink extraction flaws before static validation. This PHP source is unchanged; no current sibling relationship is claimed."
]
```

### Derivation

```json
{
  "group": "serialized-view-cookie-publish-hook",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This current candidate concerns browser-cookie object reconstruction invoking a PHP publication hook before top-level array validation. Two initial Ruby drafts shared this privileged-restoration-hook construction but were retired and completely reauthored before static observations. Those historical drafts are preserved in the Ruby cases authoring_history; the current Ruby cases use different mechanisms. Broader independence across the whole corpus remains unverified human judgment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "view_cookie.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for restore a primitive page-view preference from a browser cookie without mutating content publication state. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Restore a primitive page-view preference from a browser cookie without mutating content publication state.",
  "trust_boundary": "The browser may alter cookie bytes but may not invoke an internal draft-restoration object hook.",
  "legitimate_examples": [
    {
      "input": "Base64 PHP-serialized array with page=2",
      "expected": "Return page=2 and leave drafts.published unchanged."
    }
  ],
  "permitted_changes": [
    "Replace browser object serialization with bounded schema-validated primitive data; preserve the page preference and reject object-bearing legacy cookies."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/function.unserialize.php",
    "https://www.php.net/manual/en/language.oop5.magic.php#object.wakeup"
  ]
}
```

### Regression traps

```json
[
  "Checking the result type after unserialize cannot roll back __wakeup. Migrate the cookie to primitive JSON with versioning and reject arbitrary legacy objects."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Replace browser object serialization with bounded schema-validated primitive data; preserve the page preference and reject object-bearing legacy cookies."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-03",
  "prior_case_id": "php-remember-cookie-vulnerable",
  "prior_source_sha256": "9b0c80e4024294e4a0b8dcdb17948fcfbb98c92d76c1e83121a97df9f12ea35d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "PDO SQLite initialized with schema.sql; trusted bootstrap sets $GLOBALS[\"draftDb\"] and loads the internal class. PHP unserialize allowed_classes defaults to true; no cookie authenticity protection exists."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-04 — backup-exclusion-glob-shell

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `9a223016ff0d201e5bf45e057355ea6e0406a1cfc239e89dd7f987a546f6b5fd`. Protocol-2.0 case hash: `d8f9ad8bc9681bdc19ea988da578c7404bb84f9fb788639b3f61e6181e19e3ef`.

The exclusion glob is embedded in a shell command. Shell metacharacters run before tar handles its exclusion option; normal glob syntax may also expand prematurely.

### backup.php

```php
<?php
declare(strict_types=1);
function exportBackup(int $ownedJobId, string $exclude): string {
    if ($ownedJobId < 1 || strlen($exclude) > 100) throw new InvalidArgumentException('backup input');
    $root = '/srv/export-jobs/' . $ownedJobId . '/content';
    $archive = '/srv/archives/' . $ownedJobId . '.tar.gz';
    $command = '/usr/bin/tar -czf ' . $archive . ' -C ' . $root . ' --exclude=' . $exclude . ' .';
    exec($command, $output, $status);
    if ($status !== 0) throw new RuntimeException('backup failed');
    return $archive;
}
function backupRequest(int $authorizedJob, array $body): array {
    return ['artifact' => exportBackup($authorizedJob, $body['exclude'])];
}
```

### Derivation

```json
{
  "group": "backup-exclusion-glob-shell",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer supplies the exclusion pattern; source root, archive destination and numeric job ID are service-owned. The operation is create a gzip tar backup of one owned export job while excluding a customer-selected glob.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "backup.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for create a gzip tar backup of one owned export job while excluding a customer-selected glob. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Create a gzip tar backup of one owned export job while excluding a customer-selected glob.",
  "trust_boundary": "A customer supplies the exclusion pattern; source root, archive destination and numeric job ID are service-owned.",
  "legitimate_examples": [
    {
      "input": "ownedJobId=21; exclude=tmp/*.log",
      "expected": "Create job 21’s archive while omitting paths matching that glob."
    }
  ],
  "permitted_changes": [
    "Use array-form proc_open to pass each argument without a shell; preserve exit checking and exact tar exclusion semantics."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/function.exec.php",
    "https://www.php.net/manual/en/function.proc-open.php"
  ]
}
```

### Regression traps

```json
[
  "The glob must reach tar as one literal argument, not be expanded by the shell or stripped into a different matching rule."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use array-form proc_open to pass each argument without a shell; preserve exit checking and exact tar exclusion semantics."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-04",
  "prior_case_id": "php-diagnostics-vulnerable",
  "prior_source_sha256": "3ede5461f79d01274957c8be020ee86142d7b4f9c07380f77e388ca504246a5c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "GNU tar 1.35; fixed trusted directories/executable, unique job ID per export and no attacker-modified symlinks in source tree. Worker enforces a 5-second process deadline and archive size cap."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-05 — localized-phrase-closure-compilation

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `38a614ec9b90abd12d681b433545c3d4065088c543d5a926b9d0e44b0f89a2e3`. Protocol-2.0 case hash: `fefc7d7c8e29baab7afd2e219079934bcd73dd754e3c308279cd4b0b3d2a83ed`.

The phrase is inserted inside PHP source passed to eval, so quote termination or PHP string interpolation converts translation text into executable behavior.

### phrase_cache.php

```php
<?php
declare(strict_types=1);
function compilePhrase(string $phrase): Closure {
    if (strlen($phrase) > 500) throw new InvalidArgumentException('phrase too long');
    // Legacy cache builds a getter from translator-authored literal text.
    return eval('return function () { return "' . $phrase . '"; };');
}
function translatedLabel(array $catalog, string $key): string {
    if (!array_key_exists($key, $catalog)) throw new InvalidArgumentException('key');
    $getter = compilePhrase($catalog[$key]);
    return $getter();
}
```

### Derivation

```json
{
  "group": "localized-phrase-closure-compilation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A translator edits phrase data but is not permitted to execute PHP in the request worker. The operation is return translator-authored phrases literally, including quotes, currency signs and unicode.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "phrase_cache.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for return translator-authored phrases literally, including quotes, currency signs and unicode. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return translator-authored phrases literally, including quotes, currency signs and Unicode.",
  "trust_boundary": "A translator edits phrase data but is not permitted to execute PHP in the request worker.",
  "legitimate_examples": [
    {
      "input": "catalog={welcome: \"Welcome, Ana\"}; key=welcome",
      "expected": "Return exactly Welcome, Ana."
    }
  ],
  "permitted_changes": [
    "Use a closure that captures literal phrase data or return it directly; preserve exact text and unknown-key errors."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://www.php.net/manual/en/function.eval.php"
  ]
}
```

### Regression traps

```json
[
  "HTML escaping changes the phrase but does not define correct PHP source quoting; return literal data without compilation and preserve every character."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use a closure that captures literal phrase data or return it directly; preserve exact text and unknown-key errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-05",
  "prior_case_id": "php-dynamic-plugin-vulnerable",
  "prior_source_sha256": "345d8478500fa5e322a6aba61aa51b8664f4af00b8b1e115b6e92ed8c6c41151",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "Catalog store is bounded and tenant-authorized but stores translator strings verbatim; translatedLabel result is later emitted as JSON or escaped HTML. No feature requires executing code or variable interpolation inside phrases."
}
```

### Split

```json
"held_out"
```

## v2-php-vulnerable-06 — mysql-backslash-mode-sku-search

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `d3cff18b0f82c18f179d6d815fd5f8edaff7dee24224e3291cb0883a3283d643`. Protocol-2.0 case hash: `20c2e7ee428949b675f42cbc7ed1c7de029291f75b67459bb190914372a6f8db`.

addslashes applies backslash escaping, but the configured SQL mode treats backslashes literally. A following quote can terminate the SQL string instead of being escaped.

### stock_lookup.php

```php
<?php
declare(strict_types=1);
function findStock(mysqli $db, string $sku): array {
    if (strlen($sku) > 80) throw new InvalidArgumentException('SKU size');
    $escaped = addslashes($sku);
    $result = $db->query("SELECT sku, available FROM stock WHERE sku = '" . $escaped . "'");
    return $result->fetch_all(MYSQLI_ASSOC);
}
function configureStockConnection(mysqli $db): void {
    $db->set_charset('utf8mb4');
    $db->query("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_BACKSLASH_ESCAPES'");
}
```

### schema.sql

```php
CREATE TABLE stock(sku VARCHAR(80) PRIMARY KEY, available INTEGER NOT NULL);
INSERT INTO stock VALUES('BLUE-1', 6), ('RED-2', 0);
```

### Derivation

```json
{
  "group": "mysql-backslash-mode-sku-search",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An external partner supplies SKU text; a trusted connection setup deliberately uses SQL mode NO_BACKSLASH_ESCAPES. The operation is look up stock availability by an exact partner-supplied sku string.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "stock_lookup.php"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for look up stock availability by an exact partner-supplied sku string. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Look up stock availability by an exact partner-supplied SKU string.",
  "trust_boundary": "An external partner supplies SKU text; a trusted connection setup deliberately uses SQL mode NO_BACKSLASH_ESCAPES.",
  "legitimate_examples": [
    {
      "input": "sku=BLUE-1",
      "expected": [
        {
          "sku": "BLUE-1",
          "available": "6"
        }
      ]
    }
  ],
  "permitted_changes": [
    "Use a native mysqli prepared statement and bind the SKU as a string; keep connection mode and character set."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
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
    "https://dev.mysql.com/doc/refman/8.4/en/string-literals.html",
    "https://www.php.net/manual/en/function.addslashes.php"
  ]
}
```

### Regression traps

```json
[
  "Changing the global SQL mode to mask the bug can affect unrelated queries; bind the exact SKU and retain the configured mode and UTF-8 handling."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use a native mysqli prepared statement and bind the SKU as a string; keep connection mode and character set."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-php-vulnerable-06",
  "prior_case_id": "php-account-query-pdo-vulnerable",
  "prior_source_sha256": "edad7174d0f6712518c4b104728d55a879cf30645d0cbf669ba471f898b2a629",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "PHP 8.3.17",
  "platform": "Linux x86_64",
  "setup": "mysqli mysqlnd on PHP 8.3.17; MySQL 8.4; bootstrap calls configureStockConnection before findStock, native numeric conversion option disabled so fetch_all integer columns are strings; read-only DB role."
}
```

### Split

```json
"held_out"
```

