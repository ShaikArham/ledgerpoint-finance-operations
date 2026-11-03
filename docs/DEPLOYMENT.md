# Deploy LedgerPoint on Streamlit Community Cloud

1. Sign in to https://share.streamlit.io/ with GitHub.
2. Choose **Create app** / **Deploy an app** and select **Deploy a public app from GitHub** (labels may vary).
3. Select repository `ShaikArham/ledgerpoint-finance-operations`, branch `main`, entrypoint `app.py`.
4. Select Python 3.11 in advanced settings if offered.
5. Deploy. Streamlit Cloud installs dependencies from `requirements.txt` and launches `app.py`.
6. Verify all five tabs, reconciliation exceptions and CSV downloads on desktop and mobile.

If the private repository does not appear, check GitHub authorisation and Streamlit Community Cloud permissions. Do not make the repository public merely to troubleshoot access. A public app URL may be accessible to others even when its source repository is private.

Commits to `main` normally trigger a rebuild or rerun, sometimes with a delay. Check deployment logs if an update fails.

The application contains only fictional financial data. It is read-only, uses in-memory calculations, and has no real bank or payroll integration.
