import pandas as pd
from checks.check_install_dates import InstallDateNotInFutureCheck


def test_install_date_missing_column_returns_dataset_error(tables_factory):
    df = pd.DataFrame({"UNITID": ["U1"], "UNITNO": ["A1"], "STREET": ["X"]})
    chk = InstallDateNotInFutureCheck()
    tables = tables_factory(df)
    findings = chk.run(tables)
    assert len(findings) == 1
    assert findings[0].unitid == "(DATASET)"
    assert "Missing column: INSTALLDATE" in findings[0].message


def test_install_date_in_future_flags_row():
    df = pd.DataFrame({
        "UNITID": ["U1", "U2"],
        "UNITNO": ["A1", "A2"],
        "STREET": ["X", "Y"],
        "SERVICEOWN": ["DNO", "DNO"],
        "INSTALLDATE": ["2035-01-01", "2020-01-01"],
    })
    chk = InstallDateNotInFutureCheck()
    findings = chk.run({"ASSETS": df})
    unitids = {f.unitid for f in findings}
    assert unitids == {"U1"}
