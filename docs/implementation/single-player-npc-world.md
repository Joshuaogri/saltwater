# Saltwater single-player NPC world

Saltwater is a single-player game. There is one human player; every other person
in the world is an NPC. Police officers, commanders, dispatchers, residents,
business owners, public officials, witnesses and suspects are NPCs unless
explicitly identified as the player's character.

NPCs are world actors, not separate player accounts. They should act
autonomously according to their roles, knowledge, schedules, capabilities and
world conditions. The player interacts with the world through their own
character and game commands; the player does not administer every NPC
individually.

## Police workforce foundation

BP05 defines 500 authorised police posts. An authorised post is a position,
not proof that a person occupies it. The opening disposable BP05/BP07/BP08
establishment currently has 500 vacant posts, zero active career post
appointments and zero active unit memberships. The unit catalogue has seven
dispatchable unit profiles, but BP08 correctly marks every unit unavailable
until staffing and an explicit status transition exist.

The 9,500-person SW-DB-001 opening population includes a 500-person
POLICE_SUBSET cohort. Those are canonical people in the population fixture,
not additional NPCs to be generated from the 500 vacancies. The current
disposable fixture does not yet link that full cohort to BP06 personnel service
records. This is an explicit BP03/BP06 integration gap. Do not create duplicate
people, personnel records, appointments or unit memberships to make dispatch
appear available.

## Canonical production NPC source

The production PostgresNPCDispatchFactory loads existing active personnel from
sw_police.personnel and personnel_service_current, joins the canonical person
profile, and reads only active primary unit memberships and their current
career post appointments. It excludes the person bound to the human player's
identity. Personnel without an active unit/post membership remain unassigned;
recruits, leave/suspended personnel and civilian-only roles cannot be used as
patrol crew.

The factory reads BP08's current unit status as authoritative. A unit with no
status event remains unavailable; the factory never silently upgrades it to
available. Vacant posts are not treated as people. The adapter issues SELECT
statements only and does not create personnel, appointments, memberships,
deployments or events.

## Synthetic workforce helper

NPCWorkforceGenerator.generate() and generate_shift_roster() are synthetic
in-memory helpers for tests and sandbox scenarios. They can create one
deterministic NPC per supplied post and distribute those synthetic test actors
across Alpha, Bravo, Charlie and Delta. They are not the production source of
police personnel. Production uses the canonical personnel adapter above.

NPCWorkforceGenerator.assign_shift_groups() is also used to distribute existing
personnel identities across the four shifts without changing or multiplying
those identities. Unassigned personnel are retained as unassigned NPC actors,
not treated as dispatch-ready crew.

## NPC dispatch gameplay

NPCDispatchSimulator can choose a suitable unit, assemble a same-shift crew,
identify a crew lead and track a deployment through responding, on-scene,
busy, returning and available states when actual personnel memberships and
unit readiness support it. Specialist-domain matches are preferred; general
patrol can cover general response. Repeated assignment of the same incident
returns the existing deployment rather than duplicating it.

The player-facing command console supports `dispatch`,
`dispatch assign <incident-id>` and deployment progress commands such as
`dispatch arrive <deployment-id>`. No officer UUIDs, membership IDs or
individual NPC administration are required. In the current canonical opening
fixture, no post is staffed and no unit is available, so the command correctly
does not fabricate a response. The in-memory simulator and unit tests prove
the assignment path when suitable staffed/available units are supplied.

## Scheduling and persistence status

The recurring NPC dispatch schedule helper is connected to BP37's tick
scheduler, but the actual game-session host still needs to register it when
composing the NPC world and continue running the shared scheduler. NPC
deployment/crew state is still in-memory and does not yet survive restart.
These are outstanding implementation tasks, not completed capabilities.

## Design principles

- One human player; no NPC player accounts.
- NPCs are autonomous world actors with persistent identities and roles.
- Never create people or appointments merely because an authorised post exists.
- Dispatch only personnel with actual active membership and an available unit.
- Use game-state outcomes and believable simulation, not real-world compliance
  gates.
- Keep production database writes separate from source development.
