from __future__ import annotations
import pandas as pd
from models import Finding

# Build a flat DataFrame from findings and enrich with asset fields

def findings_to_dataframe(findings: list[Finding]) -> pd.DataFrame:
    cols = ['unitid','check_id','severity','message','field','current_value','expected']
    if not findings:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame([{
        'unitid': f.unitid,
        'check_id': f.check_id,
        'severity': f.severity,
        'message': f.message,
        'field': f.field,
        'current_value': f.current_value,
        'expected': f.expected,
    } for f in findings], columns=cols)

# Optionally join to asset details

def build_output(findings_df: pd.DataFrame, assets_df: pd.DataFrame, asset_cols=("UNITID","UNITNO","STREET")) -> pd.DataFrame:
    if findings_df.empty:
        return pd.DataFrame(columns=list(asset_cols)+["check_id","severity","message","field","current_value","expected"])
    a = assets_df.copy(); a['UNITID'] = a['UNITID'].astype(str)
    f = findings_df.copy(); f['UNITID'] = f['unitid'].astype(str)
    out = f.merge(a[list(asset_cols)].drop_duplicates('UNITID'), on='UNITID', how='left')
    return out[list(asset_cols)+["check_id","severity","message","field","current_value","expected"]]

# Excel export (Findings + Summary)

def export_findings_excel(output_df: pd.DataFrame, out_path: str) -> None:
    with pd.ExcelWriter(out_path, engine='openpyxl') as w:
        output_df.to_excel(w, index=False, sheet_name='Findings')
        if not output_df.empty:
            summary = (output_df.groupby(["check_id","severity"], dropna=False)
                       .size().reset_index(name='count')
                       .sort_values(["check_id","severity"]))
            summary.to_excel(w, index=False, sheet_name='Summary')
