from __future__ import annotations
from typing import List
import pandas as pd
from models import Finding
from .base import BaseCheck, Tables

class ServiceOwnPlugRequiresCableNodCheck(BaseCheck):
    check_id = 'SERVICEOWN_PLUG_REQUIRES_CABLENOD'
    name = "SERVICEOWN 'PL UG' has CABLENOD link(s)"
    description = "For UNITS with SERVICEOWN='PL UG', require ≥1 CABLENOD row where LINK_ID == UNITID."
    severity_default = 'ERROR'

    def __init__(self, assets_key: str = 'ASSETS', cab_key: str = 'CABLENOD',
                 unitid_col: str = 'UNITID', serviceown_col: str = 'SERVICEOWN', link_col: str = 'LINK_ID',
                 plug_value: str = 'PL UG'):
        self.assets_key = assets_key
        self.cab_key = cab_key
        self.unitid_col = unitid_col
        self.serviceown_col = serviceown_col
        self.link_col = link_col
        self.plug_value = plug_value

    def run(self, tables: Tables) -> List[Finding]:
        if self.assets_key not in tables:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing table: {self.assets_key}', field=self.assets_key)]
        if self.cab_key not in tables:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing table: {self.cab_key}', field=self.cab_key)]
        a = tables[self.assets_key]
        c = tables[self.cab_key]
        miss_a = [x for x in (self.unitid_col, self.serviceown_col) if x not in a.columns]
        if miss_a:
            return [Finding('(DATASET)', self.check_id, 'ERROR', 'Missing assets column(s): '+', '.join(miss_a), field=','.join(miss_a))]
        if self.link_col not in c.columns:
            return [Finding('(DATASET)', self.check_id, 'ERROR', f'Missing column in CABLENOD: {self.link_col}', field=self.link_col)]

        svc = a[self.serviceown_col].astype(str).str.strip().str.casefold()
        plug = self.plug_value.strip().casefold()
        plug_mask = svc.eq(plug)
        if not plug_mask.any():
            return []

        unitids = a[self.unitid_col].astype(str).str.strip()
        links = set(c[self.link_col].astype(str).str.strip().dropna())
        missing_mask = plug_mask & (~unitids.isin(links))

        out: List[Finding] = []
        for uid in unitids[missing_mask]:
            out.append(Finding(str(uid), self.check_id, self.severity_default,
                               "SERVICEOWN is 'PL UG' but no CABLENOD row with LINK_ID == UNITID.",
                               field=self.serviceown_col, current_value=self.plug_value,
                               expected='At least 1 matching CABLENOD record'))
        return out
