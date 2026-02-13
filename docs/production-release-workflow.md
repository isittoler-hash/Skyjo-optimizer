# Production Release Workflow

This workflow converts the current project from development state to a repeatable production release process.

## Phase 1: Define release gates

1. Define what "production ready" means for this project:
   - feature completeness,
   - quality thresholds,
   - security requirements,
   - operational readiness,
   - rollback readiness.
2. Record measurable acceptance criteria for each gate.
3. Assign gate owners (engineering, QA, security, operations).

**Exit criteria:** explicit sign-off checklist exists and is agreed by all owners.

---

## Phase 2: Freeze scope and create the release backlog

1. Create a release milestone for the target production version.
2. Triage all open tasks into:
   - `must-ship`,
   - `defer`,
   - `post-release improvements`.
3. Add acceptance criteria and dependencies for each `must-ship` item.
4. Freeze feature scope; require explicit approval for late additions.

**Exit criteria:** only `must-ship` items remain in active release scope.

---

## Phase 3: Harden environments and configuration

1. Create a canonical environment variable inventory.
2. Enforce startup validation for required config values.
3. Move all secrets to a managed secret source (no plaintext in repo).
4. Align staging with production topology and toggles.
5. Document deployment and rollback commands in one runbook.

**Exit criteria:** staging and production configuration are aligned and validated.

---

## Phase 4: Enforce quality gates in CI

1. Require tests, linting, and type checks on every release PR.
2. Add baseline performance and deterministic checks as blocking jobs.
3. Set minimum coverage thresholds on critical modules.
4. Block merge when any required CI check is red.

**Exit criteria:** release branch can only move forward with all quality gates green.

---

## Phase 5: Complete security hardening

1. Run dependency vulnerability scans and remediate high/critical issues.
2. Rotate credentials used during development/testing.
3. Validate least-privilege access for runtime identities.
4. Verify auth/session/token handling and input validation.
5. Confirm audit logging and incident response hooks are active.

**Exit criteria:** no unresolved high/critical vulnerabilities and security sign-off complete.

---

## Phase 6: Operational readiness and observability

1. Add structured logs with correlation/request IDs.
2. Publish metrics for latency, throughput, errors, and saturation.
3. Build dashboards for service health and release impact.
4. Configure alerts for SLO/SLA thresholds.
5. Prepare incident runbooks and escalation ownership.

**Exit criteria:** on-call team can detect, triage, and recover from key failure modes.

---

## Phase 7: Staged rollout process

1. Deploy release candidate to staging and run smoke + regression checks.
2. Execute a canary deployment in production with limited traffic.
3. Monitor error rate, latency, resource usage, and key business metrics.
4. Increase traffic in controlled increments if canary remains healthy.
5. Trigger rollback immediately if any guardrail is breached.

**Exit criteria:** version reaches full traffic with guardrails remaining green.

---

## Phase 8: Post-release stabilization

1. Run a hypercare window (24 to 72 hours) with elevated monitoring.
2. Triage and resolve launch regressions with strict SLA.
3. Hold a release retrospective and capture improvements.
4. Update docs/runbooks based on real-world incidents and fixes.
5. Close release milestone only after all gates remain healthy.

**Exit criteria:** release is stable, documented, and operationally owned.

---

## Suggested implementation timeline

- **Week 1:** Phases 1 to 3
- **Week 2:** Phases 4 to 5
- **Week 3:** Phases 6 to 7
- **Week 4:** Phase 8 + follow-up hardening

## Deliverables checklist

- [ ] Production readiness checklist with owners.
- [ ] Scope-frozen release milestone with prioritized backlog.
- [ ] Environment and secret-management documentation.
- [ ] CI gate policy for tests, linting, type checks, and regressions.
- [ ] Security sign-off report.
- [ ] Monitoring dashboards and alert definitions.
- [ ] Canary and rollback runbook.
- [ ] Post-release retrospective and action items.
