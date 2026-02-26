# Check to validate that UNITNO field follows the expected format pattern
from __future__ import annotations
import re
from typing import List
import pandas as pd
from models import Finding
from .base import BaseCheck, Tables

class UnitNoFormatCheck(BaseCheck):
    """Validates that UNITNO values match the required format using regex pattern matching."""
    check_id = 'UNITNO_FORMAT'
    name = 'UNITNO format'
    description = "Letters (1+) + optional separator + digits (1+) + optional trailing letters (1+)."
    severity_default = 'ERROR'

    def __init__(self, assets_key: str = 'ASSETS', unitid_col: str = 'UNITID', unitno_col: str = 'UNITNO',
                 pattern: str = r'^[A-Za-z]+[ .-]?\d+(?:[A-Za-z]+)?$', ignore_case: bool = True):
        """
        Initialize the UNITNO format check with configurable table, columns, and validation pattern.
        
        Args:
            assets_key: Name of the table containing asset data (default: 'ASSETS')
            unitid_col: Name of the unit identifier column (default: 'UNITID')
            unitno_col: Name of the unit number column to validate (default: 'UNITNO')
            pattern: Regex pattern to validate UNITNO format. Default pattern: 
                    letters (1+) + optional separator (space/hyphen/period) + digits (1+) + optional trailing letters
            ignore_case: Whether to perform case-insensitive matching (default: True)
        """
        self.assets_key = assets_key
        self.unitid_col = unitid_col
        self.unitno_col = unitno_col
        # Compile regex pattern with optional IGNORECASE flag
        flags = re.IGNORECASE if ignore_case else 0
        self._rx = re.compile(pattern, flags)
        self._pattern = pattern

    def run(self, tables: Tables) -> List[Finding]:
        """Execute the UNITNO format validation check."""
        # Check if the assets table exists in the provided tables dictionary
        if self.assets_key not in tables:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing table: {self.assets_key}', field=self.assets_key)]
        
        # Retrieve the assets DataFrame
        df = tables[self.assets_key]
        
        # Check if required columns exist in the DataFrame
        miss = [c for c in (self.unitid_col, self.unitno_col) if c not in df.columns]
        if miss:
            return [Finding('(DATASET)', self.check_id, 'ERROR', 'Missing column(s): '+', '.join(miss), field=','.join(miss))]
        
        # Iterate through each row and validate UNITNO format against the regex pattern
        out: List[Finding] = []
        for _, row in df[[self.unitid_col, self.unitno_col]].iterrows():
            # Extract UNITID, defaulting to '(UNKNOWN)' if null
            uid = str(row[self.unitid_col]).strip() if pd.notna(row[self.unitid_col]) else '(UNKNOWN)'
            # Extract UNITNO value
            raw = row[self.unitno_col]
            # Normalize UNITNO: convert null to empty string, otherwise strip whitespace
            val = '' if pd.isna(raw) else str(raw).strip()
            # Check if UNITNO matches the expected format pattern
            if not self._rx.match(val):
                # Create a finding for invalid format
                out.append(Finding(uid, self.check_id, self.severity_default,
                                   'UNITNO format does not match expected pattern.',
                                   field=self.unitno_col, current_value=val or None, expected=self._pattern))
        return out
