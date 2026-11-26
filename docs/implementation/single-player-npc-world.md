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
The current NPC workforce generator creates one stable NPC occupant per
authorised post, using the existing post identity, unit and position title.
NPC identity is distinct from player identity. Generation is deterministic for
a given seed and post catalogue, so repeated runs produce the same NPC roster.

The generator is an in-memory source adapter only. It does not silently create
people, personnel records, appointments, unit memberships or Neon writes.
A later persistence adapter can materialise this roster into the game's
authoritative records. NPC staffing is fictional game state; real-world
employment, legal and compliance processes are not gameplay prerequisites.

## Design principles

- One human player; no NPC player accounts.
- NPCs are autonomous world actors with identities and roles.
- Use existing authorised posts; do not expand the property or building world.
- Prefer game-state outcomes and believable simulation over real-world
  procedural gates.
- Keep production database writes separate from source development.
