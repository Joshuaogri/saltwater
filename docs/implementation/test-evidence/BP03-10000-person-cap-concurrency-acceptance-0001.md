# BP03 10,000-person population cap and concurrent admission acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46042030165)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** 5e287d5a632fdb2d571243297723a2c0742217c5

## Result

- Disposable fixture reached 9,999 living countable people.
- Two concurrent final-slot admissions were attempted.
- Exactly one admission succeeded; the other was rejected by the shared population-cap guard.
- Final reconciliation: 10,000 canonical people, 10,000 included living people, 10,000 persisted simulation tier states, 10,000 tier-history rows and population counter 10,000.
- The database emitted the expected population-cap exceeded error for the rejected transaction.
- The full disposable database measured **37,592,087 bytes** after the 10,000-person fixture. This includes the test foundation, name registry, canonical people, population histories, simulation tier state and test event records; it is not a Neon production storage estimate.
- The isolated proposal 0036 schema-only growth measured **139,264 bytes**.

## Largest BP03 relation sizes in the 10,000-person fixture

| Relation | Total bytes |
|---|---:|
| person | 2,424,832 |
| person_simulation_history | 1,859,584 |
| profile_history | 1,540,096 |
| person_simulation_state | 1,130,496 |
| population_qualification_history | 1,097,728 |
| population_history | 1,024,000 |
| population_state | 876,544 |
| population_counter | 409,600 |

Additional recorded relations: person_routine 98,304 bytes; person_attribute_claim 90,112 bytes; person_knowledge_item 81,920 bytes; person_movement_event 81,920 bytes; person_relevance_promotion 49,152 bytes; residence 24,576 bytes.

## Fixture timings

- Person-created events: 241.48 ms
- 9,999 people and name registry: 184,821.57 ms
- Population-state events: 245.28 ms
- Population-state and qualification history: 1,942.38 ms
- Final reconciliation: 2.12 ms

## Scope

This proves the current BP03 union counter and concurrent final-slot protection at the full 10,000-person boundary, with tier-state initialization for every canonical person. All records existed only in disposable PostgreSQL and were destroyed with the test environment. No production Neon migration or population seed was performed.
