# PKG-002 — player command interface foundation

**Status:** Initial application-layer implementation committed to `main`; automated validation pending.  
**Branch policy:** `main` is the only development branch. No feature branches or pull-request workflow.  
**Project:** Saltwater, an entirely fictional single-city police simulation.  
**Production database:** No Neon migration, seed, write, credential or configuration change is included or authorised by this package.

## Purpose

Turn the shared runtime kernel into a simple, text-first player entry point without adding account friction or pretending incomplete domain systems already exist.

## Implemented

- `runtime/player_interface.py`: game-native `PlayerProfile` value object and command router.
- Commands: `help`, `status`, `profile`, `start`, `pause`, `resume`, `quit`.
- Runtime lifecycle commands use the existing kernel and therefore preserve the player-presence gate and frozen-world-time rule.
- The profile explicitly distinguishes a player identity from a police-person identity and career. Missing officer/career records are shown as not assigned/not started, never fabricated.
- Unknown commands, malformed quoting and unexpected arguments fail clearly.
- `bingo` is not a general command and no hidden-truth endpoint is exposed by this interface.
- Unit tests cover command parsing, profile honesty, lifecycle transitions, bootstrap gate and pause/quit time freeze.
- GitHub Actions checks now run on pushes to `main` and include the player-interface tests.

## Deliberate limits

This is an application-layer foundation, not yet a complete playable game or persistent player save:

- The existing `InMemoryRuntimeStore` is test-only. It is not used as an authoritative save.
- No local JSON/SQLite side database is introduced; Neon remains the planned durable store.
- No player/officer/career row is created. BP-03, BP-06 and BP-07 authoritative persistence and approved domain rules must be connected before recruit creation.
- No simulation time advances automatically. A real game turn/command scheduler must be added with bounded, explicit world-tick semantics.
- No external identity provider, real-world identity checks or unnecessary login ceremony is introduced.
- A future durable player-session adapter must be implemented against the approved Neon architecture and tested on disposable PostgreSQL before any production deployment.

## Acceptance checks

| ID | Requirement | Status |
|---|---|---|
| P2-01 | Command router accepts only known commands | Implemented; CI pending |
| P2-02 | Player profile is distinct from officer/personnel identity | Implemented; CI pending |
| P2-03 | No fictional officer/career is invented when absent | Implemented; CI pending |
| P2-04 | Start obeys existing bootstrap/player-presence gate | Implemented; CI pending |
| P2-05 | Pause and quit freeze world activity | Implemented; CI pending |
| P2-06 | Hidden truth is not exposed through general commands | Implemented; CI pending |
| P2-07 | Durable player/career persistence | Not implemented |
| P2-08 | End-to-end Neon runtime connection | Not implemented; production writes remain gated |
| P2-09 | Actual recruit creation through BP-06/BP-07 | Not implemented |

## Next dependency

Complete the canonical BP-03 person, BP-06 personnel and BP-07 career persistence contracts, then implement their adapters and acceptance tests against disposable PostgreSQL. Only after that should a recruit-start flow be enabled. Preserve compact-storage measurement and the explicit Neon write-approval gate.
