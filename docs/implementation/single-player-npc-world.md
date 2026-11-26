# Saltwater single-player NPC world

Saltwater is a single-player game. There is one human player; every other person
in the world is a non-player character (NPC). Police officers, commanders,
dispatchers, residents, business owners, public officials, witnesses and
suspects are all NPCs unless explicitly identified as the player's character.

NPCs are game actors, not separate player accounts. They can be generated,
assigned work, given routines and allowed to act autonomously. The player
interacts with the world through their own character and game commands; the
player does not administer every NPC individually.

## Police workforce foundation

The BP05 organisational establishment contains 500 authorised police posts.
The NPC workforce generator creates one stable NPC occupant per authorised
post on each of four shifts, using the existing post identity, unit and position
title. The 500-post establishment therefore yields 2,000 shift occupants.
NPC identity is distinct from player identity. Generation is deterministic for
a given seed and post catalogue, so repeated runs produce the same NPC roster.

The generator is an in-memory source adapter only. It preserves each post's
sworn, civilian or mixed position category, and allocates NPCs to four rotating
shift groups. Only the current shift is counted as available; off-duty NPCs
remain part of the roster without being treated as ready for dispatch. It does
not silently create people, personnel records, appointments, unit memberships
or Neon writes.
The NPC dispatch simulator now selects an available unit for an incident,
automatically assembles an available same-shift crew, identifies a crew lead,
and tracks the unit and officers through responding, on-scene, busy, returning
and available states. Specialist-domain matches are preferred; general patrol
can cover general response. Repeated assignment of the same incident returns
the existing deployment rather than duplicating it. Shift rotation moves
available NPCs on and off duty while leaving already deployed crews in their
current operational state.

A player-facing command console is now connected to this simulator. The player
can use `dispatch`, `dispatch assign <incident-id>`, and deployment progress
commands such as `dispatch arrive <deployment-id>`; no officer UUIDs,
membership IDs or individual NPC administration are required.

This dispatch layer is an in-memory gameplay simulator, not yet a persistent
PostgreSQL workforce or a full autonomous world scheduler. It proves the
player-facing game rule: no personnel UUIDs, separate NPC accounts or manual
staff-by-staff assignments are needed to create a response. A read-only PostgreSQL integration test now exercises the actual 500-post
BP05 establishment and BP08 dispatchable unit profiles in disposable CI. A
later persistence adapter can materialise this roster into authoritative game records. NPC
staffing is fictional game state; real-world employment, legal and compliance
processes are not gameplay prerequisites.

## Design principles

- One human player; no NPC player accounts.
- NPCs are autonomous world actors with identities and roles.
- Use existing authorised posts; do not expand the property or building world.
- Prefer game-state outcomes and believable simulation over real-world
  procedural gates.
- Keep production database writes separate from source development.
