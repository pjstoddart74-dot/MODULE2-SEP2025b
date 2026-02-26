import pandas as pd
from engine import discover_checks, run_selected_checks


def test_engine_discovers_checks():
    checks = discover_checks()
    # Expect at least our four checks to be present
    for cid in [
        'MANDATORY_FIELDS',
        'INSTALL_DATE_FUTURE',
        'SERVICEOWN_PLUG_REQUIRES_CABLENOD',
        'UNITNO_FORMAT',
    ]:
        assert cid in checks


def test_engine_runs_specific_check():
    assets = pd.DataFrame({
        'UNITID': ['U1'], 'UNITNO': ['A1'], 'STREET': ['X'], 'SERVICEOWN': ['DNO'], 'INSTALLDATE': ['2020-01-01']
    })
    out = run_selected_checks({'ASSETS': assets}, selected_ids=['MANDATORY_FIELDS'])
    assert out == []
