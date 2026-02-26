"""
Test module for InstallDateNotInFutureCheck validation.

This module contains unit tests for the InstallDateNotInFutureCheck class,
which validates that asset installation dates are not set to future dates.
Tests cover:
- Missing INSTALLDATE column handling
- Detection of future installation dates
"""

import pandas as pd
from checks.check_install_dates import InstallDateNotInFutureCheck


def test_install_date_missing_column_returns_dataset_error(tables_factory):
    """
    Test that a dataset-level error is raised when INSTALLDATE column is missing.
    
    This test verifies that the check properly handles the case where the
    required INSTALLDATE column is absent from the input dataframe, returning
    a dataset-level finding with an appropriate error message.
    
    Args:
        tables_factory: Pytest fixture that creates a tables dictionary from a dataframe
        
    Returns:
        None
        
    Asserts:
        - Exactly one finding is returned
        - The finding unitid is "(DATASET)" indicating a dataset-level error
        - The error message mentions the missing INSTALLDATE column
    """
    """
    Test that a dataset-level error is raised when INSTALLDATE column is missing.
    
    This test verifies that the check properly handles the case where the
    required INSTALLDATE column is absent from the input dataframe, returning
    a dataset-level finding with an appropriate error message.
    
    Args:
        tables_factory: Pytest fixture that creates a tables dictionary from a dataframe
        
    Returns:
        None
        
    Asserts:
        - Exactly one finding is returned
        - The finding unitid is "(DATASET)" indicating a dataset-level error
        - The error message mentions the missing INSTALLDATE column
    """
    # Create a dataframe with required columns but missing INSTALLDATE
    df = pd.DataFrame({"UNITID": ["U1"], "UNITNO": ["A1"], "STREET": ["X"]})
    chk = InstallDateNotInFutureCheck()
    # Use factory to convert dataframe into the expected tables dictionary structure
    tables = tables_factory(df)
    # Execute the check against the incomplete tables
    findings = chk.run(tables)
    # Validate that exactly one error is found
    assert len(findings) == 1
    # Verify it's a dataset-level error (not a row-level error)
    assert findings[0].unitid == "(DATASET)"
    # Verify the error message is descriptive
    assert "Missing column: INSTALLDATE" in findings[0].message


def test_install_date_in_future_flags_row():
    """
    Test that rows with future installation dates are correctly identified as violations.
    
    This test verifies that the check can detect when the INSTALLDATE field
    contains a date in the future, which is an invalid state for an asset
    that should have already been installed. Only the row with the future
    date should be flagged.
    
    Returns:
        None
        
    Asserts:
        - The set of flagged UNITIDs contains only "U1" (the unit with future date)
        - The unit with past date "U2" is not flagged
    """
    """
    Test that rows with future installation dates are correctly identified as violations.
    
    This test verifies that the check can detect when the INSTALLDATE field
    contains a date in the future, which is an invalid state for an asset
    that should have already been installed. Only the row with the future
    date should be flagged.
    
    Returns:
        None
        
    Asserts:
        - The set of flagged UNITIDs contains only "U1" (the unit with future date)
        - The unit with past date "U2" is not flagged
    """
    # Create a test dataframe with two units: one with a future date and one with a valid past date
    df = pd.DataFrame({
        "UNITID": ["U1", "U2"],
        "UNITNO": ["A1", "A2"],
        "STREET": ["X", "Y"],
        "SERVICEOWN": ["DNO", "DNO"],
        "INSTALLDATE": ["2035-01-01", "2020-01-01"],  # U1 has future date, U2 has valid past date
    })
    chk = InstallDateNotInFutureCheck()
    # Execute the check against the tables
    findings = chk.run({"ASSETS": df})
    # Extract the set of UNITIDs that were flagged as having violations
    unitids = {f.unitid for f in findings}
    # Verify only the unit with the future installation date is flagged
    assert unitids == {"U1"}
