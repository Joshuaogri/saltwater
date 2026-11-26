# BP11 Dispatch Board

**Status:** First read-only dispatcher board implemented on `main`  
**Dependencies:** BP08 unit readiness; BP12 incident master  
**Production Neon:** unchanged

## Delivered

`runtime/bp11_dispatch_board.py` provides an officer-only dispatch board over the existing canonical records.

- `incident_queue` returns a bounded, priority-ordered queue of non-terminal BP12 incidents.
- `unit_readiness` reads the BP08 `sw_police.unit_readiness` projection and its unit capability catalogue.
- `snapshot` composes both views for a dispatcher console.

Every read requires a dedicated BP11 permission and is audited by the shared authorization service. Player principals cannot use the officer board. Database errors fail closed as service errors; no incident or unit records are mutated.

## Readiness is not assumed

The BP08 readiness projection currently distinguishes staffing eligibility from dispatch eligibility. Its present `dispatch_eligible` value remains false while BP09 resource readiness is not integrated. The board preserves the authoritative readiness reason (currently `resource_readiness_not_integrated`) instead of treating an available unit status and sufficient crew as proof that a vehicle, radio, equipment and other resources are ready.

Consequently this increment displays the live incident queue and unit readiness truth, but does not issue assignments or claim that a unit has been dispatched. That is an explicit separation of the board from BP08 deployment ownership and BP10 field execution, not a simulated success.

## Tests

`tests/pkg001/test_bp11_dispatch_board.py` covers canonical incident queue reads, BP08 readiness projection, combined snapshot, zero assignment side effects, default-deny access, principal-kind separation and bounded queue limits. It is included in the PKG-001 Python workflow.

## Next increment

Connect BP09 verified vehicle/device/resource readiness into BP08's dispatch eligibility projection, then implement the BP11 dispatch order lifecycle against BP08 deployment records. The board is already positioned to display those eligibility changes without inventing unit state.
