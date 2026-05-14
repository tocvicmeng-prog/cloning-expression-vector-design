# Safety Gate Activation Map

## Pending Registry

T-309 registers all four safety gates as pending predicates in `GatePredicateRegistry.with_pending_defaults()`:

| Gate | T-309 state | Activation owner |
|---|---|---|
| `BlockCompile` | `PENDING_NOT_YET_ACTIVATED` | T-502 validation hard-failure predicates |
| `BlockVendorSubmission` | `PENDING_NOT_YET_ACTIVATED` | T-1001 vendor-profile feasibility + T-1002 screening verdicts |
| `BlockOperationalProtocol` | `PENDING_NOT_YET_ACTIVATED` | T-806b advisory acknowledgement, screening, and authorisation checks |
| `BlockExport` | `PENDING_NOT_YET_ACTIVATED` | T-903 export preconditions |

## Activation Rule

Owning tasks replace the pending registration by calling `GatePredicateRegistry.activate(gate, predicate, version, content_hash)`.
The activation must also record the predicate version and content hash in the session's `DerivationEnvironment`.

## Replay Rule

Replay selects the predicate version captured at session start, not the process-current predicate. Version bumps are
recorded by `GatePredicateVersionBumped` governance events with an embedded signed decision-record payload.
