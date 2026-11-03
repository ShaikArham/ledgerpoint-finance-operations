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

## Final QA attempt — 2026-11-03

**Repository baseline:** latest changes include executive presentation improvements and a CI artifact upload step. The source files and CI YAML were inspected through the connected GitHub repository.

**Actions verification:** The connected combined-status endpoint previously returned an empty status array, and its commit-workflow lookup filters to pull-request-triggered runs. These results do not establish a pass, failure or absence of push-triggered GitHub Actions runs. A current Actions job conclusion and its logs are still unverified.

**Execution environment:** Direct `git ls-remote` failed with `Could not resolve host: github.com`. The local Python environment has pytest 9.0.2 but lacks Streamlit; therefore a full exact-repository pytest/AppTest run was not possible in this environment. No test-pass count is asserted.

**Deployment verification:** Direct access to the Streamlit app was unavailable to the web inspection tool. The deployed revision, app startup and user interactions have not been independently confirmed.

**Mobile verification:** Responsive CSS for narrow screens is present in source. No browser viewport screenshots, touch interaction or physical-device tests were performed. Treat mobile compatibility as unverified.

**New evidence path:** The CI workflow now uploads `pytest-results.xml` as an Actions artifact after the test step (if a result file exists). This enables subsequent inspection but does not prove the workflow has executed successfully.

**Release decision: NOT SIGNED OFF.** All Workstreams 9–14 have source and test coverage committed; Workstream 15 remains incomplete until current GitHub Actions, deployment, and responsive end-to-end evidence are reviewed.

## QA verification attempt — draft PR #6

Created draft PR [#6](https://github.com/ShaikArham/ledgerpoint-finance-operations/pull/6) from `qa/workstream15-ci-verification` into `main` to trigger a pull-request workflow. Its only code change is a regression asserting failed self-review leaves the approval register unchanged. **Unmerged pending a confirmed green test result.**

The first commit-associated pull-request workflow lookup returned an empty run list. No conclusion is inferred. GitHub Actions run status and logs remain unverified.

Local environment check repeated: `git ls-remote` failed DNS resolution for github.com; Python has pytest 9.0.2 but no Streamlit package. Consequently neither a full local test run nor browser/mobile rendering could be completed.

External page inspection attempts for the Streamlit app and GitHub Actions page returned disabled fetch errors. This is **not** evidence of a broken deployment. It is an access limitation.

Release remains **NOT SIGNED OFF**. Do not merge PR #6 or represent the application as tested until CI and live browser evidence are available.

## Verified CI result — 2026-11-03 21:39 UTC

**GitHub Actions run #75**, workflow `Python tests`, for draft PR #6 head commit `23c378a20e9a732498d0bd88c0bef3862a0693c2`, completed with job conclusion **success**. The job logs show **209 passed in 1.75s**, and successful Python compilation. JUnit artifact `pytest-results` (ID `13271934099`) was uploaded successfully.

Evidence: https://github.com/ShaikArham/ledgerpoint-finance-operations/actions/runs/41723750161

**Scope:** This is a verified CI pass for the pull-request branch and its exact tested commit, **not** a separate verified CI pass for the latest main-branch commit. Draft PR #6 remains unmerged. The prior statements saying no full pytest pass was available are superseded for this PR commit only.

**Still outstanding:** Live Streamlit startup/browser interactions, mobile visual checks, and confirming the final release/main commit. Remote browser fetch was disabled and the local runtime lacks Streamlit. Release sign-off remains pending those checks.
