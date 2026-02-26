from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Dict
import threading
import pandas as pd
import os

import checks  # ensure package exists
from engine import discover_checks, run_selected_checks
from io_odbc import load_dataset_odbc
from reporting import findings_to_dataframe, build_output, export_findings_excel
import sql_defs

class App(tk.Tk):
    """Main GUI application for Mayrise PFI Data Verification."""
    
    def __init__(self):
        """Initialize the application window and state."""
        super().__init__()
        self.title('Mayrise PFI Data Verification - Option A (GUI)')
        self.geometry('1120x780')

        # State
        self.conn_str = tk.StringVar(value='DSN=TYNESQL;Trusted_Connection=Yes;')
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self.assets_df: pd.DataFrame | None = None
        self.tables: Dict[str, pd.DataFrame] = {}
        self.output_df: pd.DataFrame | None = None
        self.progress_value = tk.DoubleVar(value=0.0)
        self.progress_text = tk.StringVar(value='Idle')
        self._is_running = False
        self.log_text = None

        self._build_ui()
        self._populate_checks()

    def _build_ui(self):
        # Connection frame
        frm_conn = tk.LabelFrame(self, text='ODBC connection (static SQL in sql_defs.py)')
        frm_conn.pack(fill='x', padx=10, pady=10)
        tk.Label(frm_conn, text='Connection string:').grid(row=0, column=0, sticky='w')
        tk.Entry(frm_conn, textvariable=self.conn_str, width=120).grid(row=0, column=1, padx=8, pady=5, sticky='we')
        frm_conn.grid_columnconfigure(1, weight=1)

        # Middle area: checks + log
        mid = tk.Frame(self); mid.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollable checks list
        frm_checks = tk.LabelFrame(mid, text='Select checks to run')
        frm_checks.pack(side='left', fill='both', expand=True, padx=(0,8))
        canvas = tk.Canvas(frm_checks)
        scrollbar = tk.Scrollbar(frm_checks, orient='vertical', command=canvas.yview)
        scrollable = tk.Frame(canvas)
        scrollable.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True); scrollbar.pack(side='right', fill='y')
        self.checks_container = scrollable

        # Run log panel with toolbar
        frm_log = tk.LabelFrame(mid, text='Run log')
        frm_log.pack(side='right', fill='both', expand=True)
        log_toolbar = tk.Frame(frm_log); log_toolbar.pack(fill='x', padx=8, pady=(8,0))
        tk.Button(log_toolbar, text='Clear log', command=self.clear_log).pack(side='left')
        tk.Button(log_toolbar, text='Copy log', command=self.copy_log).pack(side='left', padx=6)
        log_area = tk.Frame(frm_log); log_area.pack(fill='both', expand=True, padx=8, pady=8)
        self.log_text = tk.Text(log_area, height=18, wrap='word', state='disabled')
        log_scroll = tk.Scrollbar(log_area, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side='left', fill='both', expand=True); log_scroll.pack(side='right', fill='y')

        # Progress
        frm_prog = tk.LabelFrame(self, text='Progress'); frm_prog.pack(fill='x', padx=10, pady=(0,10))
        ttk.Progressbar(frm_prog, orient='horizontal', mode='determinate', variable=self.progress_value, maximum=100).pack(fill='x', padx=8, pady=(8,4))
        tk.Label(frm_prog, textvariable=self.progress_text, anchor='w').pack(fill='x', padx=8, pady=(0,8))

        # Action buttons
        frm_btn = tk.Frame(self); frm_btn.pack(fill='x', padx=10, pady=10)
        self.btn_run = tk.Button(frm_btn, text='Run Selected Checks', command=self.run_selected); self.btn_run.pack(side='left')
        self.btn_export = tk.Button(frm_btn, text='Export Findings to Excel', command=self.export_excel); self.btn_export.pack(side='left', padx=8)
        self.btn_view = tk.Button(frm_btn, text='View Results in Grid', command=self.show_results_grid); self.btn_view.pack(side='left', padx=8)
        self.btn_log = tk.Button(frm_btn, text='Open Log File', command=self.open_log_file); self.btn_log.pack(side='left', padx=8)

        self._log('Ready. (Option A simplified engine with GUI)')

    def _populate_checks(self):
        """Auto-discover checks from engine and populate checkboxes."""
        checks_map = discover_checks()
        for cid, cls in sorted(checks_map.items()):
            var = tk.BooleanVar(value=True)
            self.check_vars[cid] = var
            tk.Checkbutton(self.checks_container, text=f"{cid} - {cls.name}", variable=var, anchor='w').pack(fill='x', padx=8, pady=2)

    # -------------- Logging & progress helpers --------------
    def _log(self, msg: str):
        """Append timestamped message to log text widget."""
        import datetime as _dt
        ts = _dt.datetime.now().strftime('%H:%M:%S')
        line = f'[{ts}] {msg}\n'
        def _apply():
            if self.log_text is None: return
            self.log_text.configure(state='normal'); self.log_text.insert('end', line); self.log_text.see('end'); self.log_text.configure(state='disabled')
        self.after(0, _apply)

    def clear_log(self):
        """Clear all log text."""
        if self.log_text is None: return
        self.log_text.configure(state='normal'); self.log_text.delete('1.0','end'); self.log_text.configure(state='disabled'); self._log('Log cleared.')

    def copy_log(self):
        """Copy log contents to clipboard."""
        if self.log_text is None: return
        self.log_text.configure(state='normal'); text = self.log_text.get('1.0','end-1c'); self.log_text.configure(state='disabled')
        self.clipboard_clear(); self.clipboard_append(text); self._log('Log copied to clipboard.')

    def open_log_file(self):
        """Open the checks.csv log file in the default application."""
        log_file = 'checks.csv'
        if not os.path.isfile(log_file):
            messagebox.showinfo('No log file', 'The checks.csv log file has not been created yet. Run some checks first.'); return
        try:
            if os.name == 'nt':  # Windows
                os.startfile(log_file)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open {log_file}' if os.uname().sysname == 'Darwin' else f'xdg-open {log_file}')
            self._log(f'Opened log file: {log_file}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open log file:\n{e}')

    def _set_progress(self, pct: float, text: str):
        """Update progress bar and status text."""
        def _apply():
            self.progress_value.set(max(0.0, min(100.0, pct)))
            self.progress_text.set(text)
            self.update_idletasks()
        self.after(0, _apply)

    def _set_running(self, running: bool):
        """Enable/disable buttons based on run state."""
        def _apply():
            self._is_running = running
            self.btn_run.config(state=('disabled' if running else 'normal'))
            self.btn_export.config(state=('disabled' if running else 'normal'))
            self.btn_view.config(state=('disabled' if running else 'normal'))
            self.btn_log.config(state=('disabled' if running else 'normal'))
        self.after(0, _apply)

    # -------------- Run pipeline --------------
    def run_selected(self):
        """Validate inputs and launch worker thread."""
        if self._is_running: return
        conn = self.conn_str.get().strip()
        if not conn:
            messagebox.showerror('Error', 'Please enter an ODBC connection string.'); return
        selected_ids = [cid for cid, var in self.check_vars.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning('No checks', 'Please select at least one check to run.'); return
        self._log('Starting run with static SQL...'); self._log(f"Selected checks: {', '.join(selected_ids)}")
        threading.Thread(target=self._run_worker, args=(conn, selected_ids), daemon=True).start()

    def _run_worker(self, conn: str, selected_ids: list[str]):
        """Background worker: load data, run checks, generate findings."""
        self._set_running(True); self._set_progress(0, 'Connecting and loading data...')
        try:
            # Load assets table
            self._log('Loading ASSETS...')
            assets_df = load_dataset_odbc(conn, sql_defs.ALL_TABLE_SQL['ASSETS'])
            for col in ('UNITID','UNITNO','STREET'):
                if col not in assets_df.columns: raise ValueError(f"ASSETS SQL must return column '{col}'")
            self.assets_df = assets_df
            self._set_progress(25, f'Loaded assets: {len(assets_df):,} rows')

            # Load all other tables
            tables: Dict[str, pd.DataFrame] = {'ASSETS': assets_df}
            for name, sql in sql_defs.ALL_TABLE_SQL.items():
                if name == 'ASSETS': continue
                self._log(f'Loading {name}...')
                df = load_dataset_odbc(conn, sql); tables[name] = df
                self._log(f'{name}: {len(df):,} rows, {len(df.columns)} cols')
            self.tables = tables
            self._set_progress(45, 'Running checks...')

            # Execute checks and build output
            findings = run_selected_checks(self.tables, selected_ids)
            self._set_progress(85, 'Building output...')
            fdf = findings_to_dataframe(findings)
            self.output_df = build_output(fdf, self.assets_df, asset_cols=("UNITID","UNITNO","STREET"))
            self._set_progress(100, f'Complete. Findings: {len(self.output_df):,}')
            self._log(f'Run complete. Total findings: {len(self.output_df):,}')
            self.after(0, lambda: messagebox.showinfo('Completed', f'Checks complete. Findings: {len(self.output_df):,}'))
        except Exception as e:
            self._set_progress(0, 'Idle'); self._log(f'ERROR: {e}')
            self.after(0, lambda: messagebox.showerror('Error', f'Failed to run checks:\n{e}'))
        finally:
            self._set_running(False)

    # -------------- Results grid --------------
    def show_results_grid(self):
        """Display findings in a new Treeview window."""
        if self._is_running:
            self._log('Busy: wait for the current run to finish.'); return
        if self.output_df is None or self.output_df.empty:
            messagebox.showinfo('No results', 'No findings to display. Run checks first, or results are empty.'); return
        win = tk.Toplevel(self)
        win.title(f'Results grid - {len(self.output_df):,} rows')
        win.geometry('1120x560')
        bar = tk.Frame(win); bar.pack(fill='x')
        tk.Label(bar, text=f"Rows: {len(self.output_df):,}").pack(side='left', padx=8, pady=6)
        container = tk.Frame(win); container.pack(fill='both', expand=True)
        columns = list(self.output_df.columns)
        tv = ttk.Treeview(container, columns=columns, show='headings', height=20)
        vsb = tk.Scrollbar(container, orient='vertical', command=tv.yview)
        hsb = tk.Scrollbar(container, orient='horizontal', command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in columns:
            tv.heading(col, text=col); tv.column(col, width=150, anchor='w')
        for _, row in self.output_df.iterrows():
            values = [str(x) if x is not None else '' for x in row.tolist()]; tv.insert('', 'end', values=values)
        tv.grid(row=0, column=0, sticky='nsew'); vsb.grid(row=0, column=1, sticky='ns'); hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
        # Auto-size columns based on sample data
        try:
            sample = self.output_df.head(200)
            for col in columns:
                maxlen = max([len(str(x)) for x in sample[col].tolist()] + [len(col)])
                tv.column(col, width=min(380, max(100, int(maxlen*7))))
        except Exception:
            pass

    # -------------- Export --------------
    def export_excel(self):
        """Save findings to an Excel file via file dialog."""
        if self._is_running:
            messagebox.showwarning('Busy', 'Please wait until the current run finishes.'); return
        if self.output_df is None:
            messagebox.showwarning('No results', 'Run checks first.'); return
        out = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel Workbook','*.xlsx')])
        if out:
            try:
                self._log(f'Exporting findings to Excel: {out}')
                export_findings_excel(self.output_df, out)
                self._log('Export complete.'); messagebox.showinfo('Exported', f'Exported to:\n{out}')
            except Exception as e:
                self._log(f'ERROR during export: {e}'); messagebox.showerror('Error', f'Export failed:\n{e}')
