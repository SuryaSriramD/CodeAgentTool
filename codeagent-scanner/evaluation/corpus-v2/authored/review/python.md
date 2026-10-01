# python — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-python-safe-01 — unicode-member-directory-bound-query

Proposed label: **safe**. Human review: **pending**.

Source hash: `c1ef329054821d9ad471b4faa9bb2dfb840852cfdc98dd25146c9d58c5563fa6`. Protocol-2.0 case hash: `af2c8f7d400c6caee87af1a75cb51e948c05579fe6287cd29c0a5252da4dd93b`.

Both externally supplied values use SQLite parameter binding; the SQL structure and ordering are fixed. The apostrophe is an ordinary name character.

### directory.py

```python
import sqlite3

def find_members(db, exact_name, minimum_year):
    if not isinstance(exact_name, str) or len(exact_name) > 100:
        raise ValueError('name')
    if type(minimum_year) is not int or not 1900 <= minimum_year <= 2100:
        raise ValueError('year')
    rows = db.execute('SELECT handle FROM members WHERE display_name=? AND joined_year>=? ORDER BY handle',
                      (exact_name, minimum_year)).fetchall()
    return [row[0] for row in rows]

def handle_directory_request(body):
    with sqlite3.connect('/srv/directory.sqlite') as db:
        return find_members(db, body['display_name'], body['since'])
```

### schema.sql

```python
CREATE TABLE members(handle TEXT PRIMARY KEY, display_name TEXT NOT NULL, joined_year INTEGER NOT NULL);
INSERT INTO members VALUES('moira', 'O''Brien Ω', 2020);
```

### Derivation

```json
{
  "group": "unicode-member-directory-bound-query",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around Visitors submit a display name and year, both passed as SQLite values rather than SQL syntax. The operation is find public directory handles by exact unicode display name and minimum joining year.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for find public directory handles by exact unicode display name and minimum joining year. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Find public directory handles by exact Unicode display name and minimum joining year.",
  "trust_boundary": "Visitors submit a display name and year, both passed as SQLite values rather than SQL syntax.",
  "legitimate_examples": [
    {
      "input": {
        "display_name": "O'Brien Ω",
        "since": 2019
      },
      "expected": [
        "moira"
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
    "https://docs.python.org/3.12/library/sqlite3.html#sqlite3-placeholders"
  ]
}
```

### Regression traps

```json
[
  "Escaping apostrophes manually before binding changes the intended exact match and would regress this safe case."
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
  "slot_id": "v2-python-safe-01",
  "prior_case_id": "python-catalog-filter-safe",
  "prior_source_sha256": "c106016ff6b8426a3862dfffce57117722441a94985f7e929a818eac2fcba90d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "SQLite 3.46; schema.sql initializes /srv/directory.sqlite with publicly visible directory data. CPython standard sqlite3 qmark bindings."
}
```

### Split

```json
"held_out"
```

## v2-python-safe-02 — locale-catalog-contained-nested-assets

Proposed label: **safe**. Human review: **pending**.

Source hash: `43d3d30e9d69ea48e61e8c6d1c0e095d3796d32914eefe1b83cd6b141afa7160`. Protocol-2.0 case hash: `fa4b3998931d2238b21667a9243ba7c5cfd9fc3d894bdd29cd8849fcb34cef09`.

Resolved path containment is checked by path components before a read. With a deployment-owned immutable directory, neither parent traversal nor an escaping symlink passes the check.

### locale_assets.py

```python
from pathlib import Path
ROOT = Path('/opt/site/locales').resolve()

def load_catalog(relative):
    if not isinstance(relative, str) or len(relative) > 200:
        raise ValueError('catalog name')
    candidate = (ROOT / relative).resolve(strict=True)
    if not candidate.is_relative_to(ROOT) or not candidate.is_file():
        raise ValueError('catalog outside locale directory')
    return candidate.read_text(encoding='utf-8')

def catalog_response(query):
    return {'catalog': load_catalog(query['locale_file'])}
```

### Derivation

```json
{
  "group": "locale-catalog-contained-nested-assets",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A visitor selects a locale-relative path; filesystem contents and symlinks are controlled only by the deployment owner. The operation is read nested translation catalogs from a read-only deployment directory.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for read nested translation catalogs from a read-only deployment directory. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The immutable-directory assumption is essential: a writable tree would require race-resistant file opening.",
    "Only catalog files are deployed under the locale root; containment is not a substitute for per-file authorization."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read nested translation catalogs from a read-only deployment directory.",
  "trust_boundary": "A visitor selects a locale-relative path; filesystem contents and symlinks are controlled only by the deployment owner.",
  "legitimate_examples": [
    {
      "input": "locale_file=fr/common/messages.json",
      "expected": "UTF-8 text from /opt/site/locales/fr/common/messages.json."
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
    "https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.is_relative_to"
  ]
}
```

### Regression traps

```json
[
  "A string-prefix containment replacement would accept /opt/site/locales-backup; rejecting all nested paths would break valid locales."
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
  "slot_id": "v2-python-safe-02",
  "prior_case_id": "python-export-file-safe",
  "prior_source_sha256": "e3585c99e9c7b4f9ed4ef7aa1dd3b348e50d78680f9a26eb93c3cdaf59cd71d1",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Root-owned read-only /opt/site/locales; no untrusted process can swap directory entries between resolve and read. Nested fixture files and an escaping symlink are installed only as trusted evaluation data."
}
```

### Split

```json
"held_out"
```

## v2-python-safe-03 — geocoder-query-component-encoding

Proposed label: **safe**. Human review: **pending**.

Source hash: `e02e082689079db046e7ce37ac06ad245c08be945c19374811c4049d3a111a9b`. Protocol-2.0 case hash: `ffe97078eb085ababf33905bab05c808d9b4949b16da417c0d9503c495dc3ca1`.

The address is encoded as a query parameter on a constant HTTPS endpoint; redirects and environment-derived proxy settings are disabled. URL-looking address text cannot replace the host.

### geocode.py

```python
import requests

def geocode(address):
    if not isinstance(address, str) or not 1 <= len(address) <= 240:
        raise ValueError('address')
    with requests.Session() as session:
        session.trust_env = False
        response = session.get('https://geo.example.org/search',
                               params={'q': address, 'format': 'json'},
                               timeout=3, allow_redirects=False)
        if response.status_code != 200:
            raise ValueError('geocoder rejected query')
        return response.json()['coordinates']

def handle_lookup(body):
    return {'coordinates': geocode(body['address'])}
```

### Derivation

```json
{
  "group": "geocoder-query-component-encoding",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A client controls a query value, never the destination, proxy, redirect target or URL authority. The operation is resolve a postal address through the deployment-selected public geocoder.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for resolve a postal address through the deployment-selected public geocoder. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Resolve a postal address through the deployment-selected public geocoder.",
  "trust_boundary": "A client controls a query value, never the destination, proxy, redirect target or URL authority.",
  "legitimate_examples": [
    {
      "input": "address=5 Main St & Market, Paris",
      "expected": "Return coordinates from the geocoder response to that exact address."
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
    "https://requests.readthedocs.io/en/latest/user/quickstart/#passing-parameters-in-urls"
  ]
}
```

### Regression traps

```json
[
  "String-concatenating address into the URL or turning 302 responses into automatic fetches would introduce a destination-control risk."
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
  "slot_id": "v2-python-safe-03",
  "prior_case_id": "python-image-proxy-safe",
  "prior_source_sha256": "46fa206443555cdde7ac27192ee60183559bfede5c172b69cddd849e8ca6f772",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "requests 2.32.3; geo.example.org is operator-controlled, resolves to the approved public geocoder, uses a publicly trusted certificate and bounded JSON responses. No attacker control of DNS, CA roots or service configuration."
}
```

### Split

```json
"held_out"
```

## v2-python-safe-04 — trusted-git-object-inspection

Proposed label: **safe**. Human review: **pending**.

Source hash: `8d265860d8ac00fff51bad297a38227f9693091d8f0852a00711551ab0a5dc9d`. Protocol-2.0 case hash: `a08e1d187b2a5dc9d95b6e099e2c0d09656f3f762c561a691d4110fb63abfd3c`.

No shell is invoked and strict object-ID syntax excludes options and revision expressions; fixed cat-file arguments inspect an existing trusted repository.

### object_info.py

```python
import re
import subprocess
OBJECT_ID = re.compile(r'[0-9a-f]{40}\Z')

def inspect_object(oid):
    if not isinstance(oid, str) or not OBJECT_ID.fullmatch(oid):
        raise ValueError('full SHA-1 object ID required')
    result = subprocess.run(['/usr/bin/git', '--git-dir=/srv/catalog.git',
                             'cat-file', '-s', oid], check=True,
                            shell=False, capture_output=True, text=True,
                            timeout=2, env={'PATH': '/usr/bin:/bin'})
    return {'object': oid, 'bytes': int(result.stdout.strip())}

def handle_object_query(query):
    return inspect_object(query['oid'])
```

### Derivation

```json
{
  "group": "trusted-git-object-inspection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A visitor supplies exactly a lowercase 40-digit hexadecimal Git object ID; executable and repository configuration are trusted. The operation is return the byte size of a full object id from an administrator-owned git object catalog.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for return the byte size of a full object id from an administrator-owned git object catalog. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the byte size of a full object ID from an administrator-owned Git object catalog.",
  "trust_boundary": "A visitor supplies exactly a lowercase 40-digit hexadecimal Git object ID; executable and repository configuration are trusted.",
  "legitimate_examples": [
    {
      "input": "oid=0123456789012345678901234567890123456789, existing 27-byte blob",
      "expected": "Return the same object ID and bytes=27."
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
    "https://docs.python.org/3.12/library/subprocess.html#security-considerations",
    "https://git-scm.com/docs/git-cat-file"
  ]
}
```

### Regression traps

```json
[
  "Do not relax the input to revision expressions or invoke repository hooks/builds; Git output must still be parsed as an integer."
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
  "slot_id": "v2-python-safe-04",
  "prior_case_id": "python-archive-command-safe",
  "prior_source_sha256": "8c8aef96d07e4f728666f8fa995b2233c3384bf0ea15552201bf8a2edeb0db99",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Git 2.47.1 in a root-owned bare repository, SHA-1 object format; no user-controlled Git configuration, replacement refs, environment injection or filesystem write. The example object is supplied as trusted fixture setup."
}
```

### Split

```json
"held_out"
```

## v2-python-safe-05 — typed-etl-json-checkpoint

Proposed label: **safe**. Human review: **pending**.

Source hash: `198b42fa82fd309eeedbd59acfbc8111e81c2bbe6ad1a890e7b38a97d8f5aa6e`. Protocol-2.0 case hash: `9215c72b25d693cd5c63aa6ab110beeff08f9071f66aec07a5aced7854c09b66`.

JSON decoding cannot instantiate user-selected Python classes, exact field/type/range checks run before use, and a checkpoint cannot move the caller into another partition.

### checkpoint.py

```python
import json

def parse_checkpoint(raw):
    if len(raw) > 2048:
        raise ValueError('checkpoint too large')
    value = json.loads(raw)
    if type(value) is not dict or set(value) != {'partition', 'cursor'}:
        raise ValueError('checkpoint fields')
    if type(value['partition']) is not int or not 0 <= value['partition'] < 8:
        raise ValueError('partition')
    if type(value['cursor']) is not str or len(value['cursor']) > 120:
        raise ValueError('cursor')
    return value['partition'], value['cursor']

def resume_partition(raw, assigned_partition, consumer):
    partition, cursor = parse_checkpoint(raw)
    if partition != assigned_partition:
        raise ValueError('wrong assigned partition')
    return consumer.seek(partition, cursor)
```

### Derivation

```json
{
  "group": "typed-etl-json-checkpoint",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A client-held checkpoint supplies primitive data; the assigned partition and consumer object come from trusted server state. The operation is resume a stream consumer at a string cursor within its server-assigned partition.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for resume a stream consumer at a string cursor within its server-assigned partition. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Resume a stream consumer at a string cursor within its server-assigned partition.",
  "trust_boundary": "A client-held checkpoint supplies primitive data; the assigned partition and consumer object come from trusted server state.",
  "legitimate_examples": [
    {
      "input": "{\"partition\":3,\"cursor\":\"batch:008/a\"}, assigned_partition=3",
      "expected": "Call consumer.seek(3, \"batch:008/a\") and return its acknowledgment."
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
    "https://docs.python.org/3.12/library/json.html"
  ]
}
```

### Regression traps

```json
[
  "Python bool is an int subclass; replacing exact type checks with isinstance(..., int) would permit true as partition 1."
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
  "slot_id": "v2-python-safe-05",
  "prior_case_id": "python-signed-state-name-safe",
  "prior_source_sha256": "903ed8614b723ae391baf6e46008f918b0744af2204ae6d6cbac256b43234b68",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "The trusted consumer treats cursor as an opaque identifier, never as a path, query or code, and validates existence. CPython json without object_hook."
}
```

### Split

```json
"held_out"
```

## v2-python-safe-06 — enterprise-manifest-verified-https

Proposed label: **safe**. Human review: **pending**.

Source hash: `b2692cebfa9ef30113506f25b9d54928cfbf556cbaefb77b0d036d3486aa23c7`. Protocol-2.0 case hash: `84f33ed0895b4443b769383128dc5606ed344c724897bf4f71803b34493bf3f2`.

create_default_context enables certificate and hostname validation; adding the enterprise CA and a TLS minimum retains those protections. HTTPSConnection does not automatically follow redirects.

### manifest_client.py

```python
import json
import ssl
import http.client

def latest_manifest():
    context = ssl.create_default_context(cafile='/run/secrets/releases-ca.pem')
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    connection = http.client.HTTPSConnection('releases.example.org', 443,
                                            context=context, timeout=3)
    try:
        connection.request('GET', '/stable/manifest.json')
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError('manifest unavailable')
        body = response.read(16385)
        if len(body) > 16384:
            raise ValueError('manifest too large')
        return json.loads(body)
    finally:
        connection.close()
```

### Derivation

```json
{
  "group": "enterprise-manifest-verified-https",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An active network attacker may intercept traffic; host, CA file and deployment configuration are trusted. The operation is read a bounded release manifest from an enterprise https origin with its private ca.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for read a bounded release manifest from an enterprise https origin with its private ca. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a bounded release manifest from an enterprise HTTPS origin with its private CA.",
  "trust_boundary": "An active network attacker may intercept traffic; host, CA file and deployment configuration are trusted.",
  "legitimate_examples": [
    {
      "input": "The release service returns {\"version\":\"7.2\"} under its valid certificate",
      "expected": "Return the parsed version object; reject untrusted certificates."
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
    "https://docs.python.org/3.12/library/ssl.html#ssl.create_default_context"
  ]
}
```

### Regression traps

```json
[
  "Replacing the custom CA with verify-disabled handling for a development certificate would remove server authentication."
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
  "slot_id": "v2-python-safe-06",
  "prior_case_id": "python-outbound-certificates-safe",
  "prior_source_sha256": "79dd6f83056ba52040d79f7e80fd5aa809383ed47fcd283462efb1931a6bdd3f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "/run/secrets/releases-ca.pem contains the approved enterprise root, root-owned and read-only; certificate subjectAltName matches releases.example.org; no global monkey-patching of ssl."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-01 — tenant-invoice-status-export

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `36cb9e9c2f5041fedbc6097224ad1f844d186069425abe9e62538f4cd04be551`. Protocol-2.0 case hash: `a85a1acab7136bb26c67e6e67c07d70536152352ff16de19d32c998cf0f4f6b0`.

The bound tenant value does not protect the adjacent interpolated status expression; SQL operators in status can alter selection and defeat tenant isolation.

### export.py

```python
import sqlite3
from flask import Flask, request, jsonify, g
app = Flask(__name__)

def export_rows(db, tenant_id, status):
    # Authenticated tenant_id is trusted; the saved dashboard status is not.
    sql = "SELECT number, cents FROM invoices WHERE tenant_id=? AND status='" + status + "' ORDER BY number"
    return db.execute(sql, (tenant_id,)).fetchall()

@app.get('/invoices/export')
def export():
    with sqlite3.connect('/srv/billing.sqlite') as db:
        rows = export_rows(db, g.tenant_id, request.args.get('status', 'paid'))
    return jsonify(rows)
```

### schema.sql

```python
CREATE TABLE invoices(tenant_id INTEGER NOT NULL, number TEXT NOT NULL, status TEXT NOT NULL, cents INTEGER NOT NULL);
INSERT INTO invoices VALUES(7, 'A-21', 'paid', 4200);
INSERT INTO invoices VALUES(8, 'B-99', 'private', 9900);
```

### Derivation

```json
{
  "group": "tenant-invoice-status-export",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An authenticated tenant controls a saved status filter while tenant identity comes from trusted Flask middleware. The operation is export ordered invoice numbers and integer amounts for one authenticated tenant and exact status.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "export.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for export ordered invoice numbers and integer amounts for one authenticated tenant and exact status. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Export ordered invoice numbers and integer amounts for one authenticated tenant and exact status.",
  "trust_boundary": "An authenticated tenant controls a saved status filter while tenant identity comes from trusted Flask middleware.",
  "legitimate_examples": [
    {
      "input": "tenant_id=7, status=paid",
      "expected": [
        [
          "A-21",
          4200
        ]
      ]
    }
  ],
  "permitted_changes": [
    "Bind the exact status as a SQLite value and retain tenant filtering and stable ordering."
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
    "https://docs.python.org/3.12/library/sqlite3.html#sqlite3-placeholders"
  ]
}
```

### Regression traps

```json
[
  "Binding only tenant_id still leaves the status predicate executable; quotes and Unicode in legitimate statuses must remain data."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Bind the exact status as a SQLite value and retain tenant filtering and stable ordering."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-01",
  "prior_case_id": "python-catalog-filter-vulnerable",
  "prior_source_sha256": "4206b88813f68f49303101f2b60833610ad98393d630e6b6b537b1b977fecc9e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Flask 3.1.0; SQLite 3.46; schema.sql is initialized by trusted deployment. Middleware assigns g.tenant_id from authenticated identity. GET result size is capped by the deployment; no table is user-created."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-02 — preview-workspace-file-selector

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `cdff7062316f827df274035708bee785420081687f2171ce61ef1b3aeef48bb7`. Protocol-2.0 case hash: `c3f15be7571f0bcef953034248b839d35204c151150ffbd78015bc6179ff44e1`.

Path joining accepts absolute paths and parent components without checking the resulting location, so a workspace member can read outside its root.

### preview.py

```python
from pathlib import Path
from flask import Flask, request, g, Response
app = Flask(__name__)
ROOT = Path('/srv/previews')

def preview_body(workspace_id, relative_name):
    # Workspace directory names come from authenticated server state.
    base = ROOT / str(workspace_id)
    return (base / relative_name).read_bytes()

@app.get('/preview')
def preview():
    body = preview_body(g.workspace_id, request.args['file'])
    return Response(body, content_type='text/plain; charset=utf-8')
```

### Derivation

```json
{
  "group": "preview-workspace-file-selector",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The workspace ID is server-owned but a signed-in collaborator supplies a relative preview path. The operation is read a utf-8 preview file, including legitimate nested files, inside the current workspace.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "preview.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for read a utf-8 preview file, including legitimate nested files, inside the current workspace. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a UTF-8 preview file, including legitimate nested files, inside the current workspace.",
  "trust_boundary": "The workspace ID is server-owned but a signed-in collaborator supplies a relative preview path.",
  "legitimate_examples": [
    {
      "input": "workspace=42; file=chapters/intro.txt",
      "expected": "The bytes of /srv/previews/42/chapters/intro.txt."
    }
  ],
  "permitted_changes": [
    "Canonicalize and enforce directory containment, reject escapes, and retain nested paths."
  ],
  "forbidden_changes": [
    "Do not replace all filenames with a fixed allow-list or expose another workspace."
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
    "https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.resolve"
  ]
}
```

### Regression traps

```json
[
  "Rejecting every slash breaks nested chapters; a lexical prefix check also confuses sibling directory 420 with workspace 42."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Canonicalize and enforce directory containment, reject escapes, and retain nested paths.",
  "Do not replace all filenames with a fixed allow-list or expose another workspace."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-02",
  "prior_case_id": "python-export-file-vulnerable",
  "prior_source_sha256": "cd6f8a6688d841501734b928f465ee0139ad1159f83a7c2d9e14261d7ca7f0f0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Flask 3.1.0; previews are readable to the service. The fixture includes root-owned /srv/previews/42/chapters/intro.txt and a private sibling /srv/previews/43/notes.txt. Attackers cannot mutate filesystem entries during the request. Authentication assigns g.workspace_id."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-03 — queued-opml-feed-import

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `d191bbe34e2a542eae21d88692325cdceb7a60fdbf5f044054f811af0e1ba626`. Protocol-2.0 case hash: `642e793286640a8a9940026b39d60711b844c59a083f7a5c48d9e7f5bc872d46`.

A scheme check accepts loopback, private addresses and redirected internal destinations. The queued boundary does not make the URL trusted.

### worker.py

```python
import json
import requests
from urllib.parse import urlsplit

def import_message(message_bytes):
    # The public import endpoint enqueues this JSON after a size check.
    item = json.loads(message_bytes)
    source = item['feed_url']
    if urlsplit(source).scheme not in ('http', 'https'):
        raise ValueError('HTTP feed required')
    response = requests.get(source, timeout=3, allow_redirects=True)
    response.raise_for_status()
    return {'feed_id': item['feed_id'], 'xml': response.content[:65536]}
```

### ingress.py

```python
import json

def enqueue_import(body, queue):
    if len(body) > 8192:
        raise ValueError('import message too large')
    item = json.loads(body)
    if not isinstance(item.get('feed_id'), int) or not isinstance(item.get('feed_url'), str):
        raise ValueError('invalid feed import')
    queue.put(json.dumps(item).encode('utf-8'))
```

### Derivation

```json
{
  "group": "queued-opml-feed-import",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A public import request reaches a privileged background worker through a durable JSON queue. The operation is import a user-selected public http(s) feed asynchronously and return its first 64 kib with the feed id.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "ssrf",
    "cwe": "CWE-918",
    "path": "worker.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for import a user-selected public http(s) feed asynchronously and return its first 64 kib with the feed id. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import a user-selected public HTTP(S) feed asynchronously and return its first 64 KiB with the feed ID.",
  "trust_boundary": "A public import request reaches a privileged background worker through a durable JSON queue.",
  "legitimate_examples": [
    {
      "input": "{\"feed_id\":19,\"feed_url\":\"https://feeds.example.net/community.xml\"}",
      "expected": "Return feed_id 19 and that public feed XML."
    }
  ],
  "permitted_changes": [
    "Reject private/reserved destinations and unsafe redirects with connection-time destination enforcement; allow ordinary public HTTPS feeds."
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
    "https://requests.readthedocs.io/en/latest/user/advanced/"
  ]
}
```

### Regression traps

```json
[
  "Rejecting redirects entirely is allowed, but blocking all public feeds or trusting only the initial hostname is not an adequate preservation/security fix."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Reject private/reserved destinations and unsafe redirects with connection-time destination enforcement; allow ordinary public HTTPS feeds."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-03",
  "prior_case_id": "python-image-proxy-vulnerable",
  "prior_source_sha256": "28f62361e1830f4f1e010b76de073d2a2e36b6000cde4b563047fe37c9878e0b",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "requests 2.32.3; worker has access to internal HTTP services and public DNS, no outbound proxy. Public feed responses are bounded upstream to 64 KiB; authentication/rate limits protect submission. Public-host fixtures and internal-service stand-ins are deployment evidence only, not executed here."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-04 — video-thumbnail-timecode

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `b6075350f0f298864740ff194981c6580abadb1eb0bb668e450913d553cc64ec`. Protocol-2.0 case hash: `a7a8ab754e89607948a46d8fae92f06d0ef36764052169c5fec3e440867ee0d9`.

The timecode is inserted into a shell command before ffmpeg parses it, allowing shell syntax to escape the media operation.

### thumbnail.py

```python
import subprocess
from pathlib import Path
from flask import Flask, request, g, Response
app = Flask(__name__)

def make_frame(video_id, position):
    source = Path('/srv/videos') / (str(video_id) + '.mp4')
    command = f'/usr/bin/ffmpeg -v error -ss {position} -i {source} -frames:v 1 -f image2pipe -vcodec png -'
    result = subprocess.run(command, shell=True, check=True, capture_output=True, timeout=8)
    return result.stdout

@app.get('/thumbnail')
def thumbnail():
    # Ownership middleware stores an integer video ID in g.video_id.
    return Response(make_frame(g.video_id, request.args['at']), mimetype='image/png')
```

### Derivation

```json
{
  "group": "video-thumbnail-timecode",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An authenticated video owner supplies the timecode while the stored video ID and executable path are trusted. The operation is produce one png frame at a requested numeric or hh:mm:ss.mmm position from an owned video.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "thumbnail.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for produce one png frame at a requested numeric or hh:mm:ss.mmm position from an owned video. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Produce one PNG frame at a requested numeric or HH:MM:SS.mmm position from an owned video.",
  "trust_boundary": "An authenticated video owner supplies the timecode while the stored video ID and executable path are trusted.",
  "legitimate_examples": [
    {
      "input": "video_id=14; at=00:00:01.500",
      "expected": "The PNG frame at 1.5 seconds from video 14."
    }
  ],
  "permitted_changes": [
    "Use an argument array with shell=False and validate supported timecode syntax."
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
    "https://docs.python.org/3.12/library/subprocess.html#security-considerations"
  ]
}
```

### Regression traps

```json
[
  "A fix must keep PNG bytes on stdout and reject malformed timecodes without treating timestamps as filenames or silently choosing time zero."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use an argument array with shell=False and validate supported timecode syntax."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-04",
  "prior_case_id": "python-archive-command-vulnerable",
  "prior_source_sha256": "c0e80572e753c7677efdf819a9f3df2c75138c8ba20b6d2bfe40d63cc8902f3c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Flask 3.1.0; ffmpeg 7.1 at /usr/bin/ffmpeg, root-owned binaries and media filenames constructed solely from trusted integer IDs; uploads are trusted/transcoded media for this source case."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-05 — resumable-search-ticket

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `427b6a4d8e13065ade46757716034b67d14e623f95f8ee7a7cd9593dbdcf7ab4`. Protocol-2.0 case hash: `c213b0ecbefd2954a55ded08ad19223c9727673560ff879443541766751edf65`.

Base64 validates an encoding, not authenticity; pickle executes reconstruction logic before the later dictionary/int checks can reject dangerous data.

### resume.py

```python
import base64
import pickle
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post('/search/resume')
def resume():
    encoded = request.get_json()['ticket']
    if not isinstance(encoded, str) or len(encoded) > 4096:
        return {'error': 'ticket too large'}, 400
    payload = pickle.loads(base64.b64decode(encoded, validate=True))
    # Type checks happen after pickle can construct objects and call functions.
    if type(payload) is not dict or type(payload.get('offset')) is not int:
        return {'error': 'invalid ticket'}, 400
    return jsonify({'offset': payload['offset'], 'query': payload['query']})
```

### Derivation

```json
{
  "group": "resumable-search-ticket",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The client may alter a Base64 ticket before sending it to the public resume endpoint. The operation is recover a search query and page offset from a client-held resume ticket.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "resume.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for recover a search query and page offset from a client-held resume ticket. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Recover a search query and page offset from a client-held resume ticket.",
  "trust_boundary": "The client may alter a Base64 ticket before sending it to the public resume endpoint.",
  "legitimate_examples": [
    {
      "input": "Ticket encoding {query: \"blue moon\", offset: 20}",
      "expected": "Return query blue moon and offset 20."
    }
  ],
  "permitted_changes": [
    "Migrate primitive tickets to schema-validated JSON with explicit legacy rejection; retain query and offset."
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
    "https://docs.python.org/3.12/library/pickle.html"
  ]
}
```

### Regression traps

```json
[
  "Returning encoded bytes or dropping the query is not a fix. Define a primitive wire-format migration rather than accepting arbitrary legacy pickle objects."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Migrate primitive tickets to schema-validated JSON with explicit legacy rejection; retain query and offset."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-05",
  "prior_case_id": "python-signed-state-name-vulnerable",
  "prior_source_sha256": "b2e9d6165ee163e625990ac95880defc7bdd0d9b12a2dcc7345567551641f130",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "Flask 3.1.0; CPython pickle protocols 4 and 5; request size capped before decoding. query must remain a string and offset an integer in 0..10000. Resume is informational, not authorization."
}
```

### Split

```json
"held_out"
```

## v2-python-vulnerable-06 — mtls-telemetry-server-authentication

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `e7ff447a859c98fa0c2f78b633f63119241142709dad1eab0204bda4a6ef235d`. Protocol-2.0 case hash: `cf792ea2821f04d13b67ee1c3fdac39363c83a896e4745b0ee76cdb1fe517ade`.

A client certificate authenticates the client; verify=False separately disables authentication of the server and permits forged receipts or disclosure to an impostor.

### telemetry.py

```python
import requests
ENDPOINT = 'https://telemetry.example.net/v1/events'
CERT = ('/run/secrets/client.pem', '/run/secrets/client-key.pem')

def send_batch(events):
    if not 1 <= len(events) <= 25:
        raise ValueError('batch size')
    response = requests.post(ENDPOINT, json={'events': events},
                             cert=CERT, verify=False, timeout=4,
                             allow_redirects=False)
    response.raise_for_status()
    return response.json()['receipt']
```

### job.py

```python
from telemetry import send_batch

def flush_buffer(buffer):
    batch = buffer.peek(25)
    if not batch:
        return None
    receipt = send_batch(batch)
    buffer.acknowledge(len(batch), receipt)
    return receipt
```

### Derivation

```json
{
  "group": "mtls-telemetry-server-authentication",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A network attacker is outside the process; the telemetry destination and client key are trusted configuration. The operation is send buffered telemetry with a client certificate and acknowledge only a successful server receipt.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "telemetry.py"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for send buffered telemetry with a client certificate and acknowledge only a successful server receipt. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Send buffered telemetry with a client certificate and acknowledge only a successful server receipt.",
  "trust_boundary": "A network attacker is outside the process; the telemetry destination and client key are trusted configuration.",
  "legitimate_examples": [
    {
      "input": "A batch of two telemetry events",
      "expected": "Return the authenticated server receipt and acknowledge exactly two events."
    }
  ],
  "permitted_changes": [
    "Use the deployed enterprise CA bundle and preserve hostname verification and mTLS credentials."
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
    "https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification"
  ]
}
```

### Regression traps

```json
[
  "Keeping the client certificate is necessary; replacing mTLS with unauthenticated POST or acknowledging on TLS failure loses delivery semantics."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use the deployed enterprise CA bundle and preserve hostname verification and mTLS credentials."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-python-vulnerable-06",
  "prior_case_id": "python-outbound-certificates-vulnerable",
  "prior_source_sha256": "d221ff00f398aca9cb93b5764f8a6f1eeba21599588e5f452579e917eccdf3c5",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "CPython 3.12.7",
  "platform": "Linux x86_64",
  "setup": "requests 2.32.3; telemetry server uses an enterprise CA at /run/secrets/telemetry-ca.pem and a certificate valid for telemetry.example.net. Secret files are root-owned; redirects are intentionally unsupported."
}
```

### Split

```json
"held_out"
```

