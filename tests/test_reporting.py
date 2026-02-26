import pandas as pd
from reporting import build_output, findings_to_dataframe
from models import Finding


def test_findings_to_dataframe_and_join():
    assets = pd.DataFrame({
        'UNITID': ['U1','U2'], 'UNITNO': ['A1','A2'], 'STREET': ['Main','King']
    })
    # two findings -> one for U2 and one dataset-level
    findings = [
        Finding(unitid='U2', check_id='X', severity='ERROR', message='Oops', field='UNITNO', current_value='bad', expected='rx'),
        Finding(unitid='(DATASET)', check_id='Y', severity='ERROR', message='Missing something')
    ]
    fdf = findings_to_dataframe(findings)
    out = build_output(fdf, assets, asset_cols=("UNITID","UNITNO","STREET"))

    # First row should be U2 with joined fields
    row = out[out['UNITID']=='U2'].iloc[0]
    assert row['UNITNO'] == 'A2'
    assert row['STREET'] == 'King'

    # Dataset-level finding will have NaNs for asset columns (no join match)
    ds = out[out['UNITID']=='(DATASET)'].iloc[0]
    assert pd.isna(ds['UNITNO'])
