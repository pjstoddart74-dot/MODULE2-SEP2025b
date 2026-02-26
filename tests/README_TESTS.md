# Tests bundle for Option A (single `run(tables)` checks)

## How to use
1. Copy `tests/` and `pytest.ini` into the **root** of your Option A project (same level as `engine.py`, `checks/`, etc.).
2. Install dev deps:
   ```bash
   python -m pip install pytest pytest-cov
   ```
3. Run:
   ```bash
   python -m pytest --cov=checks --cov=engine --cov=reporting --cov-report=term-missing
   ```

These tests assume your project exposes:
- `checks/check_serviceown_plug_requires_cablenod.py` → `ServiceOwnPlugRequiresCableNodCheck`
- `checks/check_unitno_format.py` → `UnitNoFormatCheck`
- `checks/check_install_dates.py` → `InstallDateNotInFutureCheck`
- `checks/check_mandatory_fields.py` → `MandatoryFieldsCheck`
- `engine.py` → `discover_checks`, `run_selected_checks`
- `reporting.py` → `build_output`, `findings_to_dataframe`
