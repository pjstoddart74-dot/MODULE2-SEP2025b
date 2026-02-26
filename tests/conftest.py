import pandas as pd
import pytest

@pytest.fixture
def assets_base_df():
    # U1 and U2 are PL UG so they must appear in CABLENOD by LINK_ID => UNITID
    return pd.DataFrame({
        "UNITID": ["U1", "U2", "U3"],
        "UNITNO": ["A-001", "A-002", "A-003"],
        "STREET": ["Main St", "King St", "Queen St"],
        "SERVICEOWN": ["PL UG", "PL UG", "DNO"],
        "INSTALLDATE": ["2020-01-01", "2035-01-01", None],
    })

@pytest.fixture
def cablenod_ok_df():
    # Both U1 & U2 present, so PL UG rule passes for base data
    return pd.DataFrame({"LINK_ID": ["U1", "U2", "U9"]})

@pytest.fixture
def cablenod_missing_u2_df():
    # U2 missing here, expect a finding for U2
    return pd.DataFrame({"LINK_ID": ["U1", "X"]})

@pytest.fixture
def tables_factory():
    def _build(assets_df, **tables):
        out = {"ASSETS": assets_df}
        out.update(tables)
        return out
    return _build
