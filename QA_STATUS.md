# LedgerPoint QA evidence and limitations

Updated: 2026-11-03

## Workstream 14 review

- Fixed case-insensitive approval-request lookup to match duplicate detection.
- Approval event retains the canonical request identifier.
- Added tests for case-insensitive lookup, blank IDs and decisions after rejection.
- Maker/checker separation is based on fictional user-entered names only. It is not identity assurance.
- Approval history is immutable in the in-memory data model, but resets on session reset/restart. It is not persistent or tamper-proof.
- Approval decisions do not alter ledger postings or reconciliation results.

## Workstream 15 started

- GitHub Actions test workflow updated to run Python compilation checks before pytest.
- Test runner now writes JUnit XML evidence on a successful invocation.
- Existing smoke tests cover the 12 dashboard tabs, but browser-level responsive and mobile-device tests have not run.

## Verification register

| Scope | Source committed | Tests written | Tests executed and passed | Live verified |
| --- | --- | --- | --- | --- |
| WS9 CSV staging | Yes | Yes | Not independently confirmed | No |
| WS10 Exception cases | Yes | Yes | Not independently confirmed | No |
| WS11 Budget/forecast | Yes | Yes | Not independently confirmed | No |
| WS12 Cash flow | Yes | Yes | Not independently confirmed | No |
| WS13 Payroll demo | Yes | Yes | Not independently confirmed | No |
| WS14 Approvals/audit | Yes | Yes | Not independently confirmed | No |
| WS15 End-to-end QA | In progress | CI checks extended | Not independently confirmed | No |

## Environment constraints

The connected GitHub status endpoint returned no status entries, and the workflow-runs endpoint only queries pull-request-triggered runs, not all push runs. Empty results must not be treated as a pass.

The available local test environment has pytest but not Streamlit; external GitHub network resolution failed, so the full repository and dashboard suite could not be executed there. A complete passing test count, GitHub Actions conclusion, and deployed/mobile validation are still required before final sign-off.

## Next acceptance criteria

1. Confirm GitHub Actions runs on the latest main commit and inspect failures or passing test XML.
2. Run the full pytest suite on the exact current commit, including Streamlit AppTest.
3. Validate all 12 tabs on desktop and narrow/mobile screens.
4. Check input boundaries, state resets, CSV export safety, approval state transitions and financial reconciliation invariants.
5. Correct README descriptions that still refer to older five-tab/read-only phases, and publish a final evidence-based release report.

## Presentation iteration (2026-11-03)

- Executive opening now explains the fictional unmatched €12 debit as the primary case.
- Added numbered reviewer-stage captions to overview, reconciliation, exception cases, approvals and reporting.
- Changed the overview to prioritize investigation and next actions.
- Collapsed the optional long walkthrough and adjusted mobile metric padding.
- Added a narrative smoke test; it is committed but **not independently executed**.
- No live mobile screenshot, deployment smoke test or full pytest pass has been independently confirmed.
