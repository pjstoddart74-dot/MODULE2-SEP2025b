from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Finding:
    unitid: str
    check_id: str
    severity: str
    message: str
    field: Optional[str] = None
    current_value: Optional[str] = None
    expected: Optional[str] = None
