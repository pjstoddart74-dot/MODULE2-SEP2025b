import pandas as pd
from checks.check_mandatory_fields import MandatoryFieldsCheck


def test_mandatory_fields_missing_table_returns_dataset_error():
    chk = MandatoryFieldsCheck()
    findings = chk.run({})
    assert len(findings) == 1
    assert findings[0].unitid == "(DATASET)"
    assert "Missing table: ASSETS" in findings[0].message


def test_mandatory_fields_blank_values_flag_rows():
    df = pd.DataFrame({
        "UNITID": ["U1", "U2"],
        "UNITNO": ["", "A2"],
        "STREET": ["Main", ""],
        "SERVICEOWN": ["DNO", "DNO"],
        "INSTALLDATE": ["2020-01-01", "2020-01-01"],
    })
    chk = MandatoryFieldsCheck()
    findings = chk.run({"ASSETS": df})
    unitids = {f.unitid for f in findings}
    assert unitids == {"U1", "U2"}
