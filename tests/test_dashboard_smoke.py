"""Smoke-test Streamlit rendering, including the manual journal sandbox."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")

def test_dashboard_loads_without_uncaught_exceptions():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception, [str(error.message) for error in app.exception]
    assert len(app.tabs) == 12

def test_manual_journal_form_is_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Manual journal sandbox" in heading.value for heading in app.subheader)
    assert any(button.label == "Reset sandbox to baseline" for button in app.button)

def test_exception_case_tab_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Exception case management" in heading.value for heading in app.subheader)

def test_budget_forecast_tab_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Budget versus actual" in heading.value for heading in app.subheader)

def test_cash_flow_tab_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Cash flow and working capital" in heading.value for heading in app.subheader)

def test_payroll_demo_tab_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Illustrative payroll operations" in heading.value for heading in app.subheader)

def test_approvals_audit_tab_visible():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    assert any("Approvals and operational audit history" in heading.value for heading in app.subheader)
