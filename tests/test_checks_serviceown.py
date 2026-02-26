# Unit tests for ServiceOwnPlugRequiresCableNodCheck validation
# This check ensures that SERVICEOWN="PLUG" assets have corresponding entries in the CABLENOD table
import pandas as pd
from checks.check_serviceown_plug_requires_cablenod import ServiceOwnPlugRequiresCableNodCheck


def test_plug_no_cablenod_returns_dataset_error(assets_base_df, tables_factory):
    """Test that a dataset-level error is raised when CABLENOD table is missing entirely."""
    chk = ServiceOwnPlugRequiresCableNodCheck()
    tables = tables_factory(assets_base_df)  # no CABLENOD table provided
    findings = chk.run(tables)
    # Verify a single dataset-level error is returned
    assert len(findings) == 1
    assert findings[0].unitid == "(DATASET)"  # Dataset-level errors use "(DATASET)" as unitid
    assert "Missing table: CABLENOD" in findings[0].message


def test_plug_missing_link_column_returns_dataset_error(assets_base_df, tables_factory):
    """Test that a dataset-level error is raised when CABLENOD table lacks the required LINK_ID column."""
    chk = ServiceOwnPlugRequiresCableNodCheck()
    # Provide CABLENOD table with wrong column name instead of LINK_ID
    tables = tables_factory(assets_base_df, CABLENOD=pd.DataFrame({"WRONG": ["U1"]}))
    findings = chk.run(tables)
    # Verify a single dataset-level error is returned for missing column
    assert len(findings) == 1
    assert findings[0].unitid == "(DATASET)"
    assert "Missing column in CABLENOD: LINK_ID" in findings[0].message


def test_plug_all_linked_no_findings(assets_base_df, cablenod_ok_df, tables_factory):
    """Test that no findings are returned when all PLUG assets have corresponding CABLENOD entries."""
    chk = ServiceOwnPlugRequiresCableNodCheck()
    # Provide a valid CABLENOD table with all required PLUG assets
    tables = tables_factory(assets_base_df, CABLENOD=cablenod_ok_df)
    findings = chk.run(tables)
    # Verify that check passes with no validation errors
    assert findings == []


def test_plug_missing_u2_flags_one(assets_base_df, cablenod_missing_u2_df, tables_factory):
    """Test that missing CABLENOD entries for PLUG assets are correctly flagged."""
    chk = ServiceOwnPlugRequiresCableNodCheck()
    # Provide CABLENOD table that's missing entry for U2
    tables = tables_factory(assets_base_df, CABLENOD=cablenod_missing_u2_df)
    findings = chk.run(tables)
    # Verify only U2 is flagged as missing from CABLENOD
    unitids = {f.unitid for f in findings}
    assert unitids == {"U2"}
    # Verify the error message indicates the linking requirement (LINK_ID == UNITID)
    assert all("LINK_ID == UNITID" in f.message for f in findings)
