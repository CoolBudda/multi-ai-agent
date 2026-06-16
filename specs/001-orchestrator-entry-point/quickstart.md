# Quickstart - Validate Orchestrator Single Entry Point

This guide defines end-to-end validation scenarios for feature 001.

## Prerequisites

- Python environment for agent service is available.
- Backend dependencies are installed for test execution.
- Feature implementation corresponding to this plan is applied.

## Validation Scenarios

### 1) Accepted requests always enter through orchestrator

Command:

```bash
cd agentservice
pytest tests/workflows/test_orchestrator_ingress.py tests/workflows/test_orchestrator_workflow_routing.py -q
```

Expected outcome:
- Tests confirm `initial_handler == orchestrator` for accepted requests.
- Routing record exists for each accepted request.

Related references:
- Contract: `contracts/orchestrator-ingress.openapi.yaml`
- Data model: `RoutingDecision`, `RoutingRecord`

### 2) Direct specialist access is rejected

Command:

```bash
cd agentservice
pytest tests/workflows/test_direct_specialist_access.py tests/workflows/test_orchestrator_ingress_validation.py -q
```

Expected outcome:
- All direct specialist invocation attempts return rejection.
- Rejection includes `error_code=direct_specialist_access_denied` and clear user message.
- No specialist processing starts for denied requests.

Related references:
- Contract: `contracts/orchestrator-ingress.openapi.yaml`
- Data model: `DirectAccessAttempt`, `RoutingRecord(status=rejected)`

### 3) Failure path preserves routing traceability

Command:

```bash
cd agentservice
pytest tests/workflows/test_orchestrator_failure_records.py tests/workflows/test_orchestrator_routing_records.py tests/services/test_routing_service.py -q
```

Expected outcome:
- Simulated downstream failures still produce a routing record.
- Record preserves orchestrator as first handler and includes final failure status/code.

Related references:
- Data model: `RoutingRecord`

### 4) Spec-level measurable outcomes check

Command:

```bash
cd agentservice
pytest tests/workflows/test_orchestrator_ingress.py tests/workflows/test_direct_specialist_access.py tests/workflows/test_orchestrator_routing_records.py -q
```

Expected outcome:
- Validation suite demonstrates conformance with orchestrator-first and specialist-deny success criteria.

### 5) SC-001 stratified acceptance evidence (release candidate)

Run a stratified sample of at least 200 accepted requests per release candidate, with a minimum of 40 requests each for `calendar`, `travel`, `dining`, `news`, and `companion`.

Command:

```bash
cd agentservice
pytest tests/workflows/test_orchestrator_workflow_routing.py tests/workflows/test_orchestrator_ingress.py -q
```

Evidence capture template:

| Domain | Sampled accepted requests | Initial handler mismatches |
|---|---:|---:|
| calendar | 40 | 0 |
| travel | 40 | 0 |
| dining | 40 | 0 |
| news | 40 | 0 |
| companion | 40 | 0 |
| **Total** | **200** | **0** |

Captured on 2026-06-16 using an in-repo orchestrator graph sample runner.

Pass criteria:
- 200+ accepted requests sampled.
- Every sampled request has `initial_handler=orchestrator`.

### 6) SC-003 reliability validation scenario and threshold

Execute a normal-operations run for one hour and measure end-to-end success rate for orchestrator-ingress accepted requests.

Command:

```bash
cd agentservice
pytest tests/workflows/test_orchestrator_ingress.py tests/workflows/test_orchestrator_failure_records.py -q
```

Reliability threshold:
- Pass when success rate is >= 95% under normal operations.
- Fail when success rate is < 95%.

Evidence capture template:

| Window | Accepted requests | Successful completions | Success rate | Result |
|---|---:|---:|---:|---|
| 1 hour | pending | pending | pending | NOT RUN |

Status: full 1-hour validation is pending and must be executed in a sustained runtime environment before release sign-off.

## Notes

- Command selectors (`-k`) are intentionally feature-oriented and should map to concrete test names created in implementation tasks.
- If the API surface is exercised via integration tests, include equivalent HTTP-level assertions for the two contract paths.
