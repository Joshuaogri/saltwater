# Saltwater coding instructions

Follow the repository-wide rules in [AGENTS.md](../../AGENTS.md) before making changes.

Additional requirements:
- Work on the active blueprint only; identify its BP number and title.
- Keep all development on `main` only. Do not create branches or pull requests.
- Saltwater is entirely fictional and single-player. Preserve approved canon and existing architecture.
- ChatGPT coordinates implementation; Gemini independently reviews. Compare findings rather than blindly accepting generated code.
- Never expose secrets or send production Neon credentials to AI services.
- Do not perform production Neon writes, migrations, seeds, imports or permission changes. Use disposable PostgreSQL for testing.
- Inspect existing code and tests first; make the smallest complete fix and add focused regression coverage.
- Preserve identity, provenance, audit, idempotency, transaction and authorization safeguards. Never weaken tests or constraints.
- State only tests and checks that were actually run.
