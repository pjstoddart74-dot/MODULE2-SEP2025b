# Unit tests for validating UNITNO field format
import pytest
import pandas as pd
from checks.check_unitno_format import UnitNoFormatCheck

# Parametrized test that validates various UNITNO formats
# Tests both valid and invalid formats to ensure the check correctly identifies malformed values
@pytest.mark.parametrize("unitno, is_valid", [
    ("A1", True),  # Valid: letter followed by digit
    ("AB123", True),  # Valid: multiple letters followed by digits
    ("A-001", True),  # Valid: letter with hyphen separator
    ("A.001", True),  # Valid: letter with period separator
    ("A 001", True),  # Valid: letter with space separator
    ("A12Z", True),  # Valid: letters and digits mixed
    ("123A", False),  # Invalid: starts with digit instead of letter
    ("A_12", False),  # Invalid: underscore separator not allowed by default pattern
    ("A--12", False),  # Invalid: double separator not allowed
    ("", False),  # Invalid: empty string
    (None, False),  # Invalid: null value
])
def test_unitno_single_values(unitno, is_valid):
    # Create a test DataFrame with a single row containing the UNITNO to validate
    df = pd.DataFrame({
        "UNITID": ["U1"],
        "UNITNO": [unitno],
        "STREET": ["X"],
        "SERVICEOWN": ["DNO"],
        "INSTALLDATE": ["2020-01-01"],
    })
    # Wrap the DataFrame in the required tables dictionary structure
    tables = {"ASSETS": df}
    # Instantiate the check with default pattern (allows single optional separator)
    chk = UnitNoFormatCheck()  # uses default pattern allowing single optional sep
    # Execute the validation check
    findings = chk.run(tables)
    # Assert that valid formats produce no findings and invalid formats produce exactly one finding
    assert (len(findings) == 0) if is_valid else (len(findings) == 1)


def test_unitno_flags_only_bad_rows(assets_base_df, tables_factory):
    # Copy the base test DataFrame to avoid modifying the fixture
    df = assets_base_df.copy()
    # Modify only the U2 row with an invalid UNITNO (underscore is not allowed by default pattern)
    df.loc[df["UNITID"] == "U2", "UNITNO"] = "BAD_22"  # underscore not allowed by default pattern

    # Create check instance
    chk = UnitNoFormatCheck()
    # Create tables dictionary using the factory fixture
    tables = tables_factory(df)
    # Execute the validation check
    findings = chk.run(tables)

    # Verify that only the U2 row was flagged as invalid (not other rows)
    assert {f.unitid for f in findings} == {"U2"}
    # Verify the finding details
    f = findings[0]
    assert "UNITNO format" in f.message  # Check that the error message references UNITNO format
    assert f.field == "UNITNO"  # Confirm the field name in the finding
