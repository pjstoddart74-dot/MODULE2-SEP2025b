from __future__ import annotations
from typing import Dict, List, Type
import importlib, pkgutil
import pandas as pd
import checks
from checks.base import BaseCheck
from models import Finding
from check_logger import log_check_execution

# Auto-import all modules under checks/ so subclasses are defined

def _auto_import_check_modules() -> None:
    for m in pkgutil.iter_modules(checks.__path__):
        importlib.import_module(f"{checks.__name__}.{m.name}")

# Discover all checks as subclasses of BaseCheck

def discover_checks() -> Dict[str, Type[BaseCheck]]:
    _auto_import_check_modules()
    found: Dict[str, Type[BaseCheck]] = {}
    for cls in BaseCheck.__subclasses__():
        cid = getattr(cls, 'check_id', None)
        if cid:
            found[cid] = cls
    return found

# Run selected checks (if None, run them all)

def run_selected_checks(tables: Dict[str, pd.DataFrame], selected_ids: List[str] | None = None) -> List[Finding]:
    checks_map = discover_checks()
    if not selected_ids:
        selected_ids = list(checks_map.keys())
    findings: List[Finding] = []
    for cid in selected_ids:
        cls = checks_map.get(cid)
        if not cls:
            continue
        chk = cls()
        check_findings = chk.run(tables)
        findings.extend(check_findings)
        log_check_execution(cid, len(check_findings))
    return findings
