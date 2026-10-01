# ruby — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-ruby-safe-01 — rails-escaped-prefix-member-count

Proposed label: **safe**. Human review: **pending**.

Source hash: `e74ff3adf3bf9c6dabf899ae4e25b9f87cd4aa913d48a07d501f59da957ff3fa`. Protocol-2.0 case hash: `52d8a70c2a6f95496a71ea97652f4d6dfa7f04409e939c972ad2c8de723a453d`.

ActiveRecord binds the LIKE pattern as a value and sanitize_sql_like escapes user wildcard characters. An apostrophe does not become SQL syntax and percent remains literal prefix data.

### member_count.rb

```ruby
class MemberCount
  def self.by_literal_prefix(account_id, prefix)
    raise ArgumentError, 'prefix' unless prefix.instance_of?(String) && prefix.bytesize <= 60
    escaped = ActiveRecord::Base.sanitize_sql_like(prefix)
    pattern = escaped + '%'
    Member.where(account_id: account_id)
          .where('display_name LIKE ?', pattern)
          .count
  end
end
```

### schema.sql

```ruby
CREATE TABLE members(id BIGSERIAL PRIMARY KEY, account_id BIGINT NOT NULL, display_name TEXT NOT NULL);
INSERT INTO members(account_id, display_name) VALUES(2, '50% Club'), (2, '500 Club');
```

### Derivation

```json
{
  "group": "rails-escaped-prefix-member-count",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user supplies search text while the authenticated account ID and SQL structure remain server-controlled. The operation is count account members whose display name begins with a literal customer-entered prefix.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for count account members whose display name begins with a literal customer-entered prefix. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count account members whose display name begins with a literal customer-entered prefix.",
  "trust_boundary": "A user supplies search text while the authenticated account ID and SQL structure remain server-controlled.",
  "legitimate_examples": [
    {
      "input": "account_id=2; prefix=50%",
      "expected": 1
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
    "https://api.rubyonrails.org/classes/ActiveRecord/Sanitization/ClassMethods.html#method-i-sanitize_sql_like"
  ]
}
```

### Regression traps

```json
[
  "Removing LIKE escaping does not create SQL injection but broadens the operation; preserve literal percent/underscore semantics as well as account scoping."
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
  "slot_id": "v2-ruby-safe-01",
  "prior_case_id": "ruby-record-filter-safe",
  "prior_source_sha256": "b952ca29a13ab3d41b466242a4b388c8b7c2ba65fe1af07c5498635aca0cbde9",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Rails 7.2.2.1 with pg 1.5.9/PostgreSQL 16 default LIKE escape semantics, Member maps initialized members table; account ID authenticated."
}
```

### Split

```json
"held_out"
```

## v2-ruby-safe-02 — psych-primitive-shift-calendar

Proposed label: **safe**. Human review: **pending**.

Source hash: `1f961166cf70dac42495713e5053e3893083f9eec77a6a63008441394ec5070d`. Protocol-2.0 case hash: `a37ebe3cb4cee396c13a9b88fa947c6726f77d18e099c6f6bda253eb9088e355`.

safe_load permits no custom classes or symbols and disables aliases; subsequent exact Array/String checks restrict the result before display.

### shift_calendar.rb

```ruby
require 'psych'

def shift_names(text)
  raise ArgumentError, 'calendar too large' if text.bytesize > 4096
  entries = Psych.safe_load(text, permitted_classes: [], permitted_symbols: [], aliases: false)
  unless entries.instance_of?(Array) && entries.size <= 20 && entries.all? { |value| value.instance_of?(String) && value.bytesize <= 60 }
    raise ArgumentError, 'string shifts required'
  end
  entries.map { |name| { 'display_name' => name } }
end

def preview_shift_upload(body)
  { 'shifts' => shift_names(body) }
end
```

### Derivation

```json
{
  "group": "psych-primitive-shift-calendar",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A scheduling editor uploads YAML but cannot instantiate arbitrary Ruby classes or refer to alias graphs. The operation is preview a short yaml list of shift names as display-only calendar entries.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for preview a short yaml list of shift names as display-only calendar entries. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Preview a short YAML list of shift names as display-only calendar entries.",
  "trust_boundary": "A scheduling editor uploads YAML but cannot instantiate arbitrary Ruby classes or refer to alias graphs.",
  "legitimate_examples": [
    {
      "input": "- Morning\n- \"!ruby/object:Kernel\"",
      "expected": "Return two literal display-name strings; the quoted tag remains text."
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
    "https://docs.ruby-lang.org/en/3.3/Psych.html#method-c-safe_load"
  ]
}
```

### Regression traps

```json
[
  "Allowing Date or Symbol globally to silence parse errors is not needed for shift names; preserve strings that resemble YAML object tags when quoted."
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
  "slot_id": "v2-ruby-safe-02",
  "prior_case_id": "ruby-session-marshal-safe",
  "prior_source_sha256": "bc4b93f4e08d422a70dca63eebab5a73ee8227f49bf4bf655604d67da3854e9c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Psych 5.1.2; YAML body size bounded before parse, no downstream template evaluation. Names are rendered through escaped Rails views or JSON text."
}
```

### Split

```json
"held_out"
```

## v2-ruby-safe-03 — json-delivery-address-primitive-fields

Proposed label: **safe**. Human review: **pending**.

Source hash: `f69e8e7cc7cc73e5883a23e99e934c5c63bd9364f89a4db45f130d3bc60e164f`. Protocol-2.0 case hash: `b7adaf2a46956be73172f5a20bc22ee3be9d1a0ffc55282f400458df03b68035`.

JSON additions are explicitly disabled and only a Hash of three strings reaches the result. A json_class field is unknown input and rejected.

### address_import.rb

```ruby
require 'json'

def import_address(raw)
  raise ArgumentError, 'address size' if raw.bytesize > 2048
  value = JSON.parse(raw, create_additions: false, max_nesting: 4)
  raise ArgumentError, 'object required' unless value.instance_of?(Hash)
  allowed = %w[street city postal]
  raise ArgumentError, 'unknown address fields' unless value.keys.sort == allowed.sort
  unless allowed.all? { |key| value[key].instance_of?(String) && value[key].bytesize.between?(1, 120) }
    raise ArgumentError, 'address text required'
  end
  allowed.to_h { |key| [key, value.fetch(key)] }
end
```

### Derivation

```json
{
  "group": "json-delivery-address-primitive-fields",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An account holder supplies JSON values but has no ability to choose Ruby classes or invoke JSON additions. The operation is import three exact address text fields for a shipping-label preview.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for import three exact address text fields for a shipping-label preview. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import three exact address text fields for a shipping-label preview.",
  "trust_boundary": "An account holder supplies JSON values but has no ability to choose Ruby classes or invoke JSON additions.",
  "legitimate_examples": [
    {
      "input": "{\"street\":\"1 King St\",\"city\":\"York\",\"postal\":\"YO1\"}",
      "expected": {
        "street": "1 King St",
        "city": "York",
        "postal": "YO1"
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
    "https://docs.ruby-lang.org/en/3.3/JSON.html#module-JSON-label-Parsing+JSON"
  ]
}
```

### Regression traps

```json
[
  "Using JSON.load with additions enabled would change the object-construction policy; do not drop leading zeros from postal codes."
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
  "slot_id": "v2-ruby-safe-03",
  "prior_case_id": "ruby-profile-yaml-safe",
  "prior_source_sha256": "cdec92f8c89f701eabfa7b9704646e6d668ddcc722c7b4e26dbff238d34e38d3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "json gem 2.8.2; output is used as literal shipping text with markup escaping by the trusted renderer; this is preview data, not a permission or billing address decision."
}
```

### Split

```json
"held_out"
```

## v2-ruby-safe-04 — audio-duration-positional-process

Proposed label: **safe**. Human review: **pending**.

Source hash: `45cbbaa0a910648e583a8a77ad25045b17bbe1e5e52e11eb38d04aa69ef71b4f`. Protocol-2.0 case hash: `70fa5d692e40365328cfb0157584eb1ae6eb2a8f95834c41f7dbd53ea1597306`.

Open3 receives distinct executable and argument values, no shell string. The numeric ID produces a fixed absolute .wav path rather than options or protocol syntax.

### audio_duration.rb

```ruby
require 'open3'

def audio_duration(owned_recording_id)
  unless owned_recording_id.instance_of?(Integer) && owned_recording_id.positive?
    raise ArgumentError, 'recording ID'
  end
  file = "/srv/normalized-audio/#{owned_recording_id}.wav"
  output, error, status = Open3.capture3('/usr/bin/soxi', '-D', file)
  raise 'inspection failed' unless status.success?
  seconds = Float(output.strip)
  raise 'invalid duration' unless seconds.finite? && seconds >= 0
  seconds
end
```

### Derivation

```json
{
  "group": "audio-duration-positional-process",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The caller provides an authorized positive integer ID; executable, fixed options and stored WAV files are trusted. The operation is read the duration in seconds of a server-normalized, owned audio recording.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for read the duration in seconds of a server-normalized, owned audio recording. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read the duration in seconds of a server-normalized, owned audio recording.",
  "trust_boundary": "The caller provides an authorized positive integer ID; executable, fixed options and stored WAV files are trusted.",
  "legitimate_examples": [
    {
      "input": "recording ID 12 with a 2.5-second WAV",
      "expected": 2.5
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
    "https://docs.ruby-lang.org/en/3.3/Open3.html#method-c-capture3"
  ]
}
```

### Regression traps

```json
[
  "Do not switch to a single interpolated command string to handle spaces; preserve floating-point seconds and nonzero-exit errors."
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
  "slot_id": "v2-ruby-safe-04",
  "prior_case_id": "ruby-hostname-command-safe",
  "prior_source_sha256": "4ca061cb54e34fb443881419b68fd0d9e1d60b8d7e2031a95dd6ec06b4ae1868",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "SoX 14.4.2 with soxi at /usr/bin/soxi, WAV-only trusted normalized data; external worker deadline 3 seconds and output limit 1 KiB; root-owned storage without symlinks."
}
```

### Split

```json
"held_out"
```

## v2-ruby-safe-05 — explicit-exporter-class-registry

Proposed label: **safe**. Human review: **pending**.

Source hash: `a8fdb2e3ad0149c3f6038aebadd99bec1e4b3fb9c7a889d18c8142059e1f0376`. Protocol-2.0 case hash: `90f652f2ff45c805983103b6879024f4d2c5c1004380dc6dd3c154d29ca83d7b`.

A frozen Hash maps allowed names directly to predeclared classes; no eval, constantize or arbitrary require consumes user text. Unknown names raise an error.

### export_registry.rb

```ruby
require 'json'
class JsonSummary
  def self.render(rows)
    JSON.generate(rows)
  end
end
class PlainSummary
  def self.render(rows)
    rows.map { |row| row.fetch('label') }.join("\n")
  end
end
EXPORTERS = { 'json' => JsonSummary, 'plain' => PlainSummary }.freeze

def evaluate_export(format, rows)
  exporter = EXPORTERS.fetch(format) { raise ArgumentError, 'unknown format' }
  exporter.render(rows)
end
```

### Derivation

```json
{
  "group": "explicit-exporter-class-registry",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user selects one of two literal exporter names; classes and row schema are server-owned. The operation is render authorized summary rows in either json or plain-text format.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for render authorized summary rows in either json or plain-text format. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render authorized summary rows in either JSON or plain-text format.",
  "trust_boundary": "A user selects one of two literal exporter names; classes and row schema are server-owned.",
  "legitimate_examples": [
    {
      "input": "format=plain; rows=[{label: One},{label: Two}]",
      "expected": "Return One\nTwo."
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
    "https://docs.ruby-lang.org/en/3.3/Hash.html#method-i-fetch"
  ]
}
```

### Regression traps

```json
[
  "Replacing fetch with Object.const_get on the format would create an authority boundary; keep Unicode labels and newline formatting unchanged."
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
  "slot_id": "v2-ruby-safe-05",
  "prior_case_id": "ruby-stored-expression-safe",
  "prior_source_sha256": "d62153af431e1eacc005f88239ed5919fc8fdb1679996cb47c9eb942f3479083",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Rows are bounded to 20 server-produced records with string labels; caller chooses text/plain or application/json appropriately and never renders plain output as raw HTML."
}
```

### Split

```json
"held_out"
```

## v2-ruby-safe-06 — imap-peer-verified-mailbox-count

Proposed label: **safe**. Human review: **pending**.

Source hash: `7f11d277788b4d8c2b1cf2710a5f9d693afac924d8728dcbdb84f25dd09e05f7`. Protocol-2.0 case hash: `c88dac17618cf10b98c37e84e213d8b70313a39eb40c00a4c63403decb7e8a94`.

The SSL connection enables peer verification with the deployed CA; net-imap performs hostname checking under VERIFY_PEER before login. No untrusted hostname or SSL override is supplied.

### mailbox_count.rb

```ruby
require 'net/imap'
require 'openssl'

def unread_count(username, password)
  imap = Net::IMAP.new('imap.example.org', port: 993,
    ssl: { verify_mode: OpenSSL::SSL::VERIFY_PEER,
           ca_file: '/run/secrets/mail-ca.pem' }, open_timeout: 3)
  begin
    imap.login(username, password)
    imap.select('INBOX')
    imap.search(['UNSEEN']).length
  ensure
    imap.disconnect unless imap.disconnected?
  end
end
```

### Derivation

```json
{
  "group": "imap-peer-verified-mailbox-count",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An active network attacker must not obtain server-held mailbox credentials; hostname and CA file are trusted. The operation is return the number of unread inbox messages from the configured imap service.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for return the number of unread inbox messages from the configured imap service. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the number of unread INBOX messages from the configured IMAP service.",
  "trust_boundary": "An active network attacker must not obtain server-held mailbox credentials; hostname and CA file are trusted.",
  "legitimate_examples": [
    {
      "input": "Authenticated mailbox with three UNSEEN messages",
      "expected": 3
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
    "https://github.com/ruby/net-imap/blob/v0.5.6/lib/net/imap.rb"
  ]
}
```

### Regression traps

```json
[
  "Using VERIFY_NONE because an enterprise certificate is unfamiliar would expose credentials; retain INBOX selection and UNSEEN filtering."
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
  "slot_id": "v2-ruby-safe-06",
  "prior_case_id": "ruby-certificate-mode-safe",
  "prior_source_sha256": "19efc679e384da17850faf26fca267387b2d2d479f7340212396c48f21356af6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "net-imap 0.5.6 and openssl 3.2.0; enterprise CA root file read-only, certificate SAN matches imap.example.org; server responds within worker deadline; username/password trusted secret values."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-01 — rails-event-retention-predicate

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `310b955321a833f085f481291b99beb4c0eb8b1d31bbc2d132e3b27970f87293`. Protocol-2.0 case hash: `0cd54616b7c62977e8ae0caacb5f1010b08e2c959e6487994936befde1242e5f`.

String interpolation places the day input inside a PostgreSQL interval literal without binding or a strict integer conversion. The surrounding ActiveRecord chain does not sanitize a raw SQL string.

### retention_report.rb

```ruby
class RetentionReport
  def self.count_for(account_id, raw_days)
    days = raw_days.to_s
    raise ArgumentError, 'filter too long' if days.bytesize > 80
    # account_id is supplied by authentication; only the interval is editable.
    Event.where(account_id: account_id)
         .where("created_at >= CURRENT_TIMESTAMP - INTERVAL '#{days} days'")
         .count
  end
end
```

### events_controller.rb

```ruby
class EventsController < ApplicationController
  def retained_count
    render json: { count: RetentionReport.count_for(current_account.id, params[:days]) }
  end
end
```

### schema.sql

```ruby
CREATE TABLE events(id BIGSERIAL PRIMARY KEY, account_id BIGINT NOT NULL, created_at TIMESTAMPTZ NOT NULL);
INSERT INTO events(account_id, created_at) VALUES(4, CURRENT_TIMESTAMP - INTERVAL '2 days');
```

### Derivation

```json
{
  "group": "rails-event-retention-predicate",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An authenticated account user controls an interval fragment; Rails safely builds the account predicate but receives an unsafe raw SQL condition. The operation is count recent account events using a customer-selected retention window of whole days.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "retention_report.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for count recent account events using a customer-selected retention window of whole days. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count recent account events using a customer-selected retention window of whole days.",
  "trust_boundary": "An authenticated account user controls an interval fragment; Rails safely builds the account predicate but receives an unsafe raw SQL condition.",
  "legitimate_examples": [
    {
      "input": "account_id=4; days=7; one event two days old",
      "expected": "Return count=1."
    }
  ],
  "permitted_changes": [
    "Validate a bounded whole-day count and bind a timestamp cutoff or safely multiply a bound integer by a fixed interval."
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
    "https://guides.rubyonrails.org/security.html#sql-injection"
  ]
}
```

### Regression traps

```json
[
  "An Integer() conversion must reject malformed text rather than use to_i, which silently accepts prefixes; preserve day-window semantics and account scoping."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Validate a bounded whole-day count and bind a timestamp cutoff or safely multiply a bound integer by a fixed interval."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-01",
  "prior_case_id": "ruby-record-filter-vulnerable",
  "prior_source_sha256": "f22a073127cc8837ef41ef867545eb88dc40e55c1c2e3bde9f28b754e45fd9c5",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Rails 7.2.2.1, pg 1.5.9, PostgreSQL 16; Event maps events, application timezone UTC; current_account authenticated; evaluation fixes the reference time to avoid boundary ambiguity."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-02 — calibration-basename-open-dispatch

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `7839b6e845850bf720a94d02a06263327e9d568c08165ff23527f03847dcfe1a`. Protocol-2.0 case hash: `4cb36be8e7c9d3fd5ecd2ff400bde88d3a8883beb17b036849232b6ebf49a373`.

Kernel.open treats a leading pipe as a command stream, even though the input passes the basename check. The command is launched before CSV parsing, so later malformed-data rejection cannot undo process execution.

### calibration_import.rb

```ruby
require 'csv'
SPOOL_DIRECTORY = '/srv/calibration-imports'.freeze

def import_calibration_file(name)
  unless name.instance_of?(String) && name.bytesize.between?(1, 120)
    raise ArgumentError, 'filename'
  end
  if name.include?('/') || name.include?("\0") || ['.', '..'].include?(name)
    raise ArgumentError, 'basename required'
  end
  # Import jobs run serially; the caller selects one literal staged filename.
  bytes = Dir.chdir(SPOOL_DIRECTORY) do
    Kernel.open(name, 'rb') { |stream| stream.read(32_769) }
  end
  raise ArgumentError, 'calibration file too large' if bytes.bytesize > 32_768
  CSV.parse(bytes, headers: true).map(&:to_h)
end
```

### calibration_request.rb

```ruby
require_relative 'calibration_import'

def preview_calibration(params)
  # An authenticated operator may inspect the public staged calibration set.
  { 'readings' => import_calibration_file(params.fetch('filename')) }
end
```

### Authoring history

```json
[
  {
    "event": "replaced_before_static_validation",
    "previous_scenario": "integration-yaml-legacy-object-restoration",
    "previous_content_sha256": "f7e9f2cad10105244778e2d5d7cc0d2c2474d054088f9455d811ba8259f54f04",
    "previous_files": {
      "integration_import.rb": "require 'psych'\nrequire_relative 'legacy_policy'\n\ndef import_integration_yaml(text)\n  raise ArgumentError, 'file too large' if text.bytesize > 4096\n  value = Psych.unsafe_load(text)\n  raise ArgumentError, 'mapping required' unless value.instance_of?(Hash)\n  raise ArgumentError, 'name required' unless value['name'].instance_of?(String)\n  { 'name' => value['name'], 'enabled' => value.fetch('enabled', false) }\nend\n",
      "legacy_policy.rb": "# Internal backup support is loaded in the same process as integration import.\nmodule SecurityPolicy\n  SETTINGS = { 'mfa_required' => true }\nend\nclass LegacyPolicyBackup\n  def init_with(coder)\n    SecurityPolicy::SETTINGS['mfa_required'] = coder['mfa_required']\n  end\nend\n"
    },
    "previous_derivation_group": "privileged-object-restoration-hooks",
    "reason": "Retired the privileged-restoration-hook draft due to known shared conception with another Ruby draft and PHP vulnerable-03; this new case changes source, operation, trust boundary and vulnerability mechanism."
  }
]
```

### Authoring notes

```json
[
  "Planning slot originally targeted unsafe-deserialization. With coordinator approval it now covers shell-injection to replace a known correlated authoring draft. No rules or scanner outputs were consulted; independent human judgment is still pending."
]
```

### Derivation

```json
{
  "group": "calibration-basename-open-dispatch",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An authenticated operator selects a filename in a server-owned spool; selecting a file must not authorize launching a subprocess. The operation is parse a literal staged calibration csv basename into header-keyed reading records.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "calibration_import.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for parse a literal staged calibration csv basename into header-keyed reading records. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The spool is immutable, contains no symlinks, and is wholly authorized for this operator role; a writable spool would require additional containment and race handling.",
    "CSV data is returned as JSON text only and is never exported into spreadsheet formulas or executed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Parse a literal staged calibration CSV basename into header-keyed reading records.",
  "trust_boundary": "An authenticated operator selects a filename in a server-owned spool; selecting a file must not authorize launching a subprocess.",
  "legitimate_examples": [
    {
      "input": "filename=probe A.csv; file bytes=sensor,value\\nA,1.25\\n",
      "expected": {
        "readings": [
          {
            "sensor": "A",
            "value": "1.25"
          }
        ]
      }
    }
  ],
  "permitted_changes": [
    "Use File.open or another file-only API on the selected basename within the fixed spool, retaining bounded reads and header-keyed CSV output."
  ],
  "forbidden_changes": [
    "Do not execute the selected name, remove CSV parsing, coerce readings to numbers, or discard legitimate punctuation in filenames."
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
    "https://docs.ruby-lang.org/en/3.3/Kernel.html#method-i-open",
    "https://docs.ruby-lang.org/en/3.3/File.html#method-c-open"
  ]
}
```

### Regression traps

```json
[
  "POSIX basenames may legitimately contain spaces, pipe characters or punctuation; use file-only opening rather than silently converting those names into shell syntax or banning the documented filename set."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use File.open or another file-only API on the selected basename within the fixed spool, retaining bounded reads and header-keyed CSV output.",
  "Do not execute the selected name, remove CSV parsing, coerce readings to numbers, or discard legitimate punctuation in filenames."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-02",
  "prior_case_id": "ruby-session-marshal-vulnerable",
  "prior_source_sha256": "6c2a4f67648d9d114046d590a9fef2cb6d0f3b9db5e67c59ec96b12067f3e5bb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Ruby 3.3.6 with csv 3.3.2; one serial worker, no concurrent Dir.chdir use. Root-owned spool contains only authorized regular calibration files with no symlinks; it is immutable while a job runs. Trusted PATH and a five-second worker deadline. Every staged file is valid UTF-8 CSV with unique headers and at most 32 KiB."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-03 — tar-symlink-parent-extraction

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `7a19b9883cdef6623caa2ae52ce582cd845778110e40247ecae7b2813c68daa2`. Protocol-2.0 case hash: `e3b4ab42591d48cc74d586267beb4369e7c376369e1090ebf7b0ea0ab5f11593`.

Lexical entry-name checks do not constrain symlink targets or later resolution through them. An escaping link followed by a regular entry beneath that link makes File.binwrite operate outside the assigned extraction directory.

### bundle_extract.rb

```ruby
require 'rubygems/package'
require 'zlib'
require 'stringio'
require 'pathname'
require 'fileutils'

def extract_document_bundle(compressed, destination)
  raise ArgumentError, 'archive too large' if compressed.bytesize > 2_097_152
  count = 0
  Zlib::GzipReader.wrap(StringIO.new(compressed)) do |gzip|
    Gem::Package::TarReader.new(gzip) do |archive|
      archive.each do |entry|
        count += 1
        raise ArgumentError, 'entry limits' if count > 100 || entry.header.size > 65_536
        relative = Pathname.new(entry.full_name).cleanpath
        if relative.absolute? || relative.each_filename.any? { |part| part == '..' }
          raise ArgumentError, 'entry path escapes'
        end
        target = File.join(destination, relative.to_s)
        if entry.directory?
          FileUtils.mkdir_p(target)
        elsif entry.header.typeflag == '2'
          FileUtils.mkdir_p(File.dirname(target))
          File.symlink(entry.header.linkname, target)
        elsif entry.file?
          FileUtils.mkdir_p(File.dirname(target))
          File.binwrite(target, entry.read)
        else
          raise ArgumentError, 'unsupported entry type'
        end
      end
    end
  end
  count
end
```

### bundle_job.rb

```ruby
require_relative 'bundle_extract'

def stage_customer_bundle(upload, private_job_directory)
  # The coordinator allocates a fresh, service-owned directory per import.
  count = extract_document_bundle(upload, private_job_directory)
  { 'entries' => count, 'state' => 'staged' }
end
```

### Authoring history

```json
[
  {
    "event": "replaced_before_static_validation",
    "previous_scenario": "shared-cache-marshaled-cart",
    "previous_content_sha256": "696ea4911457f9d505c7053e6d22c88adefdc7086c3be0bea74c33ed757f6f0a",
    "previous_files": {
      "cart_cache.rb": "require 'base64'\nrequire_relative 'promotion_grant'\n\ndef restore_cart(cache, cart_id)\n  encoded = cache.get(\"cart:#{cart_id}\")\n  raise ArgumentError, 'cache record too large' if encoded.bytesize > 8192\n  cart = Marshal.load(Base64.strict_decode64(encoded))\n  unless cart.instance_of?(Array) && cart.all? { |sku| sku.instance_of?(String) }\n    raise ArgumentError, 'cart must be an array of SKUs'\n  end\n  cart\nend\n",
      "promotion_grant.rb": "# Trusted promotion snapshots use this class; an importer may not grant credit.\nmodule PromotionLedger\n  CREDITS = Hash.new(0)\nend\nclass PromotionGrant\n  def marshal_load(tuple)\n    account, cents = tuple\n    PromotionLedger::CREDITS[account] += cents\n  end\nend\n"
    },
    "previous_derivation_group": "privileged-object-restoration-hooks",
    "reason": "Retired the privileged-restoration-hook draft due to known shared conception with another Ruby draft and PHP vulnerable-03; this new case changes source, operation, trust boundary and vulnerability mechanism."
  }
]
```

### Authoring notes

```json
[
  "Planning slot originally targeted unsafe-deserialization. With coordinator approval it now covers path-traversal to replace a known correlated authoring draft. No rules or scanner outputs were consulted; independent human judgment is still pending."
]
```

### Derivation

```json
{
  "group": "tar-symlink-parent-extraction",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer controls archive entries and symlink targets; the service owns the fresh destination and can also write unrelated shared state outside it. The operation is extract a bounded document tar.gz bundle into its private job directory, preserving directories and internal symbolic links.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "bundle_extract.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for extract a bounded document tar.gz bundle into its private job directory, preserving directories and internal symbolic links. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "No archive contents are executed or loaded as plugins. The demonstrated flaw is an outside-root write through archive-controlled filesystem resolution.",
    "Lexical names, symlink targets and entry order are separate validation inputs; the initially empty directory does not make subsequent archive-created links trusted."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Extract a bounded document tar.gz bundle into its private job directory, preserving directories and internal symbolic links.",
  "trust_boundary": "A customer controls archive entries and symlink targets; the service owns the fresh destination and can also write unrelated shared state outside it.",
  "legitimate_examples": [
    {
      "input": "Archive entries: docs/ directory, docs/readme.txt containing Hello, latest symlink to docs",
      "expected": "Stage all three entries; docs/readme.txt contains Hello and latest resolves to docs inside the job directory."
    }
  ],
  "permitted_changes": [
    "Validate the effective resolution of every destination and link target within the job root before writes; stage and validate links safely while retaining legitimate internal aliases."
  ],
  "forbidden_changes": [
    "Do not write through escaping links, discard all bundle contents, flatten nested paths, or execute extracted scripts."
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
    "https://docs.ruby-lang.org/en/3.3/Gem/Package/TarReader.html",
    "https://docs.ruby-lang.org/en/3.3/Pathname.html#method-i-cleanpath",
    "https://docs.ruby-lang.org/en/3.3/File.html#method-c-symlink"
  ]
}
```

### Regression traps

```json
[
  "Removing ../ only from entry names misses the link-target boundary. Internal document aliases are part of the contract, so a fix must preserve valid internal links or explicitly reject only unsafe link behavior before any outside write."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Validate the effective resolution of every destination and link target within the job root before writes; stage and validate links safely while retaining legitimate internal aliases.",
  "Do not write through escaping links, discard all bundle contents, flatten nested paths, or execute extracted scripts."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-03",
  "prior_case_id": "ruby-profile-yaml-vulnerable",
  "prior_source_sha256": "cac5606da833902c5785c3214eb3dc0c37c2bf388cb7f871e8fb060f131b7c12",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Ruby 3.3.6 with RubyGems 3.5.22 and zlib 3.1.1 on Linux. Coordinator creates an empty mode-0700 directory and executes one bounded import there; no external process mutates entries. Archive metadata is adversarial, including entry ordering and absolute/relative link targets. Worker enforces a five-second deadline and a 10 MiB total output limit."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-04 — customer-pdf-watermark-process

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `9465a3a103f5e8caf9fb97c8b3456f336c25290b94bdbe08f1428c7a6f408fc4`. Protocol-2.0 case hash: `f6a6faba3dcafae3a3f0e524ad2d362d9e5f83e38d2a3997816f2a26b3f44cb4`.

Open3.capture3 receives one command string; shell metacharacters in a label cause shell interpretation rather than remaining one text argument.

### watermark.rb

```ruby
require 'open3'

def watermark_pdf(document_id, label)
  raise ArgumentError, 'document ID' unless document_id.instance_of?(Integer) && document_id.positive?
  raise ArgumentError, 'label length' if label.bytesize > 80
  input = "/srv/pdfs/#{document_id}.pdf"
  # The trusted tool emits the marked PDF on stdout.
  command = "/usr/local/bin/pdf-stamp --text #{label} --input #{input}"
  bytes, error, status = Open3.capture3(command)
  raise 'watermark failed' unless status.success?
  bytes
end

def download_watermark(owned_document, params)
  watermark_pdf(owned_document.id, params.fetch('label'))
end
```

### Derivation

```json
{
  "group": "customer-pdf-watermark-process",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer controls label text; the PDF ID and stamping executable are server-owned. The operation is return a copy of an owned pdf stamped with the customer’s exact plain-text label.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "watermark.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for return a copy of an owned pdf stamped with the customer’s exact plain-text label. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return a copy of an owned PDF stamped with the customer’s exact plain-text label.",
  "trust_boundary": "A customer controls label text; the PDF ID and stamping executable are server-owned.",
  "legitimate_examples": [
    {
      "input": "document_id=8; label=Reviewed by Ana",
      "expected": "Return the PDF with the literal label Reviewed by Ana on each page."
    }
  ],
  "permitted_changes": [
    "Call capture3 with the executable and a separate argument array; preserve bytes, error propagation and exact label text."
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
    "https://docs.ruby-lang.org/en/3.3/Open3.html#method-c-capture3"
  ]
}
```

### Regression traps

```json
[
  "Labels containing spaces, apostrophes or dollar signs are legitimate; rejecting all punctuation instead of separating arguments regresses the stamping feature."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Call capture3 with the executable and a separate argument array; preserve bytes, error propagation and exact label text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-04",
  "prior_case_id": "ruby-hostname-command-vulnerable",
  "prior_source_sha256": "ed528725ba16ae94aa0ab0dd078074f4e28830d2be0245a86252528000ffce41",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "Trusted pdf-stamp 1.0 executable accepts --text TEXT --input PATH and writes PDF bytes to stdout; root-owned executable uses a non-executing text renderer. Worker has a five-second external process deadline and output cap."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-05 — csv-column-generated-accessors

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `af2b7a1ce94baec1aee01637993f26cf84a925d3051fbb4cd65db80a93ac1a74`. Protocol-2.0 case hash: `9bba1342720fb8649780d8153179ac07b96404b62912535958ac01cc05234026`.

class_eval reparses interpolated field text as Ruby code. A size/type check does not constrain the text to an identifier or prevent statements from running during class definition.

### row_model.rb

```ruby
require 'json'

def project_upload(json_body)
  request = JSON.parse(json_body)
  fields = request.fetch('fields')
  values = request.fetch('values')
  raise ArgumentError, 'column count' unless fields.size.between?(1, 12) && fields.size == values.size
  model = Class.new
  fields.each do |field|
    raise ArgumentError, 'name length' unless field.instance_of?(String) && field.bytesize <= 40
    model.class_eval("attr_accessor :#{field}")
  end
  row = model.new
  fields.zip(values).each { |field, value| row.public_send("#{field}=", value) }
  fields.to_h { |field| [field, row.public_send(field)] }
end
```

### Derivation

```json
{
  "group": "csv-column-generated-accessors",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An importer controls column-name text but is authorized only to name fields, not define or execute Ruby methods. The operation is create a tabular row with user-selected identifier column names and return the associated values unchanged.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "row_model.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for create a tabular row with user-selected identifier column names and return the associated values unchanged. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Create a tabular row with user-selected identifier column names and return the associated values unchanged.",
  "trust_boundary": "An importer controls column-name text but is authorized only to name fields, not define or execute Ruby methods.",
  "legitimate_examples": [
    {
      "input": "{\"fields\":[\"city\",\"zip\"],\"values\":[\"Oslo\",\"0150\"]}",
      "expected": {
        "city": "Oslo",
        "zip": "0150"
      }
    }
  ],
  "permitted_changes": [
    "Avoid generated Ruby source; validate identifier names and use a Hash or non-evaluating accessor API."
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
    "https://docs.ruby-lang.org/en/3.3/Module.html#method-i-class_eval"
  ]
}
```

### Regression traps

```json
[
  "Preserve string values and field ordering; quoting input for SQL or HTML does not protect Ruby source. Reject reserved object-method names under a documented schema."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Avoid generated Ruby source; validate identifier names and use a Hash or non-evaluating accessor API."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-05",
  "prior_case_id": "ruby-stored-expression-vulnerable",
  "prior_source_sha256": "f1e60f26b5c9ef45d8128209bb06c71414a1491ae3be993554eb1813cabc63de",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "JSON 2.8.2; at most 12 scalar string values, body size bounded to 8 KiB by ingress. Column names contract is lowercase ASCII identifiers; no requirement to execute user-defined accessors."
}
```

### Split

```json
"held_out"
```

## v2-ruby-vulnerable-06 — smtp-starttls-optional-peer-check

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `4fcf3ec347b417dd544600b53bcae8ded52d85c9eda6f36bbf3cb484dc060961`. Protocol-2.0 case hash: `99690455e9d77d0997a5a9a91fc1a2585cde595c845f990a2f6408b98c260dd4`.

Mandatory STARTTLS encrypts the transport but VERIFY_NONE disables certificate verification. A TLS impostor can capture the PLAIN authentication exchange and message.

### smtp_delivery.rb

```ruby
require 'net/smtp'
require 'openssl'

def deliver_receipt(message, recipient, password)
  raise ArgumentError, 'recipient' unless /\A[a-z0-9._+-]+@example\.org\z/.match?(recipient)
  context = OpenSSL::SSL::SSLContext.new
  context.verify_mode = OpenSSL::SSL::VERIFY_NONE
  smtp = Net::SMTP.new('smtp.example.org', 587)
  smtp.open_timeout = 3
  smtp.read_timeout = 3
  smtp.enable_starttls(context)
  smtp.start('app.example.org', 'receipt-sender', password, :plain) do |client|
    client.send_message(message, 'receipts@example.org', recipient)
  end
  :delivered
end
```

### Derivation

```json
{
  "group": "smtp-starttls-optional-peer-check",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An active network attacker must not impersonate SMTP and receive the authentication password or receipt. The operation is authenticate and send a receipt email through the configured smtp server using mandatory starttls.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "smtp_delivery.rb"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for authenticate and send a receipt email through the configured smtp server using mandatory starttls. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authenticate and send a receipt email through the configured SMTP server using mandatory STARTTLS.",
  "trust_boundary": "An active network attacker must not impersonate SMTP and receive the authentication password or receipt.",
  "legitimate_examples": [
    {
      "input": "A verified recipient, receipt MIME body and server-held password",
      "expected": "Send the receipt only after authenticating the legitimate SMTP TLS peer."
    }
  ],
  "permitted_changes": [
    "Use an SSLContext with set_params/default peer verification and hostname verification, retaining mandatory STARTTLS."
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
    "https://github.com/ruby/net-smtp/blob/v0.5.0/lib/net/smtp.rb"
  ]
}
```

### Regression traps

```json
[
  "Changing enable_starttls to opportunistic enable_starttls_auto weakens the transport further; preserve mandatory TLS and valid recipient handling."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use an SSLContext with set_params/default peer verification and hostname verification, retaining mandatory STARTTLS."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-ruby-vulnerable-06",
  "prior_case_id": "ruby-certificate-mode-vulnerable",
  "prior_source_sha256": "12be47ee79f654533d3581d88af074a9933fc5e3ca3646f86d7ae9ba48a7829b",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Ruby 3.3.6",
  "platform": "Linux x86_64",
  "setup": "net-smtp 0.5.0 and openssl 3.2.0; publicly trusted smtp.example.org certificate; message and password come from trusted receipt/secret code, recipient is already verified for the account."
}
```

### Split

```json
"held_out"
```

