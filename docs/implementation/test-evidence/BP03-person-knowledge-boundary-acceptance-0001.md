# BP03 person knowledge boundary acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46039675633)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** `e909011b2402da69dcc7452321b7ba10a587a295`

## Implemented

- A person can acquire a sourced knowledge item linked to a canonical simulation event.
- Each item records the recipient, optional source person, information reference, knowledge kind (observed, received or inferred), acquisition tick, recorded tick, confidence, source, actor and reason.
- A person cannot acquire knowledge before the referenced source event occurs or after the current simulation tick.
- Knowledge is recorded as a reference to an information item/event, not a copy of hidden global truth.
- Knowledge history is append-only; corrections or later acquisitions require new sourced records.
- The summary projection reports item count and latest acquisition tick.
- Command execution is restricted to the game command role; read access is through the game read-only role.

## Acceptance exercised

- Create distinct canonical recipient and source people.
- Reference the source person's canonical creation event.
- Record a received knowledge item with source person, acquisition tick and confidence.
- Replay the same source reference and verify no duplicate.
- Verify all provenance and epistemic fields are retained.
- Verify the summary projection reconciles.
- Attempt to mutate a knowledge item and verify rejection.
- Entire fixture transaction rolled back; no persistent game population was created.

## Scope boundary

This is a knowledge-provenance boundary, not a complete NPC reasoning or dialogue engine. It does not itself determine whether an observation is true, infer guilt, or grant player access to private knowledge. BP-21, BP-35 and BP-42 retain their respective intelligence, event-execution and permission responsibilities. No Neon production migration or population seed was performed.
