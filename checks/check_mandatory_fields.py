# Check to validate that mandatory asset fields are present and not blank
from __future__ import annotations
from typing import List
import pandas as pd
from models import Finding
from .base import BaseCheck, Tables

class MandatoryFieldsCheck(BaseCheck):
    """Validates that required fields exist and contain non-blank values."""
    check_id = 'MANDATORY_FIELDS'
    name = 'Mandatory fields present'
    description = 'UNITID/UNITNO/STREET must exist and not be blank.'
    severity_default = 'ERROR'

    def __init__(self, assets_key: str = 'ASSETS', required=('UNITID','UNITNO','STREET')):
        """
        Initialize the mandatory fields check with configurable table and required columns.
        
        Args:
            assets_key: Name of the table containing asset data (default: 'ASSETS')
            required: Tuple of column names that must be present and non-blank (default: UNITID, UNITNO, STREET)
        """
        self.assets_key = assets_key
        self.required = list(required)

    def run(self, tables: Tables) -> List[Finding]:
        """Execute the mandatory fields validation check."""
        # Check if the assets table exists in the provided tables dictionary
        if self.assets_key not in tables:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing table: {self.assets_key}', field=self.assets_key)]
        
        # Retrieve the assets DataFrame
        df = tables[self.assets_key]
        
        # Check if all required columns exist in the DataFrame
        missing = [c for c in self.required if c not in df.columns]
        if missing:
            return [Finding('(DATASET)', self.check_id, 'ERROR', 'Missing required column(s): '+', '.join(missing), field=','.join(missing))]
        
        # Check for blank/null values in each required column
        findings: List[Finding] = []
        for col in self.required:
            # Create a mask for rows where the column is either null or blank (empty string after stripping whitespace)
            mask = df[col].isna() | (df[col].astype(str).str.strip()=='')
            if mask.any():
                # For each blank value, create a finding with the associated UNITID
                for unitid in df.loc[mask, 'UNITID'].astype(str).fillna('(UNKNOWN)'):
                    findings.append(Finding(str(unitid), self.check_id, self.severity_default,
                                            f"Mandatory field '{col}' is blank.", field=col))
        return findings
