# Historical scanner tests

These tests describe the retired CAMEL bridge, enum-based model settings, and the
original in-process API. They are preserved for research reproduction, not imported
by the production test suite. Several old tests accepted submission failures as
success or only checked a missing report.

The active tests in `codeagent-scanner/tests` exercise the durable runtime, strict
API contracts, safe source acquisition, real analyzer fixtures, and provider-neutral
review workflow. Root `pytest.ini` deliberately excludes historical scripts that
make network requests or write datasets when imported.
