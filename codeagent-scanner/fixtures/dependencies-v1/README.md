# Offline dependency release fixtures

The small lockfile examples originate from Aqua Security Trivy commit
`e1fd17a0ea4a8cf24bc4b4dd7e2cfbf4bb31b994` (v0.74.0), under Apache-2.0.
`sources.json` records direct URLs; `UPSTREAM-LICENSE` retains the upstream license.
They are input data only; no fixture is installed or executed.

Modifications for the CodeAgent release gate:

- The requirements sample pins its previously ranged MarkupSafe dependency.
- The Cargo sample includes openssl 0.10.30 to exercise a known advisory.
- `patched` variants replace the selected affected version with a fixed version.
  These are parser/advisory test inputs, not proposed dependency upgrades or
  resolvable application dependency graphs. Checksums are intentionally not used
  to install these fixtures.
- `expected.json` identifies one advisory/package pair per supported format.
  Tests require that pair in the vulnerable input and its absence in the patched
  input. Other packages/advisories may remain; the fixture is not a claim that the
  entire dependency graph is safe.
- The npm-shrinkwrap mirror illustrates a recognized but unsupported input for
  this pinned engine; it must be reported as incomplete, as must binary bun.lockb.

The release test scans all 40 supported files in one nested mixed monorepo using
the real offline Trivy engine and provisioned database. The gate also tests
malformed lockfiles and asserts that every advertised lock pattern has a fixture.
All twenty formats span eleven package ecosystems. No package-manager restore,
network resolution, application build, or source execution is permitted.
