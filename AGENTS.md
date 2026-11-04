# Working in this repository

Preserve the established architecture and testing conventions. A working alternative is not
automatically an appropriate change. Treat maintainer review feedback as a constraint on the
implementation, not merely a request to make the tests pass.

## Read the relevant implementation before editing

- Inspect the nearest existing public method, model converter, test, TestObject and fixture.
  Use those as the template for the change.
- For API work, read `thermoworks_cloud/client.py`, the relevant files in `models/`,
  `tests/test_client.py`, `tests/client_test_object.py` and `tests/client_test_data.py`.
- For Firebase behavior, consult `thermoworks_cloud/core.py`,
  `thermoworks_cloud/auth.py`, `tests/core_test_object.py` and `tests/test_data.py`.
  Consult this code for established patterns without rewriting it as
  part of unrelated API work.
- Read the current PR diff and all relevant review comments, including pending reviews.
  GitHub's ordinary PR comments endpoint does not include pending review comments; inspect
  the review-specific comments endpoint as well.
- If an existing pattern cannot satisfy the requested behavior, explain the concrete
  incompatibility before introducing a replacement. Do not redesign for hypothetical needs.

## Client and model boundaries

- Keep the request → response → JSON → model-converter pattern:
  request methods return an aiohttp response; public methods use `response.ok`,
  `await response.json()` and the relevant model converter.
- Keep special protocol behavior, such as bodyless 304 responses, explicit. Use the
  established `HTTPStatus` constants and error-building conventions in the API client.
  Do not replace the response boundary with positional status/header/payload tuples.
- Keep JSON-to-model conversion beside the corresponding model, following the existing
  `_json_to_device`, `_json_to_device_channel` and `_json_to_account` pattern.
  Do not introduce a snapshot abstraction or a parallel model hierarchy for transport data.
- Use the existing dataclasses as the public abstraction and TypedDicts for API response
  shapes. Public return values need meaningful types; avoid anonymous dictionaries or
  `Any` where a model exists. Explicit raw-response diagnostics methods are an exception.
- Preserve optional fields, additional properties, public names and existing conversions.
  Document non-obvious mappings and missing information; do not invent values or equivalence
  between differently named fields.
- Keep provider-specific endpoints configurable. The caller supplies the API base URL.
- Catch exceptions justified by the operation that can raise them. Do not surround a mapping
  loop with a growing list of exceptions to hide invalid shapes or programming mistakes.
- Distinguish observed payload behavior from documented guarantees. A single capture does
  not establish a universal relationship, such as disconnected implying paused.

## Compatibility and scope

- Make the smallest change that addresses the current request. Keep unrelated fixes,
  refactors, releases and companion Home Assistant changes out of the PR.
- API work does not authorize changes to Firebase-specific converters, metadata or tests.
- Current maintainer decision: `Fan.state` remains `Optional[int]`, with unchanged parsing.
  `FanState` provides named integer comparison values only. Do not normalize returned states
  to enum instances or widen the field type until that change is explicitly requested.
- Preserve unknown state codes and existing numeric comparisons.
- Preserve user edits and the existing code's style. Do not reformat unrelated code.

## Tests: TestObjects, fixtures and expected values

- Test through public application interfaces. Reuse existing interface tests and assertions
  wherever the behavior is shared; change the transport setup rather than weakening contracts.
- HTTP request expectations belong in TestObjects, including paths, headers and authentication.
  Extend `ClientTestObject`, `CoreTestObject` or `AuthTestObject` as appropriate.
- Response payloads and payload-building helpers belong in `client_test_data.py` or
  `test_data.py`, not in test classes. Follow existing fixture-building helpers.
- Mapping assertions use known values from the named source fixture. Do not replace these
  references with duplicated strings, timestamps, IDs or numbers in assertions:

  ```python
  expected_fan = GET_DEVICES_API_RFX_GATEWAY_RESPONSE["devices"][0]["fan"]
  assert expected_fan is not None
  assert device.fan is not None
  assert device.fan.set_temp == expected_fan["setTemp"]
  assert device.fan.state == FanState.BLOWING
  ```

- Use named enums for known domain states. Keep explicit semantic checks such as nullness
  and connection booleans where they express the tested contract. Do not confuse fixture-backed
  mapping expectations with hard-coding every expected result.
- Use contributed captures to inform small, representative fixtures. Retain provenance and
  explain deliberate reductions or synthetic edge cases. Do not copy entire accounts or
  thousands of repeated capture lines into the tests.
- Vary independent behaviors independently. Meat-probe channels do not need to be tested
  against every Billows state or every probe owned by a contributor. Connection state and
  operating state must not be coupled merely because one capture contains that combination.
- Do not assert incidental account topology, device order or contributor-specific counts
  unless that is the actual interface contract being tested.
- Do not add lint suppressions just to accommodate unnecessarily large fixtures.

## Review, verification and handoff

- Compare each requested change with the actual diff before claiming it is addressed.
  Check the maintainer's intended pattern as well as the runtime behavior.
- When a review comment asks why, answer the question with the actual rationale and evidence
  in the conversation. Distinguish observed facts, assumptions and tradeoffs. Do not substitute
  a code change or a passing test count for the requested explanation.
- Run the relevant tests and required checks. For library code, use the configured library
  environment, for example `.venv/bin/python -m pytest -q`, and the repository's pylint
  configuration. Check types when changing annotated code and report the actual scope checked.
  Companion HA tests belong in its devcontainer environment, not an unconfigured host Python.
- Run `git diff --check`. Separate pre-existing failures from regressions; do not fix unrelated
  code or suppress diagnostics without explaining what was excluded.
- A passing suite does not demonstrate architectural consistency, capture authenticity,
  complete device coverage or a successful HA deployment. Report only what was verified.
- Do not expose credentials from `.secrets`, environment files, HAR captures or diagnostics.
  Keep fixture identifiers synthetic and do not commit private captures.
- Preserve the user's PR title and description. Do not edit either, resolve review threads
  or post replies on the user's behalf unless explicitly asked.
- Keep PRs focused and proceed one at a time when requested. Creating or updating a PR does
  not authorize merging it, publishing a package or deploying to Home Assistant.
