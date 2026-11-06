# LedgerPoint film: review-only release gate (4 Nov 2026)

## Approved source and local media validation
- Film: 1920×1080 H.264, 30 fps, approximately 65.7 seconds.
- Narration: AAC, approximately 65.724 seconds; starts at 0.000 seconds.
- Video starts at 0.000 seconds; A/V stream duration delta about 0.024 seconds.
- MP4 has fast-start metadata (moov before mdat); ffmpeg full decode exited 0.
- Approved default playback is 1.0×, never 1.5×.
- Local MP4 SHA-256: `8d7cfdf2351cfc17e5ecda19` (prefix only).
- Local thumbnail SHA-256: `bb730caba9774329f2b2e09c` (prefix only).

## Mandatory file replacement on this review branch
Copy the approved release package files without transcoding:
- `assets/ledgerpoint-intro-web.mp4` (4,667,050 bytes)
- `assets/ledgerpoint-thumbnail.jpg` (92,489 bytes)
- `assets/ledgerpoint-intro-en.vtt` (12 cues, retimed to 65.72s; provisional)

The captions committed to this branch are retimed, not verified against the final spoken narration. Manual review and corrected word-level cue timings are required before publication.

## Required preview checks
1. Confirm preview is from `review/film-first-and-overview` at the expected commit and not production.
2. On desktop Chromium and mobile emulation, film loads, audio starts with video, 1× rate, no decoder errors, controls work, captions display, and replay works.
3. On real iPhone Safari and Android Chrome, check play gesture, audible narration, caption timing, rotation, low-bandwidth buffering, and the Explore reveal.
4. Verify reduced-motion preference skips animation and Explore remains keyboard accessible.
5. Check no 404 for MP4, JPEG, VTT or CV PDF, and verify response MIME types and range requests.
6. Audit About & Application, CV new-tab viewing, direct portfolio/project URLs, and absence of the security role.
7. Do not promote production or send the application email until all checks pass.

## Access blocker
The Vercel account connected to this session has no linked projects; lookup of `ledgerpoint-ai` returned 404. This does **not** prove the project is absent from another Vercel account/team.
The GitHub connector can write text but cannot ingest binary files from the isolated local workspace; the approved MP4 and JPEG are therefore not uploaded by this commit.

**Release status: HOLD.** Do not interpret this file as a successful preview deployment or a real-device test.
