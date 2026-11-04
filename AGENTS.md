# Repository conventions

- Read the nearest implementation, model converter, test, TestObject and fixture before editing.
  Follow their patterns; explain any necessary departure before implementing it.
- Preserve request → aiohttp response → `response.ok` → `await response.json()` → model converter.
  Keep converters beside their models, typed public models, and configurable provider URLs.
- Preserve existing contracts and optional/additional fields. Document non-obvious mappings;
  distinguish captured behavior from guarantees. Catch only errors justified by the operation.
- API work must not change Firebase-specific behavior. `Fan.state` remains `Optional[int]`;
  `FanState` is for comparison only until the maintainer requests otherwise.
- Test public interfaces using the existing TestObjects for HTTP expectations.
  Keep payloads and builders in `tests/client_test_data.py` or `tests/test_data.py`.
- Compare mapped values against named fixtures, not duplicated literals in assertions.
  Use enums for known states and explicit checks for semantic invariants such as nullness.
- Reduce captures to representative fixtures with provenance. Test independent behaviors
  independently; avoid contributor-specific account layouts and unnecessary combinations.
- Keep changes focused. Preserve user edits and local style; avoid unrelated refactors.
- Read all review comments, including pending reviews. Answer rationale questions directly.
  Check the actual diff against each request before claiming it is addressed.
- Run relevant tests, lint, type checks and `git diff --check`; report their scope and failures.
  Use the configured library environment and the devcontainer for companion HA tests.
  Passing tests do not prove that a change follows the requested design.
- Keep credentials and private captures out of logs and commits.
- Do not alter existing PR titles/descriptions, resolve threads, post replies, merge,
  publish or deploy without explicit authorization.
