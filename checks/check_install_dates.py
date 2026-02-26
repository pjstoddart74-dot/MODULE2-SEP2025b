# Check to validate that asset installation dates are not in the future
from __future__ import annotations
from typing import List
import pandas as pd
from models import Finding
from .base import BaseCheck, Tables

class InstallDateNotInFutureCheck(BaseCheck):
    """Validates that asset INSTALLDATE values are not in the future."""
    check_id = 'INSTALL_DATE_FUTURE'
    name = 'Install date not in the future'
    description = 'Flags assets with INSTALLDATE later than today.'
    severity_default = 'WARN'

    def __init__(self, assets_key: str = 'ASSETS', date_col: str = 'INSTALLDATE'):
        """
        Initialize the install date check with configurable table and column names.
        
        Args:
            assets_key: Name of the table containing asset data (default: 'ASSETS')
            date_col: Name of the date column to validate (default: 'INSTALLDATE')
        """
        self.assets_key = assets_key
        self.date_col = date_col

    def run(self, tables: Tables) -> List[Finding]:
        """Execute the install date validation check."""
        # Check if the assets table exists in the provided tables dictionary
        if self.assets_key not in tables:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing table: {self.assets_key}', field=self.assets_key)]
        
        # Retrieve the assets DataFrame
        df = tables[self.assets_key]
        
        # Check if the date column exists in the assets table
        if self.date_col not in df.columns:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing column: {self.date_col}', field=self.date_col)]
        
        # Convert date column to datetime, coercing invalid dates to NaT (Not a Time)
        dates = pd.to_datetime(df[self.date_col], errors='coerce')
        # Create a mask for rows where the date exists and is in the future (after today at midnight)
        mask = dates.notna() & (dates > pd.Timestamp.today().normalize())
        
        # Build findings list for all assets with future install dates
        out: List[Finding] = []
        for _, row in df.loc[mask, ['UNITID', self.date_col]].iterrows():
            # Create a finding for each asset with a future date
            out.append(Finding(str(row['UNITID']), self.check_id, self.severity_default,
                               'Install date is in the future.', field=self.date_col,
                               current_value=str(row[self.date_col]), expected='<= today'))
        return out
