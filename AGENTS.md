# Repository conventions

- Before editing, read comparable implementations and their tests, helpers and data.
  Identify the established abstractions, responsibilities, naming, typing and style.
- Extend those conventions rather than introducing a parallel approach. Explain any
  necessary departure in terms of the requested behavior, not personal preference.
- Preserve public contracts and keep changes within the requested scope. Do not use
  shared code as an opportunity to change unrelated behavior or reformat user work.
- Follow the existing test organization and assertion patterns. Test interface behavior
  with representative data; avoid coupling tests to implementation or incidental examples.
- Read review feedback in context, including pending comments. Apply the underlying
  principle consistently rather than turning each correction into a special-case rule.
- Before claiming completion, compare the diff with the request and established patterns.
  Run the relevant checks in the project's configured environment. Passing tests alone
  do not demonstrate that a change follows the intended design.
- Explain decisions when asked, distinguish evidence from assumptions, and report what
  was actually verified.
- Keep credentials and private captures out of logs and commits.
- Do not alter existing PR titles/descriptions, resolve threads, post replies, merge,
  publish or deploy without explicit authorization.
