# BP-34 — Finance and Procurement

**Project:** Saltwater, fictional sovereign city-state; one city and one jurisdiction  
**Blueprint division:** BP-34 of the fixed 44-division structure  
**Specification version:** 1.0  
**Specification status:** DESIGNED_DRAFT — user review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater BP-01–BP-44 master blueprint, original 52-division source and current 52→44 crosswalk. Fictional policy only; no real-world tax, banking, employment, procurement or accounting regime is presumed. No database write is authorised.

## 1. Purpose

BP-34 defines the financial and procurement systems needed to operate Saltwater's sovereign city-state and police service. It provides coherent, auditable financial records for public revenue and expenditure, budgets, business and household economic activity, wages and payroll, taxation and fees, grants, debt, banking/payment instruments, purchasing, supplier relationships, procurement decisions, invoices, payments, refunds, accounting periods and financial reporting.

The division must make money and purchasing consequential without turning every one of the city's at least 10,000 businesses into a deeply simulated accounting package. It uses tiered abstraction: economical aggregate or event-based financial representations for ordinary entities, with detailed transaction-level records wherever a transaction affects a case, public decision, police operation, person, business, asset, contract, liability or audit.

The governing principle is that every financial state must be explainable from attributable source transactions and configured rules. No balance, payment, tax liability, payroll result, procurement award or financial report may be fabricated merely to make totals appear plausible.

## 2. Scope and exclusions

### 2.1 BP-34 owns

- Financial architecture, chart-of-account configuration, accounting policy and transaction semantics.
- Currency, minor units, precision, rounding and conversion rules once configured.
- Public treasury, cash and bank-account references, payment instruments and financial account records.
- Public revenue, taxes, duties, rates, fees, charges, fines when financially collected, grants, transfers and other receipts.
- Public and police budgets, appropriations, allocations, commitments, expenditure controls, debt and financial periods.
- Business and household financial abstractions, income, expenditure, sales, costs, receivables, payables, debts and commercial transactions at proportionate fidelity.
- Payroll calculation and posting, deductions, employer contributions, benefits accounting and payroll payment, using approved inputs from BP-33 and police-specific authoritative employment/personnel sources.
- Procurement policy execution: requisitions, sourcing, quotations, tenders, evaluation records, approvals, awards, purchase orders, contract financial terms, receipts, invoices, liabilities, payments, refunds and supplier performance.
- Financial journals, ledgers, reconciliation, period close, financial statements, audit trails, corrections and compensating entries.
- Financial controls, delegated spending limits, budget validation and segregation-of-duties enforcement as supplied by authoritative governance records.

### 2.2 BP-34 does not own

- Canonical person identity, life status or population counting (BP-03).
- Business, supplier, employer, property, premises or organisation identity and lifecycle (BP-04).
- Police institutional structure, authority, financial delegation policy approval or command appointment (BP-05 and BP-30).
- Police personnel dossier, rank, position, career, service status or police-specific pay entitlement source (BP-06/BP-07).
- General employment contracts, attendance, shifts, leave, timesheets or approved payroll inputs (BP-33); police duty rosters and deployment (BP-08).
- Physical police asset identity, stock quantity, custody, condition, issue, return, maintenance or readiness (BP-09).
- Physical property, tenancy, lease, occupancy and access rights (BP-04).
- Court imposition of fines, compensation or financial orders (BP-28), legal liability findings (BP-27/BP-28), or police case evidence ownership (BP-15 onward).
- Canonical simulation clock and schedules (BP-37), event execution and causality (BP-35), authoritative records infrastructure (BP-38), persistence/recovery (BP-39), access-control platform (BP-42), testing governance (BP-43), or change control (BP-44).

BP-34 may calculate, record, reconcile, pay or report on externally owned decisions, but may not create the underlying authority or silently change its source.

## 3. Binding Saltwater canon and global invariants

1. Saltwater is one fictional sovereign city-state, one city and one jurisdiction. Off-map suppliers, banks, trade partners or currencies may be referenced as external dependencies but do not create playable territory or additional cities.
2. The living-person cap remains exactly 10,000 across the whole simulation. Financial accounts, payees, employees, suppliers, creditors and beneficiaries reference canonical person or organisation IDs; they never create duplicate people.
3. The city retains at least 10,000 registered businesses under BP-04. Each business may have a lightweight financial profile; deeper transaction detail is activated by relevance, economic importance, player interaction, procurement, incident/case relevance or configured simulation sampling. Abstraction must not imply false precision.
4. Police remains the deepest simulation. Police finance and procurement must be operationally meaningful, while non-police finances remain proportionate to their effects on the world.
5. Text is the permanent primary interface. Every financial operation, statement, procurement record, reconciliation and audit must be usable and inspectable through text. Optional charts or other visuals are secondary.
6. No simulation time advances while the player is outside the simulation or the game is paused. No payroll cycle, payment settlement, interest accrual, tax deadline, invoice due date, procurement deadline, budget rollover, debt collection, financial period close or supplier delivery progresses during a pause.
7. Preserve player agency, hidden case truth and NPC knowledge boundaries. Financial records may reveal only what the relevant actor can observe or access. No finance process may reveal a hidden offender, accomplice or generator truth. The exact `bingo` reveal rule remains governed by BP-01 and the simulation-wide rules.
8. Stable IDs, provenance, version history, lifecycle and explicit relationships are mandatory. Posted financial records are never silently overwritten or deleted.
9. Financial amounts must reconcile to configured currency precision and accounting policy. No invented balancing entries, unexplained write-offs, fabricated counterparties or silent rounding adjustments.
10. Storage efficiency is mandatory but may compress representation, never meaning, auditability, transaction lineage, source evidence or provenance.

## 4. Ownership and authority boundaries

| Concern | Authoritative owner | BP-34 responsibility |
|---|---|---|
| Person identity and population | BP-03 | Reference canonical payee, employee, taxpayer, debtor or beneficiary IDs |
| Business/supplier identity | BP-04 | Reference supplier/business IDs; maintain finance-specific account relationships |
| Property, lease and occupancy | BP-04 | Record rent, deposits, payment schedules and financial obligations without redefining occupancy |
| Public institution and delegation authority | BP-30 / BP-05 | Enforce valid, time-effective delegations and approval limits |
| General employment and approved time inputs | BP-33 | Calculate payroll and post/pay from approved, versioned inputs |
| Police-specific personnel/pay entitlements | BP-06 / BP-07 | Consume authoritative grade, service, appointment and entitlement inputs |
| Police duty assignment and attendance context | BP-08 / BP-33 | Consume approved payable duty/attendance inputs; do not infer hours from roster alone |
| Physical police resources and inventory | BP-09 | Own financial acquisition, purchase orders, invoices and costs; BP-09 owns physical asset/stock record |
| Court fine, compensation or financial order | BP-28 | Create receivable only from authenticated authoritative order and collection rules |
| Legal charging/dispute process | BP-27 | Reference legal status; do not adjudicate liability |
| Simulation causality | BP-35 | Emit/consume deterministic financial events under domain rules |
| Canonical time | BP-37 | Use simulation timestamps and scheduled event IDs |
| Records and schemas | BP-38 | Supply domain records, keys, constraints and audit metadata |
| Persistence/recovery | BP-39 | Preserve recoverable transaction history and reconciliation state |
| Permissions | BP-42 | Declare financial roles and record-level access requirements |
| Testing and evidence | BP-43 | Supply finance-specific acceptance criteria and test fixtures |
| Configuration/change control | BP-44 | Version financial policy and require approved change records |

A person may simultaneously be an employee, supplier owner, taxpayer, creditor, victim, witness or suspect. These are independent roles linked to one canonical person ID. A company may be an employer, supplier, landlord, customer and debtor without duplicate business identities.

## 5. Financial model and core entities

All entities use stable IDs, creation metadata, source references, effective dates where relevant, status, version, and provenance. A record's display name is not its identity.

### 5.1 Configuration and accounting entities

- **CurrencyDefinition:** currency ID/code, display name, minor-unit precision, rounding mode, effective period, enabled status and optional external conversion reference. Initial Saltwater currency is a configuration decision, not assumed.
- **AccountingPolicy:** accounting basis, recognition rules, chart-of-account version, posting controls, close rules, correction policy and effective dates.
- **Account:** account ID, code, name, account class, normal balance, parent, currency restrictions, owner institution, status and access classification.
- **FinancialPeriod:** period ID, start/end simulation timestamps, status, close/reopen authority and linked close record.
- **ExchangeRate:** base/quote currency, rate, source, effective timestamp, confidence/status and approval. No rate may be inferred from a real-world current rate without an explicit configured source.
- **FinancialInstitutionReference:** institution ID, jurisdiction/reference scope, account service, external/internal status and source. This is a financial counterparty reference, not a playable institution simulation requirement.

### 5.2 Parties and financial accounts

- **FinancialPartyLink:** finance-party ID, party type, canonical BP-03 person or BP-04 organisation reference, legal/operating role, effective dates and status.
- **FinancialAccount:** account ID, owner party, account type, currency, institution reference, masked display identifier, opening/closing state, restrictions and reconciliation reference. Credentials, PINs, passwords and secret authentication material are never stored in game records or GitHub.
- **PaymentInstrument:** instrument ID/type, payer/payee references, status, limits, validity, settlement state and external transaction reference where applicable.
- **Receivable / Payable:** obligation ID, creditor/debtor, originating source, amount/currency, due simulation date, status, dispute/hold state, settlement links and ageing.
- **DebtAgreement:** principal, rate or fixed charge, schedule, parties, security/collateral reference, terms, arrears, variation authority and lifecycle.
- **Grant / Transfer:** source fund, recipient, purpose, amount, conditions, award authority, milestones and disbursement/return records.

### 5.3 Transaction and accounting records

- **FinancialTransaction:** immutable transaction identity, type, business event/source, parties, amount, currency, effective and posting timestamps, status, idempotency key and provenance.
- **JournalEntry:** journal ID, source transaction, period, posting batch, authoriser, reversal reference and status.
- **JournalLine:** account, debit or credit amount, currency, party/cost-centre/project references, narration code and source line.
- **LedgerBalance:** derived balance or controlled snapshot with source journal watermark; not an independently editable truth.
- **Reconciliation:** statement/source reference, account, period, matched/unmatched items, variance, resolution, reviewer and sign-off.
- **FinancialAdjustment:** reason, authority, source reference, original transaction, compensating transaction and review status. It does not mutate the original.
- **AuditEvent:** actor, action, authority, timestamp, target, before/after references, reason, result and correlation ID.

### 5.4 Budget and expenditure entities

- **Budget:** owner institution, financial period, budget version, currency, status and approval.
- **BudgetLine:** cost centre/programme/account, allocated amount, restrictions and accountable owner.
- **Appropriation:** legally or institutionally authorised spending ceiling, purpose, authority, validity and amendments.
- **Allocation:** distribution of approved budget/appropriation to a controlled cost centre.
- **Commitment:** reserved amount against budget for a requisition, purchase order, contract or other approved obligation.
- **Expenditure:** recognised cost linked to source transaction, invoice/payment and account posting.
- **BudgetTransfer:** transfer between lines with reason, authority, limits and full history.
- **FinancialForecast:** explicitly labelled estimate with assumptions, version, horizon and confidence; never represented as an approved budget or actual result.

### 5.5 Procurement entities

- **Requisition:** requester, institution/unit, purpose, specification, quantity, estimated cost, funding line, urgency, required-by simulation date, status and approval chain.
- **SourcingEvent:** procurement method, invited suppliers, timetable, publication/access status, evaluation criteria and record set.
- **Quotation / TenderResponse:** supplier, price, scope, validity, delivery terms, exceptions, received timestamp and immutable submitted version.
- **Evaluation:** criteria, weights where configured, evaluator, conflict declaration, scores, rationale, moderation and decision.
- **AwardDecision:** selected supplier, authority, reasons, value, approval, alternatives and challenge/review state.
- **PurchaseOrder:** supplier, line items, quantity, unit price, currency, tax/fee treatment, delivery location, payment terms, budget commitment, approval and status.
- **ContractFinancialSchedule:** contract reference, milestones, retention, variation, payment terms, price adjustment rule and liability limits. BP-04 or the relevant institutional owner remains authoritative for non-financial contract identity/operations.
- **GoodsReceipt:** delivery reference, accepted/rejected quantities, condition note, receiver, date and discrepancy.
- **Invoice:** supplier invoice number, supplier, purchase order/contract, line items, taxes/fees, gross/net amounts, due date, duplicate fingerprint, validation and dispute status.
- **PaymentRun / Payment:** approved batch, payee, instrument, amount, currency, execution, settlement result, remittance reference and retry/idempotency state.
- **CreditNote / Refund:** original invoice/payment, reason, amount, authority, reversal/settlement links and status.
- **SupplierPerformanceRecord:** delivery, quality, dispute, service and payment performance with sourced observations; it is not an automatic blacklist or finding of misconduct.

### 5.6 Payroll and public revenue entities

- **PayrollInputSnapshot:** source employee/person, approved pay period, hours/units, pay basis, grade/entitlement source, adjustments, deductions and source version.
- **PayrollCalculation:** gross pay, taxable/assessable base where configured, deductions, employer contributions, net pay, rounding and calculation version.
- **PayrollRun:** period, included/excluded employees, control totals, approval, posting batch and settlement state.
- **PayrollPayment:** payee, net amount, payment reference, settlement and returned/failed state.
- **RevenueAssessment:** tax/fee/charge type, liable party, legal/policy basis, period, amount, calculation inputs, notice and dispute state.
- **RevenueReceipt:** amount, payer, assessment/source, payment instrument, date and ledger posting.
- **Refund/Relief:** originating assessment/receipt, authority, basis, amount, status and linked compensating entry.

## 6. Currency, amounts and calculation rules

1. All monetary values carry an explicit currency ID. No bare numeric amount may be interpreted without currency.
2. The configured currency definition sets precision and rounding. Store monetary amounts in exact minor units or another exact decimal representation; binary floating-point is prohibited for authoritative money.
3. Calculations retain sufficient intermediate precision and apply configured rounding only at defined boundaries. Record the rule and result.
4. Tax, fee, interest, discount, contribution and exchange calculations identify the rate, base, effective period, source and calculation version.
5. Foreign-currency transactions preserve original amount/currency and the approved conversion rate, converted amount and rounding difference as separate values.
6. Currency conversion must not silently rewrite the original transaction. Revaluation, if configured, is a separate attributable transaction.
7. A missing rate, ambiguous currency, expired configuration or undefined rounding rule blocks posting and creates a visible validation error.
8. Forecasts, estimates, quotes, budgets, commitments, liabilities, payments and actual expenditure are distinct values and may not be interchanged.
9. Financial totals must be reproducible from underlying transaction/journal records or a traceable snapshot with a defined source watermark.

## 7. Accounting and posting invariants

The selected accounting model is a fictional configuration decision. The specification supports a balanced double-entry model as the default design target, but the exact chart, basis and recognition policy remain open until approved. Regardless of selected model:

- Every posted transaction must balance under its configured accounting model and currency rules.
- A transaction cannot post with missing, invalid, disabled or incompatible accounts.
- A journal is either fully posted or not posted; partial posting is prohibited.
- Posting is atomic and idempotent. Retrying the same request cannot duplicate a journal, liability, payment or receipt.
- Posted journals and source transactions are immutable. Corrections use linked reversal/compensating entries.
- A reversal references the exact original posting and records actor, authority, reason and time.
- A transaction cannot be posted into a closed period unless an authorised reopening or adjustment-period rule explicitly permits it.
- A derived balance must reconcile to its source journal watermark. A stale projection is labelled stale and cannot be used as a final financial statement.
- Suspense accounts, write-offs, bad-debt provisions and rounding accounts require configured purpose, authority and review; they are never silent balancing devices.
- Inter-account transfers create linked debit/credit effects and cannot create or destroy value without an explicit revenue, expense, gain, loss or adjustment classification.
- Duplicate external references are rejected or held for review according to configured uniqueness scope.

## 8. Budget, appropriation and expenditure control

A budget is a planned financial envelope; an appropriation is an authorised spending ceiling; an allocation assigns controlled capacity; a commitment reserves capacity; an invoice creates or substantiates a payable; a payment settles an obligation; expenditure recognition follows the configured accounting policy. These states remain distinct.

Before commitment or payment, validate:
- active institution, cost centre, project and budget line;
- effective appropriation and delegated authority;
- available budget after existing commitments and recognised expenditure;
- correct currency and permitted account;
- requester/approver separation where required;
- supplier and procurement status;
- purchase order, contract, receipt and invoice references where required;
- restrictions, funding conditions and period validity.

Budget overruns are blocked by default. An approved exception must record the specific authority, ceiling, reason, period, affected line and review. No automatic budget increase is permitted. Transfers, virements, supplementary appropriations and emergency exceptions require configured authority and a complete audit record.

Budget versions are immutable snapshots. Revised budgets supersede but do not erase earlier versions. Forecasts remain separately labelled and never alter actual ledger balances.

## 9. Procurement lifecycle

### 9.1 Standard sequence

`Draft requisition → Submitted → Validated → Sourcing → Evaluation → Award approved → Purchase order issued → Delivery/receipt → Invoice matched → Payment approved → Paid/settled → Closed`

Not every procurement uses every stage. A direct purchase, framework call-off, emergency purchase, recurring service or grant-funded acquisition uses an explicitly configured path and records why it is applicable. Skipped stages are recorded, not silently omitted.

### 9.2 Requisition and sourcing

A requisition must state the operational need, requesting unit, quantity/scope, estimate, delivery requirement, funding source, urgency and requester. Requisitions cannot be approved by an actor lacking the relevant delegation or whose authority is expired, suspended or outside scope.

Sourcing methods may include competitive tender, multiple quotations, single-source justification, framework/call-off or emergency procurement. Thresholds and methods are configuration decisions. The system must not assume a real-world threshold or public procurement statute.

Suppliers are canonical BP-04 businesses or BP-03 persons where configured. Supplier eligibility, registration, beneficial/controlling relationships, conflicts, sanctions or performance restrictions are handled as explicit fictional policy records with source and review; allegations are not findings.

### 9.3 Evaluation and award

Evaluation criteria and weights, when used, are published or frozen before evaluation begins. Each evaluator declares conflicts before accessing restricted submissions. Scores and rationales are attributable and versioned. Changes after submission require a reason and authorised review.

The award record preserves all received bids/quotes, evaluation, moderation, decision-maker, delegated authority, reasons, value, selected supplier and any departures from the planned method. An award does not itself prove delivery, acceptance, invoice validity or payment.

### 9.4 Purchase order, receipt and invoice matching

Purchase orders have unique references and immutable issued versions. Changes require authorised variation/amendment and preserve previous terms. Goods receipt is a physical/operational fact supplied by the receiving owner; BP-09 records police asset/stock acceptance and condition. BP-34 consumes receipt confirmation for financial matching.

Three-way matching (purchase order, receipt and invoice) is the default control for goods where configured. Services may use approved milestones, service confirmation or contract terms. Quantity, price, tax, currency, supplier, duplicate invoice and tolerance mismatches are held for resolution, not silently adjusted.

### 9.5 Payment and closure

Payment requires a validated payable, valid payee, approved payment run, available funds or authorised facility, valid payment instrument and required approvals. A submitted payment may be pending, settled, rejected, returned, reversed or disputed. A failed payment is not treated as settled. Retrying a failed request uses the same idempotency key unless a new authorised payment instruction is created.

Procurement closure requires financial and operational status to reconcile: order quantity/value, receipts, invoices, payments, credits, outstanding liabilities, contract obligations and any asset registration handover.

## 10. Supplier, contract and conflict controls

- A supplier's canonical identity is owned by BP-04; finance maintains account links and transactional history only.
- Supplier ownership/control and relationships to public officials, police personnel or procurement decision-makers are represented by references to BP-03/BP-04/BP-36 records, with access restrictions as configured.
- A conflict declaration is a recorded statement and does not itself establish misconduct.
- A declared or detected conflict triggers configured recusal, reassignment or review; it must not be silently ignored.
- Supplier bank/payment details are restricted, versioned and independently verified under fictional policy. No credentials or secrets are stored.
- Contract financial terms are versioned. Variations require authority, reason, funding validation and a link to the affected contract/order.
- Supplier suspension, exclusion or restriction requires an authorised, reasoned and reviewable decision. A complaint, allegation, adverse rumour or intelligence report alone is not a final finding.
- Related-party, split-purchase, duplicate invoice, unusual price, repeated emergency procurement and approval-pattern alerts may be raised as review indicators, never automatic guilt findings.
- Audit/review access is logged. Sensitive bids and supplier data are not exposed to unauthorised competitors or unrelated NPCs.

## 11. Payroll and employee-related finance

BP-33 owns general employment, contract, leave, attendance and approved timesheet records. BP-06/BP-07 own police-specific personnel and career entitlements. BP-08 owns police duty assignment. BP-34 owns the financial calculation, payroll run, deductions/contributions accounting, posting and payment.

1. Payroll is calculated only from an immutable, versioned input snapshot from authoritative source records.
2. A planned roster is not proof of attendance or payable work. Approved attendance/overtime/allowance inputs are required.
3. Police pay may depend on rank, grade, position, appointment, service, qualification, acting assignment or configured entitlement; BP-34 consumes authoritative eligibility and effective dates rather than inventing them.
4. General employees use their BP-33 contract/pay basis and approved inputs.
5. Gross pay, taxable/assessable pay, deductions, employer contributions, benefits and net pay are separate calculated values.
6. Every calculation records formula/configuration version, input IDs, effective dates, rounding, adjustments and exceptions.
7. Retroactive changes produce a recalculation/adjustment run with links to original and replacement inputs. Earlier payroll records remain immutable.
8. A payroll run cannot be paid twice. Payment failures, returns, corrections and off-cycle payments are separately recorded.
9. Confidential salary and bank/payment details are restricted by role and purpose. A line manager may not automatically access every employee's full payroll record.
10. Payroll disputes, garnishments or court-ordered deductions require a source authority and review state. No deduction is inferred from an allegation or informal request.

## 12. Public revenue, taxation, fees and household/business finance

All tax, fee, duty, rate, fine-collection and relief rules are fictional configurable policy. No real-world jurisdiction's rates, exemptions, deadlines or legal definitions are presumed.

- A revenue assessment identifies its policy basis, liable party, taxable/chargeable base, rate, calculation version, period, due date, notice and review/dispute path.
- A tax or fee liability is not created merely because an NPC or business has income. It requires an enabled policy rule and valid assessment inputs.
- A fine or compensation receivable requires an authoritative BP-28 order or other configured authority; BP-34 does not decide guilt, impose sentences or invent penalties.
- Revenue receipts link to assessments and payment records. Partial payments, overpayments, arrears, refunds, reliefs and disputed balances remain distinct.
- Public grants and transfers identify the authorising institution, funding source, conditions, milestones, recipient and return/clawback rules.
- Household and business finance may be represented through opening/closing balances, periodic income/expense categories, significant transactions, debt and event-linked records. Detail increases when required for player-facing work or causally relevant events.
- Business revenue, expenses, stock purchases, wages, rent, taxes, debts, invoices and customer receipts must be mutually coherent at the selected abstraction level.
- Household financial abstraction must not fabricate exact bank balances or transaction histories when only a category-level estimate is simulated. Label estimates as estimates.
- Cash, bank transfer, card, cheque, credit, grant, barter or other payment methods exist only when enabled in configuration. Payment instrument states must reconcile across payer, payee and settlement records.
- Economic shocks, shortages, closures, wage changes and price movements are generated by BP-35 using configured causal models and available inputs, not arbitrary finance-side edits.

## 13. Debt, grants, rent and financial obligations

Debt records distinguish principal, accrued interest/charges (if configured), repayment, arrears, dispute, default, restructuring, write-off and discharge. Interest accrues only during active simulation time and under an approved rate/formula. A paused simulation produces no accrual.

Rent, deposits, service charges and lease payments reference BP-04 property, lease, landlord and tenant records. BP-34 records financial obligations and settlement history; it does not create, terminate or extend a lease, change occupancy or determine property access. Subletting or lease variation is sourced from BP-04.

Grants and transfers distinguish application, assessment, award, conditions, commitment, instalment, receipt, monitoring, variation, suspension, recovery and closure. A grant award is not the same as cash receipt. Conditions and milestones are time-valid and do not progress while paused.

## 14. Financial periods, close and reporting

Financial periods use BP-37 simulation time. Periods may be monthly, quarterly, annual or another configured cadence. Opening, soft close, hard close, adjustment period and reopening require explicit status and authority.

Period close checks:
- all required journals posted or explicitly carried forward;
- bank/cash/payment accounts reconciled or variances disclosed;
- receivables/payables and outstanding commitments identified;
- payroll and tax/fee runs reconciled;
- budget actuals and commitments reconciled;
- duplicate, suspense, unmatched and failed transactions reviewed;
- control totals, journal counts and source watermarks recorded;
- financial statements reproducible from posted records.

Reports distinguish budget, appropriation, commitments, actual expenditure, liabilities, receipts, cash movement, forecasts and variances. Each report carries period, currency, policy/configuration version, generation timestamp, source watermark, filters, preparer and reviewer. A report is not an independent source of truth and must be reproducible.

A closed period is immutable except through authorised reopening or a separately configured adjustment period. Reopening requires reason, authority, affected reports and a new audit event. Prior reports remain available and are marked superseded where appropriate.

## 15. State transitions

### 15.1 Transaction

`Draft → Validated → Approved (if required) → Posted → Reconciled`

Alternative terminal/holding states: `Rejected`, `Cancelled`, `Held`, `Disputed`, `Reversed`. A posted transaction cannot return to draft or be deleted. A reversal creates a new linked transaction.

### 15.2 Requisition and procurement

`Draft → Submitted → Validated → Sourcing → Evaluation → Awarded → Ordered → Partially received → Received → Invoiced → Partially paid → Paid → Closed`

Allowed alternate paths are explicitly configured. Rejection, cancellation, challenge, dispute, variation, supplier failure and emergency exception are separate states with reason and authority.

### 15.3 Invoice

`Received → Validating → Matched / Exception / Disputed → Approved → Payable → Part-paid → Paid`

A credit note, duplicate hold, rejection, cancellation or reversal is separately linked. A duplicate is never silently merged into the original.

### 15.4 Payroll

`Inputs pending → Inputs frozen → Calculated → Validated → Approved → Posted → Payment pending → Part-paid / Paid / Failed / Returned → Reconciled`

A corrected run is a new run with explicit relationship to the prior run. A run cannot be paid twice.

### 15.5 Assessment and receipt

`Draft → Assessed → Notified → Due → Part-paid / Paid / Overdue / Disputed → Settled / Written-off / Cancelled`

Overdue and interest states progress only during active simulation time and only under configured policy. Dispute or appeal does not automatically erase the underlying historical assessment.

## 16. Inputs, outputs and event contracts

### Inputs

- Canonical person and organisation references, status and roles from BP-03/BP-04.
- Approved employment contracts, attendance, leave, timesheet and payroll inputs from BP-33.
- Police personnel/career/pay entitlement inputs from BP-06/BP-07 and approved duty context from BP-08.
- Institutional structure, cost centres, delegated authorities and spending limits from BP-05/BP-30.
- Physical receipt, asset registration, stock and condition confirmation from BP-09.
- Property/lease/occupancy/landlord/tenant records from BP-04.
- Court orders and financial obligations from BP-28; relevant legal-process status from BP-27.
- Canonical simulation timestamps, periods and schedule events from BP-37.
- Configured economic events and causal outputs from BP-35.
- Financial configuration, account catalogue, rates, thresholds and policy versions from authorised BP-44 changes.

### Outputs

- Posted journals, account balances, receivables, payables and reconciliations.
- Budgets, commitments, expenditure, forecasts, variances and public/police financial reports.
- Approved payroll calculations, runs, payment instructions and ledger postings.
- Revenue assessments, receipts, refunds, arrears and grants/transfer records.
- Requisitions, sourcing/evaluation/award records, purchase orders, invoices, payment and supplier-performance records.
- Finance event notifications to BP-35/BP-38/BP-41 and source-linked financial facts to authorised domain consumers.
- Validation errors, exception queues, duplicate alerts, budget-control failures and audit evidence.

### Event requirements

Every event has a stable event ID, event type, source entity/version, simulation timestamp, actor/system identity, authority context, correlation ID, idempotency key where applicable, payload schema version and processing status. Consumers record receipt and outcome. Replaying an event must not duplicate a payment, journal, payroll run, assessment, commitment or procurement action.

## 17. Permissions and segregation of duties

Permissions are assigned through BP-42 and institutional roles/delegations from BP-05/BP-30. BP-34 enforces, but does not invent, authority.

Roles may include requester, budget holder, procurement officer, evaluator, approver, contract manager, goods receiver, invoice validator, payment authoriser, payroll preparer, payroll approver, cashier, reconciler, financial controller, auditor and read-only report consumer.

Controls:
- A requester cannot approve their own requisition where separation is required.
- An evaluator with a declared conflict cannot score the affected procurement.
- A goods receiver cannot silently certify their own supplier invoice as correct without the configured independent check.
- Payroll preparer and payroll approver are separated where staffing permits; any small-team exception is explicit and reviewed.
- Payment creation and payment release are distinct where configured.
- Reconciliation sign-off is independent of transaction creation for material accounts.
- No user may grant themselves a financial permission or delegation.
- Delegations are scope-limited, amount-limited, institution-limited and time-effective.
- Acting authority is valid only when the source appointment/acting record is valid.
- Emergency authority is limited to its configured purpose, ceiling, duration and retrospective review.
- Sensitive salary, tax, debt, bank and supplier bid data are access-restricted and access logged.
- NPCs and automated agents receive only permissions and information justified by their role, actions and knowledge.

## 18. Exception handling and edge cases

1. Unknown currency, missing precision or unavailable exchange rate blocks posting.
2. Rounding difference exceeds configured tolerance: hold for review; never auto-plug.
3. Duplicate transaction or external payment reference: idempotent rejection or review hold.
4. Supplier identity changes after award: preserve original supplier and require authorised novation/variation.
5. Supplier dissolves, closes or becomes inactive: preserve liabilities and history; block new commitments unless exception authorised.
6. Purchase order is amended after partial delivery: retain versioned line quantities and calculate remaining balance correctly.
7. Goods arrive without an order: record an exception receipt; do not fabricate an order or automatic liability.
8. Invoice exceeds order or receipt tolerance: hold disputed amount and preserve undisputed amount only if policy allows split handling.
9. Invoice references a nonexistent, cancelled or fully consumed order: reject or route to documented exception.
10. Duplicate invoice number from same supplier: hold using configured fingerprint and manual review; do not assume two different suppliers share identity.
11. Partial delivery, partial invoice, partial payment, credit note and refund combinations must reconcile.
12. Payment instruction submitted but settlement unknown: pending, not paid; query/reconcile before retry.
13. Payment rejected or returned: restore payable status through a linked event; never erase original attempt.
14. Payroll source input is corrected after posting: new adjustment run; no mutation of paid payroll.
15. Employee joins/leaves or changes grade mid-period: apply effective-dated proration rule only if configured; otherwise hold.
16. Overtime appears on roster but no approved attendance: exclude pending verification.
17. Conflicting attendance sources: flag discrepancy; no automatic selection of the financially favourable source.
18. Court order is varied, stayed or appealed: apply only the authoritative effective order and preserve prior assessment/payment history.
19. Person or business dies, exits or closes: close or restrict future transactions without deleting outstanding balances/history.
20. Business has multiple branches: one canonical business identity with branch/location references; account consolidation rules are configured.
21. Business is mobile/virtual: location basis must be explicit; no invented premises.
22. Household finances are estimated: mark as estimated and prohibit presentation as bank-certified exact data.
23. Budget exhausted after commitment but before invoice: honour existing valid commitment; block additional commitment; surface variance.
24. Appropriation expires while a valid contract remains: preserve contract liability and flag funding/authority resolution.
25. Emergency procurement bypasses ordinary sourcing only under a configured authority, reason, ceiling and retrospective review.
26. Evaluator conflict discovered after scoring: suspend affected decision, preserve original scores and require independent reassessment.
27. Related-party supplier discovered after award: create review; do not silently void contract or presume misconduct.
28. Procurement split across multiple requisitions to avoid threshold: flag pattern for review; do not infer guilt.
29. Supplier quote price changes after expiry: require refreshed quote or authorised exception.
30. Contract variation increases value: revalidate delegation, budget, sourcing threshold and approval.
31. Rent payment made to an agent: verify authority from BP-04/contract record; preserve landlord and recipient identities.
32. Deposit is refundable: track liability separately from income until disposition is authorised.
33. Tax assessment is disputed: preserve assessment and dispute state; pause collection only if configured authority says so.
34. Overpayment: record unapplied credit/refund liability; do not silently classify as revenue.
35. Grant recipient fails milestone: hold future instalment only under award terms; preserve previous disbursements.
36. Interest rate changes: apply effective-dated terms, never retroactively unless an authorised variation explicitly requires it.
37. Financial period close runs while source event is delayed: watermark and late-arriving event handling must prevent silent omission or duplicate posting.
38. Reconciliation statement contains transactions not in ledger: record unmatched items; do not create journal without source validation.
39. Ledger projection is stale or corrupt: mark unavailable/stale and rebuild from authoritative journal history.
40. Reversal requested twice: idempotent link to the first reversal; no duplicate correction.
41. Actor's authority expires between request and approval: validate authority at the relevant effective timestamp and block invalid approval.
42. Currency definition changes: retain old currency/version for historic records; conversion is explicit.
43. Business insolvency or debt default: preserve creditor priority and dispute status according to configured fictional rules; no arbitrary asset seizure.
44. Cash discrepancy: record count, custodian, witnesses, variance and review; no forced balancing.
45. Financial institution outage: queue or fail safely; never mark unsettled transfer as paid.
46. A person is both police employee and supplier owner: detect related-party/conflict context and restrict procurement decisions as configured.
47. A financial record is relevant to a police case: preserve source transaction, access history and disclosure/export lineage without exposing unrelated private records.
48. A report is regenerated after correction: issue a new version and retain the previous report and its source watermark.
49. A policy/rate changes while a batch is being prepared: freeze configuration version at batch initiation or explicitly restart validation.
50. Simulation is paused: all financial schedules and accruals freeze; user-initiated inspection does not itself advance time.
51. Simulation resumes: process due events in deterministic order from the last committed simulation timestamp; do not invent events during pause.
52. Person cap is reached: financial records may reference existing people, but finance cannot create an additional living person to satisfy a payee/vendor requirement.
53. Business minimum is met: finance cannot create duplicate businesses to satisfy supplier variety; request a BP-04 canonical entity.
54. An off-map supplier is referenced: store external reference only; do not create playable external geography or population.
55. Storage threshold is approached: retain mandatory audit/provenance and apply approved archival/compaction policies without loss of meaning.
56. A source event is malformed or unauthorised: quarantine it with diagnostic evidence; do not partially post.
57. Two concurrent requests consume the same budget: atomic commitment prevents overspend beyond authorised tolerance.
58. Two concurrent payments target one invoice: lock/idempotency prevents double settlement.
59. A user retries after timeout: return the original operation result by idempotency key.
60. A correction would affect a closed period: use authorised adjustment period or reopening; preserve original close evidence.
61. A payment recipient account changes: validate effective ownership and approval; preserve previous destination version.
62. A payroll run includes a separated employee: apply effective termination/payable entitlement source and flag unsupported amounts.
63. A refund exceeds original settled amount: reject or hold unless a distinct authorised basis exists.
64. A procurement award is challenged: freeze affected next steps only as configured; preserve bid confidentiality and decision record.
65. A financial report contains personal data: apply field-level permissions and redaction without changing source records.
66. An external conversion rate source is unavailable: block conversion or use a still-valid approved rate; never guess.
67. A tax/fee policy is withdrawn: retain historic assessments and use effective dates for new assessments.
68. A public institution changes name or structure: keep stable institution/account references and record authorised mapping; do not rewrite history.
69. A cost centre is closed with open commitments: require transfer, settlement or documented closure treatment.
70. A supplier delivers a substitute item: record accepted variation and BP-09 asset/stock decision; do not alter original order silently.
71. A delivery is rejected: record rejected quantity and return/disposal responsibility; no payable for rejected quantity unless contract says otherwise.
72. A contract includes retention: separate gross certified amount, retention payable and release condition.
73. A grant is returned or clawed back: create a linked receivable and recovery transaction under award authority.
74. A debt is written off: preserve legal/financial history and authorisation; write-off does not imply payment.
75. A disputed supplier invoice is partly undisputed: split only through explicit line-level records and policy, preserving total.
76. An audit identifies an error: record finding and remediation; auditor cannot directly rewrite underlying journal.
77. A system migration imports opening balances: require source reconciliation, control totals, provenance and explicit approved migration event.
78. An account is closed with residual balance: block closure until transferred, settled or authorised as a documented exception.
79. A payment is made in error: recovery/recall is a new linked process, not deletion of payment.
80. A financial actor is suspended: revoke effective permissions and block pending approvals at validation time.
81. A supplier changes legal identity through merger: preserve predecessor and successor relationship with effective date and authority.
82. A quote contains confidential trade data: restrict access to evaluators/authorised reviewers and audit each access.
83. A procurement specification changes after bids arrive: cancel/restart or use an approved clarification path; do not selectively alter criteria.
84. A public official orders expenditure verbally: require a traceable authorised decision record before commitment/posting, except a configured emergency path.
85. A business has seasonal closure: financial schedules follow BP-37 and business status; no sales are generated during closed periods absent explicit exception.
86. A household moves or changes members: BP-36/BP-03 own household/relationship changes; finance updates account links only through sourced events.
87. A business has multiple currencies: maintain currency-specific accounts and explicit conversions; never net incomparable amounts.
88. A tax exemption is applied: require valid status, scope and effective period; preserve the assessment basis.
89. A grant is paid in instalments: each instalment has its own payment and remaining commitment calculation.
90. An employee receives a one-off allowance: source eligibility and approval, calculation basis and payroll treatment are recorded.
91. An employee's pay is confidential: restrict both individual records and aggregate reports where re-identification is possible.
92. A budget transfer is requested retrospectively: block unless explicit policy authorises and records retrospective effective date.
93. A procurement order is cancelled after deposit: calculate refund/forfeiture only under contract terms and authorised decision.
94. A payment is split across funding sources: journal lines identify each source and preserve total transaction amount.
95. A payment batch contains one invalid item: configured atomicity determines whole-batch hold or item-level rejection; no ambiguous partial execution.
96. A bank statement repeats a transaction: reconciliation detects duplicate source reference and prevents double matching.
97. A supplier has unpaid invoices and a credit note: apply credit according to explicit allocation, preserving both source records.
98. A person has multiple financial roles: one canonical identity with separate role/account links and permissions.
99. A finance record is requested by an unauthorised investigator: deny or provide authorised redacted result; record access attempt.
100. A financial event is replayed after restore: idempotency and recovery watermark prevent duplicate posting.
101. A policy version is missing for historic calculation: mark calculation unreproducible/incomplete and retain original result; do not invent a replacement formula.
102. An exchange-rate correction is approved: create a new valuation event; preserve original transaction and prior report.
103. A budget forecast changes: new forecast version only; no alteration to approved budget or actuals.
104. A supplier is paid before final goods acceptance under configured terms: record advance payment and outstanding delivery risk separately.
105. A contract milestone is certified by an authorised officer: retain certificate source and approval before liability recognition.
106. A police resource purchase creates a physical asset: BP-34 financial records link to BP-09 asset ID after registration; no duplicate asset master.
107. A police resource is lost or written off: BP-09 owns physical loss/condition; BP-34 records approved financial impairment/write-off.
108. A payroll correction changes tax/fee liability: create linked amended calculation and assessment; preserve paid amounts and refund/arrears state.
109. A supplier is also a landlord: separate procurement and tenancy contracts, account purposes and approval chains.
110. A public grant funds police procurement: track restricted fund, eligible costs and reporting without bypassing BP-05/BP-30 authority.
111. A cash receipt has no identified payer: record suspense/unidentified receipt with investigation status; do not assign arbitrarily.
112. A customer refund is requested: verify original sale/receipt and refund authority; preserve original income and new refund.
113. A transaction crosses a financial period boundary: use effective date and posting date separately under configured recognition rules.
114. A user changes system time: financial timestamps continue to derive from BP-37; local device time cannot change the simulation ledger.
115. An NPC financial action is simulated: require actor role, knowledge, available funds/credit, applicable rules and causal event.
116. A hidden generator event causes financial movement: domain effects may be generated but only visible to authorised observers; no hidden offender identity leak.
117. A financial report is exported for a case: include source IDs, filters, version, redactions, chain of access and integrity metadata.
118. A backup restore loses a journal: reconciliation detects control-total mismatch and blocks normal operation pending recovery.
119. A schema/configuration update changes account mapping: migration and mapping must be versioned, reversible and tested before production adoption.
120. A financial policy change would alter canon or player rights: BP-44 approval and versioned change record are mandatory; no silent live change.

## 19. Cross-system interfaces and dependencies

- **BP-03:** canonical people, population cap, person lifecycle; financial party links only.
- **BP-04:** business, employer, landlord, tenant, supplier, premises, property and organisation identities; finance references them.
- **BP-05/BP-30:** institutional structure, cost centres, financial delegation, approval matrix and authority. BP-34 enforces current authority.
- **BP-06/BP-07:** police personnel status and pay entitlement sources.
- **BP-08/BP-33:** roster, employment, attendance, leave and approved payable inputs.
- **BP-09:** police assets, inventory, goods receipt, condition, stock and physical handover. Financial asset cost remains linked, not duplicated.
- **BP-27/BP-28:** legal processes and authoritative court orders; BP-34 handles financial execution/recording only.
- **BP-35/BP-37:** deterministic event processing and simulation time. All scheduled financial events freeze during pause.
- **BP-36:** relationships and household/business connections; used for conflict and financial-role context without redefining relationships.
- **BP-38/BP-39:** schema, constraints, immutable event/record provenance, persistence and recovery.
- **BP-41:** notifications and reports, with BP-34 as source owner for financial outputs.
- **BP-42:** permissions, confidential financial data, secret handling and access audit.
- **BP-43:** accounting invariants, performance, reconciliation, concurrency, scale, recovery and security tests.
- **BP-44:** versioned currency, account, tax, fee, budget, procurement and payroll configuration.

## 20. Storage, performance and scale

The finance model must support 10,000+ businesses, 10,000 or fewer living people, public institutions, police procurement and event-driven financial activity without a full high-volume ledger for every low-relevance business.

- Use stable integer/UUID-like IDs and compact coded enums; avoid duplicating person/business names and addresses in every transaction.
- Store canonical party references and immutable source IDs; denormalised display values are derived snapshots only when required for historical fidelity.
- Use exact integer minor units or fixed-precision decimal values, not floating point.
- Separate immutable source events/journals from derived balances, dashboards and report projections.
- Use idempotency keys, unique constraints, transactional posting and indexed period/account/party/source references.
- Tier business/household finance: lightweight profile and periodic aggregates by default; event-level detail for material, case-linked, procurement, disputed or player-inspected activity.
- Retention, aggregation and archival must preserve original records where legally/game-policy required, chain of provenance, totals and reproducibility. Never aggregate away a case-relevant transaction or audit event.
- Benchmark realistic peak payroll, procurement and month/period close batches; test concurrency and recovery.
- Before any Neon write: measure existing database size and relevant table/index/storage baseline; estimate incremental bytes/MiB, projected total and uncertainty; present the estimate and obtain explicit user approval. After an approved write, measure actual growth and compare against estimate. No schema migration, seed, import or bulk data write is authorised by this specification.

## 21. Notifications and reporting outputs

Notifications may include requisition approval/decline, budget warning, procurement stage change, tender clarification, award, delivery discrepancy, invoice mismatch, payment failure/settlement, payroll completion, tax/fee notice, overdue obligation, reconciliation variance, period close and audit finding.

Each notification identifies source record, actor/system, recipient, urgency, timestamp, action required and permission-filtered detail. Notifications do not themselves change financial state. They freeze during simulation pause and are delivered according to BP-35/BP-37 scheduling.

Reports include public budget and actuals, police budget, procurement pipeline, supplier spend, contract commitments, payroll summary, revenue and arrears, grant utilisation, debt, cash flow, ledger trial balance, reconciliation exceptions and audit findings. Reports must distinguish actual, forecast, budget, commitment and liability and carry source watermarks and access controls.

## 22. Acceptance tests

All tests are design acceptance criteria; none is represented as executed. Test fixtures must use fictional data, deterministic simulation timestamps and no production Neon writes.

- AT-001: A financial party link references one valid canonical BP-03 person or BP-04 organisation and creates no duplicate identity.
- AT-002: An attempted finance-side creation of a living person is rejected and leaves the population ledger unchanged.
- AT-003: Finance references at least 10,000 BP-04 businesses without creating duplicate business identities.
- AT-004: Off-map suppliers remain external references and create no playable territory or population.
- AT-005: Every authoritative amount carries a valid currency ID.
- AT-006: Unknown currency prevents validation and posting.
- AT-007: Monetary arithmetic uses exact minor units or configured exact decimal representation.
- AT-008: Configured rounding is applied only at defined boundaries and is recorded.
- AT-009: Foreign-currency conversion preserves original and converted amounts with rate provenance.
- AT-010: Missing or expired exchange rate blocks conversion.
- AT-011: A posted transaction balances under the configured accounting model.
- AT-012: An unbalanced journal is rejected atomically.
- AT-013: A journal cannot post to an inactive or incompatible account.
- AT-014: A posted journal cannot be edited or deleted.
- AT-015: A correction creates a linked compensating or reversal entry.
- AT-016: Reversal of a transaction twice does not duplicate the reversal.
- AT-017: Posting is idempotent when the same event is delivered repeatedly.
- AT-018: Concurrent posting cannot create duplicate journal entries.
- AT-019: Closed-period posting is blocked unless authorised adjustment/reopening rules apply.
- AT-020: A ledger projection reconciles to its declared journal watermark.
- AT-021: Stale or corrupt ledger projection is marked unavailable and rebuildable from source journals.
- AT-022: A suspense balance requires a configured purpose and review record.
- AT-023: Inter-account transfer preserves total value across linked entries.
- AT-024: Duplicate external transaction reference is held or rejected under configured uniqueness rules.
- AT-025: A budget is distinguishable from appropriation, allocation, commitment and actual expenditure.
- AT-026: A commitment reduces available budget atomically.
- AT-027: Concurrent commitments cannot exceed authorised available budget.
- AT-028: Budget overrun is blocked absent an authorised exception.
- AT-029: Budget exception records authority, ceiling, reason, period and affected line.
- AT-030: Budget transfer preserves original and revised budget versions.
- AT-031: Forecast changes do not alter actual ledger balances.
- AT-032: Appropriation expiry blocks new commitment outside its effective period.
- AT-033: Existing valid contract liability is preserved when a budget line closes.
- AT-034: Every requisition records requester, need, quantity/scope, estimate and funding source.
- AT-035: An unauthorised requester cannot approve a requisition.
- AT-036: A self-approval is blocked where segregation policy requires.
- AT-037: A sourcing event freezes its method and evaluation criteria before bid evaluation.
- AT-038: Each supplier bid/quote retains an immutable submitted version.
- AT-039: Evaluator conflict declaration is required before restricted bid access.
- AT-040: A conflicted evaluator cannot score the affected procurement.
- AT-041: Evaluation scores and rationale are attributable and versioned.
- AT-042: Award decision records alternatives, selected supplier, value, reason and authority.
- AT-043: Award does not automatically create a receipt, invoice or payment.
- AT-044: Purchase order has a unique ID and immutable issued version.
- AT-045: Purchase-order variation requires authority and preserves prior terms.
- AT-046: Goods receipt references the purchase order and records accepted/rejected quantities.
- AT-047: BP-34 cannot create or mutate BP-09 physical asset/stock identity.
- AT-048: Goods receipt discrepancy prevents invalid invoice matching.
- AT-049: Invoice supplier and purchase-order supplier mismatch is held.
- AT-050: Duplicate invoice fingerprint is detected before payable approval.
- AT-051: Three-way matching checks order, receipt and invoice where configured.
- AT-052: Service invoice uses approved milestone/service confirmation where configured.
- AT-053: Invoice above authorised tolerance is held for review.
- AT-054: Partial delivery and partial invoice amounts reconcile to order quantities and values.
- AT-055: A rejected delivery does not create a payable unless contract terms authorise it.
- AT-056: Payment requires validated payable, valid payee and required approvals.
- AT-057: Payment submitted but not settled remains pending.
- AT-058: Failed/returned payment restores the correct payable state through linked events.
- AT-059: Retrying a payment with the same idempotency key does not pay twice.
- AT-060: Two concurrent payments cannot settle one invoice beyond its outstanding amount.
- AT-061: Credit note references its source invoice and preserves both records.
- AT-062: Refund cannot exceed authorised source amount without a separate authority.
- AT-063: Payment batch handles invalid items according to configured atomicity with no ambiguous partial posting.
- AT-064: Payroll uses a frozen, versioned authoritative input snapshot.
- AT-065: A planned roster alone cannot establish payable attendance.
- AT-066: Police pay entitlement is sourced from BP-06/BP-07 effective-dated records.
- AT-067: General employment/pay basis is sourced from BP-33.
- AT-068: Gross, deductions, employer contributions and net pay remain separately represented.
- AT-069: Payroll calculation records formula/configuration version and rounding.
- AT-070: Mid-period employment or grade change uses configured effective-date rule or is held.
- AT-071: Payroll run cannot be paid twice.
- AT-072: Payroll correction creates a linked adjustment run without mutating paid history.
- AT-073: Payroll payment failure/return is separately recorded and reconciled.
- AT-074: Payroll access is restricted by role and purpose.
- AT-075: Confidential aggregate report prevents unauthorised employee re-identification.
- AT-076: Tax/fee assessment requires an enabled fictional policy and valid inputs.
- AT-077: Tax/fee calculation records base, rate, policy version and effective period.
- AT-078: A fine receivable requires an authoritative BP-28 order or configured authority.
- AT-079: Revenue receipt links to its assessment and payment record.
- AT-080: Partial payment, overpayment, arrears and refund remain distinct states.
- AT-081: Disputed assessment remains historically preserved and collection follows configured authority.
- AT-082: Tax exemption requires valid scope and effective dates.
- AT-083: Withdrawal of a tax policy does not rewrite historic assessments.
- AT-084: Business finance aggregates reconcile at their selected abstraction level.
- AT-085: Estimated household/business figures are never presented as exact bank-certified data.
- AT-086: A business financial profile references BP-04 and does not create a business.
- AT-087: Business closure preserves liabilities and financial history.
- AT-088: Household membership changes are sourced from BP-03/BP-36.
- AT-089: Grant award is distinguishable from commitment and cash receipt.
- AT-090: Grant instalments reconcile to award value and remaining commitment.
- AT-091: Failed grant milestone affects future instalments only under award terms.
- AT-092: Rent/deposit payment references BP-04 lease and does not change occupancy.
- AT-093: Refundable deposit is recorded as a liability until authorised disposition.
- AT-094: Supplier/landlord identity is canonical and may support separate financial roles.
- AT-095: Debt principal, interest, arrears, repayment and write-off are separate.
- AT-096: Interest accrues only during active simulation time and configured policy.
- AT-097: Pausing simulation freezes interest, payroll, tax, payment and procurement schedules.
- AT-098: Resuming simulation processes due events deterministically from last committed time.
- AT-099: User device clock changes do not alter financial simulation timestamps.
- AT-100: Period close checks reconciliation, open commitments, payables, receivables and source watermarks.
- AT-101: A closed period cannot be silently reopened.
- AT-102: Reopening requires authority, reason and a new audit event.
- AT-103: A regenerated financial report receives a new version and preserves the old report.
- AT-104: Reports distinguish budget, appropriation, commitments, actuals, liabilities and forecasts.
- AT-105: Report totals are reproducible from source journals or declared snapshots.
- AT-106: A late-arriving event cannot be silently omitted or double-posted during period close.
- AT-107: Bank reconciliation records matched, unmatched and variance items.
- AT-108: An unmatched statement line does not create an unsupported journal.
- AT-109: Duplicate bank statement transaction is not matched twice.
- AT-110: Cash discrepancy records custodian, count, variance and review.
- AT-111: Financial institution outage never marks an unsettled payment as paid.
- AT-112: Supplier suspension requires an authorised, reviewable decision.
- AT-113: Allegation or intelligence alone does not establish supplier misconduct.
- AT-114: Related-party relationship creates a review indicator and does not automatically prove wrongdoing.
- AT-115: Split-purchase pattern is flagged without automatic guilt determination.
- AT-116: Emergency procurement records authority, reason, ceiling and retrospective review.
- AT-117: Procurement challenge preserves submitted bids, evaluation and decision history.
- AT-118: A changed procurement specification after bids requires approved clarification or restart.
- AT-119: Contract variation revalidates budget, delegation and procurement thresholds.
- AT-120: Supplier payment details are restricted, versioned and contain no credentials/secrets.
- AT-121: A police resource acquisition links financial cost to BP-09 asset ID without duplicate asset master.
- AT-122: Physical loss/write-off is owned by BP-09; finance records approved financial effect.
- AT-123: Every financial action records actor/system, authority, timestamp, source and correlation.
- AT-124: Access to confidential salary, tax, debt, bid and bank data is permission-checked and logged.
- AT-125: An unauthorised investigator cannot access unrestricted financial records.
- AT-126: Case export includes source IDs, filters, version, redactions and integrity metadata.
- AT-127: Financial NPC action requires role, knowledge, available resources and causal event.
- AT-128: Financial output does not expose hidden offender/accomplice truth.
- AT-129: Exact `bingo` reveal protection remains enforced by global rules and cannot be bypassed by finance.
- AT-130: No finance-generated prompt tells the player what to investigate next.
- AT-131: A financial event replay after restore is idempotent.
- AT-132: Restore reconciliation detects missing journal/control-total mismatch.
- AT-133: Schema/configuration changes preserve versioned account mappings and rollback evidence.
- AT-134: Opening-balance migration requires source reconciliation and explicit approved migration event.
- AT-135: Storage compaction preserves mandatory audit and case-relevant transaction lineage.
- AT-136: Low-relevance business financial abstraction is labelled at its true precision.
- AT-137: Material business transactions can be promoted to detailed records without changing canonical business identity.
- AT-138: Population cap and 10,000-business baseline remain unchanged by finance operations.
- AT-139: Off-map trade dependency creates no playable city or territory.
- AT-140: Every financial configuration change references an approved BP-44 change record.
- AT-141: A missing policy version prevents unsupported recalculation of historic transactions.
- AT-142: A changed exchange rate creates a new valuation event and preserves the original.
- AT-143: A cost-centre closure requires explicit treatment of open commitments.
- AT-144: A contract retention amount remains separate from currently payable amount.
- AT-145: A supplier merger preserves predecessor/successor identity and effective date.
- AT-146: A payment split across funding sources identifies each source and balances.
- AT-147: A transaction crossing period boundary retains effective and posting timestamps.
- AT-148: A person holding multiple finance roles retains one canonical person identity.
- AT-149: Finance reports and notifications freeze while simulation is paused.
- AT-150: No finance-side event advances while the player is outside the simulation.
- AT-151: Financial totals remain exact under configured precision for large and small amounts.
- AT-152: Concurrent payroll and procurement postings cannot corrupt account balances.
- AT-153: A policy change during batch preparation uses frozen policy version or forces revalidation.
- AT-154: A suspended financial actor cannot approve a pending transaction.
- AT-155: A supplier account change is independently authorised and historical destination retained.
- AT-156: An unidentified receipt remains in suspense until supported allocation.
- AT-157: A customer refund links to original receipt and records new cash movement.
- AT-158: A business seasonal closure suppresses sales events unless an explicit exception exists.
- AT-159: A court variation changes a receivable only from the authoritative effective order.
- AT-160: Financial reports with personal data apply field-level permissions and redaction.
- AT-161: A source event with invalid schema or authority is quarantined without partial posting.
- AT-162: An account cannot close with unexplained residual balance.
- AT-163: A write-off preserves original debt and records authority and reason.
- AT-164: A procurement goods substitute requires approved variation and receiving decision.
- AT-165: A deposit forfeiture or return follows the referenced contract and authorised decision.
- AT-166: A public grant restricted to police use cannot fund an ineligible purchase.
- AT-167: An employee separation preserves final payable entitlement and prevents unsupported future payroll.
- AT-168: A business/person death or permanent exit closes future activity without deleting outstanding obligations.
- AT-169: A financial access denial is logged without exposing protected record contents.
- AT-170: Financial transaction and journal counts/control totals reconcile after recovery.
- AT-171: A financial statement identifies accounting policy, currency and source watermark.
- AT-172: A procurement award cannot be paid before required receipt/milestone evidence unless an approved advance-payment term exists.
- AT-173: A grant clawback creates a linked receivable rather than deleting the grant payment.
- AT-174: A budget commitment is released only when its originating obligation is cancelled, reduced or settled.
- AT-175: A payroll deduction requires valid policy or authoritative order and records the source.
- AT-176: A tax/fee refund cannot exceed the original collected amount absent separate authority.
- AT-177: A transaction cannot combine incompatible currencies in one journal without explicit conversion lines.
- AT-178: A supplier conflict discovered after award triggers controlled review while preserving contract and decision history.
- AT-179: A public official's financial approval is checked against authority at the effective decision timestamp.
- AT-180: A financial close is deterministic and repeatable from the same source watermark and configuration version.

## 23. Source traceability

The following are the exact source IDs mapped to BP-34 in the authoritative crosswalk. Original wording remains in `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`; source IDs use its stable 1-based array positions.

| Source ID | Source domain | BP-34 incorporation |
|---|---|---|
| S06.R01 | Housing, property and tenancy | Rent, deposits, lease payment obligations; BP-04 remains owner of property/tenancy |
| S06.R02 | Housing, property and tenancy | Time-valid financial terms and payment history; occupancy/access remains BP-04 |
| S07.R02 | Businesses and commercial economy | Business income, expenditure, trade, debt, contracts and finance abstraction |
| S08.R01 | Employment, labour and professional life | Payroll calculation and payment using BP-33-approved employment inputs |
| S09.R01 | Markets, trade, supply chains and logistics | Financial and procurement interfaces for goods, suppliers and trade |
| S09.R02 | Markets, trade, supply chains and logistics | Orders, deliveries, contracts and disruption-related financial state |
| S09.R03 | Markets, trade, supply chains and logistics | Off-map trade dependencies without additional playable territory |
| S09.T01 | Markets, trade, supply chains and logistics | Reconciliation across sender, carrier, receiver and related financial records |
| S10.R01 | Public finance, taxation and economic accounts | Currency, revenue, taxation, fees, expenditure, budgets, debt, grants and periods |
| S10.R02 | Public finance, taxation and economic accounts | Business and household financial abstraction |
| S10.R03 | Public finance, taxation and economic accounts | Arithmetic integrity and audit trail; no fabricated unbalanced totals |
| S10.T01 | Public finance, taxation and economic accounts | Every posted transaction balances under configured accounting model |
| S11.R02 | Government and public administration | Financial procurement interface for public procurement, permits and accountable public actions; BP-30 owns institutional authority |
| S20.R01 | Food systems and essential services | Procurement, storage/distribution finance and essential supply purchasing |
| S20.R03 | Food systems and essential services | Financial coherence for supply constraints and disruption/recovery |
| S20.T01 | Food systems and essential services | Reconciliation of essential supply states across stock and delivery records |

No other source ID is claimed as a BP-34 mapping. Related cross-system rules are implemented as interface contracts, not invented traceability IDs.

## 24. Open fictional configuration decisions

These remain explicit decisions for later configuration/review; this draft does not invent real-world defaults:

1. Saltwater currency name/code, minor-unit precision and display conventions.
2. Accounting basis, chart of accounts, account classes and recognition policy.
3. Fiscal year, financial period cadence, close calendar and adjustment-period policy.
4. Public revenue catalogue, tax/fee bases, rates, exemptions, assessment/appeal and collection rules.
5. Public treasury and banking model, permitted payment instruments, settlement semantics and external institution abstraction.
6. Public budget architecture, appropriation sources, supplementary funding and transfer/virement authority.
7. Police budget structure, cost centres, procurement delegations and spending thresholds.
8. Procurement methods, quotation/tender thresholds, evaluation rules, publication and challenge windows.
9. Emergency procurement powers, limits, duration and retrospective review.
10. Supplier registration, eligibility, conflict declarations, related-party handling, suspension and exclusion policy.
11. Invoice validation, matching tolerances, advance payment, retention and payment terms.
12. Payroll calendar, pay scales, overtime/allowance rules, deductions, employer contributions and benefits.
13. Household/business financial abstraction tiers and thresholds for detailed transaction simulation.
14. Debt, interest, credit, default, insolvency, security and write-off rules.
15. Grant categories, award criteria, milestones, monitoring, clawback and reporting.
16. Financial retention, archival, disclosure, audit and restricted-data access matrix.
17. Financial institution outage and delayed-settlement behaviour.
18. Currency conversion source, approval, rate expiry and revaluation policy.
19. Budget control exception matrix and permitted emergency overspend.
20. Public financial reporting and disclosure catalogue.

## 25. Completion status

- Specification: **DESIGNED_DRAFT**; user review/approval pending.
- Implementation: **NOT_STARTED**.
- Test execution: **NOT_STARTED**. The 180 acceptance tests above are criteria, not execution evidence.
- Verification: **NOT_STARTED**.
- Neon: **No database write performed or authorised**.
- The next division in fixed numeric order is **BP-35 — Simulation Engine**.
