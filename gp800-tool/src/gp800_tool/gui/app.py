"""GP800 Tool v2 — Main application window.

Direct Python API integration, no subprocess calls.
All ECU operations run in background threads via Worker.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from . import (BG, BG_PANEL, BG_CARD, BG_INPUT, BORDER,
               TEXT, TEXT_DIM, ACCENT, GREEN, RED, YELLOW, CYAN,
               FONT, FONT_MONO)
from .worker import Worker
from .widgets import ArcGauge, HeatmapCanvas, LogPanel, StatusBar

# Lazy imports to avoid import errors when optional deps are missing
_binary_parser = None
_validator = None
_schemas = None
_parser = None


def _ensure_imports():
    global _binary_parser, _validator, _schemas, _parser
    if _binary_parser is None:
        from .. import binary_parser as _bp
        from .. import validator as _val
        from .. import schemas as _sch
        from .. import parser as _par
        _binary_parser = _bp
        _validator = _val
        _schemas = _sch
        _parser = _par


class GP800App:
    """Main application window with tabbed interface."""

    VERSION = "2.0"

    def __init__(self):
        _ensure_imports()

        self.root = tk.Tk()
        self.root.title("GP800 Tool v2 — ECU Diagnostics")
        self.root.geometry("1050x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        # State
        self.serial_port = tk.StringVar()
        self.bin_path = tk.StringVar()
        self.connected = False
        self.ecu_conn = None  # ECUConnection instance
        self.current_dump = None  # BinaryDump
        self.live_running = False

        # Schemas
        self.schemas_dir = _schemas.find_schemas_dir()
        self.safe_ranges = None
        if self.schemas_dir:
            try:
                self.safe_ranges = _schemas.load_safe_ranges(
                    self.schemas_dir / "safe-ranges.json")
            except Exception:
                pass

        # Worker
        self.worker = Worker(self.root)

        # Theme
        self._setup_theme()

        # Build UI
        self._build_toolbar()
        self._build_tabs()
        self.log_panel = LogPanel(self.root, height=6)
        self.log_panel.pack(fill=tk.X, padx=4, pady=(0, 2))
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.log("GP800 Tool v2 gestart", "info")
        self._refresh_ports()

        # Watch bin_path changes
        self.bin_path.trace_add("write", self._on_bin_changed)

    def _setup_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=TEXT,
                         fieldbackground=BG_INPUT, bordercolor=BORDER,
                         troughcolor=BG_INPUT, arrowcolor=TEXT)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_DIM,
                         padding=[14, 6], font=(FONT, 10))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", TEXT)])
        style.configure("TButton", background=BG_INPUT, foreground=TEXT,
                         font=(FONT, 10), padding=6, borderwidth=1)
        style.map("TButton", background=[("active", BORDER)])
        style.configure("Accent.TButton", background=ACCENT, foreground="#000",
                         font=(FONT, 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#79c0ff")])
        style.configure("Danger.TButton", background=RED, foreground="#fff",
                         font=(FONT, 10, "bold"))
        style.map("Danger.TButton", background=[("active", "#ff6e6e")])
        style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=TEXT)
        style.configure("TProgressbar", troughcolor=BG_INPUT,
                         background=ACCENT, borderwidth=0)
        style.configure("Treeview", background=BG_CARD, foreground=TEXT,
                         fieldbackground=BG_CARD, rowheight=24,
                         font=(FONT_MONO, 9))
        style.configure("Treeview.Heading", background=BG_PANEL,
                         foreground=TEXT_DIM, font=(FONT, 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

    # -----------------------------------------------------------------------
    # Toolbar
    # -----------------------------------------------------------------------

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, pady=6, padx=10)
        bar.pack(fill=tk.X)

        # Left: title
        tk.Label(bar, text="GP800", fg=RED, bg=BG_PANEL,
                 font=(FONT, 16, "bold")).pack(side=tk.LEFT)
        tk.Label(bar, text="Tool", fg=TEXT, bg=BG_PANEL,
                 font=(FONT, 16)).pack(side=tk.LEFT, padx=(2, 20))

        # Serial port
        tk.Label(bar, text="Port:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=(FONT, 10)).pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(bar, textvariable=self.serial_port,
                                        width=14, state="readonly")
        self.port_combo.pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Scan", command=self._refresh_ports,
                   width=5).pack(side=tk.LEFT, padx=2)
        self.conn_btn = ttk.Button(bar, text="Verbinden",
                                    command=self._toggle_connect,
                                    style="Accent.TButton")
        self.conn_btn.pack(side=tk.LEFT, padx=(8, 20))

        # BIN file
        tk.Label(bar, text="BIN:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=(FONT, 10)).pack(side=tk.LEFT)
        tk.Entry(bar, textvariable=self.bin_path, width=30,
                 font=(FONT, 9), bg=BG_INPUT, fg=TEXT, insertbackground=TEXT,
                 relief="flat", bd=2).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Open", command=self._browse_bin,
                   width=5).pack(side=tk.LEFT)

    # -----------------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------------

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._build_dashboard()
        self._build_maps_tab()
        self._build_diag_tab()
        self._build_live_tab()
        self._build_flash_tab()

    # --- Dashboard ---

    def _build_dashboard(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Dashboard  ")

        top = tk.Frame(tab, bg=BG)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        top.columnconfigure(1, weight=1)

        # ECU Info card
        info_frame = tk.LabelFrame(top, text=" ECU Informatie ", bg=BG_CARD,
                                    fg=TEXT_DIM, font=(FONT, 10, "bold"),
                                    bd=1, relief="groove", padx=12, pady=8)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.ecu_labels = {}
        fields = [("Variant", "variant"), ("Software", "software"),
                  ("Hardware", "hardware"), ("Homologatie", "homologation"),
                  ("Checksum", "checksum"), ("Bestandsgrootte", "filesize")]
        for r, (label, key) in enumerate(fields):
            tk.Label(info_frame, text=label, fg=TEXT_DIM, bg=BG_CARD,
                     font=(FONT, 9), anchor="w").grid(row=r, column=0,
                     sticky="w", pady=2)
            lbl = tk.Label(info_frame, text="---", fg=TEXT, bg=BG_CARD,
                           font=(FONT_MONO, 10, "bold"), anchor="w")
            lbl.grid(row=r, column=1, sticky="w", padx=(10, 0), pady=2)
            self.ecu_labels[key] = lbl

        # Quick actions card
        actions_frame = tk.LabelFrame(top, text=" Acties ", bg=BG_CARD,
                                       fg=TEXT_DIM, font=(FONT, 10, "bold"),
                                       bd=1, relief="groove", padx=12, pady=8)
        actions_frame.grid(row=0, column=1, sticky="nsew")

        buttons = [
            ("Analyseer BIN", self._analyze_bin, "Accent.TButton"),
            ("Quickcheck", self._quickcheck, "TButton"),
            ("Valideer", self._validate_bin, "TButton"),
            ("ECU Uitlezen", self._read_ecu, "Accent.TButton"),
            ("Foutcodes", self._read_dtc, "TButton"),
            ("EEPROM Lezen", self._read_eeprom, "TButton"),
        ]
        for i, (text, cmd, style) in enumerate(buttons):
            r, c = divmod(i, 3)
            ttk.Button(actions_frame, text=text, command=cmd,
                       style=style, width=16).grid(row=r, column=c,
                       padx=5, pady=5)

    # --- Maps ---

    def _build_maps_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Maps  ")

        toolbar = tk.Frame(tab, bg=BG_PANEL)
        toolbar.pack(fill=tk.X, padx=6, pady=(6, 0))

        tk.Label(toolbar, text="Tabel:", fg=TEXT_DIM, bg=BG_PANEL,
                 font=(FONT, 10)).pack(side=tk.LEFT, padx=(6, 4))
        self.map_selector = ttk.Combobox(toolbar, width=25, state="readonly")
        self.map_selector.pack(side=tk.LEFT)
        self.map_selector.bind("<<ComboboxSelected>>", self._on_map_selected)

        ttk.Button(toolbar, text="Twee BINs vergelijken",
                   command=self._compare_bins).pack(side=tk.RIGHT, padx=6)
        ttk.Button(toolbar, text="BIN -> TXT",
                   command=self._export_bin2txt).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="TXT -> BIN",
                   command=self._import_txt2bin).pack(side=tk.RIGHT, padx=2)

        # Heatmap
        self.heatmap = HeatmapCanvas(tab, on_hover=self._on_heatmap_hover)
        self.heatmap.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Cell info bar
        self.map_info = tk.Label(tab, text="Laad een BIN bestand om maps te bekijken",
                                 fg=TEXT_DIM, bg=BG_PANEL,
                                 font=(FONT_MONO, 9), anchor="w")
        self.map_info.pack(fill=tk.X, padx=6, pady=(0, 6))

    # --- Diagnostics ---

    def _build_diag_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Diagnostics  ")

        toolbar = tk.Frame(tab, bg=BG_PANEL)
        toolbar.pack(fill=tk.X, padx=6, pady=(6, 0))

        ttk.Button(toolbar, text="Valideer BIN",
                   command=self._validate_bin).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="DTCs Lezen",
                   command=self._read_dtc).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="DTCs Wissen",
                   command=self._clear_dtc).pack(side=tk.LEFT, padx=2)

        # Validation results tree
        cols = ("severity", "check", "message")
        self.diag_tree = ttk.Treeview(tab, columns=cols, show="headings",
                                       height=18)
        self.diag_tree.heading("severity", text="Ernst")
        self.diag_tree.heading("check", text="Check")
        self.diag_tree.heading("message", text="Bericht")
        self.diag_tree.column("severity", width=80, anchor="center")
        self.diag_tree.column("check", width=180)
        self.diag_tree.column("message", width=600)

        # Color tags
        self.diag_tree.tag_configure("BLOCKER", foreground=RED)
        self.diag_tree.tag_configure("WARNING", foreground=YELLOW)
        self.diag_tree.tag_configure("PASS", foreground=GREEN)
        self.diag_tree.tag_configure("DTC", foreground=CYAN)

        scroll = ttk.Scrollbar(tab, orient="vertical",
                                command=self.diag_tree.yview)
        self.diag_tree.configure(yscrollcommand=scroll.set)
        self.diag_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6,
                            side=tk.LEFT)
        scroll.pack(fill=tk.Y, side=tk.RIGHT, pady=6, padx=(0, 6))

    # --- Live Data ---

    def _build_live_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Live Data  ")

        toolbar = tk.Frame(tab, bg=BG_PANEL)
        toolbar.pack(fill=tk.X, padx=6, pady=(6, 0))

        self.live_btn = ttk.Button(toolbar, text="Start", width=8,
                                    command=self._toggle_live,
                                    style="Accent.TButton")
        self.live_btn.pack(side=tk.LEFT, padx=6)

        tk.Label(toolbar, text="Update elke seconde via K-Line",
                 fg=TEXT_DIM, bg=BG_PANEL, font=(FONT, 9)).pack(
                     side=tk.LEFT, padx=10)

        # Gauges in 2x3 grid
        gauge_frame = tk.Frame(tab, bg=BG)
        gauge_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i in range(3):
            gauge_frame.columnconfigure(i, weight=1)
        for i in range(2):
            gauge_frame.rowconfigure(i, weight=1)

        self.gauges = {}
        gauge_defs = [
            ("RPM", "rpm", 0, 9500, GREEN, 7000, 8500),
            ("TPS", "%", 0, 100, CYAN, 80, 95),
            ("Koelwater", "\u00b0C", 0, 130, ACCENT, 95, 110),
            ("Lambda", "\u03bb", 0.7, 1.3, YELLOW, None, None),
            ("Batterij", "V", 10, 15, GREEN, None, None),
            ("Snelheid", "km/h", 0, 200, CYAN, 160, 180),
        ]
        for i, (label, unit, lo, hi, color, warn, danger) in enumerate(gauge_defs):
            r, c = divmod(i, 3)
            g = ArcGauge(gauge_frame, label, unit, lo, hi, color, warn, danger,
                         size=170)
            g.grid(row=r, column=c, padx=8, pady=8)
            self.gauges[label] = g

    # --- Flash ---

    def _build_flash_tab(self):
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Flash  ")

        # Warning banner
        warn_frame = tk.Frame(tab, bg=RED, pady=6)
        warn_frame.pack(fill=tk.X, padx=6, pady=(6, 0))
        tk.Label(warn_frame,
                 text="FLASHEN KAN DE ECU PERMANENT BESCHADIGEN — ALTIJD EERST BACKUP",
                 fg="#fff", bg=RED, font=(FONT, 11, "bold")).pack()

        content = tk.Frame(tab, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        content.columnconfigure(1, weight=1)

        # Checklist
        check_frame = tk.LabelFrame(content, text=" Pre-flash Checklist ",
                                     bg=BG_CARD, fg=TEXT_DIM,
                                     font=(FONT, 10, "bold"), padx=12, pady=8)
        check_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.flash_checks = {}
        checks = [
            ("backup", "ECU backup gemaakt"),
            ("battery", "Batterij > 12.0V"),
            ("binfile", "BIN bestand geselecteerd"),
            ("validated", "Safety validatie PASSED"),
            ("ignition", "Contact AAN, motor UIT"),
        ]
        for i, (key, text) in enumerate(checks):
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(check_frame, text=text, variable=var,
                                 bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                                 activebackground=BG_CARD, activeforeground=TEXT,
                                 font=(FONT, 10))
            cb.pack(anchor="w", pady=3)
            self.flash_checks[key] = var

        # Flash controls
        ctrl_frame = tk.LabelFrame(content, text=" Flash ", bg=BG_CARD,
                                    fg=TEXT_DIM, font=(FONT, 10, "bold"),
                                    padx=12, pady=8)
        ctrl_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Button(ctrl_frame, text="Valideer BIN eerst",
                   command=self._validate_for_flash).pack(pady=5, fill=tk.X)

        self.flash_progress = ttk.Progressbar(ctrl_frame, mode="determinate",
                                               style="TProgressbar")
        self.flash_progress.pack(fill=tk.X, pady=8)

        self.flash_status = tk.Label(ctrl_frame, text="Wacht op validatie...",
                                      fg=TEXT_DIM, bg=BG_CARD,
                                      font=(FONT, 10))
        self.flash_status.pack(pady=2)

        self.flash_btn = ttk.Button(ctrl_frame, text="FLASH NAAR ECU",
                                     command=self._flash_ecu,
                                     style="Danger.TButton")
        self.flash_btn.pack(pady=10, fill=tk.X)

        # Flash log
        self.flash_log = tk.Text(ctrl_frame, height=8, bg="#010409", fg=GREEN,
                                  font=(FONT_MONO, 9), relief="flat")
        self.flash_log.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    # ===================================================================
    # Actions
    # ===================================================================

    def log(self, msg: str, level: str = ""):
        self.log_panel.log(msg, level)

    def _refresh_ports(self):
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
        except ImportError:
            ports = []
            self.log("pyserial niet gevonden — pip install pyserial", "warn")
        if not ports:
            ports = ["(geen poorten)"]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)

    def _browse_bin(self):
        initial = Path(__file__).resolve().parents[3] / "map-files"
        path = filedialog.askopenfilename(
            title="Selecteer ECU binary",
            filetypes=[("BIN bestanden", "*.bin"), ("Alle bestanden", "*.*")],
            initialdir=str(initial) if initial.exists() else "")
        if path:
            self.bin_path.set(path)

    def _on_bin_changed(self, *_):
        """Auto-parse when BIN file changes."""
        path = self.bin_path.get()
        self.status_bar.set_file(path)
        if path and Path(path).is_file():
            self.worker.submit(
                lambda: _binary_parser.parse_binary(path),
                on_done=self._on_bin_parsed,
                on_error=lambda e: self.log(f"Parse error: {e}", "error"))

    def _on_bin_parsed(self, dump):
        """Called when BIN is parsed — update dashboard and maps."""
        self.current_dump = dump
        ident = dump.identity

        self.ecu_labels["variant"].config(text=ident.variant)
        self.ecu_labels["software"].config(text=ident.software_id or "---")
        self.ecu_labels["hardware"].config(text=ident.hardware_id or "---")
        self.ecu_labels["homologation"].config(text=ident.homologation or "---")
        self.ecu_labels["checksum"].config(text=f"0x{dump.cal_checksum:04X}")
        self.ecu_labels["filesize"].config(
            text=f"{dump.file_size:,} bytes")

        # Populate map selector
        named = [r for r in dump.regions if not r.name.startswith("table_")]
        names = [r.name for r in named]
        self.map_selector["values"] = names
        if names:
            self.map_selector.current(0)
            self._show_region(named[0])

        self.log(f"Geladen: {ident.variant} — {ident.software_id} "
                 f"({len(named)} tabellen)", "ok")
        self.status_bar.set_status(f"{ident.variant}", GREEN)

    def _on_map_selected(self, _event=None):
        """Show selected map in heatmap."""
        if not self.current_dump:
            return
        name = self.map_selector.get()
        for r in self.current_dump.regions:
            if r.name == name:
                self._show_region(r)
                return

    def _show_region(self, region):
        """Render a BinaryRegion on the heatmap."""
        x_labels = None
        if region.x_axis:
            x_labels = [str(v) for v in region.x_axis.values]
        y_labels = [str(i) for i in range(region.rows)]
        self.heatmap.set_data(
            region.values, x_labels=x_labels, y_labels=y_labels,
            title=f"{region.name} ({region.rows}x{region.cols})")

    def _on_heatmap_hover(self, row, col, value):
        x_info = ""
        if self.current_dump:
            name = self.map_selector.get()
            for r in self.current_dump.regions:
                if r.name == name and r.x_axis and col < len(r.x_axis.values):
                    x_info = f"  RPM={r.x_axis.values[col]}"
                    break
        self.map_info.config(
            text=f"Rij {row}  Kolom {col}{x_info}  Waarde: {value}")

    # --- BIN analysis ---

    def _analyze_bin(self):
        path = self.bin_path.get()
        if not path:
            self._browse_bin()
            return
        # Already parsed via _on_bin_changed, just switch to dashboard
        self.notebook.select(0)

    def _quickcheck(self):
        if not self.current_dump or not self.safe_ranges:
            self.log("Laad eerst een BIN bestand", "warn")
            return
        results = _validator.validate_binary(self.current_dump, self.safe_ranges)
        blockers = [r for r in results if r.severity == "BLOCKER"]
        warnings = [r for r in results if r.severity == "WARNING"]

        if blockers:
            self.log(f"RED — {len(blockers)} BLOCKER(s) — DO NOT FLASH", "error")
        elif warnings:
            self.log(f"YELLOW — {len(warnings)} warning(s) — voorzichtig", "warn")
        else:
            self.log("GREEN — alle checks PASSED", "ok")

    def _validate_bin(self):
        if not self.current_dump or not self.safe_ranges:
            self.log("Laad eerst een BIN bestand", "warn")
            return

        results = _validator.validate_binary(self.current_dump, self.safe_ranges)

        # Show in diagnostics tab
        self.diag_tree.delete(*self.diag_tree.get_children())
        for r in results:
            if r.passed:
                tag = "PASS"
                sev = "PASS"
            else:
                tag = r.severity
                sev = r.severity
            self.diag_tree.insert("", "end", values=(sev, r.check_name, r.message),
                                  tags=(tag,))

        blockers = [r for r in results if r.severity == "BLOCKER"]
        self.notebook.select(2)  # Switch to Diagnostics tab

        if blockers:
            self.log(f"Validatie: {len(blockers)} BLOCKER(s) gevonden", "error")
        else:
            self.log("Validatie: PASSED", "ok")

    def _validate_for_flash(self):
        """Validate and update flash tab status."""
        self._validate_bin()
        if self.current_dump and self.safe_ranges:
            results = _validator.validate_binary(self.current_dump, self.safe_ranges)
            blockers = [r for r in results if r.severity == "BLOCKER"]
            if not blockers:
                self.flash_checks["validated"].set(True)
                self.flash_status.config(text="Validatie PASSED", fg=GREEN)
                self._flash_log("Validatie PASSED — geen blockers\n")
            else:
                self.flash_checks["validated"].set(False)
                self.flash_status.config(
                    text=f"{len(blockers)} BLOCKER(s) — NIET flashen", fg=RED)
                self._flash_log(f"BLOCKED: {len(blockers)} safety violations\n")

    # --- ECU Communication ---

    def _toggle_connect(self):
        if self.connected:
            self._disconnect_ecu()
        else:
            self._connect_ecu()

    def _connect_ecu(self):
        port = self.serial_port.get()
        if not port or port.startswith("("):
            messagebox.showwarning("Geen port", "Selecteer een serial port.")
            return

        self.log(f"Verbinden met {port}...", "info")

        def _do_connect():
            from ..ecucomm import ECUConnection
            conn = ECUConnection(port)
            info = conn.connect()
            return conn, info

        def _on_connected(result):
            conn, info = result
            self.ecu_conn = conn
            self.connected = True
            self.conn_btn.configure(text="Verbreken")
            self.status_bar.set_connected(self.serial_port.get())
            self.log(f"Verbonden: {info.software_id}", "ok")

        self.worker.submit(_do_connect, on_done=_on_connected,
                           on_error=lambda e: self.log(f"Verbinding mislukt: {e}", "error"))

    def _disconnect_ecu(self):
        if self.ecu_conn:
            self.ecu_conn.disconnect()
            self.ecu_conn = None
        self.connected = False
        self.conn_btn.configure(text="Verbinden")
        self.status_bar.set_disconnected()
        self.log("Verbinding verbroken", "info")

    def _read_ecu(self):
        if not self.connected or not self.ecu_conn:
            self.log("Niet verbonden met ECU", "warn")
            return
        output = filedialog.asksaveasfilename(
            title="Firmware opslaan als", defaultextension=".bin",
            initialfile="ecu_backup.bin")
        if not output:
            return

        self.log("ECU firmware uitlezen...", "info")

        def _do_read(progress):
            self.ecu_conn.login()
            fw = self.ecu_conn.read_firmware(progress_callback=progress)
            Path(output).write_bytes(fw)
            return output

        def _on_progress(cur, total, msg):
            pct = int(100 * cur / total) if total else 0
            self.status_bar.set_status(f"Lezen: {pct}% — {msg}", CYAN)

        def _on_done(path):
            self.bin_path.set(path)
            self.status_bar.set_status("Uitlezen compleet", GREEN)
            self.log(f"Firmware opgeslagen: {path}", "ok")

        self.worker.submit(_do_read, on_done=_on_done,
                           on_error=lambda e: self.log(f"Leesfout: {e}", "error"),
                           on_progress=_on_progress)

    def _read_dtc(self):
        if not self.connected or not self.ecu_conn:
            self.log("Niet verbonden met ECU", "warn")
            return

        def _do_read():
            return self.ecu_conn.read_dtcs()

        def _on_done(dtcs):
            self.diag_tree.delete(*self.diag_tree.get_children())
            if not dtcs:
                self.diag_tree.insert("", "end",
                                       values=("OK", "dtc_read", "Geen foutcodes"),
                                       tags=("PASS",))
                self.log("Geen DTCs gevonden", "ok")
            else:
                for d in dtcs:
                    self.diag_tree.insert("", "end",
                                           values=("DTC", d.code_hex, str(d)),
                                           tags=("DTC",))
                self.log(f"{len(dtcs)} DTC(s) gevonden", "warn")
            self.notebook.select(2)

        self.worker.submit(_do_read, on_done=_on_done,
                           on_error=lambda e: self.log(f"DTC leesfout: {e}", "error"))

    def _clear_dtc(self):
        if not self.connected or not self.ecu_conn:
            self.log("Niet verbonden met ECU", "warn")
            return
        if not messagebox.askyesno("DTCs Wissen", "Alle foutcodes wissen?"):
            return
        self.worker.submit(
            lambda: self.ecu_conn.clear_dtcs(),
            on_done=lambda ok: self.log(
                "DTCs gewist" if ok else "Wissen mislukt", "ok" if ok else "error"),
            on_error=lambda e: self.log(f"DTC fout: {e}", "error"))

    def _read_eeprom(self):
        if not self.connected or not self.ecu_conn:
            self.log("Niet verbonden met ECU", "warn")
            return
        output = filedialog.asksaveasfilename(
            title="EEPROM opslaan", defaultextension=".eep",
            initialfile="eeprom_backup.eep")
        if not output:
            return

        def _do_read(progress):
            self.ecu_conn.login()
            data = self.ecu_conn.read_eeprom(progress_callback=progress)
            Path(output).write_bytes(data)
            return len(data)

        self.worker.submit(
            _do_read,
            on_done=lambda n: self.log(f"EEPROM opgeslagen: {n} bytes", "ok"),
            on_error=lambda e: self.log(f"EEPROM fout: {e}", "error"),
            on_progress=lambda c, t, m: self.status_bar.set_status(
                f"EEPROM: {int(100*c/t)}%", CYAN))

    # --- Live Data ---

    def _toggle_live(self):
        if self.live_running:
            self.live_running = False
            self.live_btn.configure(text="Start")
            self.log("Live data gestopt", "info")
        else:
            if not self.connected or not self.ecu_conn:
                self.log("Niet verbonden met ECU", "warn")
                return
            self.live_running = True
            self.live_btn.configure(text="Stop")
            self.log("Live data gestart", "info")
            self._poll_live()

    def _poll_live(self):
        if not self.live_running or not self.ecu_conn:
            return

        pid_map = [
            (0x0C, "RPM", 1),
            (0x11, "TPS", 1),
            (0x05, "Koelwater", 1),
            (0x14, "Lambda", 0.01),
            (0x42, "Batterij", 0.1),
            (0x0D, "Snelheid", 1),
        ]

        def _read_all():
            values = {}
            for pid, name, scale in pid_map:
                raw = self.ecu_conn.read_live_data(pid)
                values[name] = raw * scale if raw is not None else None
            return values

        def _on_data(values):
            for name, gauge in self.gauges.items():
                val = values.get(name)
                gauge.set_value(val)
            if self.live_running:
                self.root.after(800, self._poll_live)

        self.worker.submit(_read_all, on_done=_on_data,
                           on_error=lambda e: self.log(f"Live data fout: {e}", "error"))

    # --- Map Operations ---

    def _export_bin2txt(self):
        if not self.current_dump:
            self.log("Laad eerst een BIN", "warn")
            return
        output = filedialog.asksaveasfilename(
            title="Exporteren als TXT", defaultextension=".txt",
            initialfile="maps_export.txt")
        if not output:
            return

        named = [r for r in self.current_dump.regions
                 if not r.name.startswith("table_")]
        if not named:
            self.log("Geen named tables gevonden", "error")
            return

        from ..models import MapFile, MapTable
        from ..exporter import export_txt_file

        tables = {}
        for reg in named:
            x_vals = ([float(v) for v in reg.x_axis.values]
                      if reg.x_axis else [float(i) for i in range(reg.cols)])
            tables[reg.name] = MapTable(
                name=reg.name, x_axis_label="RPM", x_axis_values=x_vals,
                y_axis_label="Load",
                y_axis_values=[float(i) for i in range(reg.rows)],
                data=[[float(v) for v in row] for row in reg.values],
                value_unit=reg.value_type.replace("fuel_us", "us")
                                         .replace("degrees", "deg_btdc"))

        mf = MapFile(source_path=self.current_dump.source_path,
                     tables=tables, checksum=self.current_dump.checksum)
        export_txt_file(mf, output)
        self.log(f"Geexporteerd: {len(tables)} tabellen naar {output}", "ok")

    def _import_txt2bin(self):
        txt_file = filedialog.askopenfilename(
            title="Selecteer bewerkte TXT", filetypes=[("TXT", "*.txt")])
        if not txt_file:
            return
        base_bin = self.bin_path.get()
        if not base_bin:
            base_bin = filedialog.askopenfilename(
                title="Selecteer basis BIN", filetypes=[("BIN", "*.bin")])
        if not base_bin:
            return
        output = filedialog.asksaveasfilename(
            title="Output BIN", defaultextension=".bin",
            initialfile="modified.bin")
        if not output:
            return

        import struct as _struct
        from ..binary_parser import KNOWN_TABLES

        map_file = _parser.parse_txt_file(txt_file)
        raw = bytearray(Path(base_bin).read_bytes())
        patched = 0

        for tdef in KNOWN_TABLES:
            if tdef["offset"] is None:
                continue
            table = map_file.get_table(tdef["name"])
            if table is None or table.rows != tdef["rows"] or table.cols != tdef["cols"]:
                continue
            for r in range(tdef["rows"]):
                for c in range(tdef["cols"]):
                    off = tdef["offset"] + (r * tdef["cols"] + c) * 2
                    _struct.pack_into("<H", raw, off, int(table.data[r][c]))
            patched += 1

        Path(output).write_bytes(bytes(raw))
        self.log(f"Gepatcht: {patched} tabellen naar {output}", "ok")
        self.bin_path.set(output)

    def _compare_bins(self):
        f1 = filedialog.askopenfilename(title="Eerste BIN",
                                         filetypes=[("BIN", "*.bin")])
        if not f1:
            return
        f2 = filedialog.askopenfilename(title="Tweede BIN",
                                         filetypes=[("BIN", "*.bin")])
        if not f2:
            return

        a = _binary_parser.parse_binary(f1)
        b = _binary_parser.parse_binary(f2)
        diffs = _binary_parser.compare_binaries(a, b)

        self.diag_tree.delete(*self.diag_tree.get_children())
        if not diffs:
            self.diag_tree.insert("", "end",
                                   values=("OK", "bindiff", "Bestanden zijn identiek"),
                                   tags=("PASS",))
        else:
            for d in diffs:
                if d["type"] == "byte_diff_summary":
                    self.diag_tree.insert("", "end",
                        values=("INFO", "bytes_changed",
                                f"{d['total_changed']} bytes in {d['region_count']} regio's"),
                        tags=("DTC",))
                elif d["type"] == "identity_diff":
                    self.diag_tree.insert("", "end",
                        values=("WARNING", d["field"], f"{d['a']} -> {d['b']}"),
                        tags=("WARNING",))
        self.notebook.select(2)
        self.log(f"Vergelijking: {len(diffs)} verschil(len)", "info")

    # --- Flash ---

    def _flash_log(self, msg: str):
        self.flash_log.insert(tk.END, msg)
        self.flash_log.see(tk.END)

    def _flash_ecu(self):
        # Check all safety boxes
        for key, var in self.flash_checks.items():
            if not var.get():
                messagebox.showerror("Safety Check",
                    "Niet alle safety checks afgevinkt.\n"
                    "Alle 5 punten moeten PASS zijn.")
                return

        path = self.bin_path.get()
        port = self.serial_port.get()
        if not path or not port or not self.connected:
            messagebox.showerror("Ontbrekend",
                "BIN bestand, serial port EN ECU verbinding vereist.")
            return

        if not messagebox.askyesno("FLASH BEVESTIGING",
                "WAARSCHUWING: Dit overschrijft de ECU firmware.\n\n"
                "- Batterij > 12.0V en stabiel\n"
                "- Contact AAN, motor UIT\n"
                "- NIET de stroom onderbreken!\n\n"
                "Doorgaan?", icon="warning"):
            return

        firmware = Path(path).read_bytes()
        self._flash_log(f"Flashen: {path}\n")

        def _do_flash(progress):
            self.ecu_conn.login()
            self.ecu_conn.write_firmware(firmware, progress_callback=progress)
            return True

        def _on_progress(cur, total, msg):
            pct = int(100 * cur / total) if total else 0
            self.flash_progress["value"] = pct
            self.flash_status.config(text=f"{pct}% — {msg}", fg=CYAN)
            self._flash_log(f"[{pct}%] {msg}\n")

        def _on_done(_):
            self.flash_progress["value"] = 100
            self.flash_status.config(text="FLASH COMPLEET", fg=GREEN)
            self._flash_log("FLASH COMPLEET\nContact UIT, 10 sec wachten, herstarten.\n")
            self.log("Flash compleet!", "ok")

        def _on_error(e):
            self.flash_status.config(text=f"FLASH FOUT: {e}", fg=RED)
            self._flash_log(f"FOUT: {e}\n")
            self.log(f"Flash fout: {e}", "error")

        self.worker.submit(_do_flash, on_done=_on_done,
                           on_error=_on_error, on_progress=_on_progress)

    # ===================================================================
    # Run
    # ===================================================================

    def run(self):
        self.root.mainloop()
