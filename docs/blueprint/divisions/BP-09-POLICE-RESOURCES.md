# BP-09 — Police Resources

**Project:** Saltwater, fictional sovereign city-state; one city and one jurisdiction  
**Blueprint division:** BP-09 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test:** NOT_STARTED | **Verification:** NOT_STARTED

## 1. Purpose

Define the complete resource lifecycle supporting the Saltwater Police Service: resource categories and catalogue, acquisition, ownership/custody, inventory, allocation, assignment, reservation, issue, return, maintenance, inspection, repair, calibration, replenishment, loss, damage, write-off, disposal, retirement, facilities, vehicles, communications and computing assets, consumables, specialist equipment, resource availability, readiness, cost interfaces and audit.

BP-09 ensures that units and officers can use only resources that actually exist, are serviceable, are appropriately allocated, and are authorised for their task. It must distinguish a resource that is owned, present, allocated, issued, reserved, available, serviceable, operationally fit, accessible and authorised for use. These are not interchangeable states.

The resource model supports a detailed police simulation while keeping non-police society at the level needed to support policing. Saltwater remains one fictional sovereign city-state and one jurisdiction.

## 2. Scope and boundaries

### In scope
- Resource taxonomy, catalogue, identifiers and specifications.
- Physical and digital police assets and service resources.
- Procurement receipt, acceptance, ownership, custody and inventory.
- Locations, stores, lockers, depots, facilities and asset registers.
- Allocation to units, personnel, vehicles, facilities, incidents and tasks.
- Issue, return, transfer, reservation, loan and temporary custody.
- Availability, serviceability, readiness, compatibility and authorisation.
- Vehicle fleet, maintenance, inspection, defect and roadworthiness state.
- Equipment inspection, repair, calibration, testing and lifecycle.
- Communications devices, networks, radio equipment and operational IT assets.
- Protective and specialist equipment, evidence-processing equipment and controlled stores.
- Consumables, stock levels, expiry, replenishment and shortages.
- Facilities and physical infrastructure used by police.
- Loss, theft, damage, contamination, quarantine, write-off and disposal.
- Asset history, audit, utilisation and resource reporting.
- Resource-related cost and procurement interfaces.

### Ownership boundaries

| Concern | Owner | BP-09 responsibility |
|---|---|---|
| Police institutional structure and resource policy | BP-05/BP-30 | Consume approved mandate and policy |
| Unit membership and deployment demand | BP-08 | Allocate resources to authorised units/tasks |
| Patrol and field execution | BP-10 | Supply truthful resource state and assignments |
| Dispatch and communications workflow | BP-11 | Supply device/network capability and availability |
| Incident command and task priorities | BP-12 | Receive authorised resource requests and allocations |
| Crime scenes/evidence custody | BP-22/BP-23 | Provide equipment; never take evidential custody ownership |
| Forensic examination and calibration requirements | BP-24 | Maintain equipment/service records and calibration status |
| Custody facilities and detainee operations | BP-26 | Maintain facility/asset references; custody owns detainee process |
| Training and qualifications | BP-32 | Consume verified qualification; record equipment training assets only |
| HR and employee identity | BP-06/BP-33 | Reference personnel; no employee master data |
| Finance, procurement, budgets and payment | BP-34 | Consume approvals and costs; do not own ledger/payment |
| Geography, buildings and property | BP-02/BP-04 | Reference canonical locations/property |
| Time, shifts and simulation clock | BP-37 | Use time authority for reservations and maintenance schedules |
| Records, persistence and recovery | BP-38/BP-39 | Persist canonical asset and event records |
| Access and confidentiality | BP-42 | Enforce access and controlled-resource permissions |

BP-09 owns police resource records and their operational lifecycle. It does not own the public road network, city utilities, building ownership, employee identity, finance ledger, dispatch, incident command or evidence chain of custody.

## 3. Governing invariants

1. Every managed resource has a stable unique ID and a defined category, lifecycle state, authoritative owner/custodian and provenance.
2. A catalogue model/specification is distinct from an individual physical asset, stock lot, licence, facility, service contract or consumable quantity.
3. Ownership, custody, location, allocation, reservation, issue and operational availability are distinct relationships.
4. A resource cannot be simultaneously allocated or issued in incompatible ways unless a resource type explicitly supports shared/pooled use.
5. No unit/person may use a resource unless the resource is available, fit for purpose, within inspection/calibration/expiry, compatible, accessible and authorised for that user/task.
6. A resource's existence does not imply serviceability or readiness. Unknown/stale state is never treated as fit.
7. All movements and state changes are attributable, effective-dated, auditable and idempotent.
8. Inventory quantities cannot become negative. Serialized assets cannot be in two physical locations or assigned to two incompatible custodians at once.
9. Resource issue/return and transfer preserve custody continuity. Unresolved custody discrepancies are visible exceptions, not silently reconciled.
10. Maintenance, repair, calibration and inspection may remove an asset from availability; they cannot be bypassed by a dispatch or player command.
11. A vehicle is not dispatchable merely because it exists or is assigned to a unit; required serviceability, inspection, crew, fuel/charge and legal/operational restrictions must be met.
12. A resource request does not guarantee allocation. Shortages and conflicts must be represented truthfully.
13. Resource records never create additional living people. Police personnel remain within the hard 10,000 living-person cap.
14. Saltwater is one city-state and one jurisdiction. Police assets and facilities cannot establish another playable city or external policing jurisdiction.
15. No simulation time advances while the player is absent. Time-based reservations, leases, maintenance intervals, expiry and service schedules freeze with the simulation clock.
16. Historical facts are append-preserving. Corrections supersede or amend with provenance; they do not erase.
17. Player and NPC resource access follows the same compatibility, custody and authorisation rules.
18. Confidential assignments, specialist capability and protected locations are not exposed to unauthorised users.
19. No database write, procurement, migration, seed or bulk asset creation is authorised merely by this design document.
20. Fixed BP-01–BP-44 structure remains unchanged.

## 4. Resource taxonomy and catalogue

### 4.1 Catalogue model

A resource model describes a class/specification. Fields:
- resource_model_id, category_id, model_name and description;
- manufacturer/vendor reference where applicable;
- technical specification and permitted configuration;
- compatible accessories, consumables, vehicles, systems and facilities;
- intended functions and prohibited uses;
- operating conditions and environmental limits;
- inspection, maintenance, calibration and replacement requirements;
- training/qualification and user eligibility requirements;
- security/sensitivity classification;
- expected lifecycle and end-of-life criteria;
- policy/schema version and provenance.

The catalogue is versioned. A specification update does not silently change the recorded characteristics of historical assets; each asset references the applicable model/specification version.

### 4.2 Individual asset

Serialized asset fields:
- asset_id, resource_model_id and serial/registration/asset tag;
- acquisition/receipt and acceptance references;
- owner organisation and accountable custodian;
- current location and location history;
- lifecycle, serviceability and availability states;
- allocation, reservation and issue relationships;
- condition, inspection, maintenance and calibration status;
- warranty, service contract and replacement information;
- sensitivity/access class;
- acquisition cost reference (finance-owned);
- record version, provenance and audit timestamps.

Unique serial/registration values are enforced within their appropriate namespace. Where no manufacturer serial exists, an internal stable asset tag is assigned.

### 4.3 Non-serialized stock and consumables

Stock items are managed by item/model and lot/batch where relevant. Fields include stock_item_id, lot_id, location, quantity_on_hand, quantity_reserved, quantity_issued, reorder threshold, expiry date, condition, supplier/receipt reference and unit of measure.

For lot-tracked items, issue/consumption records identify the lot. For non-lot items, quantity movements remain attributable. The system must not create an individual serial record for every low-value consumable unless the resource's risk or traceability policy requires it.

### 4.4 Digital and intangible resources

Support software licences, service subscriptions, data-service entitlements, communication channels, managed accounts, cryptographic/security tokens and other non-physical resources. Track entitlement, permitted user/device, scope, seat/quantity, start/end, renewal, access state, vendor/service dependency and revocation. Do not store credentials or secrets in ordinary asset fields.

### 4.5 Resource categories

The catalogue must support, at minimum:
- vehicles and vehicle accessories;
- personal issue equipment;
- protective clothing and safety equipment;
- communications devices and infrastructure;
- computers, mobile devices, printers, storage and network assets;
- office and administrative equipment;
- patrol and traffic equipment;
- scene management and evidence-handling equipment;
- forensic and specialist examination equipment;
- custody and interview-room equipment;
- facilities, rooms, fixtures and controlled access systems;
- stores, consumables and replenishment stock;
- training equipment and simulation aids;
- software licences, data services and subscriptions;
- specialist or restricted equipment governed by dedicated authorisation;
- outsourced services, maintenance contracts and support entitlements.

Categories are extensible through BP-44 change control. A category does not itself grant operational authority.

## 5. Resource lifecycle and state model

### 5.1 Lifecycle states

A serialized asset may progress through:
- proposed/requested;
- approved for acquisition;
- ordered;
- received;
- acceptance pending;
- accepted/registered;
- in store;
- available;
- reserved;
- allocated;
- issued/in use;
- returned;
- under inspection;
- under maintenance/repair/calibration;
- quarantined;
- restricted/limited use;
- lost/stolen;
- damaged;
- written off;
- disposed/retired.

These are not necessarily one flat enum. Lifecycle, custody, serviceability, allocation and availability are orthogonal state dimensions where needed. For example, an asset can be allocated to a unit but temporarily unserviceable; a vehicle can be in maintenance and still owned by the police.

### 5.2 State transitions

Each transition requires:
- resource and current version;
- source and resulting state;
- actor and authority;
- effective simulation time;
- reason and supporting evidence/reference;
- location/custody change if relevant;
- policy and schema version;
- idempotency key.

Invalid transitions are rejected without partial side effects. A returned asset is not automatically serviceable; inspection may be required. A repaired asset is not available until the required acceptance/return-to-service check passes.

### 5.3 Availability calculation

Effective availability is derived from:
- lifecycle and serviceability;
- current location and access;
- allocation/issue/reservation conflicts;
- inspection/calibration/expiry;
- compatibility with requested task;
- user eligibility and authorisation;
- operational restrictions;
- maintenance windows and resource dependencies.

Expose both the result and reason codes: available, unavailable, reserved, allocated, issued, unserviceable, restricted, expired, missing, unknown/stale or awaiting inspection. Do not compress distinct causes into one opaque boolean.

## 6. Procurement, receipt and acceptance

BP-34 owns procurement authority, budgets, purchase orders, invoices and payment. BP-09 consumes approved procurement/contract references and manages physical/digital receipt.

Receipt workflow:
1. approved purchase/contract or authorised transfer exists;
2. supplier/donor/transferor and expected quantity/specification are identified;
3. receipt is recorded against order/transfer;
4. quantity, identity, specification and condition are checked;
5. discrepancies, damage, short shipment or substitution are recorded;
6. safety/security/technical acceptance tests are completed where required;
7. asset IDs or stock lots are created;
8. ownership, custody and storage location are established;
9. warranties, service intervals and licence terms are registered;
10. finance and procurement systems receive receipt/acceptance outcomes.

Receipt is not acceptance. A damaged or incorrect item remains quarantined or discrepancy-pending until resolved. No payment status is inferred from receipt. Donations, transfers and recovered property require a documented authority and provenance; recovered evidence/property is not automatically police operational stock.

## 7. Inventory, custody and location

### 7.1 Location model

Each resource location references canonical BP-02/BP-04 geography/property: headquarters, station, unit room, secure store, garage, vehicle, locker, field assignment or approved temporary location. A location has access classification, responsible custodian and permitted resource categories.

### 7.2 Custody

Custody is a time-bounded accountability relationship, not necessarily ownership. Custodian may be a person, unit, store, facility or contracted service. Custody transfer requires releasing and receiving acknowledgement, or a documented controlled exception. For unattended pooled resources, the accountable unit/store custodian is recorded.

### 7.3 Inventory checks

Support scheduled and event-triggered counts, reconciliation, spot checks, cycle counts and full stocktakes. Compare expected and observed quantities/identities; record variance, investigator/resolver, reason, corrective transaction and approval. A count does not silently overwrite the ledger. Discrepancies remain open until resolved.

### 7.4 Location movement

Every movement records origin, destination, dispatch/receipt time, responsible parties, reason, transport/transfer reference and condition where applicable. A resource cannot be simultaneously located at two places. Temporary field location must be recorded with a return/closure expectation.

## 8. Allocation, reservation, issue and return

### 8.1 Allocation

Allocation associates a resource with a unit, person, vehicle, facility or function for a defined period. It does not necessarily transfer custody or ownership. Allocation checks establishment, eligibility, compatibility, availability, authorisation and competing demand.

### 8.2 Reservation

Reservation holds a resource for an approved future task/time interval. It must include requester, approving authority where required, purpose, resource/quantity, time window, priority, expiry and cancellation policy. A reservation does not mean the item has been issued or physically moved.

### 8.3 Issue and return

Issue records recipient, issuer, item/quantity/serial, condition, accessories, purpose, expected return, authorisation and acknowledgement. Return records actual time, recipient/issuer, condition, quantity, missing parts, use/consumption, cleaning/decontamination, inspection requirement and discrepancy.

A personal issue item may remain assigned across shifts under an explicit continuing-custody policy. Shared equipment must be checked in/out for each custody interval. No issue may bypass user training, qualification or restricted-item approval.

### 8.4 Loans and external custody

Loans to another Saltwater agency or contractor require an agreement/reference, scope, custodian, term, access restrictions, return condition and accountability. Loans do not transfer ownership. No external entity gains police authority by holding a police asset.

## 9. Vehicles and fleet management

### 9.1 Vehicle record

Vehicle fields include vehicle_asset_id, fleet number, registration, model/specification, vehicle type, ownership/lease reference, assigned unit, home base, current location, odometer/usage measure, fuel/charge state, condition, roadworthiness/inspection state, maintenance schedule, insurance/permit references where represented in game canon, fitted equipment, communications fit, access/security class and lifecycle.

### 9.2 Vehicle states and dispatchability

Distinguish stored, available, reserved, allocated, deployed, out of service, under repair, inspection due, restricted, damaged, recovered, retired and disposed. Dispatchability requires:
- serviceable vehicle and current required inspections;
- no blocking defect or restriction;
- suitable vehicle class for task;
- available authorised driver/operator;
- required crew and equipment;
- sufficient fuel/charge for planned use under configured policy;
- permitted location/access and operational availability.

BP-10/BP-11 consume dispatchability; they do not override it.

### 9.3 Defects and maintenance

Drivers/operators can report defects with time, vehicle, symptoms, severity, safe-to-use assessment and evidence. A safety-critical defect immediately blocks use pending authorised inspection. Non-critical defects may permit restricted operation only under explicit policy. Maintenance records diagnosis, work order, parts, technician/provider, labour, completion, quality check and return-to-service approval.

### 9.4 Fleet use and lifecycle

Track allocation, keys/access, authorised operators, journey/usage records where the simulation requires them, refuelling/charging, cleaning, collision/damage, recovery, towing, modification, recall, lease expiry and disposal. Historical registrations and assigned units remain preserved. Vehicle replacement does not rewrite past patrol or incident records.

## 10. Communications, computing and information technology assets

Manage radios, base stations, dispatch consoles, telephones, mobile data terminals, body-worn cameras, computers, tablets, printers, network devices, servers, storage and approved software/service entitlements as resources.

For each device/service track:
- unique asset or entitlement ID;
- assigned user/unit/location;
- hardware/software version and configuration baseline;
- operational state and last check-in/health report;
- permitted system/network access reference;
- battery/power and accessory state where applicable;
- maintenance, update, support and end-of-life;
- security classification and incident/quarantine state.

BP-11 owns call-taking, CAD and radio operational workflows; BP-42 owns identity/access/security policy; BP-38 owns records. BP-09 must not store passwords, private keys, authentication secrets or unrestricted evidence content in asset notes.

A device reported lost, stolen, compromised or unaccounted for triggers a security incident interface, access/session revocation where authorised, preservation of relevant audit logs and physical recovery workflow. Device status does not establish the truth of any recorded content.

## 11. Facilities, stores and infrastructure

Track police-controlled or police-used facilities and spaces: stations, headquarters, substations, garages, secure stores, interview rooms, custody spaces, training rooms, laboratories and temporary operational sites. BP-02/BP-04 remain authoritative for city geography, buildings and property ownership; BP-09 stores police-use, occupancy, fit-out, access, maintenance and readiness relationships.

Facility records include:
- facility-use ID and canonical property/building reference;
- owning/occupying organisation reference;
- room/space identifier and function;
- occupancy and access classification;
- capacity and safety constraints;
- critical utilities/service dependencies;
- security/access-control asset references;
- inspection, maintenance, fault and closure status;
- responsible manager/custodian;
- operational availability and restrictions.

A facility may be owned by another entity and used by police under lease, licence or service arrangement. BP-09 records the police operational use and agreement reference, not property title. A facility closure triggers relocation/continuity decisions for affected units and resources; it does not automatically create a replacement building.

## 12. Consumables, stock and replenishment

Maintain stock by item, lot, location, quantity and unit of measure. Track reorder thresholds, lead times, supplier/contract reference, expiry, storage conditions, issue, consumption, waste, damage and returns.

Stock calculations:
- on hand = accepted receipts + approved returns + transfers in − issues/consumption − transfers out − approved write-offs;
- available = on hand − reserved − quarantined − otherwise unavailable;
- on order is reported separately and never counted as physically available.

Prevent negative stock and double reservation. Lot-controlled or expiring items use configured first-expiry/first-out or other approved issue policy. Expired, contaminated or recalled stock is quarantined and cannot be issued. Replenishment requests go to BP-34; a request does not create stock or imply supplier fulfilment.

## 13. Inspection, maintenance, calibration and repair

### 13.1 Schedules

Schedules are defined by model, asset, usage, time, condition or manufacturer/service requirement. Track due date/usage, interval, responsible role/provider, inspection checklist version, last result and next due calculation. Time-based schedules use BP-37 simulation time; usage-based schedules advance only when authoritative usage events occur.

### 13.2 Work orders

Work order fields: work_order_id, asset/facility, work type, reported defect/request, priority, authoriser, assigned technician/provider, parts/consumables, start/end, findings, work performed, test results, costs reference, outstanding defects and acceptance/return-to-service decision.

### 13.3 Calibration and specialist equipment

Where an instrument requires calibration, record calibration standard/reference, procedure version, provider/technician, as-found/as-left result, tolerance, certificate/reference, date, expiry/next due and impact of out-of-tolerance result. An expired or failed calibration blocks uses requiring valid calibration. BP-24 owns forensic method and result interpretation; BP-09 owns equipment maintenance/calibration state.

### 13.4 Quarantine and safety

Quarantine prevents issue/use pending inspection, decontamination, security review or discrepancy resolution. Only an authorised role may release quarantine with evidence and reason. Contamination, biohazard or hazardous condition is recorded as a safety state without exposing sensitive case detail unnecessarily.

## 14. Loss, theft, damage, recall and disposal

Report loss/theft/damage promptly with asset, last known custodian/location, discovery time, circumstances, severity, immediate restrictions and related incident reference. Trigger appropriate supervisory, security, finance, insurance, HR or investigative workflows. Do not assume employee culpability from a missing asset.

A damaged asset is assessed; serviceability is blocked or restricted based on risk. Recalls apply to all affected model/serial/lot instances, including those allocated or in the field. Disposal requires authority, data sanitisation where applicable, removal of access credentials, environmental/safety handling, transfer/sale/destruction record and finance update. Retired/disposed assets remain in historical records and cannot re-enter service without a formal reacquisition/inspection process.

## 15. Resource requests, prioritisation and shortage management

A request records requester, requesting unit, task/incident reference, item/capability/quantity, required time/place, priority, justification, alternatives, approval and fulfilment state. Outcomes include fulfilled, partially fulfilled, queued, substituted with approval, rejected, cancelled or unavailable.

Prioritisation follows command/incident policy (BP-05/BP-12) and procurement/resource policy (BP-30/BP-34). BP-09 reports actual stock, capability, lead time and competing commitments. It must not fabricate equipment, silently substitute a materially different item, or mark a partial request complete. Shortages may constrain deployment/readiness and must propagate to BP-08/BP-10/BP-11.

## 16. Inputs, outputs and event contracts

### Inputs
- BP-02/BP-04: canonical places, buildings, property and occupancy/agreement references.
- BP-05/BP-30: resource policy, authority and organisational structure.
- BP-06/BP-07/BP-08: personnel eligibility, unit membership, deployment and demand.
- BP-10/BP-11/BP-12: patrol, dispatch and incident requests/status.
- BP-22/BP-23/BP-24/BP-26: specialist/evidence/custody facility requirements and equipment status.
- BP-32: training/qualification outcomes.
- BP-34: approved procurement, contracts, budgets, cost and disposal transactions.
- BP-37: simulation time, usage intervals, schedules and pause.
- BP-42: permissions, security events and access revocation instructions.

### Outputs
- resource catalogue and asset/stock/entitlement register;
- custody, location, allocation, reservation, issue and movement history;
- availability/serviceability/readiness status with reason codes;
- vehicle dispatchability and fleet status;
- facility use/readiness and maintenance status;
- stock levels, shortages, expiry and replenishment demand;
- maintenance, inspection, calibration, repair and defect events;
- loss/damage/recall/disposal events;
- resource request fulfilment and constraints;
- auditable cost/procurement interfaces and operational notifications.

### Event envelope
Every event includes event ID, event type, subject ID, source, schema version, effective simulation time, recorded time, actor/authority, reason, prior/resulting version, idempotency key, provenance and visibility. Asset movements and state changes must be transactionally consistent within the owning store or use an outbox/inbox pattern across service boundaries. Replayed events cannot double-issue, double-consume or duplicate receipts.

## 17. Permissions and information boundaries

BP-42 controls access. Roles may include asset custodian, storekeeper, fleet manager, maintenance officer, procurement/finance reader, unit commander, operational supervisor, authorised user, security administrator and auditor. Permissions are scoped by resource category, location, unit, action and sensitivity.

- Read catalogue does not imply permission to view restricted asset locations.
- View allocation does not imply authority to issue or transfer.
- Issue authority does not imply procurement or disposal authority.
- A unit commander sees resources assigned to their remit, not all protected inventories.
- Dispatch receives only availability and capability needed to assign resources.
- Case teams receive task-specific resource status, not unrelated personnel or facility records.
- Restricted equipment and specialist capabilities require explicit permission.
- Secrets, credentials and sensitive network configuration are never displayed in ordinary resource views.
- All access to restricted assets, movement, exception, disposal and security incidents is audited.

## 18. Exceptions and edge cases

1. Receipt quantity differs from purchase order: record discrepancy; do not accept missing/substituted quantity silently.
2. Item arrives damaged: quarantine and record condition; no operational availability.
3. Asset has no serial number: assign stable internal tag.
4. Duplicate serial/registration: reject registration and investigate identity collision.
5. Asset exists in catalogue but no physical instance: do not treat as inventory.
6. Asset allocated to unit but not physically present: flag location/custody discrepancy.
7. Two users request same serialized asset: resolve reservation/priority; never double-issue.
8. Reservation expires: release only through simulation-time event and policy; no offline time passage.
9. Returned asset has missing accessory: record discrepancy and restrict as required.
10. Returned equipment requires cleaning/decontamination: quarantine until cleared.
11. Asset fails inspection: block or restrict use; create work order.
12. Maintenance completes without acceptance check: remain unavailable where check is required.
13. Calibration expires during an active task: flag and follow task-specific safety/evidential policy; do not represent as valid.
14. Calibration found out of tolerance: identify affected use interval and notify BP-24/other consumers for impact assessment.
15. Vehicle develops safety-critical defect: immediate dispatch block.
16. Vehicle has non-critical defect: restricted use only under explicit policy.
17. Vehicle is fuelled but crew unavailable: not dispatchable.
18. Crew available but vehicle unsuitable: not dispatchable for that task.
19. Vehicle is at another location: availability includes travel/recovery constraint; do not teleport.
20. Vehicle collision/incident: preserve pre-incident and post-incident states and trigger inspection.
21. Radio/network outage: show communications degradation and affected coverage; do not fabricate successful transmission.
22. Device lost/stolen: security workflow, access revocation and investigation interface.
23. Device compromised: quarantine and preserve logs; do not reuse pending clearance.
24. Software licence expires: access/entitlement status changes; no assumed renewal.
25. Facility is closed or unsafe: block affected uses and trigger relocation/continuity.
26. Facility owner is not police: preserve external ownership and police-use agreement.
27. Storekeeper leaves role: custody handover required; stock does not become ownerless.
28. Stocktake differs from ledger: create variance case; no direct overwrite.
29. Stock quantity would become negative: reject transaction.
30. Lot expires: quarantine affected quantity; other valid lots remain available.
31. Recall applies to some serials/lots: block affected instances only, trace all holders.
32. Replenishment order is pending: do not count as on-hand stock.
33. Partial fulfilment: record fulfilled and outstanding quantities separately.
34. Substitute resource differs materially: require approval and record specification comparison.
35. Emergency resource diversion: record authoriser, displaced commitment, risk and return/restore plan.
36. Asset loaned externally: retain ownership, custody, term and return obligations.
37. Recovered property is potential evidence: do not register as operational inventory until evidential/property owner releases it.
38. Asset lost with no known custodian: retain unresolved accountability; do not assign blame by inference.
39. Employee separates while holding equipment: trigger controlled return/recovery; preserve chain of custody.
40. Unit disbands with assigned resources: explicit reallocation/return and custody transfer.
41. Asset is written off but physically recovered: require formal reinstatement/acquisition decision; no automatic reuse.
42. Disposal of data-bearing device: require sanitisation/destruction evidence and access revocation.
43. Asset record correction: preserve original event and correction provenance.
44. Duplicate receipt or transfer event: idempotency prevents duplicate quantity.
45. Out-of-order movement events: reconcile by authoritative sequence; never place asset in two locations.
46. Time paused: no maintenance interval, reservation, expiry or service schedule advances.
47. Usage-based maintenance without verified usage: do not estimate or fabricate usage.
48. Unauthorised person requests restricted equipment: deny and audit without disclosing unnecessary detail.
49. Readiness data is stale: display unknown/stale, not ready.
50. Resource category is retired: preserve existing records; prevent new issue unless grandfathered policy permits.
51. A unit requests resources beyond establishment/budget: route approval; no automatic procurement.
52. An item is shared pool equipment: record pool custodian and individual checkout intervals.
53. A resource is simultaneously reserved and deployed: reject conflicting state unless explicit task policy permits pre-emption.
54. An accessory is incompatible: block the combined configuration.
55. An asset is under warranty: route eligible repair through warranty contract reference.
56. A service provider misses maintenance deadline: mark overdue and adjust readiness; record contract escalation.
57. A facility's critical utility fails: degrade or close affected function, not necessarily entire facility.
58. A temporary facility is created for an operation: require location, authority, capacity, security, expiry and closure.
59. A recalled model is in a closed unit store: still trace and quarantine; storage does not exempt it.
60. A resource is accessible but not authorised: deny use; physical access is not permission.
61. A person is qualified but not assigned/authorised: no resource privilege by qualification alone.
62. A resource is assigned but user is no longer eligible: block use and trigger return/reassignment.
63. A resource is needed for a protected case: restrict assignment metadata and location to authorised roles.
64. City population reaches 10,000: no resource process may create additional living people; vendors/technicians are already counted under population rules.
65. External location appears on a vendor/service record: store as external supplier context only; do not create another playable territory.
66. A device's clock differs from simulation time: preserve raw device timestamp separately and reconcile under BP-37; never rewrite authoritative simulation time.
67. A work order is cancelled after parts are consumed: retain consumption and cancellation reason.
68. A vehicle is sold/transferred: close police custody and access, preserve finance and historical use references.
69. Resource request is denied: preserve reason and allow configured resubmission/appeal; do not fabricate fulfilment.
70. A maintenance action affects evidence integrity: isolate equipment and notify BP-23/BP-24 for assessment.
71. A unit commander attempts self-approved disposal: enforce separation of duties if policy requires.
72. Resource is physically destroyed but record still active: reconcile via loss/damage event and authorised write-off.
73. A temporary loan is not returned: overdue status and escalation; do not silently extend.
74. A facility access-control system fails: apply safe fallback/closure procedure; do not assume doors/security work.
75. A resource's owner and custodian differ: preserve both roles and approval paths.
76. A resource is shared by multiple units: define primary custodian, reservation priority and conflict rules.
77. A critical resource is unavailable during an incident: report constraint to command/dispatch; no automatic fictional substitute.
78. Resource allocation would exceed total person cap via an NPC supplier/technician creation: block person creation at population owner; resources can exist without inventing personnel.
79. A resource's model specification changes: historical asset retains old version unless formally upgraded.
80. A retired asset is referenced by a historical incident: reference remains valid and readable under permissions.

## 19. Cross-system effects

- BP-02/BP-04 supply canonical geography, property and facility ownership references.
- BP-05/BP-08 supply unit structure, authority, membership, deployment demand and accountability.
- BP-10/BP-11 consume patrol, fleet, communications and availability status.
- BP-12 supplies incident priority and resource tasking.
- BP-22/BP-23/BP-24/BP-26 use specialist equipment/facilities while retaining their own scene, evidence, forensic and custody ownership.
- BP-30 governs resource policy; BP-32 supplies user qualification/training; BP-34 owns procurement, contracts, costs and finance.
- BP-37 controls all simulation-time schedules and pause behaviour.
- BP-38/BP-39 persist canonical records and recovery state.
- BP-40/BP-41 present resource views and notifications through authorised interfaces.
- BP-42 enforces access and security controls; BP-43 tests lifecycle and consistency; BP-44 controls catalogue/policy changes.

## 20. Acceptance tests and evidence

Each test records fixture IDs, model/policy version, source events, expected/actual state, simulation timestamps and reproducible evidence. All fixtures are fictional.

| ID | Scenario | Required result |
|---|---|---|
| RES-001 | Register catalogue model | Versioned model created; no physical stock implied |
| RES-002 | Register serialized asset | Stable ID and unique tag/serial |
| RES-003 | Duplicate serial | Reject |
| RES-004 | Receive correct purchase quantity | Receipt linked to procurement; acceptance separate |
| RES-005 | Receive damaged/substituted item | Quarantine/discrepancy; no available stock |
| RES-006 | Accept item | Asset/stock created with owner, custodian and location |
| RES-007 | Move asset | Origin/destination and custody history recorded |
| RES-008 | Attempt conflicting location | Reject or reconcile; never two locations |
| RES-009 | Allocate asset to unit | Eligibility/capacity and authority validated |
| RES-010 | Reserve asset | Time-bounded hold distinct from issue |
| RES-011 | Duplicate issue event | Apply once |
| RES-012 | Issue restricted item to unauthorised user | Deny and audit |
| RES-013 | Return item with damage | Restrict/quarantine and create follow-up |
| RES-014 | Transfer custody | Releasing/receiving acknowledgement or exception |
| RES-015 | Inventory count variance | Variance record; ledger not silently overwritten |
| RES-016 | Stock consumption exceeds available quantity | Reject negative balance |
| RES-017 | Expired lot | Quarantine lot; valid lots unaffected |
| RES-018 | Pending purchase order | Not counted as on-hand |
| RES-019 | Partial fulfilment | Outstanding quantity remains visible |
| RES-020 | Vehicle without current inspection | Not dispatchable |
| RES-021 | Vehicle with safety-critical defect | Dispatch blocked |
| RES-022 | Vehicle without eligible crew | Not dispatchable |
| RES-023 | Vehicle lacks required task compatibility | Reject task allocation |
| RES-024 | Vehicle fuel/charge insufficient | Not dispatchable under configured threshold |
| RES-025 | Maintenance completed without acceptance | Remains unavailable |
| RES-026 | Calibration expires | Uses requiring valid calibration blocked |
| RES-027 | Out-of-tolerance calibration | Impact notification and traceable interval |
| RES-028 | Lost device | Security workflow and authorised access revocation |
| RES-029 | Compromised device | Quarantine and log preservation |
| RES-030 | Software entitlement expires | Entitlement/access status updated |
| RES-031 | Facility closes | Affected functions blocked; continuity task created |
| RES-032 | External-owned facility used by police | Ownership remains external; police-use agreement referenced |
| RES-033 | Asset recall | All affected serials/lots identified and quarantined |
| RES-034 | Asset disposal | Approval, sanitisation and disposition evidence |
| RES-035 | Recovered evidence offered as inventory | Reject until evidence/property owner releases it |
| RES-036 | Unit disbands | Resources explicitly reassigned/returned |
| RES-037 | Employee separates with issued asset | Recovery workflow; history retained |
| RES-038 | Time paused | No expiry, reservation or maintenance time advances |
| RES-039 | Stale readiness inputs | Status unknown/stale, never ready |
| RES-040 | Duplicate stock receipt | Idempotency prevents duplicate quantity |
| RES-041 | Out-of-order movement events | Deterministic reconciliation |
| RES-042 | Resource request exceeds available stock | Partial/queued/denied outcome; no fabricated stock |
| RES-043 | Substitute resource requested | Material substitution requires approval |
| RES-044 | Emergency diversion | Authoriser and displaced commitment recorded |
| RES-045 | External loan overdue | Overdue and escalation; ownership retained |
| RES-046 | Model specification updated | Historical asset version preserved |
| RES-047 | Asset assigned to unqualified user | Use blocked |
| RES-048 | Qualified but unauthorised user | Use blocked |
| RES-049 | Resource shared across units | Custodian and reservation conflict rules enforced |
| RES-050 | Rebuild asset/stock projections | Deterministic results from canonical events |
| RES-051 | Resource record accessed without permission | Denied and audited |
| RES-052 | Write-off asset later recovered | No automatic reactivation |
| RES-053 | Work order cancelled after consumption | Consumed parts and cancellation retained |
| RES-054 | Resource request denied | Reason and resubmission path retained |
| RES-055 | Facility critical utility failure | Affected readiness accurately degraded |
| RES-056 | Historical incident references disposed asset | Reference remains resolvable |
| RES-057 | Resource operation attempts population over-cap | Person creation blocked by BP-03 |
| RES-058 | Resource process runs while simulation paused | No time-dependent state advances |

## 21. Non-functional and operational requirements

- **Integrity:** unique asset identity, non-negative stock, valid custody, valid locations and compatible lifecycle transitions.
- **Temporal correctness:** simulation time only; pause freezes time-based obligations.
- **Traceability:** acquisition-to-disposal lifecycle and custody chain are reconstructable.
- **Availability truthfulness:** missing/stale/failed checks never imply ready.
- **Idempotency:** duplicate receipt, issue, consumption, transfer or maintenance events apply once.
- **Security:** access is scoped; secrets are excluded; restricted assets are protected.
- **Operational resilience:** loss of a resource record projection can be rebuilt from canonical events.
- **Efficiency:** catalogue models are shared; individual assets are created only when warranted; stock is quantity/lot based; avoid duplicating finance, property, personnel and evidence data.
- **Explainability:** report why a resource is unavailable and which dependency blocks it.
- **Audit:** privileged actions, exceptions, discrepancies, overrides and disposals are recorded.
- **Interoperability:** downstream units/dispatch receive stable IDs and versioned minimal events.
- **Simulation realism:** resources are finite, location-bound and subject to maintenance, replenishment and competing demand.

## 22. Source traceability

Exact source obligations: S22.R01 (police resource capability interface for emergency response/mutual aid only); S22.R02 (police-owned equipment/resource availability); S22.T01 (police resource readiness contribution to cross-agency reconciliation). BP-09 does not own non-police agency equipment, employment or unit records.

Primary source divisions: S16 utilities/energy/communications infrastructure; S17 roads/transport/mobility; S18 buildings/facilities/physical assets; S22 emergency services/civil protection (coordination only); S23 police service governance/structure; S25 duty rosters/staffing/deployment; S27 911/CAD/dispatch; S28 patrol/response/field operations; S30 case/investigative command; S32 evidence/scene resources (BP-22/BP-23 ownership); S33 forensic specialist equipment (BP-24 method ownership); S37 arrest/search/warrants/custody (BP-25/BP-26 process ownership); S46 database/persistence; S47 storage/capacity governance (records/storage architecture interface); S48 security/permissions; S49 backup/recovery; S50 testing; S51 observability/maintenance; S52 canon/change control. All requirement/test IDs and source JSON pointers must be semantically checked against the 52→44 crosswalk before approval.

## 23. Open decisions

1. Exact resource categories, catalogue naming and controlled vocabularies.
2. Which assets are serialized, lot-tracked or quantity-only.
3. Police facilities and their property/occupancy agreements.
4. Fleet size, vehicle types, base locations, replacement policy and assignment ratios.
5. Vehicle inspection, defect severity, dispatchability and fuel/charge thresholds.
6. Personal issue versus pooled equipment policy and custody intervals.
7. Restricted-resource categories, authorisation levels and approval separation.
8. Maintenance intervals, inspection checklists, calibration standards and return-to-service authorities.
9. Consumable reorder thresholds, suppliers, lead times, expiry and stock rotation rules.
10. Emergency allocation priority and resource-conflict arbitration.
11. Digital entitlement/licence model and service provider dependencies.
12. Facility readiness formula and critical utility dependencies.
13. Procurement and disposal approval thresholds (BP-34).
14. Which resource movements require dual acknowledgement or independent witness.
15. Retention periods for usage telemetry and device-health events (BP-38/BP-44).
16. Exact resource readiness metrics and data freshness thresholds.
17. Treatment of leased, donated, recovered and externally loaned assets.
18. Which specialist assets/locations require concealed existence as well as concealed detail.

Do not invent permanent quantities, supplier contracts, fleet numbers, unit budgets or facility addresses while these decisions remain open. The architecture and invariants above remain the binding draft.

## 24. Completion criteria

BP-09 may move to DESIGNED only after semantic reconciliation of every mapped source requirement and test; explicit resolution or acceptance of open policy decisions; contract reconciliation with BP-02/BP-04/BP-05/BP-06/BP-07/BP-08/BP-10/BP-11/BP-12/BP-22/BP-23/BP-24/BP-26/BP-30/BP-32/BP-34/BP-37/BP-38/BP-39/BP-42; and user review/approval.

Implementation, testing and verification remain separate states. This specification authorises no Neon schema change, migration, seed, import, procurement transaction or database write.
