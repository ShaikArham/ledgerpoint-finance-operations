# LedgerPoint

**An independent finance-operations portfolio project by Shaik Arham Saquib.** LedgerPoint combines a public, responsive case-study website with a separate Python/Streamlit demonstration of fictional accounting workflows.

**[Explore the LedgerPoint website](https://ledgerpoint-ai.vercel.app/)** · **[Open the Streamlit demo](https://ledgerpoint-finance-operations.streamlit.app/)** · **[Reviewer guide](REVIEWER_GUIDE.md)** · **[QA status](QA_STATUS.md)**

> **Independent project.** LedgerPoint is not affiliated with, endorsed by, or commissioned by DataPoint Ireland. All businesses, customers, transactions, financial figures and scenarios are fictional. It is not production accounting software or a source of statutory tax or payroll advice.

## Website and application journey

The standalone website presents a fictional finance-operations case study with an executive overview, invoices, reconciliation, reporting, investigation material, an introductory film and an **About & Application** section. It is built with HTML, CSS and JavaScript, with no frontend framework required.

- **Website:** https://ledgerpoint-ai.vercel.app/
- **Introduction:** `assets/ledgerpoint-intro-web.mp4`, with thumbnail, poster, captions and transcript
- **View CV:** opens `assets/Shaik_Arham_Saquib_DataPoint.pdf` in a new tab
- **Download CV:** uses `/api/download-cv`, a server-side response intended to provide a downloadable PDF attachment
- **Legal and privacy notice:** `legal.html`

The download endpoint is implemented and the latest Vercel build was reported READY. **A successful download on every Safari/iPhone configuration has not yet been independently verified.** PDF behavior may vary by browser and device.

### Visitor activity notifications

`activity-alerts.js` collects basic engagement flags for a page session: website opened, introduction video played, CV viewed (link clicked) and CV download requested (link clicked). It posts a summary to the Vercel serverless endpoint `api/notify.js`, which sends an email through Resend.

- The Resend credential is read from the **server-side** environment variable `RESEND_API_KEY`. **Never commit the key** or expose it in browser JavaScript.
- Vercel network headers may supply an **approximate IP-derived city, region and country**. This is not GPS, a verified physical location or a street address; network routing, VPNs and privacy relays can make it inaccurate.
- CV clicks are **not** proof that a PDF was successfully saved or read.
- The notification endpoint currently has **no server-side rate limiting**. Add abuse protection before relying on it for sustained public traffic.
- The privacy notice should be reviewed and updated to explicitly describe activity notification processing.

## Streamlit finance demonstration

The separate `app.py` dashboard and `src/ledgerpoint/` modules demonstrate:

| Area | Fictional functionality |
| --- | --- |
| Accounting | Balanced journals, account validation, reversals, period locks and trial balance |
| Invoices | Sales and purchase invoices, CSV staging and illustrative VAT |
| Receivables and settlements | Receipts, supplier payments, balances and ageing |
| Bank reconciliation | Reference/amount matching, duplicates and unmatched entries |
| Reporting | Profit and loss, simplified balance sheet, monthly results and variance |
| Controls and investigations | Exception cases, maker-checker-style session demonstrations and close checks |
| Additional scenarios | Budget, cash movement and simplified fictional payroll |

The built-in October 2026 scenario includes a deliberately unresolved bank-only debit. It is **not** automatically posted. Approval history is session-only, with no real user authentication, immutable audit trail or payment authority. Payroll does **not** calculate Irish PAYE, USC, PRSI or statutory deductions.

## Run locally

Use Python 3.11+ and Git. On Windows PowerShell:

```powershell
git clone https://github.com/ShaikArham/ledgerpoint-finance-operations.git
cd ledgerpoint-finance-operations
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The website's `api/` routes are Vercel serverless functions. A static local file server does not reproduce those endpoints or Vercel's geolocation headers.

## Key repository files

```text
index.html                 Public case-study website
styles.css, script.js      Website styling and interactions
intro.js, film.*           Introduction and film presentation
activity-alerts.js         Client-side activity summary
api/notify.js              Server-side Resend notification endpoint
api/download-cv.js         Server-side PDF attachment endpoint
assets/                    Video, captions, images and public CV
vercel.json                Vercel routing and security headers
legal.html                 Legal and privacy information
app.py                     Streamlit finance dashboard
src/ledgerpoint/           Python finance-operations modules
tests/                     Automated tests
docs/                      Accounting assumptions, phase and release notes
.github/workflows/         GitHub Actions workflows
```

## Deployment and verification

The website is hosted on Vercel. The active review work has been developed on `review/film-first-and-overview`; the `main` branch and GitHub Pages workflow may not reflect the latest Vercel website. An intermediate preview build at commit `881005a` failed because the configuration referenced a function not yet committed. A later deployment containing `api/download-cv.js` reached **READY**. This does not by itself prove end-to-end Safari download behavior.

Review [release results](docs/RELEASE_RESULTS.md), [video release gate](docs/VIDEO_RELEASE_GATE_2026-11-04.md), [QA status](QA_STATUS.md) and [the reviewer guide](REVIEWER_GUIDE.md) for the scope and limitations of earlier checks. Historical test counts are not evidence of a fresh test run.

## Security and privacy boundaries

- Do not commit API keys, `.env` files, passwords or other secrets.
- Public CV and portfolio assets are intentionally accessible to anyone with the URL.
- This demo does not use real financial, payroll, customer or banking records.
- It does not connect to a real bank, submit payments, or provide statutory accounts.
- Approximate location and browser classification are fallible; no visitor identity is established by these notifications.

**Author:** Shaik Arham Saquib · Independent portfolio project · November 2026
