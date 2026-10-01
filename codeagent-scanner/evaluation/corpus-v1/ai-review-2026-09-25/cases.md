# Case-by-case AI technical review

204 cases reviewed on 2026-09-25. These are AI assessments, not independent human approvals. All source below is quoted as review evidence; it was not executed. See [summary and release blockers](README.md) and [CSV](cases.csv).

Safe siblings are independently evaluated, not gold fixes. A supported targeted label does not mean release readiness or absence of every possible vulnerability. Every case remains subject to the corpus-wide independence and scope findings.

## python-catalog-filter-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L9) · Source SHA-256: `4206b88813f68f49303101f2b60833610ad98393d630e6b6b537b1b977fecc9e`

**app.py** (line numbers in findings refer to this file)

```python
from flask import request
from db import connection
def search():
    name = request.args['name']
    return connection.execute("SELECT name FROM products WHERE name = '" + name + "'").fetchall()
```

**db.py** (line numbers in findings refer to this file)

```python
import sqlite3
connection = sqlite3.connect(":memory:")
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.py"}]

**Original rationale:** Query parameter is concatenated into a SQL string.

**Original remediation constraints:**

- Bind the name parameter; preserve quoted/unicode names.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:4-5 carries the Flask query value directly into a quoted SQLite SQL expression; no binding or escaping occurs. CWE-89 fits if products exists. db.py:1-2 explicitly opens a fresh in-memory database but never initializes that table, so reachability of a successful query needs a declared setup contract.

**Assumptions:**

- A Flask request context invokes search().
- The same connection has an initialized products(name) table before search(), and remains on an allowed SQLite thread.

**Issues and recommended actions:**

- **minor / MISSING_DATABASE_INITIALIZATION** — db.py:2 opens a fresh :memory: database and no supplied file creates products; app.py:5 therefore does not demonstrate the described successful lookup as written. Document fixture setup and expected schema/data, or include initialization in a new corpus version; do not count startup errors as security success.
  References: [docs.python.org: sqlite3.html](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders).

**Derivation group (AI assessment):** `python:catalog-filter`. This is an audit annotation, not a validated sampling design.

## python-catalog-filter-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L46) · Source SHA-256: `c106016ff6b8426a3862dfffce57117722441a94985f7e929a818eac2fcba90d`

**app.py** (line numbers in findings refer to this file)

```python
from flask import request
from db import connection
def search():
    name = request.args['name']
    return connection.execute("SELECT name FROM products WHERE name = ?", (name,)).fetchall()
```

**db.py** (line numbers in findings refer to this file)

```python
import sqlite3
connection = sqlite3.connect(":memory:")
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind the name parameter; preserve quoted/unicode names.

**Original remediation constraints:**

- Bind the name parameter; preserve quoted/unicode names.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:4-5 passes name as the single bound value of a ? placeholder, preserving quotes and Unicode as data. This is the correct SQLite API. db.py:1-2 creates an empty in-memory database, so the example still requires a declared products-table initialization step to represent a functioning lookup.

**Assumptions:**

- A Flask request context invokes search().
- The same connection has an initialized products(name) table before search(), and remains on an allowed SQLite thread.

**Issues and recommended actions:**

- **minor / MISSING_DATABASE_INITIALIZATION** — db.py:2 opens a fresh :memory: database and no supplied file creates products; app.py:5 therefore does not demonstrate the described successful lookup as written. Document fixture setup and expected schema/data, or include initialization in a new corpus version; do not count startup errors as security success.
  References: [docs.python.org: sqlite3.html](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders).

**Derivation group (AI assessment):** `python:catalog-filter`. This is an audit annotation, not a validated sampling design.

## python-export-file-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L77) · Source SHA-256: `cd6f8a6688d841501734b928f465ee0139ad1159f83a7c2d9e14261d7ca7f0f0`

**app.py** (line numbers in findings refer to this file)

```python
from pathlib import Path
from flask import request
def download():
    return (Path('/srv/exports') / request.args['file']).read_bytes()
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.py"}]

**Original rationale:** User path can escape export directory.

**Original remediation constraints:**

- Resolve and enforce containment; retain nested legitimate export paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:4 joins an untrusted Flask query value to /srv/exports and reads it directly. Parent traversal, and an absolute path overriding the root, reach files outside the intended tree; CWE-22 is appropriate.

**Assumptions:**

- Python 3.9+ supplies Path.is_relative_to().
- The directory and ancestor symlinks cannot be modified by an attacker between resolve() and read_bytes(); the check is not an atomic defense against a hostile filesystem.
- Flask invokes download() with attacker-controlled file text.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:export-file`. This is an audit annotation, not a validated sampling design.

## python-export-file-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L113) · Source SHA-256: `e3585c99e9c7b4f9ed4ef7aa1dd3b348e50d78680f9a26eb93c3cdaf59cd71d1`

**app.py** (line numbers in findings refer to this file)

```python
from pathlib import Path
from flask import request
def download():
    root = Path('/srv/exports').resolve()
    target = (root / request.args['file']).resolve()
    if not target.is_relative_to(root):
        raise ValueError('outside export directory')
    return target.read_bytes()
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Resolve and enforce containment; retain nested legitimate export paths.

**Original remediation constraints:**

- Resolve and enforce containment; retain nested legitimate export paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:4-8 resolves root and target before checking path ancestry, rejecting both parent traversal and existing symlinks that resolve outside the root while retaining nested export paths. Path.is_relative_to alone would be lexical, but resolution precedes it here.

**Assumptions:**

- Python 3.9+ supplies Path.is_relative_to().
- The directory and ancestor symlinks cannot be modified by an attacker between resolve() and read_bytes(); the check is not an atomic defense against a hostile filesystem.
- Flask invokes download() with attacker-controlled file text.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:export-file`. This is an audit annotation, not a validated sampling design.

## python-image-proxy-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L143) · Source SHA-256: `28f62361e1830f4f1e010b76de073d2a2e36b6000cde4b563047fe37c9878e0b`

**app.py** (line numbers in findings refer to this file)

```python
import requests
from flask import request
def proxy():
    return requests.get(request.args['url'], timeout=3).content
```

**Expected findings:** [{"family": "ssrf", "cwe": "CWE-918", "path": "app.py"}]

**Original rationale:** Arbitrary URL allows internal service requests.

**Original remediation constraints:**

- Select only configured asset URLs and prohibit redirects to uncontrolled destinations.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:4 gives an attacker the entire requests URL, including scheme, host, port and path. A server-side call can reach internal HTTP services; CWE-918 fits. Default redirects add a second uncontrolled destination path.

**Assumptions:**

- The function runs on a server with network access.
- Configured asset hosts, DNS and proxy settings are trusted and are not rebound or replaced by the caller.
- The intended public API may use asset identifiers instead of arbitrary URL strings; that restriction is explicitly accepted by the remediation constraint.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:image-proxy`. This is an audit annotation, not a validated sampling design.

## python-image-proxy-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L179) · Source SHA-256: `46fa206443555cdde7ac27192ee60183559bfede5c172b69cddd849e8ca6f772`

**app.py** (line numbers in findings refer to this file)

```python
import requests
from flask import request
ASSETS = {'logo': 'https://static.example.org/logo.png', 'icon': 'https://static.example.org/icon.png'}
def proxy():
    return requests.get(ASSETS[request.args['asset']], allow_redirects=False, timeout=3).content
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Select only configured asset URLs and prohibit redirects to uncontrolled destinations.

**Original remediation constraints:**

- Select only configured asset URLs and prohibit redirects to uncontrolled destinations.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:3-5 limits selection to two configured HTTPS URLs and disables redirects. Unknown asset IDs fail during dictionary lookup before a request is made. No user URL enters the transport.

**Assumptions:**

- The function runs on a server with network access.
- Configured asset hosts, DNS and proxy settings are trusted and are not rebound or replaced by the caller.
- The intended public API may use asset identifiers instead of arbitrary URL strings; that restriction is explicitly accepted by the remediation constraint.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:image-proxy`. This is an audit annotation, not a validated sampling design.

## python-archive-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L209) · Source SHA-256: `c0e80572e753c7677efdf819a9f3df2c75138c8ba20b6d2bfe40d63cc8902f3c`

**app.py** (line numbers in findings refer to this file)

```python
import subprocess
from flask import request
def archive():
    return subprocess.run('tar -tf ' + request.args['archive'], shell=True, capture_output=True).stdout
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.py"}]

**Original rationale:** Archive name is interpreted by a shell.

**Original remediation constraints:**

- Avoid shell interpretation and option injection; keep listing archive entries.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:4 concatenates the request archive into a shell command and sets shell=True. Shell metacharacters are interpreted before tar receives arguments, so CWE-78 is directly supported.

**Assumptions:**

- The server uses a trusted tar supporting --list and --file and a trusted PATH.
- The benchmark targets shell/option interpretation, not archive authorization or tar remote-archive policy; if only local archives are allowed, the corpus must separately specify that requirement.
- Flask provides one string archive argument.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:archive-command`. This is an audit annotation, not a validated sampling design.

## python-archive-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L245) · Source SHA-256: `8c8aef96d07e4f728666f8fa995b2233c3384bf0ea15552201bf8a2edeb0db99`

**app.py** (line numbers in findings refer to this file)

```python
import subprocess
from flask import request
def archive():
    return subprocess.run(['tar', '--list', '--file', request.args['archive']], shell=False, capture_output=True).stdout
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Avoid shell interpretation and option injection; keep listing archive entries.

**Original remediation constraints:**

- Avoid shell interpretation and option injection; keep listing archive entries.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:4 supplies a fixed executable and argument vector with shell=False; the request value is the mandatory operand of --file rather than a separate option. Shell punctuation is passed as archive text, and tar listing remains the operation.

**Assumptions:**

- The server uses a trusted tar supporting --list and --file and a trusted PATH.
- The benchmark targets shell/option interpretation, not archive authorization or tar remote-archive policy; if only local archives are allowed, the corpus must separately specify that requirement.
- Flask provides one string archive argument.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:archive-command`. This is an audit annotation, not a validated sampling design.

## python-signed-state-name-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L275) · Source SHA-256: `b2e9d6165ee163e625990ac95880defc7bdd0d9b12a2dcc7345567551641f130`

**app.py** (line numbers in findings refer to this file)

```python
import pickle
from flask import request
def restore():
    signed_state = request.get_data()
    return pickle.loads(signed_state)
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.py"}]

**Original rationale:** Variable name claims signing but no signature is verified before pickle.

**Original remediation constraints:**

- Decode data-only JSON and check the expected mapping shape.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:4-5 reads raw request bytes and sends them to pickle.loads without authenticating a signature. The variable name signed_state has no protective effect; attacker-controlled pickle instructions can invoke object reconstruction behavior. CWE-502 is appropriate.

**Assumptions:**

- The request body is untrusted and the handler is reachable.
- The explicitly requested migration to JSON is allowed at the wire-format boundary; existing pickle clients/state require an independently specified migration if backward compatibility is required.
- Request/body resource limits are supplied outside this deserialization-specific example.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:signed-state-name`. This is an audit annotation, not a validated sampling design.

## python-signed-state-name-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L311) · Source SHA-256: `903ed8614b723ae391baf6e46008f918b0744af2204ae6d6cbac256b43234b68`

**app.py** (line numbers in findings refer to this file)

```python
import json
from flask import request
def restore():
    signed_state = request.get_data()
    value = json.loads(signed_state)
    if not isinstance(value, dict):
        raise ValueError('expected mapping')
    return value
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Decode data-only JSON and check the expected mapping shape.

**Original remediation constraints:**

- Decode data-only JSON and check the expected mapping shape.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:4-8 parses bytes with json.loads, does not install object hooks, and requires a dict. No pickle or arbitrary class construction remains; this meets the specified data-only mapping constraint.

**Assumptions:**

- The request body is untrusted and the handler is reachable.
- The explicitly requested migration to JSON is allowed at the wire-format boundary; existing pickle clients/state require an independently specified migration if backward compatibility is required.
- Request/body resource limits are supplied outside this deserialization-specific example.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:signed-state-name`. This is an audit annotation, not a validated sampling design.

## python-outbound-certificates-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L341) · Source SHA-256: `d221ff00f398aca9cb93b5764f8a6f1eeba21599588e5f452579e917eccdf3c5`

**app.py** (line numbers in findings refer to this file)

```python
import requests
def fetch_status():
    return requests.get('https://status.example.org', verify=False, timeout=5).json()
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.py"}]

**Original rationale:** Certificate verification is disabled for a remote endpoint.

**Original remediation constraints:**

- Retain CA and hostname verification while supporting configured trust roots.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.py:3 explicitly sets verify=False for an HTTPS request, bypassing certificate and hostname authentication. A fixed destination does not prevent an on-path attacker from impersonating it; CWE-295 fits.

**Assumptions:**

- Requests is used without an adapter that overrides TLS verification.
- The CA bundle exists and is trusted; the example path assumes a Linux distribution providing that bundle.
- An on-path attacker is in scope; control of the fixed hostname is not required.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:outbound-certificates`. This is an audit annotation, not a validated sampling design.

## python-outbound-certificates-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L377) · Source SHA-256: `79dd6f83056ba52040d79f7e80fd5aa809383ed47fcd283462efb1931a6bdd3f`

**app.py** (line numbers in findings refer to this file)

```python
import requests
def fetch_status():
    return requests.get('https://status.example.org', verify='/etc/ssl/certs/ca-certificates.crt', timeout=5).json()
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Retain CA and hostname verification while supporting configured trust roots.

**Original remediation constraints:**

- Retain CA and hostname verification while supporting configured trust roots.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.py:3 supplies a CA bundle path through verify, which enables trust-chain and hostname validation rather than disabling it. The configured trust-root behavior matches the remediation constraint.

**Assumptions:**

- Requests is used without an adapter that overrides TLS verification.
- The CA bundle exists and is trusted; the example path assumes a Linux distribution providing that bundle.
- An on-path attacker is in scope; control of the fixed hostname is not required.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `python:outbound-certificates`. This is an audit annotation, not a validated sampling design.

## javascript-log-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L407) · Source SHA-256: `a44bfd3876ba4a943fbb93290449886da8579918e32deb3bdab3d72f6b384c29`

**app.js** (line numbers in findings refer to this file)

```javascript
const cp = require('child_process');
function handle(req) { return cp.execSync('grep ' + req.query.term + ' /var/log/app.log'); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.js"}]

**Original rationale:** Request text enters a shell command.

**Original remediation constraints:**

- Use an argument vector and terminate options without deleting command functionality.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.js:2 concatenates req.query.term into execSync, which invokes a shell. A term containing shell syntax changes the command; CWE-78 fits directly.

**Assumptions:**

- A Node.js server invokes handle() with one string query term.
- A trusted GNU/BSD grep supporting -- is on trusted PATH.
- Regular-expression search is intentional; the case targets shell injection rather than regex resource consumption.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:log-command`. This is an audit annotation, not a validated sampling design.

## javascript-log-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L443) · Source SHA-256: `112ce1671d2a529d8f5e4cf7e129a505df72a7ad6e39411560c3c57b5e695a68`

**app.js** (line numbers in findings refer to this file)

```javascript
const cp = require('child_process');
function handle(req) { return cp.execFileSync('grep', ['--', req.query.term, '/var/log/app.log']); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use an argument vector and terminate options without deleting command functionality.

**Original remediation constraints:**

- Use an argument vector and terminate options without deleting command functionality.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.js:2 uses execFileSync with a fixed grep executable, a separate term argument and -- before user data. The shell is not invoked by default and leading-dash terms cannot select grep options. The fixed log file remains the searched file.

**Assumptions:**

- A Node.js server invokes handle() with one string query term.
- A trusted GNU/BSD grep supporting -- is on trusted PATH.
- Regular-expression search is intentional; the case targets shell injection rather than regex resource consumption.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:log-command`. This is an audit annotation, not a validated sampling design.

## javascript-template-load-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L473) · Source SHA-256: `cdd6a9f09314264c8386cd7959dfeea2cfa46cb20c6d6ab7f659aeb97285a728`

**app.js** (line numbers in findings refer to this file)

```javascript
const fs = require('fs');
function handle(req) { return fs.readFileSync('/srv/templates/' + req.params.name); }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.js"}]

**Original rationale:** Request path escapes the intended root.

**Original remediation constraints:**

- Map public identifiers to fixed file paths; reject unknown identifiers.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.js:2 appends req.params.name to a fixed directory string before readFileSync. Decoded ../ segments escape that directory, supporting CWE-22; the route must allow a value containing traversal segments.

**Assumptions:**

- The runtime supports Object.hasOwn and the supplied code executes server-side.
- The vulnerable route supplies a string containing decoded traversal, rather than a router that excludes every slash/traversal spelling.
- The fixed template paths and filesystem are trusted; restricting the public API to listed identifiers is authorized.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:template-load`. This is an audit annotation, not a validated sampling design.

## javascript-template-load-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L509) · Source SHA-256: `289115f3c913e0b27d1c6606a4027a3e55bddc8270b52d80de978c6c06ef7c49`

**app.js** (line numbers in findings refer to this file)

```javascript
const fs = require('fs');
const templates = { invoice: '/srv/templates/invoice.html', receipt: '/srv/templates/receipt.html' };
function handle(req) { if (!Object.hasOwn(templates, req.params.name)) throw Error('unknown'); return fs.readFileSync(templates[req.params.name]); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Map public identifiers to fixed file paths; reject unknown identifiers.

**Original remediation constraints:**

- Map public identifiers to fixed file paths; reject unknown identifiers.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.js:2-3 resolves only own properties of a fixed template map. Object.hasOwn prevents inherited names such as constructor from being accepted, and no caller-controlled path is concatenated into the filesystem operation.

**Assumptions:**

- The runtime supports Object.hasOwn and the supplied code executes server-side.
- The vulnerable route supplies a string containing decoded traversal, rather than a router that excludes every slash/traversal spelling.
- The fixed template paths and filesystem are trusted; restricting the public API to listed identifiers is authorized.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:template-load`. This is an audit annotation, not a validated sampling design.

## javascript-webhook-preview-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L539) · Source SHA-256: `57febf93f7f060cb7d96c5fae6e65b98cce8d66b3afab4a928a0af3f64b2155b`

**app.js** (line numbers in findings refer to this file)

```javascript
async function preview(req) { return (await fetch(req.body.url)).text(); }
```

**Expected findings:** [{"family": "ssrf", "cwe": "CWE-918", "path": "app.js"}]

**Original rationale:** Untrusted URL can address internal services.

**Original remediation constraints:**

- Use fixed external targets and reject redirect traversal.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.js:1 performs server-side fetch on req.body.url with no destination restriction. Internal addresses and redirect targets are reachable; CWE-918 fits under the server-side execution assumption.

**Assumptions:**

- This is a Node.js server with global fetch, not browser-only code.
- Configured host/DNS/proxy settings are trusted.
- The intended safe API accepts a public target ID and may reject arbitrary user URLs.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:webhook-preview`. This is an audit annotation, not a validated sampling design.

## javascript-webhook-preview-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L575) · Source SHA-256: `d50ebb71a5ac25baf886d6165e1404961b7dbdd99935b1416b0b895ab5c31fe3`

**app.js** (line numbers in findings refer to this file)

```javascript
async function preview(req) { const targets = { docs: 'https://docs.example.org/index' }; if (!Object.hasOwn(targets, req.body.target)) throw Error('unknown'); return (await fetch(targets[req.body.target], {redirect: 'error'})).text(); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use fixed external targets and reject redirect traversal.

**Original remediation constraints:**

- Use fixed external targets and reject redirect traversal.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.js:1 selects an own property from a fixed HTTPS destination map and sets redirect:error. Unknown identifiers fail before fetch and HTTP redirects are rejected, so the caller cannot select an internal destination through this code.

**Assumptions:**

- This is a Node.js server with global fetch, not browser-only code.
- Configured host/DNS/proxy settings are trusted.
- The intended safe API accepts a public target ID and may reject arbitrary user URLs.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:webhook-preview`. This is an audit annotation, not a validated sampling design.

## javascript-calculator-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L605) · Source SHA-256: `4c0df99f048d58ea6afccd1d2b9836e20932d862bc679e4cc08a85e4ab569381`

**app.js** (line numbers in findings refer to this file)

```javascript
function calculate(req) { return eval(req.body.expression); }
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.js"}]

**Original rationale:** Arbitrary input is evaluated as source.

**Original remediation constraints:**

- Use explicit numeric conversion and preserve supported numeric computation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable CWE-95 label is supported. The legitimate behavior required of a repair is underspecified in this case; this is a review-contract concern, not evidence that the scoring implementation uses a wrong reference fix.

**AI rationale:** app.js:1 evaluates req.body.expression as JavaScript, supporting CWE-95. This case asks for explicit numeric conversion while preserving supported numeric computation, but does not say whether legitimate inputs include arithmetic expressions such as 1+2 or only number literals. That case-local ambiguity can lead independent proposal reviewers to disagree about rejecting ordinary expressions.

**Assumptions:**

- The request field is an attacker-controlled string.
- The intended numeric grammar and operation have not been specified.

**Issues and recommended actions:**

- **major / LEGITIMATE_OPERATION_UNDERSPECIFIED** — app.js:1 accepts general JavaScript expressions, while this case's remediation constraints require numeric conversion without defining the permitted numeric grammar or input/output examples. A fix that rejects 1+2 may be valid for a number-only contract or a regression for an arithmetic calculator. Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

**Derivation group (AI assessment):** `javascript:calculator`. This is an audit annotation, not a validated sampling design.

## javascript-calculator-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L641) · Source SHA-256: `e9719ed81dff33eeaa52a40a0c88cf7c1827cc566b830537d515f92cae3bb28f`

**app.js** (line numbers in findings refer to this file)

```javascript
function calculate(req) { const value = Number(req.body.expression); if (!Number.isFinite(value)) throw Error('number required'); return value * 2; }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use explicit numeric conversion and preserve supported numeric computation.

**Original remediation constraints:**

- Use explicit numeric conversion and preserve supported numeric computation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe security label is supported when assessed independently. A behavior difference from a separate vulnerable case does not make this label wrong.

**AI rationale:** app.js:1 uses Number, checks finiteness and doubles the parsed number. It does not execute the input as JavaScript; the safe security label is supported. Its behavior differs from the vulnerable scenario, but benchmark.py evaluates each case independently and never treats this source as a reference fix for that other case.

**Assumptions:**

- The request field is an attacker-controlled string.
- This independent safe case computes twice a finite Number conversion; it is not a gold remediation for the vulnerable calculator.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:calculator`. This is an audit annotation, not a validated sampling design.

## javascript-account-lookup-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L671) · Source SHA-256: `c3ef1a5e47556f280ffb27b4832435606f00ef37ed19521e9054335e9366fcfb`

**app.js** (line numbers in findings refer to this file)

```javascript
async function lookup(req, db) { return db.query("SELECT id FROM accounts WHERE email='" + req.query.email + "'"); }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.js"}]

**Original rationale:** SQL literal incorporates caller input.

**Original remediation constraints:**

- Bind the value as a parameter and preserve the returned columns.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.js:1 concatenates caller email into a quoted SQL literal; a real SQL driver receives attacker-controlled syntax and CWE-89 fits. The db parameter is untyped and unconfigured, leaving placeholder syntax, return shape and the valid remediation API undecided.

**Assumptions:**

- lookup() is called with attacker-controlled email and a real database client.
- The accounts table and id/email columns exist.

**Issues and recommended actions:**

- **major / DATABASE_DRIVER_UNSPECIFIED** — app.js:1 calls a generic db.query; the paired ?-placeholder solution is not valid or equally safe for every possible driver. Declare a specific driver/version, SQL mode, query-input type and result contract so that reviewers can evaluate actual parameter binding.
  References: [github.com: mysql](https://github.com/mysqljs/mysql#escaping-query-values), [node-postgres.com: queries](https://node-postgres.com/features/queries#parameterized-query).

**Derivation group (AI assessment):** `javascript:account-lookup`. This is an audit annotation, not a validated sampling design.

## javascript-account-lookup-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L707) · Source SHA-256: `f1364945f7c60505bb02c9677f149350478c58f183da8ff5f67efb11cb2483d7`

**app.js** (line numbers in findings refer to this file)

```javascript
async function lookup(req, db) { return db.query('SELECT id FROM accounts WHERE email=?', [req.query.email]); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind the value as a parameter and preserve the returned columns.

**Original remediation constraints:**

- Bind the value as a parameter and preserve the returned columns.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** Safe only under a specified driver and scalar-input contract; the unconditional empty expected_findings label is not established by the supplied source.

**AI rationale:** app.js:1 passes req.query.email as a ? replacement, which can safely represent a scalar string in a declared compatible driver. It is not universally a prepared statement: mysqljs query performs client-side escaping by value shape, and an object such as {email:1} can expand the predicate to email=`email`=1. No scalar check or specific driver is present.

**Assumptions:**

- The safe label currently depends on an unstated database driver and a guarantee that email is a scalar string.
- The endpoint uses a query parser whose structured-value behavior must be pinned.

**Issues and recommended actions:**

- **major / SQL_SAFE_LABEL_DEPENDS_ON_DRIVER_AND_INPUT_SHAPE** — app.js:1 forwards unvalidated req.query.email to a generic ? substitution API. For mysqljs-compatible formatting, object-shaped input is expanded as SQL assignments instead of a single bound scalar; the official driver explicitly requires shape validation. Name the exact driver and require a scalar string or use a real prepared/execute API with documented parameter semantics. Include nested-query input as a counterexample in the revised corpus.
  References: [github.com: mysql](https://github.com/mysqljs/mysql#escaping-query-values).

**Derivation group (AI assessment):** `javascript:account-lookup`. This is an audit annotation, not a validated sampling design.

## javascript-payment-client-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L737) · Source SHA-256: `aab9911825b401f9fb3823300e52b1c09a09607c02597e944ed5e3d79b0d8fc6`

**app.js** (line numbers in findings refer to this file)

```javascript
const https = require('https');
const agent = new https.Agent({ rejectUnauthorized: false });
module.exports = agent;
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.js"}]

**Original rationale:** HTTP agent accepts untrusted certificates.

**Original remediation constraints:**

- Preserve certificate verification, including hostname checks.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.js:2-3 constructs and exports an HTTPS agent with rejectUnauthorized:false. This is a real insecure TLS configuration matching CWE-295, although no request using the exported agent is supplied.

**Assumptions:**

- A consuming HTTPS request uses the exported agent without overriding its verification settings.
- This is a structural configuration case; it does not establish an observed exploitable request path.
- The Node.js trust store and configured request hostname are trusted.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:payment-client`. This is an audit annotation, not a validated sampling design.

## javascript-payment-client-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L773) · Source SHA-256: `6330621fb6bc3626f6753ab57e124b1ef10c5b8932ea371e8003f20f984d2e17`

**app.js** (line numbers in findings refer to this file)

```javascript
const https = require('https');
const agent = new https.Agent({ rejectUnauthorized: true });
module.exports = agent;
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve certificate verification, including hostname checks.

**Original remediation constraints:**

- Preserve certificate verification, including hostname checks.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.js:2-3 exports an HTTPS agent with rejectUnauthorized:true and no custom identity-check override. The demonstrated certificate-verification configuration is safe.

**Assumptions:**

- A consuming HTTPS request uses the exported agent without overriding its verification settings.
- This is a structural configuration case; it does not establish an observed exploitable request path.
- The Node.js trust store and configured request hostname are trusted.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `javascript:payment-client`. This is an audit annotation, not a validated sampling design.

## typescript-backup-process-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L803) · Source SHA-256: `bbd3d1816488c4fa2ab9b78caf8425b4ea5552c3f62983c5170908d98d186246`

**app.ts** (line numbers in findings refer to this file)

```typescript
import { exec } from 'node:child_process';
export function backup(req: any) { exec(`backup-tool ${req.body.destination}`); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.ts"}]

**Original rationale:** Request text enters a shell command.

**Original remediation constraints:**

- Use an argument vector and terminate options without deleting command functionality.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.ts:2 interpolates destination into child_process.exec, whose shell interpretation supports CWE-78.

**Assumptions:**

- A Node.js application invokes backup() with an untrusted string destination.
- backup-tool is intended to be a trusted installed executable with a declared command-line interface.

**Issues and recommended actions:**

- **minor / UNSPECIFIED_EXECUTABLE_CONTRACT** — app.ts:2 invokes a fictional/unspecified backup-tool, so the corpus does not establish whether -- is accepted or which input preserves backup behavior. Document the trusted utility contract and representative valid destination/output, or use an actual pinned utility with those semantics.
  References: [nodejs.org: child_process.html](https://nodejs.org/api/child_process.html#child_processexecfilefile-args-options-callback).

**Derivation group (AI assessment):** `typescript:backup-process`. This is an audit annotation, not a validated sampling design.

## typescript-backup-process-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L839) · Source SHA-256: `354754d22e7829e9f90ae4ffb7f1aa2a9648f4b5900a1ebf6a2ec47fe2ead99a`

**app.ts** (line numbers in findings refer to this file)

```typescript
import { execFile } from 'node:child_process';
export function backup(req: any) { execFile('backup-tool', ['--', req.body.destination]); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use an argument vector and terminate options without deleting command functionality.

**Original remediation constraints:**

- Use an argument vector and terminate options without deleting command functionality.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.ts:2 uses execFile with a separate destination and --, removing shell interpretation. Whether -- protects options and still performs a backup depends on the undefined backup-tool interface.

**Assumptions:**

- A Node.js application invokes backup() with an untrusted string destination.
- backup-tool is intended to be a trusted installed executable with a declared command-line interface.

**Issues and recommended actions:**

- **minor / UNSPECIFIED_EXECUTABLE_CONTRACT** — app.ts:2 invokes a fictional/unspecified backup-tool, so the corpus does not establish whether -- is accepted or which input preserves backup behavior. Document the trusted utility contract and representative valid destination/output, or use an actual pinned utility with those semantics.
  References: [nodejs.org: child_process.html](https://nodejs.org/api/child_process.html#child_processexecfilefile-args-options-callback).

**Derivation group (AI assessment):** `typescript:backup-process`. This is an audit annotation, not a validated sampling design.

## typescript-document-load-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L869) · Source SHA-256: `5ee56c3d58023993730d0cb0c5814c0aeff00ca48ff3769bae79c8d10e6bd7ad`

**app.ts** (line numbers in findings refer to this file)

```typescript
import fs from 'node:fs';
export function load(req: any) { return fs.readFileSync(`/srv/docs/${req.query.path}`); }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.ts"}]

**Original rationale:** Request path escapes the intended root.

**Original remediation constraints:**

- Map public identifiers to fixed file paths; reject unknown identifiers.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.ts:2 interpolates req.query.path directly into a path below /srv/docs. Relative parent components are normalized by the filesystem and can reach other readable files; CWE-22 fits.

**Assumptions:**

- A Node.js server supplies an untrusted string path.
- The TypeScript module configuration supports the node:fs default import and a trusted filesystem.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `typescript:document-load`. This is an audit annotation, not a validated sampling design.

## typescript-document-load-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L905) · Source SHA-256: `6e527914bed97473d34a968098f4fb9c51f24d5255d5fe22da291ef926846a9c`

**app.ts** (line numbers in findings refer to this file)

```typescript
import fs from 'node:fs';
const docs: Record<string, string> = { terms: '/srv/docs/terms.pdf', help: '/srv/docs/help.pdf' };
export function load(req: any) { const p = docs[req.query.path]; if (!p) throw Error('unknown'); return fs.readFileSync(p); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Map public identifiers to fixed file paths; reject unknown identifiers.

**Original remediation constraints:**

- Map public identifiers to fixed file paths; reject unknown identifiers.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.ts:2-3 uses a fixed document map, so ordinary string IDs cannot construct an arbitrary file path. However, the truthiness check also admits inherited values such as constructor; in an ordinary unmodified prototype these are wrong-typed values that cause readFileSync to reject, not demonstrated traversal.

**Assumptions:**

- Object.prototype is not polluted by another component.
- The fixed files and filesystem are trusted.
- Node rejects inherited function/object values as invalid filesystem path types.

**Issues and recommended actions:**

- **minor / INHERITED_LOOKUP_NOT_EXPLICIT_ALLOWLIST** — app.ts:3 uses docs[key] and a truthiness check rather than an own-property check. Inherited names reach the filesystem API and violate the claimed explicit rejection contract, but no traversal exploit is established here. Use Object.hasOwn or a null-prototype/Map lookup and validate the input as a string, making the counterexample unambiguous.
  References: [tc39.es: ordinary-and-exotic-objects-behaviours.html](https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinaryget).

**Derivation group (AI assessment):** `typescript:document-load`. This is an audit annotation, not a validated sampling design.

## typescript-feed-preview-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L935) · Source SHA-256: `05244b4f37ec10ec4caa7e87cc144582d6e192b98f510256b4406ffe8e8e31d8`

**app.ts** (line numbers in findings refer to this file)

```typescript
import axios from 'axios';
export async function preview(req: any) { return (await axios.get(req.query.url)).data; }
```

**Expected findings:** [{"family": "ssrf", "cwe": "CWE-918", "path": "app.ts"}]

**Original rationale:** Untrusted URL can address internal services.

**Original remediation constraints:**

- Use fixed external targets and reject redirect traversal.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.ts:2 passes the entire caller URL to axios.get, allowing an untrusted requester to select server-side destinations. No address restriction or redirect policy is present; CWE-918 fits in Node.

**Assumptions:**

- This is server-side Axios using its Node HTTP adapter.
- The caller controls req.query.url and the server can reach a sensitive internal network destination.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `typescript:feed-preview`. This is an audit annotation, not a validated sampling design.

## typescript-feed-preview-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L971) · Source SHA-256: `3e87072299485e772ba8ec9e96cf8ffdfcbdc68cd6581e58e6cfaa15b465cb28`

**app.ts** (line numbers in findings refer to this file)

```typescript
import axios from 'axios';
const feeds: Record<string, string> = { news: 'https://news.example.org/feed' };
export async function preview(req: any) { const url = feeds[req.query.feed]; if (!url) throw Error('unknown'); return (await axios.get(url, {maxRedirects: 0})).data; }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use fixed external targets and reject redirect traversal.

**Original remediation constraints:**

- Use fixed external targets and reject redirect traversal.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.ts:2-3 selects a configured HTTPS feed and sets maxRedirects:0, which disables redirects for Axios in Node. The remaining plain-object lookup can produce inherited wrong-typed values; it does not show an attacker-chosen URL without a separate prototype mutation.

**Assumptions:**

- Axios uses the Node HTTP adapter; maxRedirects is a Node option and must not be assumed to control browser redirects.
- Object.prototype, the fixed host, DNS, proxy settings and global Axios defaults are trusted.
- The authorized API uses a feed ID instead of an arbitrary URL.

**Issues and recommended actions:**

- **minor / INHERITED_LOOKUP_NOT_EXPLICIT_ALLOWLIST** — app.ts:3 accepts any truthy feeds[key], including inherited non-URL values. The ordinary consequence is a URL/type error, not a demonstrated SSRF bypass. Use Object.hasOwn or Map and a string input check; record Node HTTP adapter semantics for maxRedirects.
  References: [tc39.es: ordinary-and-exotic-objects-behaviours.html](https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html#sec-ordinaryget), [axios.rest: request-config](https://axios.rest/pages/advanced/request-config#maxredirects-node-js-only).

**Derivation group (AI assessment):** `typescript:feed-preview`. This is an audit annotation, not a validated sampling design.

## typescript-formula-parser-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1001) · Source SHA-256: `7db75ab11c3a2c6bd86c844c1f0b3f55b11cda2bcc0930486663978b4d194bc0`

**app.ts** (line numbers in findings refer to this file)

```typescript
export function calculate(input: string): unknown { return new Function('return ' + input)(); }
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.ts"}]

**Original rationale:** Arbitrary input is evaluated as source.

**Original remediation constraints:**

- Use explicit numeric conversion and preserve supported numeric computation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable CWE-95 label is supported. The legitimate behavior required of a repair is underspecified in this case; this is a review-contract concern, not evidence that the scoring implementation uses a wrong reference fix.

**AI rationale:** app.ts:1 constructs and executes a Function from the supplied text, supporting CWE-95. The same case asks for numeric conversion while preserving supported numeric computation, but does not define whether a formula such as 1+2 must remain supported. The missing legitimate-input boundary is relevant to human review of proposals for this case itself.

**Assumptions:**

- The string argument crosses an untrusted-input boundary.
- The acceptable formula grammar and arithmetic operation are currently unspecified.

**Issues and recommended actions:**

- **major / LEGITIMATE_OPERATION_UNDERSPECIFIED** — app.ts:1 evaluates expressions while the remediation constraint asks for explicit numeric conversion. It does not specify accepted formula syntax, whether expression evaluation is a required feature, or examples of legitimate outputs. Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

**Derivation group (AI assessment):** `typescript:formula-parser`. This is an audit annotation, not a validated sampling design.

## typescript-formula-parser-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1037) · Source SHA-256: `27c55c39e5a48cc65f043fa0e919b076f38b4fe807e6d5eb0ccc6d2642a98e28`

**app.ts** (line numbers in findings refer to this file)

```typescript
export function calculate(input: string): number { const value = Number(input); if (!Number.isFinite(value)) throw Error('invalid'); return value + 1; }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use explicit numeric conversion and preserve supported numeric computation.

**Original remediation constraints:**

- Use explicit numeric conversion and preserve supported numeric computation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe security label is supported when assessed independently. A behavior difference from a separate vulnerable case does not make this label wrong.

**AI rationale:** app.ts:1 converts input to a finite number and adds one, without constructing executable code. The safe security label is supported. Adding one differs from the vulnerable case, but the runner does not supply this safe case to reviewers as that case's expected fix.

**Assumptions:**

- The string argument is untrusted.
- This independent safe case adds one to a finite numeric input; it is not a gold remediation for the vulnerable formula parser.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `typescript:formula-parser`. This is an audit annotation, not a validated sampling design.

## typescript-invoice-lookup-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1067) · Source SHA-256: `ddcb0a268d1a17fb2121d5d232872d40ed1a7cb3dccd7df1a8928bcbbeb7c5b3`

**app.ts** (line numbers in findings refer to this file)

```typescript
export function find(db: any, reference: string) { return db.query(`SELECT total FROM invoices WHERE ref='${reference}'`); }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.ts"}]

**Original rationale:** SQL literal incorporates caller input.

**Original remediation constraints:**

- Bind the value as a parameter and preserve the returned columns.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.ts:1 inserts reference into a quoted SQL template with no binding, supporting CWE-89 when the caller is untrusted.

**Assumptions:**

- reference is untrusted even though TypeScript annotates it as string.
- The intended database client is node-postgres or another explicitly declared $1-binding API, and invoices(total,ref) exists.

**Issues and recommended actions:**

- **minor / DATABASE_DRIVER_UNSPECIFIED** — app.ts:1 uses db:any while the safe counterpart requires the node-postgres-style $1 API. Declare the concrete client and version so a valid fix cannot be rejected or a nonfunctional placeholder accepted.
  References: [node-postgres.com: queries](https://node-postgres.com/features/queries#parameterized-query).

**Derivation group (AI assessment):** `typescript:invoice-lookup`. This is an audit annotation, not a validated sampling design.

## typescript-invoice-lookup-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1103) · Source SHA-256: `422282a2a7033f62de1a9a891242c6394855c0800f4d2b96eda48eb13e80f403`

**app.ts** (line numbers in findings refer to this file)

```typescript
export function find(db: any, reference: string) { return db.query('SELECT total FROM invoices WHERE ref=$1', [reference]); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind the value as a parameter and preserve the returned columns.

**Original remediation constraints:**

- Bind the value as a parameter and preserve the returned columns.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.ts:1 uses a $1 parameter and separate values, which is valid and safe for node-postgres. db:any does not establish that this is the actual driver; MySQL-style clients do not use that placeholder contract.

**Assumptions:**

- reference is untrusted even though TypeScript annotates it as string.
- The intended database client is node-postgres or another explicitly declared $1-binding API, and invoices(total,ref) exists.

**Issues and recommended actions:**

- **minor / DATABASE_DRIVER_UNSPECIFIED** — app.ts:1 uses db:any while the safe counterpart requires the node-postgres-style $1 API. Declare the concrete client and version so a valid fix cannot be rejected or a nonfunctional placeholder accepted.
  References: [node-postgres.com: queries](https://node-postgres.com/features/queries#parameterized-query).

**Derivation group (AI assessment):** `typescript:invoice-lookup`. This is an audit annotation, not a validated sampling design.

## typescript-metadata-client-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1133) · Source SHA-256: `c74a21f8e8d3fca91d446ffc2d39451ed89b6aac45dca2af8fc6bca9b946ca5c`

**app.ts** (line numbers in findings refer to this file)

```typescript
import https from 'node:https';
export const agent = new https.Agent({rejectUnauthorized: false});
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.ts"}]

**Original rationale:** HTTP agent accepts untrusted certificates.

**Original remediation constraints:**

- Preserve certificate verification, including hostname checks.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.ts:2 exports an HTTPS agent with certificate verification disabled. CWE-295 fits a structural TLS misconfiguration; there is no request call demonstrating use.

**Assumptions:**

- The Node.js TypeScript module setup supports the default HTTPS import.
- A consumer uses this exported agent for HTTPS without overriding its options.
- This is a structural configuration scenario, closely analogous to javascript-payment-client.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `typescript:metadata-client`. This is an audit annotation, not a validated sampling design.

## typescript-metadata-client-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1169) · Source SHA-256: `22cd98b81ccb66e023ea9bfe1d575d1a05bedb5831c58ac7883fd353a9eedb1f`

**app.ts** (line numbers in findings refer to this file)

```typescript
import https from 'node:https';
export const agent = new https.Agent({rejectUnauthorized: true});
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve certificate verification, including hostname checks.

**Original remediation constraints:**

- Preserve certificate verification, including hostname checks.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.ts:2 exports an HTTPS agent with rejection of unauthorized certificates enabled. No hostname-check bypass is present in the supplied code.

**Assumptions:**

- The Node.js TypeScript module setup supports the default HTTPS import.
- A consumer uses this exported agent for HTTPS without overriding its options.
- This is a structural configuration scenario, closely analogous to javascript-payment-client.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `typescript:metadata-client`. This is an audit annotation, not a validated sampling design.

## java-customer-search-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1199) · Source SHA-256: `60055bef017a84ea343831982ea831981a2c61cc29170f023e6f158a192a2d83`

**app.java** (line numbers in findings refer to this file)

```java
import java.sql.*;
class App { ResultSet search(Connection db, String name) throws Exception { return db.createStatement().executeQuery("SELECT id FROM customers WHERE name='" + name + "'"); } }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.java"}]

**Original rationale:** JDBC Statement incorporates caller text.

**Original remediation constraints:**

- Use a JDBC bound string parameter and retain query semantics.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** A caller-controlled string is inserted inside a SQL literal and sent to JDBC Statement.executeQuery. Quote-breaking input can change the query; CWE-89 and sql-injection are appropriate. Binding the single parameter is a focused remedy.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## java-customer-search-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1235) · Source SHA-256: `1f66b907b33d28cdb806cfe6d7c1f4d5f60368828987b45dee1ef6c41ee5077b`

**app.java** (line numbers in findings refer to this file)

```java
import java.sql.*;
class App { ResultSet search(Connection db, String name) throws Exception { PreparedStatement q = db.prepareStatement("SELECT id FROM customers WHERE name=?"); q.setString(1, name); return q.executeQuery(); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a JDBC bound string parameter and retain query semantics.

**Original remediation constraints:**

- Use a JDBC bound string parameter and retain query semantics.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The SQL structure is literal and caller input is supplied with setString, so apostrophes and Unicode stay data. The returned ResultSet preserves the demonstrated query result shape. No second SQL sink is present.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## java-xml-upload-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1265) · Source SHA-256: `86597e0f92bf6444cc685b86a6c2d14216cf83351064fac499c4d15464c0d0fb`

**app.java** (line numbers in findings refer to this file)

```java
import javax.xml.parsers.*;
import java.io.*;
class App { Object parse(InputStream body) throws Exception { return DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(body); } }
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.java"}]

**Original rationale:** Default XML factory permits external entities in untrusted XML.

**Original remediation constraints:**

- Disable DOCTYPE before constructing the parser and keep ordinary XML support.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** External entity resolution is plausible under the documented JDK defaults even though secure processing is enabled by default. The source has no explicit external-access restriction, resolver or DOCTYPE rejection. CWE-611 is appropriate in that environment.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.java:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## java-xml-upload-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1301) · Source SHA-256: `f662df25646d5a49095c4938cdd05fda424737d03926c087f72605d7c5976798`

**app.java** (line numbers in findings refer to this file)

```java
import javax.xml.parsers.*;
import java.io.*;
class App { Object parse(InputStream body) throws Exception { var f = DocumentBuilderFactory.newInstance(); f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); return f.newDocumentBuilder().parse(body); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Disable DOCTYPE before constructing the parser and keep ordinary XML support.

**Original remediation constraints:**

- Disable DOCTYPE before constructing the parser and keep ordinary XML support.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The feature is set on the same factory before construction. Rejecting DOCTYPE blocks the document-defined external entity path, and failure to support the feature throws before parsing. Ordinary DOCTYPE-free XML remains supported.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.java:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## java-session-restore-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1331) · Source SHA-256: `49ac7a28f1dcd130b6199da1d57b19222af2992236ba658c1031def7c0cb6144`

**app.java** (line numbers in findings refer to this file)

```java
import java.io.*;
class App { Object restore(InputStream body) throws Exception { return new ObjectInputStream(body).readObject(); } }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.java"}]

**Original rationale:** Native serialization executes reachable gadget behavior.

**Original remediation constraints:**

- Use bounded data-only representation, not unrestricted native objects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **major / UNDEFINED_RESTORATION_CONTRACT** — app.java:2: readObject can return arbitrary object types, while this case requires a bounded data-only replacement and preservation of the demonstrated operation/input-output behavior. No legitimate data model, encoding or allowed wire-format migration defines what an acceptable repair must retain. Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.
  References: [docs.oracle.com: java-serialization-filters.html](https://docs.oracle.com/en/java/javase/25/core/java-serialization-filters.html).
- **minor / OVERSTATED_GADGET_EVIDENCE** — app.java:2: The rationale asserts reachable gadget behavior, but this source only shows unrestricted readObject and supplies neither classpath assumptions nor a gadget with an observable effect. Describe potential dangerous deserialization under an explicit classpath/filter model; do not score an unproved specific execution consequence as established.
  References: [docs.oracle.com: java-serialization-filters.html](https://docs.oracle.com/en/java/javase/25/core/java-serialization-filters.html).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## java-session-restore-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1367) · Source SHA-256: `a411152b0584b11979efe161758951b89d8560c1b467d7fa133c50149ccf4ba1`

**app.java** (line numbers in findings refer to this file)

```java
import java.io.*;
import java.nio.charset.StandardCharsets;
class App { String restore(InputStream body) throws Exception { return new String(body.readNBytes(4096), StandardCharsets.UTF_8); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use bounded data-only representation, not unrestricted native objects.

**Original remediation constraints:**

- Use bounded data-only representation, not unrestricted native objects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone function reads at most 4096 bytes as UTF-8 and never constructs attacker-selected native objects. Its CWE-502 negative label is supported. The source explicitly defines bounded raw-text behavior; it is not evaluated as a gold repair for the separately submitted object-restoration case.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **minor / RAW_TEXT_REFERENCE_SCOPE** — app.java:3: Reading the first 4096 bytes is a bounded raw-text operation; it does not decode Java serialization and may return a prefix for longer input. That does not contradict this standalone safe label, but prevents assuming the case is a behavior-preserving reference fix for another case. Describe this case as bounded text reading. If used later as a remediation reference, separately define permitted format migration and oversize-input behavior.
  References: [docs.oracle.com: InputStream.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html#readNBytes(int)).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## java-legacy-digest-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1397) · Source SHA-256: `65df3ed33660f1ff5515fa3f1d0c6cfa1e273f37fb41830570a868d9662fad07`

**app.java** (line numbers in findings refer to this file)

```java
import java.security.*;
class App { byte[] digest(byte[] data) throws Exception { return MessageDigest.getInstance("MD5").digest(data); } }
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.java"}]

**Original rationale:** Security digest uses collision-broken MD5.

**Original remediation constraints:**

- Use SHA-256 for the integrity digest; do not claim password hashing suitability.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

**Issues and recommended actions:**

- **major / DIGEST_SECURITY_CONTEXT_MISSING** — app.java:2: The function only returns a digest; security-critical use appears solely in evaluation rationale. A non-security MD5 checksum can be legitimate, whereas an unauthenticated attacker-replaceable checksum remains unsafe even after SHA-256 substitution. Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## java-legacy-digest-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1433) · Source SHA-256: `17411e6758087b4caed1502e5d69eb836a0e131a6ceefa68fab44897b570da13`

**app.java** (line numbers in findings refer to this file)

```java
import java.security.*;
class App { byte[] digest(byte[] data) throws Exception { return MessageDigest.getInstance("SHA-256").digest(data); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256 for the integrity digest; do not claim password hashing suitability.

**Original remediation constraints:**

- Use SHA-256 for the integrity digest; do not claim password hashing suitability.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The standalone function computes SHA-256, with no password hashing or authentication construction shown. Its weak-cryptography negative label and SHA-256 preservation constraint are coherent locally.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.

**Issues and recommended actions:**

- **minor / DIGEST_SCOPE** — app.java:2: SHA-256 is a suitable general collision-resistant digest here. This small function does not establish authenticated integrity or password-hashing suitability, and those broader claims should not be inferred. Retain the safe negative label; state that it concerns algorithm choice and makes no broader claim about unseen consumers.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## java-support-shell-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1463) · Source SHA-256: `482903a19170d9d77db5add04af75293674df20f17c1c8c77e374f3532edbd7c`

**app.java** (line numbers in findings refer to this file)

```java
class App { Process lookup(String host) throws Exception { return new ProcessBuilder("sh", "-c", "getent hosts " + host).start(); } }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.java"}]

**Original rationale:** Host becomes executable shell syntax.

**Original remediation constraints:**

- Invoke getent with separate arguments and no shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The user-controlled value becomes part of the command interpreted by sh -c. Shell operators can introduce extra commands, matching CWE-78. A direct argument vector preserves the intended single lookup/stat operation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## java-support-shell-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1499) · Source SHA-256: `2692612a70c02fbe2f69a3139be0baa892a74f4a8ea61dd05358161cf975f8cb`

**app.java** (line numbers in findings refer to this file)

```java
class App { Process lookup(String host) throws Exception { return new ProcessBuilder("getent", "hosts", host).start(); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Invoke getent with separate arguments and no shell.

**Original remediation constraints:**

- Invoke getent with separate arguments and no shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** getent and hosts are separate literal arguments, and host is a single data argument. This removes shell metacharacter interpretation; the demonstrated shell-injection negative label is appropriate.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

**Issues and recommended actions:**

- **minor / UTILITY_ARGUMENT_CONTRACT** — app.java:1: The safe variant removes the shell, but its acceptance of leading-dash or malformed host strings depends on getent option parsing and the intended host-input contract. No general command-argument safety claim should be inferred from this negative shell-injection label. Document the supported getent/platform and valid hostname/IP domain, or use a compatible option terminator/validation if the operation permits arbitrary caller strings.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## java-hostname-check-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1529) · Source SHA-256: `aa53de27727156d7c66a06c0deddc8ad2612e7060cd3f29fd63654e84ccfb0d8`

**app.java** (line numbers in findings refer to this file)

```java
import javax.net.ssl.*;
class App { HostnameVerifier verifier() { return (host, session) -> true; } }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.java"}]

**Original rationale:** Custom hostname verifier accepts every host.

**Original remediation constraints:**

- Use a real hostname verifier and retain system trust behavior.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **major / HOSTNAME_CONSUMER_UNSPECIFIED** — app.java:2: The source only constructs/returns a verifier and never shows the client that uses it. getDefaultHostnameVerifier returns mutable global HttpsURLConnection policy; it is not evidence that an arbitrary consumer will perform complete hostname verification. Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## java-hostname-check-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1565) · Source SHA-256: `48ffadfe494c741ca583500c43f599143bea4dcb952feff2934f9c4c59749525`

**app.java** (line numbers in findings refer to this file)

```java
import javax.net.ssl.*;
class App { HostnameVerifier verifier() { return HttpsURLConnection.getDefaultHostnameVerifier(); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a real hostname verifier and retain system trust behavior.

**Original remediation constraints:**

- Use a real hostname verifier and retain system trust behavior.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** Fetching the platform default introduces no permissive verifier in this fragment. As an HttpsURLConnection configuration counterexample it is safe under unmodified defaults, but its behavior cannot be assumed for arbitrary third-party clients or replaced global defaults.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **minor / DEFAULT_VERIFIER_SCOPE** — app.java:2: The code retrieves the HttpsURLConnection default and introduces no insecure override. This supports the standalone safe configuration label under an unmodified platform default; it is not a universal verifier guarantee for arbitrary third-party consumers. Keep the safe label and document its intended HttpsURLConnection context. Consumer/global-default assumptions are scope notes, not evidence of a vulnerability in this supplied source.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## go-order-query-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1595) · Source SHA-256: `1e162f40ede1f3310ee6f660c3bc00696a942b54b5f548b6e368ff268f517075`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "database/sql"
func Orders(db *sql.DB, customer string) (*sql.Rows,error) { return db.Query("SELECT id FROM orders WHERE customer='" + customer + "'") }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.go"}]

**Original rationale:** User customer value enters SQL syntax.

**Original remediation constraints:**

- Use a bound query argument and preserve result rows.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.go:3 concatenates customer into SQL literal syntax before db.Query; quote-breaking input supports CWE-89.

**Assumptions:**

- customer is untrusted; the database connection and orders table are initialized by trusted code.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `go-order-query`. This is an audit annotation, not a validated sampling design.

## go-order-query-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1631) · Source SHA-256: `f77c19bd88a6c13a319119ec6fd83f16d7267b14985e07fb4972901f52d13433`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "database/sql"
func Orders(db *sql.DB, customer string) (*sql.Rows,error) { return db.Query("SELECT id FROM orders WHERE customer=$1", customer) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a bound query argument and preserve result rows.

**Original remediation constraints:**

- Use a bound query argument and preserve result rows.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.go:3 separates customer from the query text using a positional argument. This is injection-safe with a compatible driver, but the generic database/sql type does not establish that $1 is its placeholder syntax.

**Assumptions:**

- customer is untrusted; the database connection and orders table are initialized by trusted code.

**Issues and recommended actions:**

- **major / DATABASE_DRIVER_UNSPECIFIED** — app.go:3 uses PostgreSQL-style $1 through the driver-neutral database/sql interface. Declare the driver/database and schema; preserve the same database in the positive and negative cases.
  References: [go.dev: sql-injection](https://go.dev/doc/database/sql-injection).

**Derivation group (AI assessment):** `go-order-query`. This is an audit annotation, not a validated sampling design.

## go-custom-transport-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1661) · Source SHA-256: `ce6058eb4f6de90e053c36e6d288b28f06df5a4c3ce74802d3d38b36fb5bb6ba`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "crypto/tls"
func TransportTLS() *tls.Config { return &tls.Config{InsecureSkipVerify:true} }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.go"}]

**Original rationale:** TLS config disables identity and chain verification.

**Original remediation constraints:**

- Keep verification enabled and set a minimum TLS version.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.go:3 constructs a TLS client configuration that skips the default certificate-chain and hostname checks; no replacement verifier is supplied. CWE-295 fits this unsafe configuration.

**Assumptions:**

- This config is attached to an outbound TLS client/HTTP transport without later mutation; it is not an unused config or server-only setting.
- Trusted root configuration and server-name selection follow normal client behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `go-client-tls-verification`. This is an audit annotation, not a validated sampling design.

## go-custom-transport-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1697) · Source SHA-256: `b7b8ed3786ae324cf711b69cc4a4a8a841b77a3a4b70ecd63206ab39b35afb80`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "crypto/tls"
func TransportTLS() *tls.Config { return &tls.Config{MinVersion:tls.VersionTLS12} }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Keep verification enabled and set a minimum TLS version.

**Original remediation constraints:**

- Keep verification enabled and set a minimum TLS version.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.go:3 leaves certificate verification enabled and sets TLS 1.2 as the minimum. No permissive callback appears.

**Assumptions:**

- This config is attached to an outbound TLS client/HTTP transport without later mutation; it is not an unused config or server-only setting.
- Trusted root configuration and server-name selection follow normal client behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `go-client-tls-verification`. This is an audit annotation, not a validated sampling design.

## go-url-fetcher-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1727) · Source SHA-256: `0f0fa57bbd6d6e4fbd34ea12e2b175af138c55fb24bc0ad81c78e80c393ce4e6`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "net/http"
func Fetch(r *http.Request) (*http.Response,error) { return http.Get(r.URL.Query().Get("url")) }
```

**Expected findings:** [{"family": "ssrf", "cwe": "CWE-918", "path": "app.go"}]

**Original rationale:** Query-selected URL reaches outbound HTTP client.

**Original remediation constraints:**

- Permit only configured public destination and disable redirects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.go:3 sends the request-selected url to http.Get, allowing the requester to choose an outbound destination. CWE-918 fits a server that can reach resources unavailable to that requester.

**Assumptions:**

- The vulnerable helper runs in a server-side request context with privileged network reachability.
- The safe destination, proxy settings, DNS administration and trust roots are controlled by the operator.

**Issues and recommended actions:**

- **major / ALLOWED_REQUEST_CONTRACT_UNSPECIFIED** — app.go:3 accepts url, while the rubric requires a configured destination without specifying legitimate URLs or selector behavior. State the allowed destination/input and expected response contract so a reviewer can distinguish security restrictions from deleting supported behavior.

**Derivation group (AI assessment):** `go-url-fetcher`. This is an audit annotation, not a validated sampling design.

## go-url-fetcher-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1763) · Source SHA-256: `933e75d7c3d10d387e95294517e8843081adbe7b231e9cb78d2c2e016188c0bf`

**app.go** (line numbers in findings refer to this file)

```go
package app
import ("net/http"; "fmt")
func Fetch(r *http.Request) (*http.Response,error) { if r.URL.Query().Get("feed") != "news" { return nil,fmt.Errorf("unknown feed") }; c:=http.Client{CheckRedirect:func(_ *http.Request,_ []*http.Request)error{return http.ErrUseLastResponse}}; return c.Get("https://news.example.org/rss") }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Permit only configured public destination and disable redirects.

**Original remediation constraints:**

- Permit only configured public destination and disable redirects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.go:3 accepts only a news selector, chooses a fixed HTTPS destination, and prevents redirect following. No caller-supplied URL reaches the client.

**Assumptions:**

- The vulnerable helper runs in a server-side request context with privileged network reachability.
- The safe destination, proxy settings, DNS administration and trust roots are controlled by the operator.

**Issues and recommended actions:**

- **minor / COUNTERPART_IS_NOT_A_DROP_IN_FIX** — app.go:3 uses feed=news; the separate vulnerable example accepts url. This does not invalidate the standalone safe label. Document the independent input contract; do not treat this sibling as an automatically behavior-preserving remediation.

**Derivation group (AI assessment):** `go-url-fetcher`. This is an audit annotation, not a validated sampling design.

## go-diagnostic-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1793) · Source SHA-256: `af601c9d9d0e3a1e7854db5a6703707bd5cf25a500a3870e3c1ed5a0d46e4b46`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "os/exec"
func Lookup(name string) ([]byte,error) { return exec.Command("sh", "-c", "id " + name).Output() }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.go"}]

**Original rationale:** User name is parsed as shell source.

**Original remediation constraints:**

- Use separate arguments and guard option interpretation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.go:3 concatenates name into sh -c source. The shell interprets metacharacters, supporting CWE-78.

**Assumptions:**

- name is untrusted and the intended operation looks up one username.
- A trusted GNU-compatible id executable supporting -- is resolved through a trusted PATH.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `go-diagnostic-command`. This is an audit annotation, not a validated sampling design.

## go-diagnostic-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1829) · Source SHA-256: `777188587952c275e6f790b049acf0e2311c32c3edaac5dcbd952841ceebded1`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "os/exec"
func Lookup(name string) ([]byte,error) { return exec.Command("id", "--", name).Output() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use separate arguments and guard option interpretation.

**Original remediation constraints:**

- Use separate arguments and guard option interpretation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.go:3 invokes id directly and passes -- before the username; name is data in one argument and cannot introduce shell syntax.

**Assumptions:**

- name is untrusted and the intended operation looks up one username.
- A trusted GNU-compatible id executable supporting -- is resolved through a trusted PATH.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `go-diagnostic-command`. This is an audit annotation, not a validated sampling design.

## go-artifact-reader-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1859) · Source SHA-256: `5486b33d2316a3ab3b0e22de017977f3c27c8f9e34ead290643f880c4cdeb5dd`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "os"
func Read(name string) ([]byte,error) { return os.ReadFile("/srv/artifacts/" + name) }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.go"}]

**Original rationale:** Relative traversal can access arbitrary readable files.

**Original remediation constraints:**

- Resolve public artifact IDs to trusted fixed paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.go:3 prefixes an untrusted name with /srv/artifacts/ but does not constrain parent segments. A readable file outside that directory can be selected.

**Assumptions:**

- Only public artifacts are authorized; the vulnerable parameter crosses that access boundary.
- The allowlist, artifact file and its parent directories are not writable by the requester.

**Issues and recommended actions:**

- **minor / PUBLIC_ARTIFACT_CONTRACT_UNSPECIFIED** — app.go:3 and the constraints do not enumerate the legitimate artifact IDs or current path-to-ID mapping. Specify the allowed artifact set and compatibility requirements for the proposed public-ID interface.

**Derivation group (AI assessment):** `go-artifact-reader`. This is an audit annotation, not a validated sampling design.

## go-artifact-reader-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1895) · Source SHA-256: `9b280ff86df54d27396abb204fe6f381a14a9b551e17cfaea587994a38e8e653`

**app.go** (line numbers in findings refer to this file)

```go
package app
import ("os"; "fmt")
func Read(name string) ([]byte,error) { allowed:=map[string]string{"summary":"/srv/artifacts/summary.txt"}; p,ok:=allowed[name]; if !ok { return nil,fmt.Errorf("unknown artifact") }; return os.ReadFile(p) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Resolve public artifact IDs to trusted fixed paths.

**Original remediation constraints:**

- Resolve public artifact IDs to trusted fixed paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.go:3 maps the sole public ID summary to a fixed path and rejects unknown keys. Caller text cannot form traversal segments in the opened pathname.

**Assumptions:**

- Only public artifacts are authorized; the vulnerable parameter crosses that access boundary.
- The allowlist, artifact file and its parent directories are not writable by the requester.

**Issues and recommended actions:**

- **minor / COUNTERPART_IS_NOT_A_DROP_IN_FIX** — app.go:3 maps summary to summary.txt, whereas the vulnerable sibling treats name as a relative filename. Record this standalone safe API contract; require explicit caller migration if this design is proposed as a fix to the sibling.

**Derivation group (AI assessment):** `go-artifact-reader`. This is an audit annotation, not a validated sampling design.

## go-checksum-authentication-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1925) · Source SHA-256: `af1c595202bf676e0dc79028c1d938c6f50bb3d0639a3cd4892525c68621113e`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "crypto/md5"
func Integrity(data []byte) [16]byte { return md5.Sum(data) }
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.go"}]

**Original rationale:** Integrity check uses a collision-broken algorithm.

**Original remediation constraints:**

- Use SHA-256 and correctly adapt the digest size.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.go:3 uses MD5, a collision-broken digest, but the source contains no comparison, authenticated reference or security-sensitive consumer. A weak-algorithm observation is supported; exploitability is conditional.

**Assumptions:**

- No caller or expected-digest storage is supplied.
- Digest changes necessarily change output bytes; approved compatibility may include migrating digest consumers and stored values.

**Issues and recommended actions:**

- **major / SECURITY_PURPOSE_UNSPECIFIED** — app.go:3 computes and returns a digest; the security dependency that makes collisions consequential is not supplied. State whether this is collision-resistant content verification against a trusted reference, authentication, or a nonsecurity checksum; include the consumer and permitted migration.
  References: [pkg.go.dev: md5](https://pkg.go.dev/crypto/md5).

**Derivation group (AI assessment):** `go-checksum-authentication`. This is an audit annotation, not a validated sampling design.

## go-checksum-authentication-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L1961) · Source SHA-256: `79c3561efd454f080b8f90fa74d3892ba857513e2b7323d7a31b9266701fe71a`

**app.go** (line numbers in findings refer to this file)

```go
package app
import "crypto/sha256"
func Integrity(data []byte) [32]byte { return sha256.Sum256(data) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256 and correctly adapt the digest size.

**Original remediation constraints:**

- Use SHA-256 and correctly adapt the digest size.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.go:3 uses SHA-256 and the correct 32-byte return size. This removes the MD5 weakness, but an unkeyed digest is not by itself message authentication despite the scenario name.

**Assumptions:**

- No caller or expected-digest storage is supplied.
- Digest changes necessarily change output bytes; approved compatibility may include migrating digest consumers and stored values.

**Issues and recommended actions:**

- **major / AUTHENTICATION_CONTRACT_UNSPECIFIED** — app.go:3 is an unkeyed SHA-256 helper. Its safety claim must not imply authenticity without a trusted reference or keyed/signature construction. Define the intended verification property and caller protocol; keep a weak-digest negative label scoped to that property.

**Derivation group (AI assessment):** `go-checksum-authentication`. This is an audit annotation, not a validated sampling design.

## c-audit-format-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L1991) · Source SHA-256: `822abcc3e5e8cde1098ee79117e29f0eb337eeb172b7f35ed53f497af431dc46`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void audit(const char *message) { printf(message); }
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.c"}]

**Original rationale:** Untrusted text is used as a printf format string.

**Original remediation constraints:**

- Use a constant format with a string conversion, preserving percent signs as data.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.c:2 passes the caller string as the printf format; conversions are interpreted without matching arguments. CWE-134 is appropriate.

**Assumptions:**

- message is an untrusted, valid NUL-terminated string; the application intends literal text output.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## c-audit-format-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2027) · Source SHA-256: `c4ebb2b0f5ee16644eb28f34601bb8af86796bfc00dae3cc9ada68e9b52d13bc`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void audit(const char *message) { printf("%s", message); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a constant format with a string conversion, preserving percent signs as data.

**Original remediation constraints:**

- Use a constant format with a string conversion, preserving percent signs as data.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.c:2 uses the constant %s format and treats all caller percent signs as data.

**Assumptions:**

- message is an untrusted, valid NUL-terminated string; the application intends literal text output.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## c-archive-shell-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2057) · Source SHA-256: `e5656c00a84f99853b9ce46603ba5a830af0691bf1a185fe4b89dea10ba14829`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdlib.h>
#include <stdio.h>
int run(const char *name) { char command[1024]; snprintf(command,sizeof command,"tar -tf %s",name); return system(command); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.c"}]

**Original rationale:** Caller-controlled content is passed to shell execution.

**Original remediation constraints:**

- Preserve the operation with a direct API or argument vector, without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.c:3 places name in the command interpreted by system; snprintf bounds the command buffer but does not prevent shell injection.

**Assumptions:**

- The archive filename is untrusted, but the executable and local archive access policy are trusted.
- The safe snippet targets a GNU-compatible tar at /usr/bin/tar.

**Issues and recommended actions:**

- **minor / PROCESS_LIFECYCLE_CONTRACT_UNSPECIFIED** — app.c:3 waits via system and returns a wait status; the corpus supplies no caller that establishes the required return/lifecycle behavior. Make preservation of caller lifetime and exit-status semantics explicit when accepting a direct process fix. A child process with argv and wait is one design to evaluate.
  References: [pubs.opengroup.org: exec.html](https://pubs.opengroup.org/onlinepubs/007904875/functions/exec.html), [pubs.opengroup.org: popen.html](https://pubs.opengroup.org/onlinepubs/009696799/functions/popen.html).

**Derivation group (AI assessment):** `c-archive-shell`. This is an audit annotation, not a validated sampling design.

## c-archive-shell-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2093) · Source SHA-256: `f6ed03caec7921e1cbc203ebe2a4809b00453caf72222b99ceb23c2e2666c722`

**app.c** (line numbers in findings refer to this file)

```c
#include <unistd.h>
int run(const char *name) { return execl("/usr/bin/tar", "tar", "--list", "--file", name, (char*)0); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve the operation with a direct API or argument vector, without a shell.

**Original remediation constraints:**

- Preserve the operation with a direct API or argument vector, without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 passes the archive name as a separate execl argument. Shell syntax is not evaluated. Successful exec replaces the caller process, which must be intentional for this standalone example.

**Assumptions:**

- The archive filename is untrusted, but the executable and local archive access policy are trusted.
- The safe snippet targets a GNU-compatible tar at /usr/bin/tar.

**Issues and recommended actions:**

- **major / EXEC_REPLACES_PROCESS** — app.c:2 has no successful return from execl. It is a shell-safe independent example, not a drop-in replacement for the system-based sibling. Declare that replacing the current process is intended, or provide a child-process caller if this is meant to model a returning helper.
  References: [pubs.opengroup.org: exec.html](https://pubs.opengroup.org/onlinepubs/007904875/functions/exec.html).

**Derivation group (AI assessment):** `c-archive-shell`. This is an audit annotation, not a validated sampling design.

## c-bounded-copy-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2123) · Source SHA-256: `628289d9209d2d80fd72ef2676b5523ff30a65a7dba489f44fd5aa90bd3b6ff0`

**app.c** (line numbers in findings refer to this file)

```c
#include <string.h>
void save(const char *value) { char out[16]; strcpy(out,value); }
```

**Expected findings:** [{"family": "buffer-overflow", "cwe": "CWE-120", "path": "app.c"}]

**Original rationale:** Unbounded copy can exceed a fixed-size destination.

**Original remediation constraints:**

- Bound writes or use a dynamically sized string; preserve termination.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 copies arbitrary-length input into out[16] without a bound, supporting CWE-120 for sufficiently long input. The local buffer is never consumed.

**Assumptions:**

- value is a valid NUL-terminated string with caller-controlled length.

**Issues and recommended actions:**

- **major / NO_OBSERVABLE_OPERATION** — app.c:2 discards the local copy; there is no observable application behavior against which to assess a behavior-preserving fix. Add a realistic consumer and state whether overlength input must be rejected, preserved dynamically, or intentionally truncated.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## c-bounded-copy-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2159) · Source SHA-256: `61e21c07bf91e29c2b7376352a4440f4dad378c9198724f5485995f53a0012b3`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void save(const char *value) { char out[16]; snprintf(out,sizeof out,"%s",value); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bound writes or use a dynamically sized string; preserve termination.

**Original remediation constraints:**

- Bound writes or use a dynamically sized string; preserve termination.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 bounds writes to 16 bytes and terminates the result. Inputs longer than 15 bytes are silently truncated, and the result is never observed.

**Assumptions:**

- value is a valid NUL-terminated string with caller-controlled length.

**Issues and recommended actions:**

- **major / TRUNCATION_POLICY_UNSPECIFIED** — app.c:2 discards both the bounded copy and snprintf return value. The code is bounded, but useful output and truncation policy are absent. Give the independent case an observable result and explicit overlength behavior; do not infer full data preservation from bounded writes.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## c-stream-format-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2189) · Source SHA-256: `203b48e4d055989416efa7cd50676a2702beb0e03b846faefbd9bc9941c4dd31`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void emit(FILE *log, const char *value) { fprintf(log,value); }
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.c"}]

**Original rationale:** The logging/rendering sink interprets caller percent conversions.

**Original remediation constraints:**

- Render the entire supplied text as data with a bounded destination where applicable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.c:2 uses value as fprintf format text; an untrusted caller can introduce conversions. CWE-134 fits.

**Assumptions:**

- log is a valid trusted FILE stream; value is an untrusted valid NUL-terminated string intended for literal rendering.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## c-stream-format-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2225) · Source SHA-256: `8ca96eb45a4950dafc1ebd01b8ffe7a91a587f90a9d6d37744f814c71f7b620e`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void emit(FILE *log, const char *value) { fputs(value,log); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Render the entire supplied text as data with a bounded destination where applicable.

**Original remediation constraints:**

- Render the entire supplied text as data with a bounded destination where applicable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.c:2 writes value through fputs, which does not interpret printf conversions.

**Assumptions:**

- log is a valid trusted FILE stream; value is an untrusted valid NUL-terminated string intended for literal rendering.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## c-popen-pipeline-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2255) · Source SHA-256: `7d95b1c77b372d62c3912eb6d352a14d748ef04f22aa5603bcc45df934baf05e`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
FILE *query(const char *value) { char command[1024]; snprintf(command,sizeof command,"cat %s",value); return popen(command,"r"); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.c"}]

**Original rationale:** popen interprets arbitrary command syntax.

**Original remediation constraints:**

- Use direct file/process APIs; avoid retaining hidden shell expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 inserts value into a cat command parsed by popen through a shell. The command buffer bound does not prevent CWE-78.

**Assumptions:**

- The application is authorized to read the requested path; this case targets command interpretation, not an unspecified path-access boundary.
- Callers manage the returned stream with the matching API.

**Issues and recommended actions:**

- **major / STREAM_OWNERSHIP_CONTEXT_MISSING** — app.c:2 returns a popen stream whose caller should use pclose. A proposed fopen substitution requires a caller cleanup change. Supply the stream consumer/cleanup contract in the revised case so reviewers can assess any direct-file remediation without missing ownership regressions.
  References: [pubs.opengroup.org: popen.html](https://pubs.opengroup.org/onlinepubs/009696799/functions/popen.html).

**Derivation group (AI assessment):** `c-popen-pipeline`. This is an audit annotation, not a validated sampling design.

## c-popen-pipeline-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2291) · Source SHA-256: `6d057d49e3165db6b3e341c65a38bf5d5ebc5091afa4b8da9bd2680b4241a4f8`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
FILE *query(const char *value) { return fopen(value,"r"); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use direct file/process APIs; avoid retaining hidden shell expansion.

**Original remediation constraints:**

- Use direct file/process APIs; avoid retaining hidden shell expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.c:2 uses fopen directly. It opens a literal path without a shell, supporting the negative shell-injection label.

**Assumptions:**

- The application is authorized to read the requested path; this case targets command interpretation, not an unspecified path-access boundary.
- Callers manage the returned stream with the matching API.

**Issues and recommended actions:**

- **minor / COUNTERPART_CLEANUP_DIFFERS** — app.c:2 returns an ordinary file stream, unlike the independently scanned popen sibling. Document fclose ownership; do not accept this as a sibling remediation without reviewing consumers and pclose-to-fclose migration.
  References: [pubs.opengroup.org: popen.html](https://pubs.opengroup.org/onlinepubs/009696799/functions/popen.html).

**Derivation group (AI assessment):** `c-popen-pipeline`. This is an audit annotation, not a validated sampling design.

## c-formatted-copy-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2321) · Source SHA-256: `700f6bafc85dfab372f7893a0ca14b49e2d6695ddc4feae1e1c5e9dd26ae4f78`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void label(const char *value) { char b[24]; sprintf(b,"prefix:%s",value); }
```

**Expected findings:** [{"family": "buffer-overflow", "cwe": "CWE-120", "path": "app.c"}]

**Original rationale:** Formatting/concatenation lacks destination capacity.

**Original remediation constraints:**

- Respect buffer capacity or use a dynamically sized container.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 adds prefix: and unbounded caller text into b[24]; sufficiently long input overflows the local buffer. The format itself is constant, so CWE-120 is the relevant label.

**Assumptions:**

- value is a valid untrusted NUL-terminated string; snprintf has conforming C99/POSIX behavior.

**Issues and recommended actions:**

- **major / NO_OBSERVABLE_OPERATION** — app.c:2 computes a local label that is never returned or consumed. Provide a real label consumer and define size limits/error behavior before judging preserved functionality.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## c-formatted-copy-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2357) · Source SHA-256: `c4f5931d8cc8363139df8772105706846c761230d2bf952e671deb8c339a8f3f`

**app.c** (line numbers in findings refer to this file)

```c
#include <stdio.h>
void label(const char *value) { char b[24]; snprintf(b,sizeof b,"prefix:%s",value); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Respect buffer capacity or use a dynamically sized container.

**Original remediation constraints:**

- Respect buffer capacity or use a dynamically sized container.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.c:2 bounds the prefix and text to b capacity, eliminating that overwrite. It discards truncation information and the computed string.

**Assumptions:**

- value is a valid untrusted NUL-terminated string; snprintf has conforming C99/POSIX behavior.

**Issues and recommended actions:**

- **major / TRUNCATION_POLICY_UNSPECIFIED** — app.c:2 silently truncates long labels and never consumes the output. Specify whether truncation is acceptable and expose the relevant output/error behavior in the case.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## cpp-diagnostic-format-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2387) · Source SHA-256: `f9ca171b7b32a519e3f4b8f79aa04d50a5f120049e6fe81af36528d0a7c18f44`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
void report(const char *message) { std::fprintf(stderr, message); }
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.cpp"}]

**Original rationale:** Untrusted text is used as a printf format string.

**Original remediation constraints:**

- Use a constant format with a string conversion, preserving percent signs as data.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.cpp:2 forwards message into the fprintf format position. Namespace qualification does not change the uncontrolled-format semantics.

**Assumptions:**

- message is untrusted and valid NUL-terminated text, intended for literal diagnostic output.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## cpp-diagnostic-format-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2423) · Source SHA-256: `e9a327b83eabeb891e2a89346e4a27ebe57961505686bdb34db0504f32c12699`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
void report(const char *message) { std::fprintf(stderr, "%s", message); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a constant format with a string conversion, preserving percent signs as data.

**Original remediation constraints:**

- Use a constant format with a string conversion, preserving percent signs as data.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.cpp:2 uses a fixed %s conversion, so percent sequences in message are printed as data.

**Assumptions:**

- message is untrusted and valid NUL-terminated text, intended for literal diagnostic output.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `c-cpp-stdio-untrusted-format`. This is an audit annotation, not a validated sampling design.

## cpp-cleanup-shell-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2453) · Source SHA-256: `ac77d062b31b2118ace9d3aa804625a4792969c89cc6e7fcfaeb4528ea6e0d9c`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdlib>
#include <string>
int cleanup(const std::string &name) { return std::system(("rm " + name).c_str()); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.cpp"}]

**Original rationale:** Caller-controlled content is passed to shell execution.

**Original remediation constraints:**

- Preserve the operation with a direct API or argument vector, without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.cpp:3 sends rm plus caller-controlled name through std::system; shell metacharacters can alter execution.

**Assumptions:**

- The caller may remove the selected path; executable lookup and the surrounding process environment are trusted.

**Issues and recommended actions:**

- **minor / DELETE_API_CONTRACT_UNSPECIFIED** — app.cpp:3 returns a system wait status and invokes rm without directory removal options. Specify allowed object types and return/error expectations before accepting a direct filesystem replacement.

**Derivation group (AI assessment):** `cpp-cleanup-shell`. This is an audit annotation, not a validated sampling design.

## cpp-cleanup-shell-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2489) · Source SHA-256: `245b489f03fd7941807190790522b42ceadd7c5d5f42052f5df2d7570ab70441`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
#include <string>
int cleanup(const std::string &name) { return std::remove(name.c_str()); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve the operation with a direct API or argument vector, without a shell.

**Original remediation constraints:**

- Preserve the operation with a direct API or argument vector, without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.cpp:3 invokes std::remove directly on the literal pathname without shell interpretation.

**Assumptions:**

- The caller may remove the selected path; executable lookup and the surrounding process environment are trusted.

**Issues and recommended actions:**

- **minor / COUNTERPART_DELETE_SEMANTICS_DIFFER** — app.cpp:3 uses remove with its own return/error convention and can remove an empty directory; the rm-based sibling has different semantics. Treat this as a separate negative case; document file-only policy and caller changes if used as a remediation design.

**Derivation group (AI assessment):** `cpp-cleanup-shell`. This is an audit annotation, not a validated sampling design.

## cpp-name-copy-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2519) · Source SHA-256: `fdcd2853b5eb0c8911f314dbac07653f6d6e0752e40fbfea7b6063b56732ae38`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstring>
void name(const char *input) { char out[32]; std::strcpy(out,input); }
```

**Expected findings:** [{"family": "buffer-overflow", "cwe": "CWE-120", "path": "app.cpp"}]

**Original rationale:** Unbounded copy can exceed a fixed-size destination.

**Original remediation constraints:**

- Bound writes or use a dynamically sized string; preserve termination.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.cpp:2 copies caller text into out[32] with no bound. CWE-120 fits long input, but the copied name is never used.

**Assumptions:**

- input is a valid untrusted NUL-terminated string.
- Ordinary allocation failure is outside this targeted buffer-overflow label.

**Issues and recommended actions:**

- **major / NO_OBSERVABLE_OPERATION** — app.cpp:2 discards the only copied value, making legitimate functionality unclear for proposal review. Add a real consumer/result contract and define any allowed API migration.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## cpp-name-copy-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2555) · Source SHA-256: `3af35cc51c651465ef62a139eb70fb4f1cdf47f86bf692e267e9c6f5a591e7f9`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <string>
std::string name(const char *input) { return std::string(input); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bound writes or use a dynamically sized string; preserve termination.

**Original remediation constraints:**

- Bound writes or use a dynamically sized string; preserve termination.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.cpp:2 constructs a dynamically sized string and returns it; there is no fixed destination overflow.

**Assumptions:**

- input is a valid untrusted NUL-terminated string.
- Ordinary allocation failure is outside this targeted buffer-overflow label.

**Issues and recommended actions:**

- **minor / COUNTERPART_API_DIFFERS** — app.cpp:2 returns std::string, while the sibling has a void signature. This is a valid standalone safer API, not automatic caller compatibility. Review declarations and callers if a proposed fix adopts this return type.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-copy`. This is an audit annotation, not a validated sampling design.

## cpp-buffer-format-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2585) · Source SHA-256: `64e0b1cf2813217becb23bdb63ed878d2209f8c483ee32a290b4a16b69648f26`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
void render(char *out, const char *value) { std::sprintf(out,value); }
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.cpp"}]

**Original rationale:** The logging/rendering sink interprets caller percent conversions.

**Original remediation constraints:**

- Render the entire supplied text as data with a bounded destination where applicable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.cpp:2 has both caller-controlled format interpretation and no destination capacity. CWE-134 is valid but the supplied expected findings omit the separate unbounded-write concern.

**Assumptions:**

- out is writable and value is valid untrusted NUL-terminated text.
- For the negative label, n must not exceed the actual out allocation and pointers must obey snprintf preconditions.

**Issues and recommended actions:**

- **major / EXPECTED_FINDINGS_INCOMPLETE** — app.cpp:2 uses unbounded sprintf with an unknown destination capacity; fixing only the format leaves a potential overwrite. Add the relevant buffer-overflow expected finding or explicitly document multi-weakness scope, and include caller capacity context.
- **major / FULL_TEXT_CAPACITY_CONTRACT** — app.cpp:2 has no way to determine destination capacity while the constraints require full rendering. Define dynamic output, safe rejection, or another approved capacity contract so a reviewer can assess fixes consistently.

**Derivation group (AI assessment):** `c-cpp-stdio-buffer-format`. This is an audit annotation, not a validated sampling design.

## cpp-buffer-format-safe

**AI verdict:** revise · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2621) · Source SHA-256: `8e072ec04044df507a5c5f9d93ca3f5265967a997c26bacc22d284508224dc4b`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
#include <cstddef>
void render(char *out, std::size_t n, const char *value) { std::snprintf(out,n,"%s",value); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Render the entire supplied text as data with a bounded destination where applicable.

**Original remediation constraints:**

- Render the entire supplied text as data with a bounded destination where applicable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.cpp:3 fixes the format and bounds the write when n is accurate. However, it can truncate input while the case constraints demand rendering the entire supplied text.

**Assumptions:**

- out is writable and value is valid untrusted NUL-terminated text.
- For the negative label, n must not exceed the actual out allocation and pointers must obey snprintf preconditions.

**Issues and recommended actions:**

- **major / SAFE_CODE_CONTRADICTS_FULL_TEXT_CONSTRAINT** — app.cpp:3 ignores snprintf return value; input exceeding n-1 is truncated, contradicting the explicit full-text requirement. Specify a sufficient-capacity precondition with caller evidence, expose and handle truncation, or revise the approved behavior contract.

**Derivation group (AI assessment):** `c-cpp-stdio-buffer-format`. This is an audit annotation, not a validated sampling design.

## cpp-query-pipeline-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2651) · Source SHA-256: `07ab3319d90eda1e6ea81648e5ed697e42eabf9cf60a0d5ee38929ed43c80d76`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstdio>
#include <string>
FILE *query(const std::string &host) { return popen(("ping -c 1 " + host).c_str(),"r"); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.cpp"}]

**Original rationale:** popen interprets arbitrary command syntax.

**Original remediation constraints:**

- Use direct file/process APIs; avoid retaining hidden shell expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.cpp:3 concatenates host into a ping command consumed by popen; untrusted metacharacters are shell source, supporting CWE-78.

**Assumptions:**

- host is untrusted; the original function is intended to expose one ping operation to a stream consumer.
- The safe snippet requires a trusted /bin/ping implementation accepting the shown arguments including --.

**Issues and recommended actions:**

- **minor / PIPE_CONSUMER_CONTEXT_MISSING** — app.cpp:3 returns FILE* from popen; the corpus omits readers, cleanup and required subprocess exit handling. Include a bounded consumer contract; assess direct-argv proposals for preservation of stream output and parent lifetime.
  References: [pubs.opengroup.org: popen.html](https://pubs.opengroup.org/onlinepubs/009696799/functions/popen.html).

**Derivation group (AI assessment):** `cpp-query-pipeline`. This is an audit annotation, not a validated sampling design.

## cpp-query-pipeline-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2687) · Source SHA-256: `08388d58dae5fa51ab774dfc2d91078056610c7c95c0dcac02d8688bc6796a15`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <unistd.h>
#include <string>
int query(const std::string &host) { return execl("/bin/ping", "ping", "-c", "1", "--", host.c_str(), (char*)0); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use direct file/process APIs; avoid retaining hidden shell expansion.

**Original remediation constraints:**

- Use direct file/process APIs; avoid retaining hidden shell expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.cpp:3 passes host as one argument to execl, avoiding shell parsing. The program becomes ping on success; no output stream is returned.

**Assumptions:**

- host is untrusted; the original function is intended to expose one ping operation to a stream consumer.
- The safe snippet requires a trusted /bin/ping implementation accepting the shown arguments including --.

**Issues and recommended actions:**

- **major / EXEC_AND_OUTPUT_CONTRACT_UNSPECIFIED** — app.cpp:3 returns int only on failure and replaces the process on success. The separate sibling returns FILE*; they are not interchangeable. Declare an intentionally process-replacing negative example, or supply pipe/child/wait context for a returning API. Do not use this independent safe case as a gold fix.
  References: [pubs.opengroup.org: exec.html](https://pubs.opengroup.org/onlinepubs/007904875/functions/exec.html).

**Derivation group (AI assessment):** `cpp-query-pipeline`. This is an audit annotation, not a validated sampling design.

## cpp-joined-buffer-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2717) · Source SHA-256: `c975d4eedd684e7491186d239f8f17d7d1107fca37fc74a793365274ff162b14`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <cstring>
void join(char *out, const char *input) { std::strcat(out,input); }
```

**Expected findings:** [{"family": "buffer-overflow", "cwe": "CWE-120", "path": "app.cpp"}]

**Original rationale:** Formatting/concatenation lacks destination capacity.

**Original remediation constraints:**

- Respect buffer capacity or use a dynamically sized container.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.cpp:2 appends untrusted text with strcat without receiving or checking out capacity. A sufficiently long append supports CWE-120.

**Assumptions:**

- The vulnerable out initially contains a terminated string but has insufficient spare capacity for some attacker-controlled inputs.
- String inputs are valid and ordinary memory-allocation failure is outside the target label.

**Issues and recommended actions:**

- **minor / MUTATION_CONTRACT_CONTEXT** — app.cpp:2 mutates caller storage. A remediation that returns a new value must update consumers rather than silently lose the mutation. Include a caller or state that mutation/return-contract migration must be reviewed.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-concatenation`. This is an audit annotation, not a validated sampling design.

## cpp-joined-buffer-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2753) · Source SHA-256: `eead61f11b301044a73210fce9e4ce6d5b6b6b2cd738f6cbffc8a5b1f3b292c0`

**app.cpp** (line numbers in findings refer to this file)

```cpp
#include <string>
std::string join(std::string out, const std::string &input) { return out + input; }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Respect buffer capacity or use a dynamically sized container.

**Original remediation constraints:**

- Respect buffer capacity or use a dynamically sized container.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.cpp:2 returns a newly concatenated dynamically sized std::string; it has no fixed-capacity append.

**Assumptions:**

- The vulnerable out initially contains a terminated string but has insufficient spare capacity for some attacker-controlled inputs.
- String inputs are valid and ordinary memory-allocation failure is outside the target label.

**Issues and recommended actions:**

- **minor / COUNTERPART_MUTATION_DIFFERS** — app.cpp:2 takes out by value and returns the result. It does not mutate the caller as the separate strcat sibling does. Keep the standalone negative label; do not use this code as a drop-in remediation without caller changes.

**Derivation group (AI assessment):** `c-cpp-fixed-buffer-concatenation`. This is an audit annotation, not a validated sampling design.

## ruby-record-filter-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2783) · Source SHA-256: `f22a073127cc8837ef41ef867545eb88dc40e55c1c2e3bde9f28b754e45fd9c5`

**app.rb** (line numbers in findings refer to this file)

```ruby
class UsersController
  def search
    User.where("email = '#{params[:email]}'")
  end
end
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.rb"}]

**Original rationale:** ActiveRecord where string interpolates user text.

**Original remediation constraints:**

- Use hash conditions or bound parameters and preserve exact email lookup.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.rb:3 interpolates request email into an ActiveRecord SQL condition string. A quote in the value becomes SQL syntax, so CWE-89 fits once the relation is evaluated.

**Assumptions:**

- The snippet is incorporated into a Rails controller where params is defined and User is an ActiveRecord model.
- The controller/relation is actually evaluated by the request path; ActiveRecord relations are lazy.
- email is a string; array-valued filters are not claimed to preserve exact single-email semantics.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:record-filter`. This is an audit annotation, not a validated sampling design.

## ruby-record-filter-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2819) · Source SHA-256: `b952ca29a13ab3d41b466242a4b388c8b7c2ba65fe1af07c5498635aca0cbde9`

**app.rb** (line numbers in findings refer to this file)

```ruby
class UsersController
  def search
    User.where(email: params[:email])
  end
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use hash conditions or bound parameters and preserve exact email lookup.

**Original remediation constraints:**

- Use hash conditions or bound parameters and preserve exact email lookup.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.rb:3 passes a hash condition to ActiveRecord, keeping the email as a value rather than SQL source. A string value preserves exact email matching and quoted characters.

**Assumptions:**

- The snippet is incorporated into a Rails controller where params is defined and User is an ActiveRecord model.
- The controller/relation is actually evaluated by the request path; ActiveRecord relations are lazy.
- email is a string; array-valued filters are not claimed to preserve exact single-email semantics.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:record-filter`. This is an audit annotation, not a validated sampling design.

## ruby-session-marshal-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2849) · Source SHA-256: `6c2a4f67648d9d114046d590a9fef2cb6d0f3b9db5e67c59ec96b12067f3e5bb`

**app.rb** (line numbers in findings refer to this file)

```ruby
def restore(body)
  Marshal.load(body)
end
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.rb"}]

**Original rationale:** Marshal restores arbitrary Ruby objects.

**Original remediation constraints:**

- Use a data-only object format with a type check.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.rb:2 directly unmarshals the caller body, permitting reconstruction of arbitrary loaded Ruby classes. CWE-502 fits; the exact code-execution effect depends on classes available in the host process.

**Assumptions:**

- body contains untrusted serialized input.
- The accepted remediation explicitly permits a JSON wire-format migration; old Marshal clients are outside the demonstrated input contract.
- Overall input-size limits are supplied by the application.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:session-marshal`. This is an audit annotation, not a validated sampling design.

## ruby-session-marshal-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2885) · Source SHA-256: `bc4b93f4e08d422a70dca63eebab5a73ee8227f49bf4bf655604d67da3854e9c`

**app.rb** (line numbers in findings refer to this file)

```ruby
require 'json'
def restore(body)
  result = JSON.parse(body)
  raise 'object required' unless result.is_a?(Hash)
  result
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a data-only object format with a type check.

**Original remediation constraints:**

- Use a data-only object format with a type check.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.rb:3-5 calls JSON.parse and enforces Hash, preventing arbitrary class selection. No create-additions option is enabled. The requested data-only object format is implemented.

**Assumptions:**

- body contains untrusted serialized input.
- The accepted remediation explicitly permits a JSON wire-format migration; old Marshal clients are outside the demonstrated input contract.
- Overall input-size limits are supplied by the application.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:session-marshal`. This is an audit annotation, not a validated sampling design.

## ruby-profile-yaml-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2915) · Source SHA-256: `cac5606da833902c5785c3214eb3dc0c37c2bf388cb7f871e8fb060f131b7c12`

**app.rb** (line numbers in findings refer to this file)

```ruby
require 'yaml'
def profile(body)
  YAML.unsafe_load(body)
end
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.rb"}]

**Original rationale:** YAML unsafe loader permits application object construction.

**Original remediation constraints:**

- Disallow arbitrary classes, symbols and aliases.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.rb:3 invokes YAML.unsafe_load on the supplied body. This permits arbitrary class deserialization and object construction, supporting CWE-502 under the untrusted-body assumption.

**Assumptions:**

- Ruby loads a Psych version exposing these keyword options.
- body is untrusted profile YAML; arbitrary application objects are not a legitimate required profile type.
- Primitive YAML input remains an allowed profile representation.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:profile-yaml`. This is an audit annotation, not a validated sampling design.

## ruby-profile-yaml-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L2951) · Source SHA-256: `cdec92f8c89f701eabfa7b9704646e6d668ddcc722c7b4e26dbff238d34e38d3`

**app.rb** (line numbers in findings refer to this file)

```ruby
require 'yaml'
def profile(body)
  YAML.safe_load(body, permitted_classes: [], permitted_symbols: [], aliases: false)
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Disallow arbitrary classes, symbols and aliases.

**Original remediation constraints:**

- Disallow arbitrary classes, symbols and aliases.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.rb:3 uses safe_load with empty permitted class/symbol lists and aliases:false. Only permitted primitive data is constructed and alias references are rejected; the stated counterexample is supported.

**Assumptions:**

- Ruby loads a Psych version exposing these keyword options.
- body is untrusted profile YAML; arbitrary application objects are not a legitimate required profile type.
- Primitive YAML input remains an allowed profile representation.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:profile-yaml`. This is an audit annotation, not a validated sampling design.

## ruby-hostname-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L2981) · Source SHA-256: `ed528725ba16ae94aa0ab0dd078074f4e28830d2be0245a86252528000ffce41`

**app.rb** (line numbers in findings refer to this file)

```ruby
def resolve(name)
  system("getent hosts #{name}")
end
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.rb"}]

**Original rationale:** String-form system includes attacker shell syntax.

**Original remediation constraints:**

- Use multi-argument system and retain lookup behavior.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.rb:2 passes one interpolated string to system. A user name containing shell metacharacters triggers shell interpretation; CWE-78 fits. The same input surface also requires command-option handling in a fix.

**Assumptions:**

- The Ruby process runs on a platform with trusted getent available.
- name is an untrusted hostname string and the lookup is invoked.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:hostname-command`. This is an audit annotation, not a validated sampling design.

## ruby-hostname-command-safe

**AI verdict:** revise · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3017) · Source SHA-256: `4ca061cb54e34fb443881419b68fd0d9e1d60b8d7e2031a95dd6ec06b4ae1868`

**app.rb** (line numbers in findings refer to this file)

```ruby
def resolve(name)
  system('getent', 'hosts', name)
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use multi-argument system and retain lookup behavior.

**Original remediation constraints:**

- Use multi-argument system and retain lookup behavior.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported against CWE-78 specifically, but the empty all-findings expectation is incomplete because attacker-controlled command options remain (CWE-88).

**AI rationale:** app.rb:2 uses Ruby multi-argument system, so shell metacharacters are passed literally. GNU getent still parses options using argp_parse with default flags: a supplied name such as --help or --service=files can select an option rather than remain a hosts key. This is argument injection, not shell injection.

**Assumptions:**

- The utility is GNU/glibc getent with ordinary GNU option parsing.
- name is an arbitrary caller-controlled string, including values beginning with a dash.

**Issues and recommended actions:**

- **major / UNTERMINATED_COMMAND_OPTIONS** — app.rb:2 fixes shell interpretation but gives an untrusted string to getent without ending option parsing. The all-safe label omits the remaining option-control behavior. Pass an option terminator before the hostname according to the pinned getent contract and include a leading-dash counterexample; alternatively constrain input to a validated hostname grammar.
  References: [ruby-doc.org: Kernel.html](https://ruby-doc.org/3.4/Kernel.html#method-i-system), [raw.githubusercontent.com: getent.c](https://raw.githubusercontent.com/bminor/glibc/master/nss/getent.c).

**Derivation group (AI assessment):** `ruby:hostname-command`. This is an audit annotation, not a validated sampling design.

## ruby-stored-expression-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3047) · Source SHA-256: `f1e60f26b5c9ef45d8128209bb06c71414a1491ae3be993554eb1813cabc63de`

**app.rb** (line numbers in findings refer to this file)

```ruby
def value(expression)
  eval(expression)
end
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.rb"}]

**Original rationale:** Expression string runs Ruby code.

**Original remediation constraints:**

- Use numeric parsing for the intended numeric operation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable CWE-95 label is supported. The legitimate behavior required of a repair is underspecified in this case; this is a review-contract concern, not evidence that the scoring implementation uses a wrong reference fix.

**AI rationale:** app.rb:2 evaluates untrusted expression text as Ruby source, supporting CWE-95. The instruction to use numeric parsing for the intended numeric operation leaves the allowed expression grammar and output contract unstated. Human reviewers need that case-local distinction to decide whether a proposed restricted parser preserves legitimate use.

**Assumptions:**

- expression is attacker-controlled text.
- The intended numeric operation and accepted syntax have not been stated.

**Issues and recommended actions:**

- **major / LEGITIMATE_OPERATION_UNDERSPECIFIED** — app.rb:2 accepts arbitrary Ruby expression syntax, but the remediation constraints do not define the intended numeric operation or which nonliteral arithmetic expressions are legitimate. A reviewer cannot infer the required safe grammar from the unrelated safe-case implementation. Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

**Derivation group (AI assessment):** `ruby:stored-expression`. This is an audit annotation, not a validated sampling design.

## ruby-stored-expression-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3083) · Source SHA-256: `d62153af431e1eacc005f88239ed5919fc8fdb1679996cb47c9eb942f3479083`

**app.rb** (line numbers in findings refer to this file)

```ruby
def value(expression)
  Float(expression) * 2
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use numeric parsing for the intended numeric operation.

**Original remediation constraints:**

- Use numeric parsing for the intended numeric operation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe security label is supported when assessed independently. A behavior difference from a separate vulnerable case does not make this label wrong.

**AI rationale:** app.rb:2 parses with Float and multiplies by two, without evaluating Ruby source. This supports the safe security label. The distinct output contract does not itself invalidate this independently evaluated safe case or demonstrate a scoring defect.

**Assumptions:**

- expression is caller-controlled text.
- This independent safe case doubles a Float conversion; it is not a gold remediation for the vulnerable stored-expression case.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:stored-expression`. This is an audit annotation, not a validated sampling design.

## ruby-certificate-mode-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3113) · Source SHA-256: `12be47ee79f654533d3581d88af074a9933fc5e3ca3646f86d7ae9ba48a7829b`

**app.rb** (line numbers in findings refer to this file)

```ruby
require 'net/http'
def client(host)
  http = Net::HTTP.new(host,443)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_NONE
  http
end
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.rb"}]

**Original rationale:** HTTPS peer verification is disabled.

**Original remediation constraints:**

- Keep TLS peer validation enabled.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.rb:3-6 enables TLS then sets VERIFY_NONE before returning the Net::HTTP client. This disables server certificate authentication and fits CWE-295 as a structural client configuration.

**Assumptions:**

- The supported Ruby/OpenSSL version uses standard Net::HTTP TLS and hostname-verification defaults.
- The returned client is used for an HTTPS request without later insecure modification.
- This demonstrates client configuration rather than an actual HTTP operation.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:certificate-mode`. This is an audit annotation, not a validated sampling design.

## ruby-certificate-mode-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3149) · Source SHA-256: `19efc679e384da17850faf26fca267387b2d2d479f7340212396c48f21356af6`

**app.rb** (line numbers in findings refer to this file)

```ruby
require 'net/http'
def client(host)
  http = Net::HTTP.new(host,443)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_PEER
  http
end
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Keep TLS peer validation enabled.

**Original remediation constraints:**

- Keep TLS peer validation enabled.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.rb:3-6 enables TLS and retains VERIFY_PEER. Modern Net::HTTP retains its default hostname verification; the supplied code does not override it.

**Assumptions:**

- The supported Ruby/OpenSSL version uses standard Net::HTTP TLS and hostname-verification defaults.
- The returned client is used for an HTTPS request without later insecure modification.
- This demonstrates client configuration rather than an actual HTTP operation.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `ruby:certificate-mode`. This is an audit annotation, not a validated sampling design.

## php-member-filter-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3179) · Source SHA-256: `e3ef8ae00115a8caf02ca17f4784961c42a880e5a762ea0b66a2a8a5448215f7`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function find_member($db) { return mysqli_query($db, "SELECT id FROM users WHERE name='" . $_GET['name'] . "'"); }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.php"}]

**Original rationale:** mysqli query concatenates a request parameter.

**Original remediation constraints:**

- Use prepared parameters while retaining query/result semantics.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.php:2 concatenates $_GET[name] into a quoted mysqli SQL string. A caller-controlled quote can alter query structure, supporting CWE-89.

**Assumptions:**

- The mysqli connection is valid and users(id,name) exists.
- The safe variant requires mysqlnd for mysqli_stmt_get_result, as documented by PHP; that runtime dependency should be pinned.
- The request name is a scalar string and intended query errors are handled by the hosting application.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:member-filter`. This is an audit annotation, not a validated sampling design.

## php-member-filter-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3215) · Source SHA-256: `33bb25cdcf98d3160779404921fd5d042536b018462b29bb91e34d438fa32efc`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function find_member($db) { $q = mysqli_prepare($db, "SELECT id FROM users WHERE name=?"); mysqli_stmt_bind_param($q, 's', $_GET['name']); mysqli_stmt_execute($q); return mysqli_stmt_get_result($q); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use prepared parameters while retaining query/result semantics.

**Original remediation constraints:**

- Use prepared parameters while retaining query/result semantics.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.php:2 prepares a fixed query, binds the value with string type, executes, and retrieves a mysqli_result. This separates SQL from the input and preserves the SELECT result abstraction.

**Assumptions:**

- The mysqli connection is valid and users(id,name) exists.
- The safe variant requires mysqlnd for mysqli_stmt_get_result, as documented by PHP; that runtime dependency should be pinned.
- The request name is a scalar string and intended query errors are handled by the hosting application.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:member-filter`. This is an audit annotation, not a validated sampling design.

## php-download-path-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3245) · Source SHA-256: `ffa920cbdc0e6c919375f4c0b9ad94c23fcd19eb0fd6c36b0c81acec535a898d`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function download() { return file_get_contents('/srv/downloads/' . $_GET['name']); }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.php"}]

**Original rationale:** File name allows traversal outside downloads.

**Original remediation constraints:**

- Use an allow-listed document identifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.php:2 concatenates $_GET[name] below /srv/downloads and reads it. Relative parent segments can escape the root, supporting CWE-22.

**Assumptions:**

- The intended public download API may be restricted to the configured manual identifier.
- Configured file paths and filesystem permissions are trusted.
- The request key is scalar; invalid array-valued parameters are rejected by the PHP call contract rather than treated as paths.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:download-path`. This is an audit annotation, not a validated sampling design.

## php-download-path-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3281) · Source SHA-256: `7806bd24567266b5ba7e6f8abd0123d62efca8a91d4bfc56433b4c827ce33a55`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function download() { $files = ['manual' => '/srv/downloads/manual.pdf']; if (!array_key_exists($_GET['name'], $files)) throw new Exception('unknown'); return file_get_contents($files[$_GET['name']]); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use an allow-listed document identifier.

**Original remediation constraints:**

- Use an allow-listed document identifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.php:2 maps only a present allowlisted identifier to a fixed filename, rejects unknown keys before reading, and never combines caller bytes with a filesystem path.

**Assumptions:**

- The intended public download API may be restricted to the configured manual identifier.
- Configured file paths and filesystem permissions are trusted.
- The request key is scalar; invalid array-valued parameters are rejected by the PHP call contract rather than treated as paths.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:download-path`. This is an audit annotation, not a validated sampling design.

## php-remember-cookie-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3311) · Source SHA-256: `9b0c80e4024294e4a0b8dcdb17948fcfbb98c92d76c1e83121a97df9f12ea35d`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function restore() { return unserialize($_COOKIE['state']); }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.php"}]

**Original rationale:** Cookie creates arbitrary serialized objects.

**Original remediation constraints:**

- Use data-only JSON with bounded depth and error handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.php:2 unserializes raw cookie data with no class restriction or authenticity check. Attacker-chosen objects can invoke deserialization hooks when corresponding classes exist; CWE-502 fits.

**Assumptions:**

- The PHP runtime supports JSON_THROW_ON_ERROR (PHP 7.3+).
- The cookie is untrusted; application authentication/authorization does not trust restored privilege claims solely because parsing is safe.
- The specified remediation authorizes JSON migration; the host catches JSON exceptions and enforces an overall cookie-size limit.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:remember-cookie`. This is an audit annotation, not a validated sampling design.

## php-remember-cookie-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3347) · Source SHA-256: `981a994c9640ead872473a20a34797d705ab83fa0a9436265c74471bf524c2c0`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function restore() { return json_decode($_COOKIE['state'], true, 32, JSON_THROW_ON_ERROR); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use data-only JSON with bounded depth and error handling.

**Original remediation constraints:**

- Use data-only JSON with bounded depth and error handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.php:2 uses JSON decoding into arrays, caps nesting at 32 and requests exceptions on malformed JSON. No arbitrary PHP object instantiation remains. The constraint does not require a top-level mapping, so accepting JSON scalars is not itself a mismatch.

**Assumptions:**

- The PHP runtime supports JSON_THROW_ON_ERROR (PHP 7.3+).
- The cookie is untrusted; application authentication/authorization does not trust restored privilege claims solely because parsing is safe.
- The specified remediation authorizes JSON migration; the host catches JSON exceptions and enforces an overall cookie-size limit.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:remember-cookie`. This is an audit annotation, not a validated sampling design.

## php-diagnostics-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3377) · Source SHA-256: `3ede5461f79d01274957c8be020ee86142d7b4f9c07380f77e388ca504246a5c`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function ping() { return shell_exec('ping -c 1 ' . $_GET['host']); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.php"}]

**Original rationale:** Host text changes the shell command.

**Original remediation constraints:**

- Quote the complete argument and terminate command options.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.php:2 appends an untrusted host to shell_exec. Shell punctuation can alter the command, so CWE-78 fits.

**Assumptions:**

- The server uses a POSIX shell and a Linux/compatible ping supporting -c and --; these are not portable Windows semantics.
- The locale and trusted executable path are controlled by the service.
- Arbitrary ICMP destination selection is the intended diagnostic capability, not a promise that this routine restricts network reachability.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:diagnostics`. This is an audit annotation, not a validated sampling design.

## php-diagnostics-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3413) · Source SHA-256: `11e5a0bc7e607b7f4121c163b2b7c208dabb428c1e742b451d51705ab2b2b855`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function ping() { return shell_exec('ping -c 1 -- ' . escapeshellarg($_GET['host'])); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Quote the complete argument and terminate command options.

**Original remediation constraints:**

- Quote the complete argument and terminate command options.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.php:2 places -- before one escapeshellarg-quoted host. Under a POSIX shell and a ping accepting --, the host is a single argument and cannot select options or inject shell syntax.

**Assumptions:**

- The server uses a POSIX shell and a Linux/compatible ping supporting -c and --; these are not portable Windows semantics.
- The locale and trusted executable path are controlled by the service.
- Arbitrary ICMP destination selection is the intended diagnostic capability, not a promise that this routine restricts network reachability.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:diagnostics`. This is an audit annotation, not a validated sampling design.

## php-dynamic-plugin-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3443) · Source SHA-256: `345d8478500fa5e322a6aba61aa51b8664f4af00b8b1e115b6e92ed8c6c41151`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function transform($source) { return eval($source); }
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.php"}]

**Original rationale:** Plugin text is evaluated as PHP.

**Original remediation constraints:**

- Provide the intended string transformation without executing source.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable CWE-95 label is supported. The legitimate behavior required of a repair is underspecified in this case; this is a review-contract concern, not evidence that the scoring implementation uses a wrong reference fix.

**AI rationale:** app.php:2 evaluates supplied PHP code and returns its result, supporting CWE-95. This case asks for the intended string transformation without identifying that transformation, permitted operations, or normal input/output examples. The vulnerability label is sound; the legitimate replacement behavior needs definition within this case before proposals can be reviewed consistently.

**Assumptions:**

- source is attacker-controlled.
- The proposed intended string transformation has not been defined in the vulnerable program.

**Issues and recommended actions:**

- **major / LEGITIMATE_OPERATION_UNDERSPECIFIED** — app.php:2 exposes PHP evaluation, while the remediation constraint says to provide the intended string transformation without naming it. No case-local example establishes whether uppercase conversion, a selected plugin operation, or another transformation is required. Specify legitimate input syntax, intended operations, rejection behavior and representative input/output examples in this case's remediation contract. Preserve rejection of executable source. Version revised metadata and obtain human approval before freezing; do not use the paired safe case as an unstated gold fix.

**Derivation group (AI assessment):** `php:dynamic-plugin`. This is an audit annotation, not a validated sampling design.

## php-dynamic-plugin-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3479) · Source SHA-256: `0d17938d2c1393e4a57591398d11a1999def9f16b8a1f1a79a488a73c3614c56`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function transform($source) { return strtoupper($source); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Provide the intended string transformation without executing source.

**Original remediation constraints:**

- Provide the intended string transformation without executing source.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe security label is supported when assessed independently. A behavior difference from a separate vulnerable case does not make this label wrong.

**AI rationale:** app.php:2 applies strtoupper to the supplied string and never executes PHP source. The safe security label is supported. It is a separate uppercase-transform example, not a behavior-preserving gold fix for the eval scenario; the benchmark does not use it as one.

**Assumptions:**

- source is caller-controlled text.
- The operation of this independent safe case is strtoupper string conversion; it is not a gold remediation for the vulnerable plugin evaluator.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:dynamic-plugin`. This is an audit annotation, not a validated sampling design.

## php-account-query-pdo-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3509) · Source SHA-256: `edad7174d0f6712518c4b104728d55a879cf30645d0cbf669ba471f898b2a629`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function balance($pdo, $account) { return $pdo->query("SELECT balance FROM accounts WHERE id=" . $account); }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.php"}]

**Original rationale:** PDO query incorporates account input.

**Original remediation constraints:**

- Bind account ID separately and retain returned balance.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label and expected family/CWE are supported under the stated assumptions.

**AI rationale:** app.php:2 concatenates account directly into a numeric SQL expression. If the caller controls that string, it can introduce operators or additional SQL syntax; CWE-89 fits without requiring stacked statements.

**Assumptions:**

- account is caller-controlled text, not an already validated integer supplied by a trusted layer.
- A real PDO driver supports ? placeholders and the accounts(id,balance) schema.
- PDO driver encoding and any emulation settings are correctly configured for the supported deployment.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:account-query-pdo`. This is an audit annotation, not a validated sampling design.

## php-account-query-pdo-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3545) · Source SHA-256: `7a0fab2b68fbf88e1ee61bfe3fd685fce48827c31fa1034ac45ec420dc31ddb4`

**app.php** (line numbers in findings refer to this file)

```php
<?php
function balance($pdo, $account) { $q=$pdo->prepare('SELECT balance FROM accounts WHERE id=?'); $q->execute([$account]); return $q; }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind account ID separately and retain returned balance.

**Original remediation constraints:**

- Bind account ID separately and retain returned balance.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed safe label is supported for the demonstrated target security property under the stated assumptions.

**AI rationale:** app.php:2 prepares a fixed statement, supplies account as a positional parameter and returns the executed statement, preserving the PDOStatement-style result. Account data is not concatenated into SQL.

**Assumptions:**

- account is caller-controlled text, not an already validated integer supplied by a trusted layer.
- A real PDO driver supports ? placeholders and the accounts(id,balance) schema.
- PDO driver encoding and any emulation settings are correctly configured for the supported deployment.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `php:account-query-pdo`. This is an audit annotation, not a validated sampling design.

## kotlin-invoice-jdbc-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3575) · Source SHA-256: `a00547465c4ab146a51c1f80bbb0b10ec921c638eba37209a405961485de2cae`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.sql.Connection
fun invoice(db: Connection, ref: String) = db.createStatement().executeQuery("SELECT total FROM invoices WHERE ref='$ref'")
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.kt"}]

**Original rationale:** String template injects JDBC SQL.

**Original remediation constraints:**

- Use PreparedStatement parameters.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** A caller-controlled string is inserted inside a SQL literal and sent to JDBC Statement.executeQuery. Quote-breaking input can change the query; CWE-89 and sql-injection are appropriate. Binding the single parameter is a focused remedy.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## kotlin-invoice-jdbc-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3611) · Source SHA-256: `d00c22ec7199e665415f7914be43da215589d192677e1cf86f644f58d1ff20a3`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.sql.Connection
fun invoice(db: Connection, ref: String): java.sql.ResultSet { val q = db.prepareStatement("SELECT total FROM invoices WHERE ref=?"); q.setString(1, ref); return q.executeQuery() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use PreparedStatement parameters.

**Original remediation constraints:**

- Use PreparedStatement parameters.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The SQL structure is literal and caller input is supplied with setString, so apostrophes and Unicode stay data. The returned ResultSet preserves the demonstrated query result shape. No second SQL sink is present.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## kotlin-xml-dom-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3641) · Source SHA-256: `be498e4a38de7b6e22208003452ca69627b6581061ab43971d7649c9864b71e9`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import javax.xml.parsers.DocumentBuilderFactory
import java.io.InputStream
fun parse(input: InputStream) = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(input)
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.kt"}]

**Original rationale:** Default DOM parser may expand external entities.

**Original remediation constraints:**

- Disable DOCTYPE on the factory used for this parser.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** External entity resolution is plausible under the documented JDK defaults even though secure processing is enabled by default. The source has no explicit external-access restriction, resolver or DOCTYPE rejection. CWE-611 is appropriate in that environment.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.kt:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## kotlin-xml-dom-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3677) · Source SHA-256: `61f5923337b627995d85280a1bca665ee4586b13f0a35071875b498aac11f583`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import javax.xml.parsers.DocumentBuilderFactory
import java.io.InputStream
fun parse(input: InputStream): org.w3c.dom.Document { val f=DocumentBuilderFactory.newInstance(); f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); return f.newDocumentBuilder().parse(input) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Disable DOCTYPE on the factory used for this parser.

**Original remediation constraints:**

- Disable DOCTYPE on the factory used for this parser.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The feature is set on the same factory before construction. Rejecting DOCTYPE blocks the document-defined external entity path, and failure to support the feature throws before parsing. Ordinary DOCTYPE-free XML remains supported.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.kt:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## kotlin-native-state-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3707) · Source SHA-256: `1cf10c9ee6189ce19fd3183bbc22b285b23ec974f5f33f2645e8580ec8b3d3de`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.io.*
fun decode(body: InputStream): Any = ObjectInputStream(body).readObject()
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.kt"}]

**Original rationale:** Native object stream loads untrusted objects.

**Original remediation constraints:**

- Read bounded data rather than native serialized objects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **major / UNDEFINED_RESTORATION_CONTRACT** — app.kt:2: readObject can return arbitrary object types, while this case requires a bounded data-only replacement and preservation of the demonstrated operation/input-output behavior. No legitimate data model, encoding or allowed wire-format migration defines what an acceptable repair must retain. Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.
  References: [docs.oracle.com: java-serialization-filters.html](https://docs.oracle.com/en/java/javase/25/core/java-serialization-filters.html).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## kotlin-native-state-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3743) · Source SHA-256: `4434a7e165505b4aa2d0b3a91d2455770f5cdfeafa58e80c48ee2b8b837995f7`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.io.*
fun decode(body: InputStream): String = body.readNBytes(4096).toString(Charsets.UTF_8)
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Read bounded data rather than native serialized objects.

**Original remediation constraints:**

- Read bounded data rather than native serialized objects.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone function reads at most 4096 bytes as UTF-8 and never constructs attacker-selected native objects. Its CWE-502 negative label is supported. The source explicitly defines bounded raw-text behavior; it is not evaluated as a gold repair for the separately submitted object-restoration case.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **minor / RAW_TEXT_REFERENCE_SCOPE** — app.kt:2: Reading the first 4096 bytes is a bounded raw-text operation; it does not decode Java serialization and may return a prefix for longer input. That does not contradict this standalone safe label, but prevents assuming the case is a behavior-preserving reference fix for another case. Describe this case as bounded text reading. If used later as a remediation reference, separately define permitted format migration and oversize-input behavior.
  References: [docs.oracle.com: InputStream.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html#readNBytes(int)).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## kotlin-digest-choice-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3773) · Source SHA-256: `a0d717dd33cac01c453edbd3247b6781de0698cd53b4389d476313336eb7168d`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.security.MessageDigest
fun digest(data: ByteArray) = MessageDigest.getInstance("MD5").digest(data)
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.kt"}]

**Original rationale:** Integrity digest uses MD5.

**Original remediation constraints:**

- Use SHA-256 without claiming suitability for passwords.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

**Issues and recommended actions:**

- **major / DIGEST_SECURITY_CONTEXT_MISSING** — app.kt:2: The function only returns a digest; security-critical use appears solely in evaluation rationale. A non-security MD5 checksum can be legitimate, whereas an unauthenticated attacker-replaceable checksum remains unsafe even after SHA-256 substitution. Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## kotlin-digest-choice-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3809) · Source SHA-256: `064293eae65a1883f73d6c6a2b6f0a7c9b036806d974678bb49c59cbd978f290`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import java.security.MessageDigest
fun digest(data: ByteArray) = MessageDigest.getInstance("SHA-256").digest(data)
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256 without claiming suitability for passwords.

**Original remediation constraints:**

- Use SHA-256 without claiming suitability for passwords.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The standalone function computes SHA-256, with no password hashing or authentication construction shown. Its weak-cryptography negative label and SHA-256 preservation constraint are coherent locally.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.

**Issues and recommended actions:**

- **minor / DIGEST_SCOPE** — app.kt:2: SHA-256 is a suitable general collision-resistant digest here. This small function does not establish authenticated integrity or password-hashing suitability, and those broader claims should not be inferred. Retain the safe negative label; state that it concerns algorithm choice and makes no broader claim about unseen consumers.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## kotlin-maintenance-shell-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3839) · Source SHA-256: `2763f094afcea3695525ec9ad70e09be878df0dc2bb4d13e19d972dcb69a23a7`

**app.kt** (line numbers in findings refer to this file)

```kotlin
fun inspect(path: String) = ProcessBuilder("sh", "-c", "stat $path").start()
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.kt"}]

**Original rationale:** User path is shell syntax.

**Original remediation constraints:**

- Pass path as an argument after an option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The user-controlled value becomes part of the command interpreted by sh -c. Shell operators can introduce extra commands, matching CWE-78. A direct argument vector preserves the intended single lookup/stat operation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## kotlin-maintenance-shell-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3875) · Source SHA-256: `b60747fded701a5c01b5f8cb90eddf138b2c6ea74d30c5d7182b14ec2de6f2f6`

**app.kt** (line numbers in findings refer to this file)

```kotlin
fun inspect(path: String) = ProcessBuilder("stat", "--", path).start()
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Pass path as an argument after an option terminator.

**Original remediation constraints:**

- Pass path as an argument after an option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The utility and user input occupy separate ProcessBuilder arguments and no shell interprets metacharacters. The option terminator in stat/id also prevents an input beginning with a dash from becoming an option.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## kotlin-host-verifier-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3905) · Source SHA-256: `399d49cefa16d49714b1ff74b2e2116b4d08694e9061ca821994116fc592a577`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import javax.net.ssl.HostnameVerifier
fun verifier() = HostnameVerifier { _, _ -> true }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.kt"}]

**Original rationale:** Verifier unconditionally accepts hostname mismatches.

**Original remediation constraints:**

- Delegate to a real hostname verifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **major / HOSTNAME_CONSUMER_UNSPECIFIED** — app.kt:2: The source only constructs/returns a verifier and never shows the client that uses it. getDefaultHostnameVerifier returns mutable global HttpsURLConnection policy; it is not evidence that an arbitrary consumer will perform complete hostname verification. Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## kotlin-host-verifier-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L3941) · Source SHA-256: `cd0d872c73c7062ebe2ca262c1ca7c1551c4fd5d23de13c226d54065c062331a`

**app.kt** (line numbers in findings refer to this file)

```kotlin
import javax.net.ssl.HttpsURLConnection
fun verifier() = HttpsURLConnection.getDefaultHostnameVerifier()
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Delegate to a real hostname verifier.

**Original remediation constraints:**

- Delegate to a real hostname verifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** Fetching the platform default introduces no permissive verifier in this fragment. As an HttpsURLConnection configuration counterexample it is safe under unmodified defaults, but its behavior cannot be assumed for arbitrary third-party clients or replaced global defaults.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **minor / DEFAULT_VERIFIER_SCOPE** — app.kt:2: The code retrieves the HttpsURLConnection default and introduces no insecure override. This supports the standalone safe configuration label under an unmodified platform default; it is not a universal verifier guarantee for arbitrary third-party consumers. Keep the safe label and document its intended HttpsURLConnection context. Consumer/global-default assumptions are scope notes, not evidence of a vulnerability in this supplied source.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## scala-customer-jdbc-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L3971) · Source SHA-256: `47134407f8fc2e6fe7ddb9ac76e3ddc3e6d42f2e73227237d3a26934a37d04e6`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.sql.Connection
object App { def find(db: Connection, name: String) = db.createStatement().executeQuery(s"SELECT id FROM customers WHERE name='$name'") }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.scala"}]

**Original rationale:** Interpolated SQL query includes caller input.

**Original remediation constraints:**

- Bind name through JDBC rather than interpolation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** A caller-controlled string is inserted inside a SQL literal and sent to JDBC Statement.executeQuery. Quote-breaking input can change the query; CWE-89 and sql-injection are appropriate. Binding the single parameter is a focused remedy.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## scala-customer-jdbc-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4007) · Source SHA-256: `2b33283f9fb058e835962f1ccf155687dcb857429ec9c7ce3f52469101140c97`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.sql.Connection
object App { def find(db: Connection, name: String) = { val q=db.prepareStatement("SELECT id FROM customers WHERE name=?"); q.setString(1,name); q.executeQuery() } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind name through JDBC rather than interpolation.

**Original remediation constraints:**

- Bind name through JDBC rather than interpolation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The SQL structure is literal and caller input is supplied with setString, so apostrophes and Unicode stay data. The returned ResultSet preserves the demonstrated query result shape. No second SQL sink is present.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The string parameter is attacker-controlled; the Connection is trusted and the named table exists.
- The consumer owns ResultSet/Statement cleanup; this corpus labels injection, not general JDBC resource-lifetime behavior.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jdbc-bound-name`. This is an audit annotation, not a validated sampling design.

## scala-document-factory-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4037) · Source SHA-256: `6dbd8018308a8de76b3e2d26fdc1a3b0c4a0318fe5b9e68c29b19299b279c662`

**app.scala** (line numbers in findings refer to this file)

```scala
import javax.xml.parsers.DocumentBuilderFactory
import java.io.InputStream
object App { def parse(body: InputStream) = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(body) }
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.scala"}]

**Original rationale:** DOM XML parser has unsafe entity defaults.

**Original remediation constraints:**

- Set the disallow-DOCTYPE feature on the same factory instance.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** External entity resolution is plausible under the documented JDK defaults even though secure processing is enabled by default. The source has no explicit external-access restriction, resolver or DOCTYPE rejection. CWE-611 is appropriate in that environment.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.scala:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## scala-document-factory-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4073) · Source SHA-256: `41643d354c50131d7ab785aa280c305fe202fda020c5e1e85294a077fdc425e2`

**app.scala** (line numbers in findings refer to this file)

```scala
import javax.xml.parsers.DocumentBuilderFactory
import java.io.InputStream
object App { def parse(body: InputStream) = { val f=DocumentBuilderFactory.newInstance(); f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); f.newDocumentBuilder().parse(body) } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Set the disallow-DOCTYPE feature on the same factory instance.

**Original remediation constraints:**

- Set the disallow-DOCTYPE feature on the same factory instance.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The feature is set on the same factory before construction. Rejecting DOCTYPE blocks the document-defined external entity path, and failure to support the feature throws before parsing. Ordinary DOCTYPE-free XML remains supported.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- Attacker-controlled XML reaches parse; the intended runtime is an OpenJDK/Oracle JDK DOM provider supporting the Apache disallow-doctype-decl feature.
- The vulnerable runtime has no system/JAXP configuration denying DTD access; ordinary accepted documents do not require a DOCTYPE.
- Input size is bounded outside this fragment; safe means protected against the labeled XXE family, not every XML denial-of-service condition.

**Issues and recommended actions:**

- **minor / XML_RUNTIME_ASSUMPTIONS** — app.scala:3: newInstance selects a provider and JAXP settings can be supplied outside this source; the metadata does not pin those settings. The vulnerable label must not be justified merely by assuming modern secure-processing defaults disable external entities. Record the JDK/provider and external-access settings, plus the contract that ordinary input excludes DTD-dependent documents. Do not reject this label solely because FEATURE_SECURE_PROCESSING is on by default.
  References: [docs.oracle.com: java-api-xml-processing-jaxp-security-guide.html](https://docs.oracle.com/en/java/javase/25/security/java-api-xml-processing-jaxp-security-guide.html), [docs.oracle.com: DocumentBuilderFactory.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/parsers/DocumentBuilderFactory.html).

**Derivation group (AI assessment):** `jaxp-dom-doctype`. This is an audit annotation, not a validated sampling design.

## scala-job-state-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4103) · Source SHA-256: `ea0a676e820eb1d20b982cf870b4e8ff81b399f9d4e141762fc79c7260dac274`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.io._
object App { def restore(in: InputStream): AnyRef = new ObjectInputStream(in).readObject() }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.scala"}]

**Original rationale:** Untrusted state is restored as Java objects.

**Original remediation constraints:**

- Decode bounded data-only input.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** ObjectInputStream.readObject accepts attacker-selected serialized classes without a local restriction. CWE-502 is reasonable, but concrete gadget execution depends on the available classes and filters; no specific execution chain is demonstrated.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The byte stream is attacker-controlled and no stream/JVM-wide deserialization filter is supplied elsewhere.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **major / UNDEFINED_RESTORATION_CONTRACT** — app.scala:2: readObject can return arbitrary object types, while this case requires a bounded data-only replacement and preservation of the demonstrated operation/input-output behavior. No legitimate data model, encoding or allowed wire-format migration defines what an acceptable repair must retain. Define the legitimate restored value/schema, serialization contract, bounds and permitted migration for this vulnerable case. The separately submitted safe example is not a gold repair and does not resolve these case-local constraints.
  References: [docs.oracle.com: java-serialization-filters.html](https://docs.oracle.com/en/java/javase/25/core/java-serialization-filters.html).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## scala-job-state-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4139) · Source SHA-256: `e1bf819f4e170c74cc71cfc880bae4999befa2e444bef255ff6a1462652c5252`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.io._
object App { def restore(in: InputStream): String = new String(in.readNBytes(4096), java.nio.charset.StandardCharsets.UTF_8) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Decode bounded data-only input.

**Original remediation constraints:**

- Decode bounded data-only input.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone function reads at most 4096 bytes as UTF-8 and never constructs attacker-selected native objects. Its CWE-502 negative label is supported. The source explicitly defines bounded raw-text behavior; it is not evaluated as a gold repair for the separately submitted object-restoration case.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The JVM supports readNBytes(int) (Java 11 or later) for the safe counterpart.

**Issues and recommended actions:**

- **minor / RAW_TEXT_REFERENCE_SCOPE** — app.scala:2: Reading the first 4096 bytes is a bounded raw-text operation; it does not decode Java serialization and may return a prefix for longer input. That does not contradict this standalone safe label, but prevents assuming the case is a behavior-preserving reference fix for another case. Describe this case as bounded text reading. If used later as a remediation reference, separately define permitted format migration and oversize-input behavior.
  References: [docs.oracle.com: InputStream.html](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/InputStream.html#readNBytes(int)).

**Derivation group (AI assessment):** `java-object-stream-to-raw-text`. This is an audit annotation, not a validated sampling design.

## scala-integrity-hash-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4169) · Source SHA-256: `da145aa8a4608384db07278ecc052e02168bed553f8a8b819cea948651f94b5c`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.security.MessageDigest
object App { def digest(data: Array[Byte]) = MessageDigest.getInstance("MD5").digest(data) }
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.scala"}]

**Original rationale:** Security integrity operation uses MD5.

**Original remediation constraints:**

- Retain integrity digest using SHA-256.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** MD5 is inappropriate for a collision-resistant integrity operation, matching CWE-328 if the claimed security role actually exists. The function alone does not establish that role.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.
- Consumers can accept the changed digest length/algorithm or an explicit migration is part of the legitimate contract.

**Issues and recommended actions:**

- **major / DIGEST_SECURITY_CONTEXT_MISSING** — app.scala:2: The function only returns a digest; security-critical use appears solely in evaluation rationale. A non-security MD5 checksum can be legitimate, whereas an unauthenticated attacker-replaceable checksum remains unsafe even after SHA-256 substitution. Include a minimal caller or explicit source-visible contract showing the trusted expected digest and collision-resistance requirement. Define how callers handle algorithm/output-length migration and include a real non-security misleading counterexample.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## scala-integrity-hash-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4205) · Source SHA-256: `ef3e4d10c818323e5bb674d731576d12afb84388266821127a40b0bd492cdb63`

**app.scala** (line numbers in findings refer to this file)

```scala
import java.security.MessageDigest
object App { def digest(data: Array[Byte]) = MessageDigest.getInstance("SHA-256").digest(data) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Retain integrity digest using SHA-256.

**Original remediation constraints:**

- Retain integrity digest using SHA-256.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The standalone function computes SHA-256, with no password hashing or authentication construction shown. Its weak-cryptography negative label and SHA-256 preservation constraint are coherent locally.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The digest is used where collision resistance is required; it is not merely a cache identifier/checksum for accidental corruption.
- The expected digest is authenticated or otherwise trusted. A plain SHA-256 checksum is not message authentication and is not password hashing.

**Issues and recommended actions:**

- **minor / DIGEST_SCOPE** — app.scala:2: SHA-256 is a suitable general collision-resistant digest here. This small function does not establish authenticated integrity or password-hashing suitability, and those broader claims should not be inferred. Retain the safe negative label; state that it concerns algorithm choice and makes no broader claim about unseen consumers.
  References: [www.rfc-editor.org: rfc6151](https://www.rfc-editor.org/info/rfc6151/).

**Derivation group (AI assessment):** `java-md5-sha256`. This is an audit annotation, not a validated sampling design.

## scala-system-query-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4235) · Source SHA-256: `04b52457bbb2848526c4c07f91322908fd157719259e0cff1a97d172c43e7542`

**app.scala** (line numbers in findings refer to this file)

```scala
object App { def lookup(user: String) = new ProcessBuilder("sh", "-c", s"id $user").start() }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.scala"}]

**Original rationale:** Interpolated argument is interpreted by shell.

**Original remediation constraints:**

- Call the utility with a separate literal argument vector.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The user-controlled value becomes part of the command interpreted by sh -c. Shell operators can introduce extra commands, matching CWE-78. A direct argument vector preserves the intended single lookup/stat operation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## scala-system-query-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4271) · Source SHA-256: `e1007fa48744866226bc266050e989fc90d160db32dddc81a3419c4391417d02`

**app.scala** (line numbers in findings refer to this file)

```scala
object App { def lookup(user: String) = new ProcessBuilder("id", "--", user).start() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Call the utility with a separate literal argument vector.

**Original remediation constraints:**

- Call the utility with a separate literal argument vector.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The utility and user input occupy separate ProcessBuilder arguments and no shell interprets metacharacters. The option terminator in stat/id also prevents an input beginning with a dash from becoming an option.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The parameter is attacker-controlled and the target is a POSIX-like environment with the stated utility installed.
- Executable lookup/PATH is trusted; this case is about shell interpretation, not executable-search-path hijacking.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `jvm-shell-argv`. This is an audit annotation, not a validated sampling design.

## scala-tls-hostnames-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4301) · Source SHA-256: `513558a3b5f60c72119a44503767897ea4e85b4e9e00f888b50bbc9abdc48765`

**app.scala** (line numbers in findings refer to this file)

```scala
import javax.net.ssl._
object App { val verifier = new HostnameVerifier { def verify(h: String, s: SSLSession): Boolean = true } }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.scala"}]

**Original rationale:** Custom verifier accepts any server hostname.

**Original remediation constraints:**

- Use the platform hostname verifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The verifier implementation always accepts a hostname result, which is an unsafe configuration if consumed by an HTTPS client. It does not itself execute a network request or disable certificate-chain validation.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **major / HOSTNAME_CONSUMER_UNSPECIFIED** — app.scala:2: The source only constructs/returns a verifier and never shows the client that uses it. getDefaultHostnameVerifier returns mutable global HttpsURLConnection policy; it is not evidence that an arbitrary consumer will perform complete hostname verification. Add a minimal intended HTTPS-client wiring point and trusted-default assumption. State that the finding concerns hostname checks (CWE-297 is more specific, while CWE-295 is acceptable as a parent), not wholesale TLS chain validation.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## scala-tls-hostnames-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4337) · Source SHA-256: `7b9561506cf6ae2d449979f805c14700942dd34be6b08f6853c44d8d0fb14f9f`

**app.scala** (line numbers in findings refer to this file)

```scala
import javax.net.ssl._
object App { val verifier = HttpsURLConnection.getDefaultHostnameVerifier() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use the platform hostname verifier.

**Original remediation constraints:**

- Use the platform hostname verifier.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** Fetching the platform default introduces no permissive verifier in this fragment. As an HttpsURLConnection configuration counterexample it is safe under unmodified defaults, but its behavior cannot be assumed for arbitrary third-party clients or replaced global defaults.

**Assumptions:**

- The snippet is a callable source-analysis unit; omitted application entry points and routine imports/build configuration alone are not grounds to reject it.
- The returned/stored HostnameVerifier is installed on the intended HTTPS client, whose certificate-chain validation remains enabled.
- For the safe case, no code has replaced the global HttpsURLConnection default with a permissive verifier.

**Issues and recommended actions:**

- **minor / DEFAULT_VERIFIER_SCOPE** — app.scala:2: The code retrieves the HttpsURLConnection default and introduces no insecure override. This supports the standalone safe configuration label under an unmodified platform default; it is not a universal verifier guarantee for arbitrary third-party consumers. Keep the safe label and document its intended HttpsURLConnection context. Consumer/global-default assumptions are scope notes, not evidence of a vulnerability in this supplied source.
  References: [docs.oracle.com: HttpsURLConnection.html](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/javax/net/ssl/HttpsURLConnection.html).

**Derivation group (AI assessment):** `jvm-hostname-verifier`. This is an audit annotation, not a validated sampling design.

## swift-server-trust-policy-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4367) · Source SHA-256: `b887375addf8c4931fce9639431b446c7f302b4d3b50131ae5f2dba19ba88c2c`

**app.swift** (line numbers in findings refer to this file)

```swift
import Alamofire
let manager = ServerTrustManager(evaluators: ["api.example.org": DisabledTrustEvaluator()])
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.swift"}]

**Original rationale:** Alamofire disables server trust evaluation.

**Original remediation constraints:**

- Use default chain and hostname validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** unsafe trust policy is supported; exploitable TLS bypass is conditional

**AI rationale:** DisabledTrustEvaluator deliberately skips Alamofire evaluation, so its use is a valid policy concern. However this snippet neither installs the manager into a Session nor establishes whether ATS allows trust relaxation for the target domain.

**Assumptions:**

- Alamofire 5 is available on a Darwin Foundation target.
- The manager is passed to the Session making requests to api.example.org; a standalone unused manager has no network effect.

**Issues and recommended actions:**

- **major / TLS_PLATFORM_AND_WIRING_MISSING** — app.swift:2: An unused ServerTrustManager does not affect requests. The rationale treats disabling Alamofire evaluation as an unconditional server-trust bypass, although Darwin URLSession can enforce ATS independently. Pin the intended Darwin/Alamofire configuration, show Session use and record relevant ATS/domain exceptions, or limit the expected claim to an unsafe inactive policy. Do not weaken TLS settings merely to make a benchmark appear vulnerable.
  References: [github.com: AdvancedUsage.md](https://github.com/Alamofire/Alamofire/blob/master/Documentation/AdvancedUsage.md), [developer.apple.com: performing-manual-server-trust-authentication](https://developer.apple.com/documentation/Foundation/performing-manual-server-trust-authentication).

**Derivation group (AI assessment):** `swift-alamofire-trust`. This is an audit annotation, not a validated sampling design.

## swift-server-trust-policy-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4403) · Source SHA-256: `b82d1ab8e892dcfc74c28c307a3b08af1dd9e4d6e9e3054ac12be08ae53b09a1`

**app.swift** (line numbers in findings refer to this file)

```swift
import Alamofire
let manager = ServerTrustManager(evaluators: ["api.example.org": DefaultTrustEvaluator(validateHost: true)])
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use default chain and hostname validation.

**Original remediation constraints:**

- Use default chain and hostname validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** DefaultTrustEvaluator(validateHost: true) requests the normal chain and hostname checks for the configured host. The other-host behavior is fail-closed with the manager default. No direct insecure trust override appears.

**Assumptions:**

- Alamofire 5 is available on a Darwin Foundation target.
- The manager is passed to the Session making requests to api.example.org; a standalone unused manager has no network effect.

**Issues and recommended actions:**

- **minor / ALAMOFIRE_CONSUMER_NOT_SHOWN** — app.swift:2: The snippet constructs a trust-policy map without connecting it to a Session or request. This is a structural configuration example, not a complete trust-boundary scenario. Show the Session consumer or explicitly designate this as a policy-construction unit and document its platform/version.
  References: [alamofire.github.io: DefaultTrustEvaluator.html](https://alamofire.github.io/Alamofire/Classes/DefaultTrustEvaluator.html), [github.com: AdvancedUsage.md](https://github.com/Alamofire/Alamofire/blob/master/Documentation/AdvancedUsage.md).

**Derivation group (AI assessment):** `swift-alamofire-trust`. This is an audit annotation, not a validated sampling design.

## swift-archive-import-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4433) · Source SHA-256: `1116ee7d141614c17ec58c9e6181e23360d8e99f22c348e7380b948459453c9d`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func decode(_ data: Data) -> Any? { return NSKeyedUnarchiver.unarchiveObject(with: data) }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.swift"}]

**Original rationale:** Legacy unarchive allows unrestricted object classes.

**Original remediation constraints:**

- Restrict decoding to the expected secure-coding class.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The deprecated convenience method decodes an archive without a caller-supplied expected-class restriction, supporting CWE-502 for untrusted archives. Actual consequences depend on available classes and the platform.

**Assumptions:**

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

**Issues and recommended actions:**

- **major / ARCHIVE_CONTRACT_UNSPECIFIED** — app.swift:2: This case returns arbitrary archived objects but requires a fix that restricts decoding to the expected secure-coding class while preserving legitimate behavior. The expected class/object graph and supported caller/error contract are absent, so a model cannot derive the permitted narrowing from the supplied program. State the legitimate archive root/object graph and compatibility/error expectations for this vulnerable case. Do not infer them from the independently evaluated NSString safe case.
  References: [developer.apple.com: NSKeyedUnarchiver](https://developer.apple.com/documentation/Foundation/NSKeyedUnarchiver?language=objc), [developer.apple.com: requiressecurecoding](https://developer.apple.com/documentation/foundation/nskeyedunarchiver/requiressecurecoding?language=objc).

**Derivation group (AI assessment):** `swift-keyed-unarchive`. This is an audit annotation, not a validated sampling design.

## swift-archive-import-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4469) · Source SHA-256: `deb807259279d429bb057e5f9f98ac40ead6ce8c30f202ab54515a4027d31432`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func decode(_ data: Data) throws -> NSString? { return try NSKeyedUnarchiver.unarchivedObject(ofClass: NSString.self, from: data) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Restrict decoding to the expected secure-coding class.

**Original remediation constraints:**

- Restrict decoding to the expected secure-coding class.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone API explicitly returns NSString? and restricts decoding to that expected root class, supporting the CWE-502 negative label. Throwing behavior is part of its own signature. It is not used as a gold repair for the separately submitted unrestricted decoder.

**Assumptions:**

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

**Issues and recommended actions:**

- **minor / ARCHIVE_REFERENCE_SCOPE** — app.swift:2: NSString is explicitly the accepted root type in this safe case. Its narrower type and throwing signature are coherent locally; they should not be assumed to preserve another API that accepted arbitrary objects. Retain the safe label. Any future use as a remediation reference requires an independently specified original archive schema and caller/error contract.
  References: [developer.apple.com: NSKeyedUnarchiver](https://developer.apple.com/documentation/Foundation/NSKeyedUnarchiver?language=objc), [developer.apple.com: requiressecurecoding](https://developer.apple.com/documentation/foundation/nskeyedunarchiver/requiressecurecoding?language=objc).

**Derivation group (AI assessment):** `swift-keyed-unarchive`. This is an audit annotation, not a validated sampling design.

## swift-session-challenge-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4499) · Source SHA-256: `5bc6051eef49b0f389dd1764f47153c03de80bc97d6a618a68299f777410fb47`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func answer(_ challenge: URLAuthenticationChallenge, completion: (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) { completion(.useCredential, URLCredential(trust: challenge.protectionSpace.serverTrust!)) }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.swift"}]

**Original rationale:** Server trust is accepted without evaluation.

**Original remediation constraints:**

- Let the platform evaluate the server trust challenge.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** unsafe trust-handling pattern is supported; unconditional bypass label needs platform assumptions

**AI rationale:** The helper supplies a trust credential without evaluating trust. Its actual bypass potential depends on domain ATS policy; the unconditional force unwrap also assumes every forwarded challenge is a server-trust challenge.

**Assumptions:**

- A URLSessionDelegate forwards actual authentication challenges to this helper on Darwin.
- The URLSession and URLSessionTask ownership/lifetimes are outside this small helper.

**Issues and recommended actions:**

- **major / ATS_CONDITION_MISSING** — app.swift:2: The rationale claims that server trust is accepted without qualification. Apple documents that ATS-protected domains do not permit loosening trust requirements, and no platform/domain ATS policy or delegate wiring is included. Document target platform, domain policy and delegation. Keep the finding as an unsafe manual-authentication pattern unless evidence establishes the claimed bypass.
  References: [developer.apple.com: performing-manual-server-trust-authentication](https://developer.apple.com/documentation/Foundation/performing-manual-server-trust-authentication).
- **major / NON_SERVER_CHALLENGE_CRASH** — app.swift:2: serverTrust! can be nil for a non-server-trust authentication challenge; the unrestricted helper signature and missing authenticationMethod guard leave an unintended crash path outside the sole TLS finding. Specify that the caller filters server-trust challenges, or add the guard/default handling in the scenario and include the associated behavior constraint.
  References: [developer.apple.com: performing-manual-server-trust-authentication](https://developer.apple.com/documentation/Foundation/performing-manual-server-trust-authentication).

**Derivation group (AI assessment):** `swift-challenge-trust`. This is an audit annotation, not a validated sampling design.

## swift-session-challenge-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4535) · Source SHA-256: `ee7c86704a9bcc3560ffd8d41df2e5becd9f8cd43199fc599e44580519da2876`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func answer(_ challenge: URLAuthenticationChallenge, completion: (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) { completion(.performDefaultHandling, nil) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Let the platform evaluate the server trust challenge.

**Original remediation constraints:**

- Let the platform evaluate the server trust challenge.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** performDefaultHandling delegates the entire challenge decision to the URL loading system, with no trust-bypass credential supplied. This is an appropriate safe alternative for standard server trust and other authentication challenges.

**Assumptions:**

- A URLSessionDelegate forwards actual authentication challenges to this helper on Darwin.
- The URLSession and URLSessionTask ownership/lifetimes are outside this small helper.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `swift-challenge-trust`. This is an audit annotation, not a validated sampling design.

## swift-archive-file-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4565) · Source SHA-256: `cfd7701d00b4c85e87f1112e74c837e2fb5436ad125a79bf21dc872eeed9987e`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func restore(_ path: String) -> Any? { return NSKeyedUnarchiver.unarchiveObject(withFile: path) }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.swift"}]

**Original rationale:** File archive imports unrestricted object types.

**Original remediation constraints:**

- Read the file then restrict unarchiving to the expected class.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** The deprecated convenience method decodes an archive without a caller-supplied expected-class restriction, supporting CWE-502 for untrusted archives. Actual consequences depend on available classes and the platform.

**Assumptions:**

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

**Issues and recommended actions:**

- **major / ARCHIVE_CONTRACT_UNSPECIFIED** — app.swift:2: This case returns arbitrary archived objects but requires a fix that restricts decoding to the expected secure-coding class while preserving legitimate behavior. The expected class/object graph and supported caller/error contract are absent, so a model cannot derive the permitted narrowing from the supplied program. State the legitimate archive root/object graph and compatibility/error expectations for this vulnerable case. Do not infer them from the independently evaluated NSString safe case.
  References: [developer.apple.com: NSKeyedUnarchiver](https://developer.apple.com/documentation/Foundation/NSKeyedUnarchiver?language=objc), [developer.apple.com: requiressecurecoding](https://developer.apple.com/documentation/foundation/nskeyedunarchiver/requiressecurecoding?language=objc).

**Derivation group (AI assessment):** `swift-keyed-unarchive`. This is an audit annotation, not a validated sampling design.

## swift-archive-file-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4601) · Source SHA-256: `73fdbd2c7e66b586f77d636073c86107f426fe098816bba4055ab6819ae123ca`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func restore(_ path: String) throws -> NSString? { let data = try Data(contentsOf: URL(fileURLWithPath: path)); return try NSKeyedUnarchiver.unarchivedObject(ofClass: NSString.self, from: data) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Read the file then restrict unarchiving to the expected class.

**Original remediation constraints:**

- Read the file then restrict unarchiving to the expected class.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone API explicitly returns NSString? and restricts decoding to that expected root class, supporting the CWE-502 negative label. Throwing behavior is part of its own signature. It is not used as a gold repair for the separately submitted unrestricted decoder.

**Assumptions:**

- Darwin Foundation supports these keyed-archive APIs; attacker-controlled archive contents reach the function.
- The file-path variant assumes the caller may select an authorized archive file; it does not itself assert a protected directory boundary.
- No concrete dangerous class/gadget execution is proved by these two-line snippets.

**Issues and recommended actions:**

- **minor / ARCHIVE_REFERENCE_SCOPE** — app.swift:2: NSString is explicitly the accepted root type in this safe case. Its narrower type and throwing signature are coherent locally; they should not be assumed to preserve another API that accepted arbitrary objects. Retain the safe label. Any future use as a remediation reference requires an independently specified original archive schema and caller/error contract.
  References: [developer.apple.com: NSKeyedUnarchiver](https://developer.apple.com/documentation/Foundation/NSKeyedUnarchiver?language=objc), [developer.apple.com: requiressecurecoding](https://developer.apple.com/documentation/foundation/nskeyedunarchiver/requiressecurecoding?language=objc).

**Derivation group (AI assessment):** `swift-keyed-unarchive`. This is an audit annotation, not a validated sampling design.

## swift-format-log-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4631) · Source SHA-256: `760c322b7040f17d73c9043d579053df0fc21a9916e44c0c3ef2ba48cecad060`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func log(_ input: String) { NSLog(input) }
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.swift"}]

**Original rationale:** Untrusted text controls Foundation formatting.

**Original remediation constraints:**

- Use a constant format and treat input as an object argument.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** Input occupies NSLog's format position with no matching variadic arguments. Crafted percent directives can cause invalid reads/crashes or unintended output; CWE-134 is appropriate. A literal object-format argument preserves the intended logging operation.

**Assumptions:**

- Input can contain attacker-controlled percent-format directives and the target uses Darwin Foundation NSLog.
- The desired operation logs arbitrary text; confidentiality/redaction of log contents is a separate policy.

**Issues and recommended actions:**

- **minor / PLATFORM_SCOPE** — app.swift:2: The source is a minimal Foundation formatting example, with no platform/version declaration. The assessment applies to the documented printf-style NSLog contract; it does not assert a specific arbitrary-code-execution exploit. Record the Foundation target and keep the expected consequence at the demonstrated uncontrolled-format level.
  References: [developer.apple.com: tn2347](https://developer.apple.com/library/archive/technotes/tn2347/).

**Derivation group (AI assessment):** `swift-nslog-format`. This is an audit annotation, not a validated sampling design.

## swift-format-log-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4667) · Source SHA-256: `a49f04dacabe3dbda9281d18d46b33ab364cebd0ba001cff46a121561352557d`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func log(_ input: String) { NSLog("%@", input) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a constant format and treat input as an object argument.

**Original remediation constraints:**

- Use a constant format and treat input as an object argument.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** The format is a constant %@ and input is an object argument, so percent sequences inside input remain data. It preserves arbitrary text logging and removes the demonstrated formatting risk.

**Assumptions:**

- Input can contain attacker-controlled percent-format directives and the target uses Darwin Foundation NSLog.
- The desired operation logs arbitrary text; confidentiality/redaction of log contents is a separate policy.

**Issues and recommended actions:**

- **minor / PLATFORM_SCOPE** — app.swift:2: The source is a minimal Foundation formatting example, with no platform/version declaration. The assessment applies to the documented printf-style NSLog contract; it does not assert a specific arbitrary-code-execution exploit. Record the Foundation target and keep the expected consequence at the demonstrated uncontrolled-format level.
  References: [developer.apple.com: tn2347](https://developer.apple.com/library/archive/technotes/tn2347/).

**Derivation group (AI assessment):** `swift-nslog-format`. This is an audit annotation, not a validated sampling design.

## swift-path-selection-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4697) · Source SHA-256: `306292695447d73cccb2ac51fcf7bae873f30d1027859ea5929b60fed3b70aeb`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func read(_ name: String) throws -> Data { return try Data(contentsOf: URL(fileURLWithPath: "/srv/docs/" + name)) }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.swift"}]

**Original rationale:** Untrusted name can escape the document directory.

**Original remediation constraints:**

- Map known document IDs to fixed paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** vulnerable label supported under the listed trust-boundary assumptions

**AI rationale:** Concatenating a name containing parent-directory components into /srv/docs/ produces an escaping file path, so CWE-22 is supported under the documented confinement intent. The proposed ID mapping is safe in principle but its legitimate input set is unspecified.

**Assumptions:**

- For the vulnerable case, name is attacker-controlled and reads must remain within /srv/docs.
- For the safe case, the document map and target filesystem paths are trusted and cannot be replaced by attacker-controlled symlinks.

**Issues and recommended actions:**

- **major / DOCUMENT_ID_CONTRACT_MISSING** — app.swift:2: This function accepts filenames relative to /srv/docs, while its required remedy is to map known document IDs to fixed paths and preserve legitimate input/output behavior. The legitimate ID set, mapping and permitted API migration are unspecified in this case. Define the intended public ID/filename contract and allowed documents for this vulnerable case, or permit containment validation that preserves authorized filenames. Do not infer the contract from an independently evaluated safe case.

**Derivation group (AI assessment):** `swift-path-map`. This is an audit annotation, not a validated sampling design.

## swift-path-selection-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4733) · Source SHA-256: `aaffdd4b669528e5cbc72461b6252fce62f91e2ba2cc5cb2c86ccf47822f6e5a`

**app.swift** (line numbers in findings refer to this file)

```swift
import Foundation
func read(_ name: String) throws -> Data { let docs = ["terms": "/srv/docs/terms.txt"]; guard let path = docs[name] else { throw NSError(domain: "input", code: 1) }; return try Data(contentsOf: URL(fileURLWithPath: path)) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Map known document IDs to fixed paths.

**Original remediation constraints:**

- Map known document IDs to fixed paths.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** safe label supported for the stated vulnerability family

**AI rationale:** This standalone function defines a one-ID API: terms selects a literal trusted path and other IDs are rejected. Untrusted traversal strings cannot become filesystem paths, so the CWE-22 negative label is coherent. It is not a gold repair for the separate filename-based function.

**Assumptions:**

- For the vulnerable case, name is attacker-controlled and reads must remain within /srv/docs.
- For the safe case, the document map and target filesystem paths are trusted and cannot be replaced by attacker-controlled symlinks.

**Issues and recommended actions:**

- **minor / DOCUMENT_MAP_REFERENCE_SCOPE** — app.swift:2: The literal map defines the accepted ID contract for this safe function. That contract differs from a general filename API, but the difference does not make this independently evaluated negative case invalid. Keep the safe label under trusted-filesystem assumptions. Do not present this one-ID API as an automatically behavior-preserving repair for arbitrary filename-based readers.

**Derivation group (AI assessment):** `swift-path-map`. This is an audit annotation, not a validated sampling design.

## rust-account-sqlx-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4763) · Source SHA-256: `7c7e547c1c5b305305a60f47ca393910b1f3b24045dd82a9a7da02009a217acd`

**app.rs** (line numbers in findings refer to this file)

```rust
async fn find(db: &sqlx::PgPool, name: &str) -> Result<(),sqlx::Error> { sqlx::query(&format!("SELECT id FROM users WHERE name='{}'", name)).execute(db).await?; Ok(()) }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.rs"}]

**Original rationale:** Formatting input into SQL changes query structure.

**Original remediation constraints:**

- Use sqlx bind with the same selected records.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-89 is supported for attacker-controlled name with SQLx 0.8.x.

**AI rationale:** app.rs:1 interpolates name inside a quoted SQL literal before preparing/executing it. Single-statement preparation does not prevent predicate injection; no returned rows does not remove timing/error or query-structure impact.

**Assumptions:**

- The caller supplies untrusted name; the provided PgPool is usable against a users table.
- A compatible SQLx version and PostgreSQL async runtime/features are present; no repository code was compiled or executed.

**Issues and recommended actions:**

- **major / SQLX_OPERATION_AND_VERSION_UNSPECIFIED** — app.rs:1: The function executes a SELECT but returns only Result<(), Error>; the remediation rubric refers to selected records that this API never returns. No crate version/features are declared. Specify SQLx 0.8.x/PostgreSQL runtime features and whether executing versus returning the lookup is intended. Add a small caller/result contract in a revised corpus; preserve the same contract in both variants.
  References: [raw.githubusercontent.com: query.rs](https://raw.githubusercontent.com/launchbadge/sqlx/v0.8.6/sqlx-core/src/query.rs), [docs.rs: fn.query.html](https://docs.rs/sqlx/latest/sqlx/fn.query.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-sqlx-account-lookup`. This is an audit annotation, not a validated sampling design.

## rust-account-sqlx-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4799) · Source SHA-256: `440eb73c4f43c005a2fe7dc47a669bf0921e87d9b539066267a335a3cade6d15`

**app.rs** (line numbers in findings refer to this file)

```rust
async fn find(db: &sqlx::PgPool, name: &str) -> Result<(),sqlx::Error> { sqlx::query("SELECT id FROM users WHERE name=$1").bind(name).execute(db).await?; Ok(()) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use sqlx bind with the same selected records.

**Original remediation constraints:**

- Use sqlx bind with the same selected records.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The bound $1 value is safe against the targeted CWE-89 under a compatible SQLx/PostgreSQL version.

**AI rationale:** app.rs:1 keeps the statement literal and binds name as data. Quoted and Unicode values remain values. The safe implementation still discards rows, matching the shown function but leaving the account-lookup contract underspecified.

**Assumptions:**

- The caller supplies untrusted name; the provided PgPool is usable against a users table.
- A compatible SQLx version and PostgreSQL async runtime/features are present; no repository code was compiled or executed.

**Issues and recommended actions:**

- **major / SQLX_OPERATION_AND_VERSION_UNSPECIFIED** — app.rs:1: The function executes a SELECT but returns only Result<(), Error>; the remediation rubric refers to selected records that this API never returns. No crate version/features are declared. Specify SQLx 0.8.x/PostgreSQL runtime features and whether executing versus returning the lookup is intended. Add a small caller/result contract in a revised corpus; preserve the same contract in both variants.
  References: [raw.githubusercontent.com: query.rs](https://raw.githubusercontent.com/launchbadge/sqlx/v0.8.6/sqlx-core/src/query.rs), [docs.rs: fn.query.html](https://docs.rs/sqlx/latest/sqlx/fn.query.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-sqlx-account-lookup`. This is an audit annotation, not a validated sampling design.

## rust-reqwest-certificates-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4829) · Source SHA-256: `959459b934ce0dd213bf15147ed92d8b65052baddf0967da8320c4283ef40f28`

**app.rs** (line numbers in findings refer to this file)

```rust
fn client() -> reqwest::Client { reqwest::Client::builder().danger_accept_invalid_certs(true).build().unwrap() }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.rs"}]

**Original rationale:** Client ignores invalid server certificates.

**Original remediation constraints:**

- Keep certificate verification active.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted CWE-295 configuration label is supported.

**AI rationale:** app.rs:1 explicitly disables certificate chain verification in the returned reqwest client. The snippet is a configuration factory; exploitation additionally requires using this client for HTTPS on an adversary-influenced network.

**Assumptions:**

- reqwest 0.12.28 with a documented TLS feature and a non-WebAssembly target.
- The returned client is used for HTTPS; no later configuration bypasses verification.

**Issues and recommended actions:**

- **minor / TLS_BUILD_PROFILE_UNPINNED** — app.rs:1: Cargo version, enabled TLS backend/features and the consumer of this client are absent. Record the intended crate version/features and HTTPS-use precondition as case metadata. Hostname and chain variants should share a broader TLS-configuration cluster.
  References: [docs.rs: struct.ClientBuilder.html](https://docs.rs/reqwest/0.12.28/reqwest/struct.ClientBuilder.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-reqwest-tls-verification`. This is an audit annotation, not a validated sampling design.

## rust-reqwest-certificates-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4865) · Source SHA-256: `6b2670e341b76874eb77d557288e8d98445c1fc69b2847f93e7d1e93c22b4420`

**app.rs** (line numbers in findings refer to this file)

```rust
fn client() -> reqwest::Client { reqwest::Client::builder().danger_accept_invalid_certs(false).build().unwrap() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Keep certificate verification active.

**Original remediation constraints:**

- Keep certificate verification active.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The explicit false setting is a valid safe counterexample for the targeted TLS check.

**AI rationale:** app.rs:1 explicitly retains certificate chain verification in the returned reqwest client. The snippet is a configuration factory; exploitation additionally requires using this client for HTTPS on an adversary-influenced network.

**Assumptions:**

- reqwest 0.12.28 with a documented TLS feature and a non-WebAssembly target.
- The returned client is used for HTTPS; no later configuration bypasses verification.

**Issues and recommended actions:**

- **minor / TLS_BUILD_PROFILE_UNPINNED** — app.rs:1: Cargo version, enabled TLS backend/features and the consumer of this client are absent. Record the intended crate version/features and HTTPS-use precondition as case metadata. Hostname and chain variants should share a broader TLS-configuration cluster.
  References: [docs.rs: struct.ClientBuilder.html](https://docs.rs/reqwest/0.12.28/reqwest/struct.ClientBuilder.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-reqwest-tls-verification`. This is an audit annotation, not a validated sampling design.

## rust-shell-maintenance-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4895) · Source SHA-256: `cb69f602244af353bc45fafa60134cfc3b3c916012623b1acc495798a58e47d7`

**app.rs** (line numbers in findings refer to this file)

```rust
use std::process::Command;
fn inspect(name: &str) { Command::new("sh").arg("-c").arg(format!("stat {}",name)).status().unwrap(); }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.rs"}]

**Original rationale:** Input is interpolated into shell source.

**Original remediation constraints:**

- Use direct process arguments with an option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-78 is supported for untrusted name.

**AI rationale:** app.rs:2 places name in sh -c program text; shell metacharacters change the command. Passing the string through Command.arg does not neutralize the explicit sh interpreter.

**Assumptions:**

- A Unix environment has sh and a stat implementation supporting --, such as GNU stat.
- name is one filename rather than an intentionally executable shell expression; the executable search path is trusted.

**Issues and recommended actions:**

- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-stat-process`. This is an audit annotation, not a validated sampling design.

## rust-shell-maintenance-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4931) · Source SHA-256: `30d8b25e83cab522264ff9e04db69a29f5692c3c1137350b37ddeb9554557624`

**app.rs** (line numbers in findings refer to this file)

```rust
use std::process::Command;
fn inspect(name: &str) { Command::new("stat").arg("--").arg(name).status().unwrap(); }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use direct process arguments with an option terminator.

**Original remediation constraints:**

- Use direct process arguments with an option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The direct argument-vector call is safe against the intended shell-injection and leading-option attacks.

**AI rationale:** app.rs:2 invokes stat directly, passes an option terminator and keeps name a single literal operand. This preserves the intended single-file inspection, including spaces, without shell interpretation.

**Assumptions:**

- A Unix environment has sh and a stat implementation supporting --, such as GNU stat.
- name is one filename rather than an intentionally executable shell expression; the executable search path is trusted.

**Issues and recommended actions:**

- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-stat-process`. This is an audit annotation, not a validated sampling design.

## rust-sqlite-update-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L4961) · Source SHA-256: `f84f88d5137c1d2b0d501e73fe3d003975e997ac2dffa8145b34d6cbcfc8fdde`

**app.rs** (line numbers in findings refer to this file)

```rust
fn update(db: &rusqlite::Connection, value: &str) -> rusqlite::Result<usize> { db.execute(&format!("UPDATE settings SET value='{}'",value), []) }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.rs"}]

**Original rationale:** rusqlite statement embeds a supplied string.

**Original remediation constraints:**

- Bind the value and preserve the update operation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The unquoted-data boundary supports CWE-89.

**AI rationale:** app.rs:1 embeds value inside a quoted UPDATE assignment. An attacker can change assignment/expression structure even if the driver rejects stacked statements. The all-rows update exists in both cases and must be part of the intended operation.

**Assumptions:**

- value crosses an untrusted boundary and db is a usable SQLite connection.
- Updating every settings row is intentional, and the returned affected-row count is preserved.

**Issues and recommended actions:**

- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-rusqlite-update`. This is an audit annotation, not a validated sampling design.

## rust-sqlite-update-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L4997) · Source SHA-256: `cecd64722fe2d3c7ba33483edf65efecde67a2a1a08c8e9dab37082e20645d8d`

**app.rs** (line numbers in findings refer to this file)

```rust
fn update(db: &rusqlite::Connection, value: &str) -> rusqlite::Result<usize> { db.execute("UPDATE settings SET value=?1", [value]) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind the value and preserve the update operation.

**Original remediation constraints:**

- Bind the value and preserve the update operation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The ?1 binding is a valid safe counterexample for CWE-89.

**AI rationale:** app.rs:1 uses a fixed UPDATE and binds the sole value. No supplied SQL is re-parsed as query structure. The case intentionally updates all rows; adding an arbitrary WHERE clause would change behavior.

**Assumptions:**

- value crosses an untrusted boundary and db is a usable SQLite connection.
- Updating every settings row is intentional, and the returned affected-row count is preserved.

**Issues and recommended actions:**

- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-rusqlite-update`. This is an audit annotation, not a validated sampling design.

## rust-hostname-acceptance-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5027) · Source SHA-256: `e63b9bfaa63f368118037c58a9ca5ce35d7bf375e0c9bc7602d777644713bcdc`

**app.rs** (line numbers in findings refer to this file)

```rust
fn client() -> reqwest::Client { reqwest::Client::builder().danger_accept_invalid_hostnames(true).build().unwrap() }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.rs"}]

**Original rationale:** Client ignores hostname mismatch.

**Original remediation constraints:**

- Preserve hostname verification on TLS connections.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted CWE-295 configuration label is supported.

**AI rationale:** app.rs:1 explicitly disables hostname verification in the returned reqwest client. The snippet is a configuration factory; exploitation additionally requires using this client for HTTPS on an adversary-influenced network.

**Assumptions:**

- reqwest 0.12.28 with a documented TLS feature and a non-WebAssembly target.
- The returned client is used for HTTPS; no later configuration bypasses verification.

**Issues and recommended actions:**

- **minor / TLS_BUILD_PROFILE_UNPINNED** — app.rs:1: Cargo version, enabled TLS backend/features and the consumer of this client are absent. Record the intended crate version/features and HTTPS-use precondition as case metadata. Hostname and chain variants should share a broader TLS-configuration cluster.
  References: [docs.rs: struct.ClientBuilder.html](https://docs.rs/reqwest/0.12.28/reqwest/struct.ClientBuilder.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-reqwest-tls-verification`. This is an audit annotation, not a validated sampling design.

## rust-hostname-acceptance-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5063) · Source SHA-256: `19b753ca36818bca14e2f8f64001bdbc2de2e54e9750ef2e4f3846846cc0815a`

**app.rs** (line numbers in findings refer to this file)

```rust
fn client() -> reqwest::Client { reqwest::Client::builder().danger_accept_invalid_hostnames(false).build().unwrap() }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve hostname verification on TLS connections.

**Original remediation constraints:**

- Preserve hostname verification on TLS connections.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The explicit false setting is a valid safe counterexample for the targeted TLS check.

**AI rationale:** app.rs:1 explicitly retains hostname verification in the returned reqwest client. The snippet is a configuration factory; exploitation additionally requires using this client for HTTPS on an adversary-influenced network.

**Assumptions:**

- reqwest 0.12.28 with a documented TLS feature and a non-WebAssembly target.
- The returned client is used for HTTPS; no later configuration bypasses verification.

**Issues and recommended actions:**

- **minor / TLS_BUILD_PROFILE_UNPINNED** — app.rs:1: Cargo version, enabled TLS backend/features and the consumer of this client are absent. Record the intended crate version/features and HTTPS-use precondition as case metadata. Hostname and chain variants should share a broader TLS-configuration cluster.
  References: [docs.rs: struct.ClientBuilder.html](https://docs.rs/reqwest/0.12.28/reqwest/struct.ClientBuilder.html).
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-reqwest-tls-verification`. This is an audit annotation, not a validated sampling design.

## rust-artifact-file-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5093) · Source SHA-256: `9b426afde88ac7d5af0bc4ca2085d9906a6dd874dd42331f6fde1558bf00b99a`

**app.rs** (line numbers in findings refer to this file)

```rust
fn artifact(name: &str) -> std::io::Result<Vec<u8>> { std::fs::read(std::path::Path::new("/srv/artifacts").join(name)) }
```

**Expected findings:** [{"family": "path-traversal", "cwe": "CWE-22", "path": "app.rs"}]

**Original rationale:** Join accepts absolute and traversal paths.

**Original remediation constraints:**

- Resolve public artifact names only through a fixed mapping.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-22 is supported; the allowable filename-to-public-identifier contract needs clarification before assessing proposed fixes.

**AI rationale:** app.rs:1 joins an unchecked name and reads it. Absolute paths replace the base and traversal reaches parent directories. Its own remediation constraints demand fixed public-name mappings while preserving the operation, but do not define which legitimate artifact names must remain accepted.

**Assumptions:**

- The operating system supplies Unix-style /srv paths and the service can read files outside the artifact directory.
- For the safe mapping, report.json and its parent directories cannot be replaced by an attacker-controlled symlink.

**Issues and recommended actions:**

- **major / ARTIFACT_ALLOWLIST_CONTRACT_UNSPECIFIED** — app.rs:1: The case requires mapping public artifact names without identifying the legitimate names or allowed files. A reviewer cannot determine whether an arbitrary reduced mapping preserves required access from this case alone. Record the accepted public identifiers, permitted files and any allowed API migration in this vulnerable case. Do not use the separately submitted safe sibling as a gold fix.
- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-artifact-selection`. This is an audit annotation, not a validated sampling design.

## rust-artifact-file-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5129) · Source SHA-256: `738190f95338fcbba24cbf2c7300990aef8658efc56703bea2c67e76a820c7cb`

**app.rs** (line numbers in findings refer to this file)

```rust
fn artifact(name: &str) -> std::io::Result<Vec<u8>> { let p = match name { "report" => "/srv/artifacts/report.json", _ => return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput,"unknown")) }; std::fs::read(p) }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Resolve public artifact names only through a fixed mapping.

**Original remediation constraints:**

- Resolve public artifact names only through a fixed mapping.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The fixed mapping supports the standalone safe label for caller-controlled path traversal.

**AI rationale:** app.rs:1 accepts only the report identifier and selects a literal path; traversal strings never become a pathname. This source independently defines an identifier-based API. Its different interface from the vulnerable sibling is not evidence that its safe label is wrong and it is not a reference patch for that sibling.

**Assumptions:**

- The standalone public API intentionally exposes the report identifier only.
- report.json and parent directories are trusted and cannot be replaced with an attacker-controlled symlink.

**Issues and recommended actions:**

- **minor / PAIRED_CASE_DEPENDENCE** — app.rs:1: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `rust-artifact-selection`. This is an audit annotation, not a validated sampling design.

## bash-user-expression-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5159) · Source SHA-256: `5c0133dff261390af2421c0cf4f30ffa36386d6ecaa90a1119b2e0d1ca609426`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
expression="$1"
eval "$expression"
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.sh"}]

**Original rationale:** Argument becomes a shell program.

**Original remediation constraints:**

- Treat supplied expression as data without evaluating it.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The targeted mechanism is assessed below; the case contract or ground-truth scope needs clarification/revision before approval.

**AI rationale:** app.sh:4 evaluates caller text as a shell program. CWE-95 is supported only if a less-trusted caller crosses a boundary where such execution is not the authorized purpose.

**Assumptions:**

- The intended vulnerable application boundary must be defined; a script deliberately running its owner's commands is not automatically a privilege violation.
- The safe snippet's own operation is literal display, not an arithmetic interpreter.

**Issues and recommended actions:**

- **major / LEGITIMATE_OPERATION_UNSPECIFIED** — app.sh:4 evaluates arbitrary shell text, but the rubric simultaneously asks for no evaluation and preservation of the demonstrated operation. No permitted expression grammar or expected outputs are supplied. Define the legitimate operation/trust boundary and behavior-preserving alternatives; do not use the independent printf sibling as an automatic gold fix.
  References: [www.gnu.org: bash.html](https://www.gnu.org/s/bash/manual/bash.html).

**Derivation group (AI assessment):** `bash-user-expression`. This is an audit annotation, not a validated sampling design.

## bash-user-expression-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5195) · Source SHA-256: `ad79485988184017b99d2b08422af4c26dc93aed97e5f7d75aea72f69511e4c4`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
expression="$1"
printf '%s\n' "$expression"
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Treat supplied expression as data without evaluating it.

**Original remediation constraints:**

- Treat supplied expression as data without evaluating it.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:4 prints expression as literal data with a constant format. It does not execute the string, so its independent negative evaluation label is supported.

**Assumptions:**

- The intended vulnerable application boundary must be defined; a script deliberately running its owner's commands is not automatically a privilege violation.
- The safe snippet's own operation is literal display, not an arithmetic interpreter.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-user-expression`. This is an audit annotation, not a validated sampling design.

## bash-curl-certificates-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5225) · Source SHA-256: `d23adc750dc52bc1ef9ffdf9cd693b813f5a1fabc57a978035cfc5a04a28a34d`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
curl --insecure --fail https://api.example.org/status
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.sh"}]

**Original rationale:** Curl bypasses certificate validation.

**Original remediation constraints:**

- Use trusted CA verification and retain failure handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.sh:3 explicitly disables curl certificate verification for an HTTPS transfer; CWE-295 is supported.

**Assumptions:**

- The curl binary/configuration are trusted and the attacker can influence network traffic.
- The safe case targets a system with the stated readable, trusted PEM CA bundle.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-http-client-certificate-validation`. This is an audit annotation, not a validated sampling design.

## bash-curl-certificates-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5261) · Source SHA-256: `38567682544bf0b366eb0eb6910c5d4c6a3b9af3246273e8e1a1ad38a12c38c0`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
curl --fail --cacert /etc/ssl/certs/ca-certificates.crt https://api.example.org/status
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use trusted CA verification and retain failure handling.

**Original remediation constraints:**

- Use trusted CA verification and retain failure handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:3 retains failure handling and selects a CA bundle without --insecure. Peer verification remains enabled.

**Assumptions:**

- The curl binary/configuration are trusted and the attacker can influence network traffic.
- The safe case targets a system with the stated readable, trusted PEM CA bundle.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-http-client-certificate-validation`. This is an audit annotation, not a validated sampling design.

## bash-variable-indirection-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5291) · Source SHA-256: `1b13742a2c67e397d8ea7fe3670207ed07dfdd39491d4809593701362ab29d80`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
key="$1"
eval "printf '%s\n' \$$key"
```

**Expected findings:** [{"family": "dynamic-evaluation", "cwe": "CWE-95", "path": "app.sh"}]

**Original rationale:** Variable-name argument is interpolated into eval.

**Original remediation constraints:**

- Allow-list permitted variable names and use native indirect expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.sh:4 interpolates an unchecked variable-name argument into eval source. Text outside a permitted identifier can alter the generated shell program.

**Assumptions:**

- Only HOME and USER are intended public values; untrusted callers select the name, not the shell execution environment.
- Both permitted variables are set, or nounset failure is an accepted input/environment error.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-variable-indirection`. This is an audit annotation, not a validated sampling design.

## bash-variable-indirection-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5327) · Source SHA-256: `35964157a4926389364ca2c75eef8268f79635ce39a34a32054bd47f6f0c6351`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
case "$1" in HOME|USER) printf '%s\n' "${!1}" ;; *) exit 2 ;; esac
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Allow-list permitted variable names and use native indirect expansion.

**Original remediation constraints:**

- Allow-list permitted variable names and use native indirect expansion.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:3 restricts the name to HOME or USER before native indirect expansion and prints via a constant format. The requester cannot choose shell syntax or other variables.

**Assumptions:**

- Only HOME and USER are intended public values; untrusted callers select the name, not the shell execution environment.
- Both permitted variables are set, or nounset failure is an accepted input/environment error.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-variable-indirection`. This is an audit annotation, not a validated sampling design.

## bash-wget-certificates-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5357) · Source SHA-256: `27060cf5792952208109a72e7f6e0605ca388d164ecda3c5137eb91d9916481f`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
wget --no-check-certificate -O metadata.json https://assets.example.org/metadata.json
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.sh"}]

**Original rationale:** Wget ignores untrusted server certificates.

**Original remediation constraints:**

- Retain certificate checks for the HTTPS download.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.sh:3 explicitly bypasses certificate checks during HTTPS download, supporting CWE-295.

**Assumptions:**

- Trusted GNU Wget configuration retains its default certificate verification; destination and output location are operator controlled.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-http-client-certificate-validation`. This is an audit annotation, not a validated sampling design.

## bash-wget-certificates-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5393) · Source SHA-256: `f221eab0e296172f8b43d599db5ad79662bd80f642485fb60e35af7cdbd63009`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
wget --https-only -O metadata.json https://assets.example.org/metadata.json
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Retain certificate checks for the HTTPS download.

**Original remediation constraints:**

- Retain certificate checks for the HTTPS download.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:3 removes the bypass, leaving certificate checks enabled for the initial HTTPS transfer. The added --https-only option is for recursive link following, not evidence of a universal redirect policy.

**Assumptions:**

- Trusted GNU Wget configuration retains its default certificate verification; destination and output location are operator controlled.

**Issues and recommended actions:**

- **minor / HTTPS_ONLY_SCOPE** — app.sh:3 uses --https-only without recursive mode. It does not add the broad protocol restriction its name may suggest. Keep the certificate-validation negative label scoped to HTTPS; explicitly define and enforce redirect policy if end-to-end HTTPS-only behavior is required.
  References: [www.gnu.org: wget.html](https://www.gnu.org/software/wget/manual/wget.html).

**Derivation group (AI assessment):** `bash-http-client-certificate-validation`. This is an audit annotation, not a validated sampling design.

## bash-nested-shell-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5423) · Source SHA-256: `2cfb163dc16139fa845c1763c003b760dd36203fdc5f3d4d856cdcc3d9d2e67c`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
name="$1"
bash -c "stat $name"
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.sh"}]

**Original rationale:** Argument becomes source in a second shell.

**Original remediation constraints:**

- Call stat with a quoted argument and option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.sh:4 interpolates name into the source passed to another Bash process; quoting around the outer argument does not prevent the inner shell interpreting it.

**Assumptions:**

- The caller supplies an untrusted pathname; stat through a trusted PATH is GNU-compatible and accepts --.
- The application is permitted to obtain metadata for the requested path.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-nested-shell`. This is an audit annotation, not a validated sampling design.

## bash-nested-shell-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5459) · Source SHA-256: `81a4edde66550e01fa002b0b6ad72de271d42cb7ba61bfe3a62e35a3cad38431`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
name="$1"
stat -- "$name"
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Call stat with a quoted argument and option terminator.

**Original remediation constraints:**

- Call stat with a quoted argument and option terminator.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:4 directly invokes stat with a quoted single argument and --, preventing shell and option interpretation of the path.

**Assumptions:**

- The caller supplies an untrusted pathname; stat through a trusted PATH is GNU-compatible and accepts --.
- The application is permitted to obtain metadata for the requested path.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-nested-shell`. This is an audit annotation, not a validated sampling design.

## bash-format-argument-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5489) · Source SHA-256: `304583118bbc16f6903130edeb24ac88550d2cb4a651e478ff606c743b9ec7f6`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
printf "$1"
```

**Expected findings:** [{"family": "format-string", "cwe": "CWE-134", "path": "app.sh"}]

**Original rationale:** Caller text controls printf escape and format interpretation.

**Original remediation constraints:**

- Render caller content using a constant string format.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The proposed vulnerable label is supported under the stated assumptions.

**AI rationale:** app.sh:3 uses the caller string as Bash printf format. It can change escape/conversion interpretation; this supports CWE-134 without claiming C-style memory corruption or arbitrary shell execution.

**Assumptions:**

- The application intends to display untrusted text literally; Bash built-in printf semantics apply.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-builtin-untrusted-format`. This is an audit annotation, not a validated sampling design.

## bash-format-argument-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5525) · Source SHA-256: `05e0d8a74b44b61ccf69d4a721492a00cacd199d46769e23d4dd1bf7d8f337f9`

**app.sh** (line numbers in findings refer to this file)

```bash
#!/usr/bin/env bash
set -eu
printf '%s' "$1"
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Render caller content using a constant string format.

**Original remediation constraints:**

- Render caller content using a constant string format.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The safe label is supported for the targeted vulnerability family under the stated assumptions.

**AI rationale:** app.sh:3 uses the fixed %s format, preserving caller percent and backslash characters as literal data.

**Assumptions:**

- The application intends to display untrusted text literally; Bash built-in printf semantics apply.

No additional case-local issue was identified under the listed assumptions.

**Derivation group (AI assessment):** `bash-builtin-untrusted-format`. This is an audit annotation, not a validated sampling design.

## csharp-account-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5555) · Source SHA-256: `d46f47a585a71793ebb6aaefa8d92e9fac94dffa211292ce1e2e66fbe4959d33`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Data.SqlClient;
class App { SqlCommand Find(string user) { return new SqlCommand("SELECT id FROM users WHERE name='"+user+"'"); } }
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.cs"}]

**Original rationale:** SqlCommand embeds untrusted input.

**Original remediation constraints:**

- Use SQL parameters while preserving account lookup.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The constructed command supports the CWE-89 label when executed with untrusted input.

**AI rationale:** app.cs:2 concatenates a caller string into a quoted SELECT predicate. Returning a SqlCommand is not itself database execution, but it is a valid unsafe command factory if the consumer executes it unchanged.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-account-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5591) · Source SHA-256: `3c792be4cf2a6595f70c20aab3f7865960f17ebef5542e7003ad118f2913671e`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Data.SqlClient;
class App { SqlCommand Find(string user) { var q=new SqlCommand("SELECT id FROM users WHERE name=@name"); q.Parameters.AddWithValue("@name",user); return q; } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SQL parameters while preserving account lookup.

**Original remediation constraints:**

- Use SQL parameters while preserving account lookup.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The named SQL parameter prevents the targeted CWE-89.

**AI rationale:** app.cs:2 creates fixed command text and binds the caller value with AddWithValue. Parameter inference may affect performance/types, but it does not reintroduce SQL syntax injection here. The returned command shape is preserved.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-shell-command-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5621) · Source SHA-256: `85a022c8c2bfe815c981777d1e5464491798874a292030c25182f50da82c2f0e`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Diagnostics;
class App { Process Run(string text) { return Process.Start("cmd.exe", "/c " + text); } }
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.cs"}]

**Original rationale:** Input is passed to an explicit command shell.

**Original remediation constraints:**

- Use direct program invocation with individual arguments.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The explicit cmd.exe /c sink supports CWE-78; its own required safe operation is insufficiently defined.

**AI rationale:** The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / SHELL_OPERATION_CONTRACT_UNSPECIFIED** — app.cs:2: The vulnerable case's own source accepts arbitrary shell program text, while its constraints require direct executable invocation and preservation of the operation. It does not identify the legitimate executable, argument grammar or allowed commands. Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-shell-command-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5657) · Source SHA-256: `c1d8ec5474a5bd1c9c49bd29fd279da97bceb871c95e683deba70df2fa52b77f`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Diagnostics;
class App { Process Run(string text) { var p=new ProcessStartInfo("ping"); p.ArgumentList.Add("--"); p.ArgumentList.Add(text); return Process.Start(p); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use direct program invocation with individual arguments.

**Original remediation constraints:**

- Use direct program invocation with individual arguments.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The standalone direct-argument call supports the targeted shell-injection safe label; its operational platform remains unspecified.

**AI rationale:** The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

**Assumptions:**

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / PING_PLATFORM_CONTRACT_UNSPECIFIED** — app.cs:2: The standalone safe case passes -- to ping but declares no OS or executable implementation. This is a GNU-style terminator; Windows ping's documented grammar does not include it. The sibling's cmd.exe cannot be used to silently assign this case a platform. Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
  References: [learn.microsoft.com: ping](https://learn.microsoft.com/en-gb/windows-server/administration/windows-commands/ping), [learn.microsoft.com: system.diagnostics.processstartinfo.argumentlist](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist?view=net-10.0), [learn.microsoft.com: system.diagnostics.processstartinfo.useshellexecute](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.useshellexecute?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-tls-handler-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5687) · Source SHA-256: `d954764fc18f905c7bc50b4d61009cb532804966232fd9b5457e04c0e1f322fb`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Net.Http;
class App { HttpClientHandler Handler() { return new HttpClientHandler { ServerCertificateCustomValidationCallback = (r,c,ch,e) => true }; } }
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.cs"}]

**Original rationale:** Custom validation accepts all certificates.

**Original remediation constraints:**

- Use default certificate and hostname verification.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The unconditional callback is an unsafe TLS-validation configuration under CWE-295.

**AI rationale:** app.cs:2 returns true for every certificate-validation callback invocation, disregarding the reported trust errors. This is a configuration-level finding; the returned handler must be used by an HTTPS client for exposure.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-tls-handler-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5723) · Source SHA-256: `06c00d5a72f45920ba59989a97e664a0743f69d11605309a6ad8ed8d1799eb16`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Net.Http;
class App { HttpClientHandler Handler() { return new HttpClientHandler(); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use default certificate and hostname verification.

**Original remediation constraints:**

- Use default certificate and hostname verification.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The default handler is a supported safe counterexample for this certificate-validation bypass.

**AI rationale:** app.cs:2 returns an HttpClientHandler without replacing certificate verification. It has no callback that approves arbitrary certificates; no false positive should be generated solely for constructing the handler.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-state-formatter-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5753) · Source SHA-256: `ccc3b2a2949775339c4f65be636a51e451e0207bed7300178b49dd287ffe88e4`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
class App { object Load(Stream body) { return new BinaryFormatter().Deserialize(body); } }
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.cs"}]

**Original rationale:** BinaryFormatter deserializes untrusted object graphs.

**Original remediation constraints:**

- Use a data-only constrained type representation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-502 is plausible only with an enabled legacy or compatibility BinaryFormatter implementation; the unqualified label is unsupported.

**AI rationale:** The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **blocker / BINARYFORMATTER_RUNTIME_LABEL** — app.cs:3: On .NET 9+ the in-box BinaryFormatter always throws, so this source does not demonstrate reachable object-graph deserialization there. Earlier versions also have project-dependent disabling behavior. Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
  References: [learn.microsoft.com: binaryformatter-removal](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/binaryformatter-removal).
- **major / SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED** — app.cs:3: This vulnerable case's own constraints require a constrained data-only representation while preserving an object-returning legacy binary deserializer. No accepted object schema, wire-format migration or compatible-data requirement is specified. Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
  References: [learn.microsoft.com: choose-a-serializer](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/choose-a-serializer).
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-state-formatter-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5789) · Source SHA-256: `331fb6b9f1961f2bccd5cbd6575743d5dd7136905fd6591c9483641e17da36f4`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.IO;
using System.Text.Json;
class App { string[] Load(Stream body) { return JsonSerializer.Deserialize<string[]>(body); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a data-only constrained type representation.

**Original remediation constraints:**

- Use a data-only constrained type representation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** Typed string-array JSON supports the standalone safe label for unsafe object deserialization.

**AI rationale:** This standalone case accepts a JSON stream and deserializes a string array without polymorphic object construction. The different format and result type from the BinaryFormatter sibling are not defects in this independent safe scenario. The data-only constraint is supported by the concrete target type, under normal input-size limits.

**Assumptions:**

- The standalone API intentionally accepts JSON string-array input.
- The caller supplies an explicit input-size bound; custom unsafe converters are absent.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-integrity-alias-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5819) · Source SHA-256: `19cb8cf0d80349ac18356be2f31641b0e6594dcc54f2689769ea470bcf47d87a`

**app.cs** (line numbers in findings refer to this file)

```csharp
using Digest = System.Security.Cryptography.MD5;
class App { byte[] Hash(byte[] data) { return Digest.Create().ComputeHash(data); } }
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.cs"}]

**Original rationale:** Aliased digest type resolves to MD5.

**Original remediation constraints:**

- Use SHA-256 through the alias and preserve digest output handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** MD5 is present, but CWE-328 vulnerability depends on an unstated security-sensitive use.

**AI rationale:** app.cs:2 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / DIGEST_SECURITY_PURPOSE_UNSPECIFIED** — app.cs:2: No consumer establishes a collision-sensitive security decision; the case name/rationale asserts integrity but the code is a generic byte-array hash helper. Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
  References: [learn.microsoft.com: ca5351](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5351).
- **minor / DIGEST_OUTPUT_MIGRATION_UNSPECIFIED** — app.cs:2: This vulnerable case itself requires changing MD5 to SHA-256 and preserving digest output handling, but supplies no consumer or storage contract for the changed digest length. Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
  References: [learn.microsoft.com: system.security.cryptography.md5](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.md5?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-integrity-alias-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5855) · Source SHA-256: `7733ce10e1c098ca7f69f5d33bf5dee2389a1513cb681382465ae6e8322ceac9`

**app.cs** (line numbers in findings refer to this file)

```csharp
using Digest = System.Security.Cryptography.SHA256;
class App { byte[] Hash(byte[] data) { return Digest.Create().ComputeHash(data); } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256 through the alias and preserve digest output handling.

**Original remediation constraints:**

- Use SHA-256 through the alias and preserve digest output handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** SHA-256 is a valid safe counterexample to the narrow weak-digest check.

**AI rationale:** app.cs:2 uses SHA-256 and returns a byte array. This standalone source uses the SHA-256 primitive. No claim is made that an unkeyed hash alone provides authenticity or password hashing.

**Assumptions:**

- This standalone API intentionally returns a SHA-256 byte-array digest.
- No claim is made that an unkeyed digest provides authenticity or is appropriate for password storage.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-xml-resolver-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5885) · Source SHA-256: `3345837c0d7f817d61fd7269ed66f7536c1ec3205bd5dbe45d38ef560eaa6b35`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Xml;
class App { XmlReaderSettings Settings() { return new XmlReaderSettings { DtdProcessing=DtdProcessing.Parse, XmlResolver=new XmlUrlResolver() }; } }
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.cs"}]

**Original rationale:** DTD parser permits network entity resolution.

**Original remediation constraints:**

- Prohibit DTDs and keep resolver disabled.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The combination of DTD parsing and XmlUrlResolver supports the configuration-level CWE-611 label.

**AI rationale:** app.cs:2 explicitly enables both DTD processing and an external-resource resolver. Unlike a DtdProcessing-only example, it does not rely on obsolete resolver defaults. Exposure requires passing the returned settings to a reader that parses untrusted XML.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

## csharp-xml-resolver-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5921) · Source SHA-256: `5b4524246acc63ccbada5ff08df8b87bd243ed3c3f3f3fbdfa70cb0dce81305c`

**app.cs** (line numbers in findings refer to this file)

```csharp
using System.Xml;
class App { XmlReaderSettings Settings() { return new XmlReaderSettings { DtdProcessing=DtdProcessing.Prohibit, XmlResolver=null }; } }
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Prohibit DTDs and keep resolver disabled.

**Original remediation constraints:**

- Prohibit DTDs and keep resolver disabled.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** DTD prohibition plus a null resolver is a supported safe counterexample for CWE-611.

**AI rationale:** app.cs:2 rejects DTDs and supplies no external resolver. It addresses both halves of the unsafe sibling and does not depend on a default resolver changing between framework versions.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.cs:1-2: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.cs:1-2: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-order-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L5951) · Source SHA-256: `62bc8cf8a4aabdbbc10527463b30cf274777a81eea5fcd56e3c217e809bdc114`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Data.SqlClient
Module App
Function Find(ref As String) As SqlCommand
Return New SqlCommand("SELECT id FROM orders WHERE ref='" & ref & "'")
End Function
End Module
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.vb"}]

**Original rationale:** SQL command concatenates supplied order reference.

**Original remediation constraints:**

- Bind reference with a named SQL parameter.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The constructed command supports the CWE-89 label when executed with untrusted input.

**AI rationale:** app.vb:4 concatenates a caller string into a quoted SELECT predicate. Returning a SqlCommand is not itself database execution, but it is a valid unsafe command factory if the consumer executes it unchanged.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-order-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L5987) · Source SHA-256: `fd5456e0f251d8a49b67c46455b0f77a0cd6f3666b8324589dd561389040d32a`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Data.SqlClient
Module App
Function Find(ref As String) As SqlCommand
Dim q = New SqlCommand("SELECT id FROM orders WHERE ref=@ref")
q.Parameters.AddWithValue("@ref", ref)
Return q
End Function
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Bind reference with a named SQL parameter.

**Original remediation constraints:**

- Bind reference with a named SQL parameter.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The named SQL parameter prevents the targeted CWE-89.

**AI rationale:** app.vb:4 creates fixed command text and binds the caller value with AddWithValue. Parameter inference may affect performance/types, but it does not reintroduce SQL syntax injection here. The returned command shape is preserved.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-8: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-8: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-diagnostic-shell-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6017) · Source SHA-256: `8b3c8dd715da6e9c59f56c81fb8a10250c70f7d3298e424f061129ee8d568929`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Diagnostics
Module App
Sub Run(text As String)
Process.Start("cmd.exe", "/c " & text)
End Sub
End Module
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.vb"}]

**Original rationale:** Command shell receives caller-supplied source.

**Original remediation constraints:**

- Use explicit argument list to the required executable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The explicit cmd.exe /c sink supports CWE-78; its own required safe operation is insufficiently defined.

**AI rationale:** The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / SHELL_OPERATION_CONTRACT_UNSPECIFIED** — app.vb:4: The vulnerable case's own source accepts arbitrary shell program text, while its constraints require direct executable invocation and preservation of the operation. It does not identify the legitimate executable, argument grammar or allowed commands. Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-diagnostic-shell-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6053) · Source SHA-256: `df1953f26552003f00ff68ca464aaa3e62b8e3927141a90cff29fd413bc63362`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Diagnostics
Module App
Sub Run(text As String)
Dim p = New ProcessStartInfo("ping")
p.ArgumentList.Add("--")
p.ArgumentList.Add(text)
Process.Start(p)
End Sub
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use explicit argument list to the required executable.

**Original remediation constraints:**

- Use explicit argument list to the required executable.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The standalone direct-argument call supports the targeted shell-injection safe label; its operational platform remains unspecified.

**AI rationale:** The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

**Assumptions:**

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-9: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / PING_PLATFORM_CONTRACT_UNSPECIFIED** — app.vb:4: The standalone safe case passes -- to ping but declares no OS or executable implementation. This is a GNU-style terminator; Windows ping's documented grammar does not include it. The sibling's cmd.exe cannot be used to silently assign this case a platform. Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
  References: [learn.microsoft.com: ping](https://learn.microsoft.com/en-gb/windows-server/administration/windows-commands/ping), [learn.microsoft.com: system.diagnostics.processstartinfo.argumentlist](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist?view=net-10.0), [learn.microsoft.com: system.diagnostics.processstartinfo.useshellexecute](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.useshellexecute?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-9: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-certificate-callback-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6083) · Source SHA-256: `cfaa7fe4623f1c46fa5f4438f94f77095dff3e050f7d42ebaea4e650f17ab5f7`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Net.Http
Module App
Function Handler() As HttpClientHandler
Dim h = New HttpClientHandler()
h.ServerCertificateCustomValidationCallback = Function(r, c, ch, e) True
Return h
End Function
End Module
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.vb"}]

**Original rationale:** Callback returns true for every certificate.

**Original remediation constraints:**

- Preserve platform TLS validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The unconditional callback is an unsafe TLS-validation configuration under CWE-295.

**AI rationale:** app.vb:5 returns true for every certificate-validation callback invocation, disregarding the reported trust errors. This is a configuration-level finding; the returned handler must be used by an HTTPS client for exposure.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-8: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-8: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-certificate-callback-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6119) · Source SHA-256: `7559de36fa8935341599b1c11b1793293154daa670a748f8af5f2d5872d47a43`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Net.Http
Module App
Function Handler() As HttpClientHandler
Return New HttpClientHandler()
End Function
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Preserve platform TLS validation.

**Original remediation constraints:**

- Preserve platform TLS validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The default handler is a supported safe counterexample for this certificate-validation bypass.

**AI rationale:** app.vb:4 returns an HttpClientHandler without replacing certificate verification. It has no callback that approves arbitrary certificates; no false positive should be generated solely for constructing the handler.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-import-formatter-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6149) · Source SHA-256: `8dc8a8315e17f2b25d880c62763fb59edf4441642daa4960292f3efeb058a590`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.IO
Imports System.Runtime.Serialization.Formatters.Binary
Module App
Function Load(body As Stream) As Object
Return New BinaryFormatter().Deserialize(body)
End Function
End Module
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.vb"}]

**Original rationale:** Untrusted binary serialization constructs arbitrary objects.

**Original remediation constraints:**

- Use typed data-only JSON.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-502 is plausible only with an enabled legacy or compatibility BinaryFormatter implementation; the unqualified label is unsupported.

**AI rationale:** The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-7: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **blocker / BINARYFORMATTER_RUNTIME_LABEL** — app.vb:5: On .NET 9+ the in-box BinaryFormatter always throws, so this source does not demonstrate reachable object-graph deserialization there. Earlier versions also have project-dependent disabling behavior. Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
  References: [learn.microsoft.com: binaryformatter-removal](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/binaryformatter-removal).
- **major / SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED** — app.vb:5: This vulnerable case's own constraints require a constrained data-only representation while preserving an object-returning legacy binary deserializer. No accepted object schema, wire-format migration or compatible-data requirement is specified. Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
  References: [learn.microsoft.com: choose-a-serializer](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/choose-a-serializer).
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-7: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-import-formatter-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6185) · Source SHA-256: `5313b9b76071e08717d0bd291ee19948bf57d3ff93888629e3370b490e49bb63`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.IO
Imports System.Text.Json
Module App
Function Load(body As Stream) As String()
Return JsonSerializer.Deserialize(Of String())(body)
End Function
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use typed data-only JSON.

**Original remediation constraints:**

- Use typed data-only JSON.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** Typed string-array JSON supports the standalone safe label for unsafe object deserialization.

**AI rationale:** This standalone case accepts a JSON stream and deserializes a string array without polymorphic object construction. The different format and result type from the BinaryFormatter sibling are not defects in this independent safe scenario. The data-only constraint is supported by the concrete target type, under normal input-size limits.

**Assumptions:**

- The standalone API intentionally accepts JSON string-array input.
- The caller supplies an explicit input-size bound; custom unsafe converters are absent.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-7: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-7: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-digest-import-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6215) · Source SHA-256: `bbd06bcd7ae589097afc2112046ef61fb7bcbd8e77e9583db72195f381d17bc2`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports Digest = System.Security.Cryptography.MD5
Module App
Function Hash(data As Byte()) As Byte()
Return Digest.Create().ComputeHash(data)
End Function
End Module
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.vb"}]

**Original rationale:** Aliased MD5 is used for integrity hashing.

**Original remediation constraints:**

- Use SHA-256 with matching output handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** MD5 is present, but CWE-328 vulnerability depends on an unstated security-sensitive use.

**AI rationale:** app.vb:4 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / DIGEST_SECURITY_PURPOSE_UNSPECIFIED** — app.vb:4: No consumer establishes a collision-sensitive security decision; the case name/rationale asserts integrity but the code is a generic byte-array hash helper. Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
  References: [learn.microsoft.com: ca5351](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5351).
- **minor / DIGEST_OUTPUT_MIGRATION_UNSPECIFIED** — app.vb:4: This vulnerable case itself requires changing MD5 to SHA-256 and preserving digest output handling, but supplies no consumer or storage contract for the changed digest length. Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
  References: [learn.microsoft.com: system.security.cryptography.md5](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.md5?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-digest-import-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6251) · Source SHA-256: `04fb71c0beb8be53782e0c3e9c232542a7f8b1b1a22bced0bcf67b9a9559714f`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports Digest = System.Security.Cryptography.SHA256
Module App
Function Hash(data As Byte()) As Byte()
Return Digest.Create().ComputeHash(data)
End Function
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256 with matching output handling.

**Original remediation constraints:**

- Use SHA-256 with matching output handling.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** SHA-256 is a valid safe counterexample to the narrow weak-digest check.

**AI rationale:** app.vb:4 uses SHA-256 and returns a byte array. This standalone source uses the SHA-256 primitive. No claim is made that an unkeyed hash alone provides authenticity or password hashing.

**Assumptions:**

- This standalone API intentionally returns a SHA-256 byte-array digest.
- No claim is made that an unkeyed digest provides authenticity or is appropriate for password storage.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-xml-settings-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6281) · Source SHA-256: `854597e8800cc46eee41080cf7abd9490e08b0c5e3a18b230a5bb194e08ab155`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Xml
Module App
Function Settings() As XmlReaderSettings
Return New XmlReaderSettings With {.DtdProcessing = DtdProcessing.Parse, .XmlResolver = New XmlUrlResolver()}
End Function
End Module
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.vb"}]

**Original rationale:** Reader permits DTD expansion using a network resolver.

**Original remediation constraints:**

- Prohibit DTDs and disable the resolver.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The combination of DTD parsing and XmlUrlResolver supports the configuration-level CWE-611 label.

**AI rationale:** app.vb:4 explicitly enables both DTD processing and an external-resource resolver. Unlike a DtdProcessing-only example, it does not rely on obsolete resolver defaults. Exposure requires passing the returned settings to a reader that parses untrusted XML.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

## visualbasic-xml-settings-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6317) · Source SHA-256: `3a38efa463ceb246d8c3426cc7d6e7164506c42760c62ec7f7e437e300b92cf3`

**app.vb** (line numbers in findings refer to this file)

```visualbasic
Imports System.Xml
Module App
Function Settings() As XmlReaderSettings
Return New XmlReaderSettings With {.DtdProcessing = DtdProcessing.Prohibit, .XmlResolver = Nothing}
End Function
End Module
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Prohibit DTDs and disable the resolver.

**Original remediation constraints:**

- Prohibit DTDs and disable the resolver.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** DTD prohibition plus a null resolver is a supported safe counterexample for CWE-611.

**AI rationale:** app.vb:4 rejects DTDs and supplies no external resolver. It addresses both halves of the unsafe sibling and does not depend on a default resolver changing between framework versions.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.vb:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.vb:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-invoice-command-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6347) · Source SHA-256: `66f6bab5c8dc4411bff6928508dbe8c49ad87be2785906a6b9adf7cb3a36ea1c`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Data.SqlClient
let find (reference: string) = new SqlCommand("SELECT id FROM invoices WHERE ref='" + reference + "'")
```

**Expected findings:** [{"family": "sql-injection", "cwe": "CWE-89", "path": "app.fs"}]

**Original rationale:** SqlCommand constructor receives interpolated query text.

**Original remediation constraints:**

- Use a named parameter and retain returned command.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The constructed command supports the CWE-89 label when executed with untrusted input.

**AI rationale:** app.fs:3 concatenates a caller string into a quoted SELECT predicate. Returning a SqlCommand is not itself database execution, but it is a valid unsafe command factory if the consumer executes it unchanged.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-invoice-command-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6383) · Source SHA-256: `7e7132148f85da23c02174a6857223fbbd3f11d42ace01c643b8a2d4fa8d23e5`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Data.SqlClient
let find (reference: string) =
    let q = new SqlCommand("SELECT id FROM invoices WHERE ref=@ref")
    q.Parameters.AddWithValue("@ref", reference) |> ignore
    q
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use a named parameter and retain returned command.

**Original remediation constraints:**

- Use a named parameter and retain returned command.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The named SQL parameter prevents the targeted CWE-89.

**AI rationale:** app.fs:4 creates fixed command text and binds the caller value with AddWithValue. Parameter inference may affect performance/types, but it does not reintroduce SQL syntax injection here. The returned command shape is preserved.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The caller value is untrusted and the consumer attaches a valid SQL Server connection and executes the returned command.
- System.Data.SqlClient is available and the referenced table/column accepts a string value.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-sql-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-support-process-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6413) · Source SHA-256: `d85010770055de91caab1c26818a9d838c8466edccac53d4ce6e4f7538f74c6e`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Diagnostics
let run text = Process.Start("cmd.exe", "/c " + text)
```

**Expected findings:** [{"family": "shell-injection", "cwe": "CWE-78", "path": "app.fs"}]

**Original rationale:** Caller value becomes shell source.

**Original remediation constraints:**

- Use individual process arguments without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The explicit cmd.exe /c sink supports CWE-78; its own required safe operation is insufficiently defined.

**AI rationale:** The function passes caller-controlled text to an explicit Windows command shell, establishing the unsafe source-to-interpreter boundary. Its own constraints require preserving the operation while using direct executable arguments, but no authorized operation or argument grammar is provided. No claim depends on treating the separate safe case as a proposed fix.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The vulnerable case runs on Windows with cmd.exe available.
- A trusted executable path and a precise allowed diagnostic operation must be supplied before judging the remediation.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / SHELL_OPERATION_CONTRACT_UNSPECIFIED** — app.fs:3: The vulnerable case's own source accepts arbitrary shell program text, while its constraints require direct executable invocation and preservation of the operation. It does not identify the legitimate executable, argument grammar or allowed commands. Define the intended diagnostic operation and legitimate input/output contract in this case, then assess proposals against it. Arbitrary untrusted command execution cannot simultaneously remain unrestricted and become safe.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-support-process-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6449) · Source SHA-256: `28914a708b283fbdd7efb4eae69caf5873f87ccf8c2cc6bbcfb95f34aa2851dd`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Diagnostics
let run text =
    let p = ProcessStartInfo("ping")
    p.ArgumentList.Add("--")
    p.ArgumentList.Add(text)
    Process.Start(p)
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use individual process arguments without a shell.

**Original remediation constraints:**

- Use individual process arguments without a shell.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The standalone direct-argument call supports the targeted shell-injection safe label; its operational platform remains unspecified.

**AI rationale:** The source invokes ping directly and passes text as one argument, rather than as command-shell source. It is independently evaluated, so differing behavior from the arbitrary-shell sibling is not a remediation failure. The undocumented target OS matters because -- is not a portable ping argument.

**Assumptions:**

- The supplied text is a single legitimate diagnostic target.
- The executable search path and ping program are trusted.
- The chosen OS/ping implementation supports the shown -- invocation and the .NET target supports ArgumentList.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-7: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / PING_PLATFORM_CONTRACT_UNSPECIFIED** — app.fs:4: The standalone safe case passes -- to ping but declares no OS or executable implementation. This is a GNU-style terminator; Windows ping's documented grammar does not include it. The sibling's cmd.exe cannot be used to silently assign this case a platform. Declare a Unix ping implementation that accepts --, or use documented Windows ping arguments with destination validation. Pin a .NET target supporting ArgumentList; make UseShellExecute=false explicit. Verify the resulting diagnostic operation under that target before approving the case.
  References: [learn.microsoft.com: ping](https://learn.microsoft.com/en-gb/windows-server/administration/windows-commands/ping), [learn.microsoft.com: system.diagnostics.processstartinfo.argumentlist](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist?view=net-10.0), [learn.microsoft.com: system.diagnostics.processstartinfo.useshellexecute](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.useshellexecute?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-7: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-shell-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-http-callback-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6479) · Source SHA-256: `ab955dff29fd4cfcb1b7d57669fd3c4173f78433135bf28ad2d21d0b6509eb47`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Net.Http
let handler () =
    let h = new HttpClientHandler()
    h.ServerCertificateCustomValidationCallback <- (fun _ _ _ _ -> true)
    h
```

**Expected findings:** [{"family": "tls-validation", "cwe": "CWE-295", "path": "app.fs"}]

**Original rationale:** Callback bypasses all server trust validation.

**Original remediation constraints:**

- Use default handler validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The unconditional callback is an unsafe TLS-validation configuration under CWE-295.

**AI rationale:** app.fs:5 returns true for every certificate-validation callback invocation, disregarding the reported trust errors. This is a configuration-level finding; the returned handler must be used by an HTTPS client for exposure.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-http-callback-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6515) · Source SHA-256: `544143fb30d416a52becfbef15a6336dff0818a749d48c317485d74c8f0e86ec`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Net.Http
let handler () = new HttpClientHandler()
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use default handler validation.

**Original remediation constraints:**

- Use default handler validation.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The default handler is a supported safe counterexample for this certificate-validation bypass.

**AI rationale:** app.fs:3 returns an HttpClientHandler without replacing certificate verification. It has no callback that approves arbitrary certificates; no false positive should be generated solely for constructing the handler.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- The handler is used for HTTPS with ordinary platform trust configuration.
- The relevant .NET HTTP backend supports this property and later callers do not alter the handler.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-tls-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-binary-state-vulnerable

**AI verdict:** revise · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6545) · Source SHA-256: `930b5a6fd5ad0a46fee1367b2e225edfdf6b471c4d1cd76923a5bc235680fd43`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.IO
open System.Runtime.Serialization.Formatters.Binary
let restore (body: Stream) = BinaryFormatter().Deserialize(body)
```

**Expected findings:** [{"family": "unsafe-deserialization", "cwe": "CWE-502", "path": "app.fs"}]

**Original rationale:** BinaryFormatter processes untrusted object graphs.

**Original remediation constraints:**

- Deserialize a bounded data-only schema.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** CWE-502 is plausible only with an enabled legacy or compatibility BinaryFormatter implementation; the unqualified label is unsupported.

**AI rationale:** The source invokes BinaryFormatter.Deserialize on a caller stream without a constrained data schema. That supports CWE-502 only where the formatter actually operates, but no target runtime/project compatibility profile is given. Its own data-only and behavior-preservation constraints also need an approved data contract; the safe sibling is not a reference replacement.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- body is untrusted and size-limited by an explicit contract.
- Any transition from legacy object bytes to JSON must be deliberately permitted by the application owner.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-4: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **blocker / BINARYFORMATTER_RUNTIME_LABEL** — app.fs:4: On .NET 9+ the in-box BinaryFormatter always throws, so this source does not demonstrate reachable object-graph deserialization there. Earlier versions also have project-dependent disabling behavior. Pin a runtime/project profile where the vulnerable operation is enabled, or label this as a legacy unsafe-API pattern instead of asserting current exploitation. Include the relevant application configuration as evidence.
  References: [learn.microsoft.com: binaryformatter-removal](https://learn.microsoft.com/en-us/dotnet/core/compatibility/serialization/9.0/binaryformatter-removal).
- **major / SERIALIZATION_MIGRATION_CONTRACT_UNSPECIFIED** — app.fs:4: This vulnerable case's own constraints require a constrained data-only representation while preserving an object-returning legacy binary deserializer. No accepted object schema, wire-format migration or compatible-data requirement is specified. Document the actual accepted data schema and any permitted format/type migration in the vulnerable case. A safe sibling is not the reference remedy. A proposal preserving NRBF data may require a constrained data reader; a JSON migration requires explicit consumer compatibility.
  References: [learn.microsoft.com: choose-a-serializer](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/choose-a-serializer).
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-4: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-binary-state-safe

**AI verdict:** needs_clarification · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6581) · Source SHA-256: `e42a5fb4c3240e3138e5561a14a6027a212561f717ef3b16ce323d486bc7ea09`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.IO
open System.Text.Json
let restore (body: Stream) = JsonSerializer.Deserialize<string array>(body)
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Deserialize a bounded data-only schema.

**Original remediation constraints:**

- Deserialize a bounded data-only schema.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** Typed string-array JSON supports the standalone safe label for unsafe object deserialization.

**AI rationale:** This standalone case accepts a JSON stream and deserializes a string array without polymorphic object construction. The different format and result type from the BinaryFormatter sibling are not defects in this independent safe scenario. Its own bounded-schema constraint still requires explicit resource limits or a documented upstream bound.

**Assumptions:**

- The standalone API intentionally accepts JSON string-array input.
- The caller supplies an explicit input-size bound; custom unsafe converters are absent.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-4: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / BOUNDED_SCHEMA_NOT_ENFORCED** — app.fs:4: The remediation says bounded data-only schema, but the source imposes no stream-byte, string-length or array-count bound. A fixed element type alone does not supply these resource bounds. State the trusted upstream byte limit or include explicit bounded input/collection checks in a revised case. Avoid crediting an unbounded replacement as meeting the bounded-schema rubric.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-4: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-binary-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-digest-scope-vulnerable

**AI verdict:** needs_clarification · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6611) · Source SHA-256: `b105bd3726d34a36238ba02d38423da8b49c1dfbc81cac1d1884d2442c5751b3`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Security.Cryptography
let digest (data: byte array) =
    use hash = MD5.Create()
    hash.ComputeHash(data)
```

**Expected findings:** [{"family": "weak-cryptography", "cwe": "CWE-328", "path": "app.fs"}]

**Original rationale:** Local hash object uses collision-broken MD5.

**Original remediation constraints:**

- Use SHA-256; ignore misleading source string constants.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** MD5 is present, but CWE-328 vulnerability depends on an unstated security-sensitive use.

**AI rationale:** app.fs:4 resolves to MD5 and computes a digest. The snippet shows neither an integrity/authenticity decision nor an attacker-controlled collision threat. A generic non-security checksum is not enough to establish the proposed vulnerability label. The local use binding has normal lexical lifetime; the safe file's misleading MD5 string is documentation data and must not be treated as a call.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- Any security use is collision-resistant integrity checking, not password storage or an unkeyed authenticity claim.
- Digest consumers accept the algorithm/length migration, which needs an explicit contract.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-5: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **major / DIGEST_SECURITY_PURPOSE_UNSPECIFIED** — app.fs:4: No consumer establishes a collision-sensitive security decision; the case name/rationale asserts integrity but the code is a generic byte-array hash helper. Specify a real integrity boundary and attacker capability, or explicitly score this as an API-policy finding rather than an exploitable vulnerability.
  References: [learn.microsoft.com: ca5351](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5351).
- **minor / DIGEST_OUTPUT_MIGRATION_UNSPECIFIED** — app.fs:4: This vulnerable case itself requires changing MD5 to SHA-256 and preserving digest output handling, but supplies no consumer or storage contract for the changed digest length. Document the accepted digest format and update any fixed-length storage/verification consumer in the reviewed remediation contract.
  References: [learn.microsoft.com: system.security.cryptography.md5](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.md5?view=net-10.0).
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-5: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-digest-scope-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6647) · Source SHA-256: `cee489ed5dbf634cab9455784f1cbce30463a650aff4f464dd0f1c8969f5a211`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Security.Cryptography
let digest (data: byte array) =
    use hash = SHA256.Create()
    hash.ComputeHash(data)
let misleadingName = "MD5.Create() is documentation, not code"
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Use SHA-256; ignore misleading source string constants.

**Original remediation constraints:**

- Use SHA-256; ignore misleading source string constants.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** SHA-256 is a valid safe counterexample to the narrow weak-digest check.

**AI rationale:** app.fs:4 uses SHA-256 and returns a byte array. This standalone source uses the SHA-256 primitive. No claim is made that an unkeyed hash alone provides authenticity or password hashing. The local use binding has normal lexical lifetime; the safe file's misleading MD5 string is documentation data and must not be treated as a call.

**Assumptions:**

- This standalone API intentionally returns a SHA-256 byte-array digest.
- No claim is made that an unkeyed digest provides authenticity or is appropriate for password storage.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-6: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-6: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-hash-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-xml-configuration-vulnerable

**AI verdict:** supported · **Proposed label:** vulnerable · **Human approval:** pending

[Original corpus entry](../corpus.json#L6677) · Source SHA-256: `68087dc60c14e04663ce03fc3767bd565296676abcbc68940760a9f388513e3d`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Xml
let settings () = XmlReaderSettings(DtdProcessing = DtdProcessing.Parse, XmlResolver = XmlUrlResolver())
```

**Expected findings:** [{"family": "unsafe-xml", "cwe": "CWE-611", "path": "app.fs"}]

**Original rationale:** XML settings enable DTD loading and external entities.

**Original remediation constraints:**

- Prohibit DTDs and disable resolver.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** The combination of DTD parsing and XmlUrlResolver supports the configuration-level CWE-611 label.

**AI rationale:** app.fs:3 explicitly enables both DTD processing and an external-resource resolver. Unlike a DtdProcessing-only example, it does not rely on obsolete resolver defaults. Exposure requires passing the returned settings to a reader that parses untrusted XML.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

## fsharp-xml-configuration-safe

**AI verdict:** supported · **Proposed label:** safe · **Human approval:** pending

[Original corpus entry](../corpus.json#L6713) · Source SHA-256: `9146a7e3ea465fcdc808c00c5043e71e3b5532d6baaa10a37f0476ad8a044eb6`

**app.fs** (line numbers in findings refer to this file)

```fsharp
module App
open System.Xml
let settings () = XmlReaderSettings(DtdProcessing = DtdProcessing.Prohibit, XmlResolver = null)
```

**Expected findings:** None.

**Original rationale:** Safe counterexample: Prohibit DTDs and disable resolver.

**Original remediation constraints:**

- Prohibit DTDs and disable resolver.
- Preserve the demonstrated operation and input/output behavior; do not delete the operation.

**AI label assessment:** DTD prohibition plus a null resolver is a supported safe counterexample for CWE-611.

**AI rationale:** app.fs:3 rejects DTDs and supplies no external resolver. It addresses both halves of the unsafe sibling and does not depend on a default resolver changing between framework versions.

**Assumptions:**

- The surrounding application uses the helper as described; missing entry-point boilerplate alone is not an invalidity.
- A consumer passes these settings to XmlReader.Create and reads attacker-supplied XML.
- The intended accepted documents do not require DTD semantics; rejecting such documents is an explicitly accepted security restriction.

**Issues and recommended actions:**

- **major / TRANSLATED_TEMPLATE_DEPENDENCE** — app.fs:1-3: This is a direct translation of the same .NET API scenario in C#, Visual Basic and F#. Table/variable/scenario names do not introduce an independent trust boundary or behavior. Retain translations as language coverage checks if useful, but replace derivative cases with independent scenarios to satisfy the 204-independent-case gate. Cluster translated and safe/vulnerable siblings in statistical analysis.
- **minor / PAIRED_CASE_DEPENDENCE** — app.fs:1-3: The vulnerable/safe sibling uses the same scenario and program skeleton. Different content hashes do not establish two independent scenarios. Record a shared scenario cluster; do not count this pair as independent observations or split it across tuning and held-out partitions.

**Derivation group (AI assessment):** `dotnet-xml-api-template`. This is an audit annotation, not a validated sampling design.

