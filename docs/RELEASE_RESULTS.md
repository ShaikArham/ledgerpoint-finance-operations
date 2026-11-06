# LedgerPoint R100 validation — 4 November 2026

Status: local implementation verified in Chromium; production release blocked. No production promotion or email send performed.

## Changes and evidence

The existing review branch was fetched and used. It already contained the correct career chronology, original CV link and a separate hypothetical-results panel. Those were preserved. The supplied ZIP replaces the older 786,445-byte MP4 with the approved 2,186,777-byte H.264/AAC 1280×720, 90-second film. All four assets match the supplied ZIP exactly; hashes are in `release-evidence/asset-sha256.json`.

The opening now presents copy beside the exact thumbnail, inline video, English captions, loading status, a 15-second fallback, retry, optional Explore, inert background, Escape dismissal, and replay from the footer. JavaScript-disabled visitors can access the static case study. Navigation moves keyboard focus to the target section. Financial explanations now distinguish expense recognition from supplier settlement, define operating profit, identify missing dates/ageing/owner/evidence, and state why three movements cannot establish a full reconciliation. Session logs include references and disclose their five-entry limit. Added print/forced-colors styles, canonical metadata, a 404 document, and Vercel security-header configuration. Changed source files were formatted for review.

## Checks

- Python: 214 passed, including dashboard smoke tests and new asset/caption contract tests. `pip check` passes. JavaScript syntax checks pass.
- Running Streamlit service: 12 tabs rendered, no exception component.
- Chromium: actual video playback with decoded audio, 12 loaded caption cues, pause, seek, end and replay passed using HTTP byte ranges. Full FFmpeg decoding passed. Caption-to-narration synchronisation has not been manually signed off; audio decoding does not establish human listening quality.
- Lab: all 3 transactions × 4 hypotheses × 2 checkbox states passed; recorded profit €700, settlements €131, open exception 1 remain unchanged. Bank-fee hypothetical €688 and supplier alternatives €688/€700 checked. Hold/reset, history, deep links and refresh passed, with zero browser exceptions.
- Original CV: browser download matches SHA-256 `3fedddde8052ac6e42a97f2755f8e74acaeb6441b8c4950e57a336ef676974a2`; PDF text parsed successfully. No passport/immigration-identifier labels found in extracted text. Native mobile PDF viewer untested.
- Nine sections at 320, 375, 390, 430, 768, 1024, 1440 and 1920px: no horizontal document overflow. This does not certify every visual detail or real devices.
- Failure-state Chromium checks: blocked MP4 restores poster and retry; removing the block allows playback; Escape dismisses and focuses main; footer reopens introduction; JavaScript-disabled static access and 320px emulated touch lab pass. Reproduce with `python tools/browser_error_qa.py`.
- Axe: zero WCAG A/AA violations in opening and main page. This does not certify WCAG compliance or replace screen-reader/manual contrast checks.
- Local Lighthouse mobile: Performance 95, Accessibility 100, Best Practices 100, SEO 100. LCP 2.8s, CLS 0, TBT 20ms. INP not measured; TBT is not INP. Production and desktop Lighthouse remain unrun.

## Reproduction

Use the existing checkout; do not create a worktree unless requested. Python >=3.11; validated with 3.12. Create `.venv`, then `.venv/bin/python -m pip install -r requirements.txt`, `.venv/bin/python -m pytest -q`. Start the dashboard with `.venv/bin/python -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false`.

Browser suite: install Playwright in a separate QA environment with Chromium available, serve the checkout using `python tools/serve_preview.py` (local byte-range support), then run `LEDGERPOINT_QA_URL=http://127.0.0.1:8001 python tools/browser_qa.py`. The default Python simple server is sufficient for static navigation but cannot validate seeking because it lacks byte-range support. Test artifacts go to `/tmp/ledgerpoint-*`; retained summaries are in `docs/release-evidence/`. No localhost preview is published.

## Deployment and external blockers

The runtime's restricted network policy denies the production Vercel domain (HTTP CONNECT 403); Vercel credentials are absent and no Vercel or Gmail connector is available. The prior review URL and production URL are reference values, not newly verified deployments. No new preview URL, deployment ID or production commit can be claimed.

Environment draft saved: tested installation instructions, service startup instructions, required custom domains (production, known review, api.vercel.com, vercel.com, www.datapoint.ie), and a VERCEL_TOKEN secret requirement scoped to api.vercel.com. User must review/save environment settings, securely bind the credential, and publish the environment. Draft saving does not apply network changes or publish snapshots. New preview hostnames may require additive allowance once Vercel returns them.

Release gates still open: authenticated preview deployment and smoke tests; production asset/hash/header/social-image parity; actual iPhone Safari and other requested browser/device coverage; manual screen-reader and 200%/400% zoom testing; manual caption synchronisation; final external/contact link checks. Security headers are configured but not verified on Vercel. The 80-row audit register distinguishes local evidence from remaining gaps.

Gmail: unchanged and unsent. Existing draft/recipient/attachment were not independently accessible. Update only after production verification as requested.

## Provisional score

82/100 against the R100 rubric: visual 13/15, media 8/10, financial 15/15, lab 15/15, mobile 8/10, accessibility 7/10, performance 4/5, reliability 4/5, application 8/10, production 0/5. This is a local-development assessment, not release approval or a 100/100 claim.
