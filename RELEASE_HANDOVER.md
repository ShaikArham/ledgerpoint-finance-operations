# LedgerPoint release handover

Status: REVIEW BUILD. Production approval withheld pending verified media and real-device QA.

## Current implementation
- Branch: `review/film-first-and-overview`
- Production: https://ledgerpoint-ai.vercel.app/
- Review: https://ledgerpoint-finance-operations-puhirysvf.vercel.app/
- Finance scenario: fictional October 2026; €1,000 net sales, €300 net expenses, €700 recorded operating profit, €131 net matched settlements, €12 unresolved bank debit.
- Hypothetical lab changes never mutate posted figures.

## Binary assets required before release
Place these exact files from `LedgerPoint_Release_Assets_With_Original_CV.zip` into the repository's `assets/` folder or deploy to stable public URLs and update HTML/JS:
- `assets/ledgerpoint-intro-web.mp4`
- `assets/ledgerpoint-thumbnail.jpg`
- `assets/ledgerpoint-intro-en.vtt`
- `assets/Shaik_Arham_Saquib_DataPoint.pdf` (the original approved CV; do not replace)

The current GitHub text-file connector cannot transfer local binary files. Do not claim these assets have been published without checking actual HTTP 200 responses and playback.

## Required acceptance tests
1. Film poster loads at its exact URL and matches approved image.
2. MP4 returns HTTP 200 with video/mp4; plays with sound inline in desktop Chrome and iPhone Safari; replay and captions work.
3. Original CV PDF downloads successfully from the About section and opens as the original document.
4. Verify responsive layouts at 320, 375, 390, 430, 768, 1024, 1440, and 1920px.
5. Test investigation lab all three transactions, four hypotheses, hold and reset. Recorded €700 and €131 must not change.
6. Check keyboard navigation, focus, all anchors, external URLs, console and network errors.
7. Only after these pass, promote to production and verify production alias.

## Email
A Gmail draft to Lydia@DataPoint.ie has been created with the original CV attached. It has NOT been sent. Review the link and remove the pre-send note before sending; do not send a preview URL if production is required.
