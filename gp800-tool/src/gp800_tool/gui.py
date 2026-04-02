"""GP800 Tool — Graphical User Interface.

Tkinter-based GUI for ECU diagnostics, map editing, and flashing.
No extra dependencies — Tkinter is built into Python.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path


class GP800App:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GP800 Tool — ECU Diagnostics")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)

        # State
        self.serial_port = tk.StringVar(value="")
        self.bin_file = tk.StringVar(value="")
        self.ecu_connected = False

        # Style
        self.root.configure(bg="#1a1a2e")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"),
                         foreground="#e94560", background="#1a1a2e")
        style.configure("Status.TLabel", font=("Segoe UI", 10),
                         foreground="#0f3460", background="#16213e")
        style.configure("Green.TLabel", foreground="#00ff88", background="#1a1a2e")
        style.configure("Red.TLabel", foreground="#e94560", background="#1a1a2e")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=8)

        self._build_ui()

    def _build_ui(self):
        """Build the main UI layout."""
        # Title bar
        title_frame = tk.Frame(self.root, bg="#1a1a2e", pady=8)
        title_frame.pack(fill=tk.X)
        ttk.Label(title_frame, text="GP800 Tool", style="Title.TLabel").pack(side=tk.LEFT, padx=15)
        self.status_label = ttk.Label(title_frame, text="Niet verbonden",
                                       style="Red.TLabel", font=("Segoe UI", 10))
        self.status_label.pack(side=tk.RIGHT, padx=15)

        # Connection bar
        conn_frame = tk.Frame(self.root, bg="#16213e", pady=6, padx=10)
        conn_frame.pack(fill=tk.X)

        tk.Label(conn_frame, text="Serial Port:", fg="white", bg="#16213e",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.serial_port,
                                        width=15, state="readonly")
        self.port_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(conn_frame, text="Refresh", command=self._refresh_ports).pack(side=tk.LEFT, padx=2)
        ttk.Button(conn_frame, text="Verbinden", command=self._connect_ecu,
                   style="Action.TButton").pack(side=tk.LEFT, padx=10)

        tk.Label(conn_frame, text="BIN:", fg="white", bg="#16213e",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(20, 0))
        tk.Entry(conn_frame, textvariable=self.bin_file, width=30,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=5)
        ttk.Button(conn_frame, text="Browse", command=self._browse_bin).pack(side=tk.LEFT)

        # Main content — notebook with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Dashboard
        self.tab_dashboard = tk.Frame(notebook, bg="#0f3460")
        notebook.add(self.tab_dashboard, text="  Dashboard  ")
        self._build_dashboard()

        # Tab 2: Map Editor
        self.tab_maps = tk.Frame(notebook, bg="#0f3460")
        notebook.add(self.tab_maps, text="  Maps  ")
        self._build_maps_tab()

        # Tab 3: Diagnostics
        self.tab_diag = tk.Frame(notebook, bg="#0f3460")
        notebook.add(self.tab_diag, text="  Diagnostics  ")
        self._build_diag_tab()

        # Tab 4: Live Data
        self.tab_live = tk.Frame(notebook, bg="#0f3460")
        notebook.add(self.tab_live, text="  Live Data  ")
        self._build_live_tab()

        # Tab 5: Flash
        self.tab_flash = tk.Frame(notebook, bg="#0f3460")
        notebook.add(self.tab_flash, text="  Flash  ")
        self._build_flash_tab()

        # Output log at bottom
        log_frame = tk.Frame(self.root, bg="#1a1a2e")
        log_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8,
                                                   bg="#0a0a1a", fg="#00ff88",
                                                   font=("Consolas", 9),
                                                   insertbackground="#00ff88")
        self.log_text.pack(fill=tk.X)
        self._log("GP800 Tool gestart. Selecteer een serial port en verbind met de ECU.")

        # Initial port scan
        self._refresh_ports()

    def _build_dashboard(self):
        """Dashboard tab with ECU info and quick actions."""
        f = self.tab_dashboard

        # ECU Info panel
        info_frame = tk.LabelFrame(f, text="ECU Informatie", bg="#0f3460", fg="white",
                                    font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        self.ecu_info_labels = {}
        for row, (key, label) in enumerate([
            ("variant", "Voertuig:"), ("software", "Software:"),
            ("hardware", "Hardware:"), ("homologation", "Homologatie:"),
            ("checksum", "Checksum:")
        ]):
            tk.Label(info_frame, text=label, fg="#888", bg="#0f3460",
                     font=("Segoe UI", 10), anchor="w").grid(row=row, column=0, sticky="w", pady=2)
            lbl = tk.Label(info_frame, text="—", fg="white", bg="#0f3460",
                           font=("Segoe UI", 10, "bold"), anchor="w")
            lbl.grid(row=row, column=1, sticky="w", padx=10, pady=2)
            self.ecu_info_labels[key] = lbl

        # Quick actions
        actions_frame = tk.LabelFrame(f, text="Acties", bg="#0f3460", fg="white",
                                       font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)

        buttons = [
            ("ECU Uitlezen", self._read_ecu, "Action.TButton"),
            ("Foutcodes (DTC)", self._read_dtc, "Action.TButton"),
            ("EEPROM Lezen", self._read_eeprom, "Action.TButton"),
            ("Quickcheck", self._quickcheck, "Action.TButton"),
            ("BIN Analyseren", self._analyze_bin, "Action.TButton"),
        ]
        for i, (text, cmd, style) in enumerate(buttons):
            ttk.Button(actions_frame, text=text, command=cmd,
                       style=style).grid(row=0, column=i, padx=5, pady=5)

    def _build_maps_tab(self):
        """Map editor tab."""
        f = self.tab_maps

        btn_frame = tk.Frame(f, bg="#0f3460")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="BIN → TXT Exporteren",
                   command=self._export_bin2txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="TXT → BIN Importeren",
                   command=self._import_txt2bin).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Twee BINs Vergelijken",
                   command=self._compare_bins).pack(side=tk.LEFT, padx=5)

        self.map_text = scrolledtext.ScrolledText(f, bg="#0a0a1a", fg="#00ccff",
                                                   font=("Consolas", 10),
                                                   insertbackground="#00ccff")
        self.map_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _build_diag_tab(self):
        """Diagnostics tab."""
        f = self.tab_diag

        btn_frame = tk.Frame(f, bg="#0f3460")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="DTCs Lezen",
                   command=self._read_dtc).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="DTCs Wissen",
                   command=self._clear_dtc).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Valideren",
                   command=self._validate).pack(side=tk.LEFT, padx=5)

        self.diag_text = scrolledtext.ScrolledText(f, bg="#0a0a1a", fg="#ffcc00",
                                                    font=("Consolas", 10),
                                                    insertbackground="#ffcc00")
        self.diag_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _build_live_tab(self):
        """Live data tab with gauges."""
        f = self.tab_live

        btn_frame = tk.Frame(f, bg="#0f3460")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.live_running = False
        self.live_btn = ttk.Button(btn_frame, text="Start Live Data",
                                    command=self._toggle_live)
        self.live_btn.pack(side=tk.LEFT, padx=5)

        # Gauge display
        gauge_frame = tk.Frame(f, bg="#0f3460")
        gauge_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.gauges = {}
        for i, (name, unit, color) in enumerate([
            ("RPM", "rpm", "#e94560"),
            ("TPS", "%", "#00ff88"),
            ("Coolant", "°C", "#00ccff"),
            ("Lambda", "λ", "#ffcc00"),
        ]):
            gf = tk.LabelFrame(gauge_frame, text=name, bg="#16213e", fg="white",
                                font=("Segoe UI", 10, "bold"), padx=20, pady=10)
            gf.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            gauge_frame.columnconfigure(i % 2, weight=1)
            gauge_frame.rowconfigure(i // 2, weight=1)

            val_label = tk.Label(gf, text="---", fg=color, bg="#16213e",
                                  font=("Consolas", 36, "bold"))
            val_label.pack()
            tk.Label(gf, text=unit, fg="#888", bg="#16213e",
                     font=("Segoe UI", 12)).pack()
            self.gauges[name] = val_label

    def _build_flash_tab(self):
        """Flash tab with safety checks."""
        f = self.tab_flash

        # Warning
        warn = tk.Label(f, text="⚠  FLASHEN IS ONOMKEERBAAR — ALTIJD EERST BACKUP MAKEN  ⚠",
                         fg="#e94560", bg="#0f3460", font=("Segoe UI", 12, "bold"))
        warn.pack(pady=15)

        # Steps
        steps_frame = tk.LabelFrame(f, text="Flash Procedure", bg="#0f3460", fg="white",
                                     font=("Segoe UI", 11, "bold"), padx=15, pady=10)
        steps_frame.pack(fill=tk.X, padx=10)

        self.flash_checks = {}
        for i, text in enumerate([
            "1. ECU backup gemaakt",
            "2. Batterij > 12.0V",
            "3. BIN bestand geselecteerd",
            "4. Safety validatie PASSED",
            "5. Contactsleutel AAN, motor UIT",
        ]):
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(steps_frame, text=text, variable=var,
                                 bg="#0f3460", fg="white", selectcolor="#16213e",
                                 font=("Segoe UI", 10), activebackground="#0f3460")
            cb.pack(anchor="w", pady=2)
            self.flash_checks[i] = var

        btn_frame = tk.Frame(f, bg="#0f3460")
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Valideer BIN",
                   command=self._validate).pack(side=tk.LEFT, padx=10)
        self.flash_btn = ttk.Button(btn_frame, text="FLASH NAAR ECU",
                                     command=self._flash_ecu, style="Danger.TButton")
        self.flash_btn.pack(side=tk.LEFT, padx=10)

        self.flash_text = scrolledtext.ScrolledText(f, height=8, bg="#0a0a1a", fg="#00ff88",
                                                     font=("Consolas", 10))
        self.flash_text.pack(fill=tk.X, padx=10, pady=10)

    # --- Port Management ---

    def _refresh_ports(self):
        """Scan for available serial ports."""
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
        except ImportError:
            ports = []
            self._log("pyserial niet gevonden — installeer met: pip install pyserial")

        if not ports:
            ports = ["Geen poorten gevonden"]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)
        self._log(f"Serial ports: {', '.join(ports)}")

    def _browse_bin(self):
        """Open file dialog to select a .bin file."""
        path = filedialog.askopenfilename(
            title="Selecteer ECU binary",
            filetypes=[("BIN bestanden", "*.bin"), ("Alle bestanden", "*.*")],
            initialdir=str(Path(__file__).parent.parent.parent.parent / "map-files")
        )
        if path:
            self.bin_file.set(path)
            self._log(f"BIN bestand: {path}")

    # --- ECU Operations ---

    def _run_command(self, args, output_widget=None):
        """Run a gp800-tool command in a thread."""
        import subprocess
        target = output_widget or self.log_text

        def _run():
            try:
                cmd = [sys.executable, "-m", "gp800_tool.cli"] + args
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                output = result.stdout + result.stderr
                self.root.after(0, lambda: self._append_text(target, output))
            except Exception as e:
                self.root.after(0, lambda: self._append_text(target, f"ERROR: {e}\n"))

        threading.Thread(target=_run, daemon=True).start()

    def _append_text(self, widget, text):
        widget.insert(tk.END, text + "\n")
        widget.see(tk.END)

    def _log(self, msg):
        self._append_text(self.log_text, f"[LOG] {msg}")

    def _connect_ecu(self):
        port = self.serial_port.get()
        if not port or port == "Geen poorten gevonden":
            messagebox.showwarning("Geen port", "Selecteer eerst een serial port.")
            return
        self._log(f"Verbinden met {port}...")
        self._run_command(["connect", port])

    def _read_ecu(self):
        port = self.serial_port.get()
        if not port or port == "Geen poorten gevonden":
            messagebox.showwarning("Geen port", "Selecteer eerst een serial port.")
            return
        output = filedialog.asksaveasfilename(
            title="Opslaan als", defaultextension=".bin",
            filetypes=[("BIN bestanden", "*.bin")],
            initialfile="ecu_backup.bin"
        )
        if output:
            self._log(f"ECU uitlezen naar {output}...")
            self._run_command(["read", port, output])

    def _read_dtc(self):
        port = self.serial_port.get()
        if not port or port == "Geen poorten gevonden":
            messagebox.showwarning("Geen port", "Selecteer eerst een serial port.")
            return
        self._log("Foutcodes uitlezen...")
        self._run_command(["dtc", port], self.diag_text)

    def _clear_dtc(self):
        port = self.serial_port.get()
        if not port:
            return
        if messagebox.askyesno("DTCs Wissen", "Alle foutcodes wissen?"):
            self._run_command(["dtc", port, "--clear"], self.diag_text)

    def _read_eeprom(self):
        port = self.serial_port.get()
        if not port:
            return
        output = filedialog.asksaveasfilename(
            title="EEPROM opslaan als", defaultextension=".eep",
            initialfile="eeprom_backup.eep"
        )
        if output:
            self._run_command(["eeprom", port, output])

    def _quickcheck(self):
        path = self.bin_file.get()
        if not path:
            messagebox.showwarning("Geen bestand", "Selecteer eerst een BIN bestand.")
            return
        self._run_command(["quickcheck", path])

    def _analyze_bin(self):
        path = self.bin_file.get()
        if not path:
            path = filedialog.askopenfilename(
                title="Selecteer BIN", filetypes=[("BIN", "*.bin")])
            if path:
                self.bin_file.set(path)
        if path:
            self._run_command(["bindump", path, "--tables", "--no-axes"])

    def _validate(self):
        path = self.bin_file.get()
        if not path:
            messagebox.showwarning("Geen bestand", "Selecteer eerst een BIN bestand.")
            return
        self._run_command(["validate", path], self.flash_text if hasattr(self, 'flash_text') else None)

    def _export_bin2txt(self):
        path = self.bin_file.get()
        if not path:
            messagebox.showwarning("Geen bestand", "Selecteer eerst een BIN bestand.")
            return
        output = filedialog.asksaveasfilename(
            title="Exporteren als", defaultextension=".txt",
            initialfile="maps_export.txt"
        )
        if output:
            self._run_command(["bin2txt", path, output], self.map_text)

    def _import_txt2bin(self):
        txt_file = filedialog.askopenfilename(
            title="Selecteer bewerkte TXT", filetypes=[("TXT", "*.txt")])
        if not txt_file:
            return
        base_bin = self.bin_file.get()
        if not base_bin:
            base_bin = filedialog.askopenfilename(
                title="Selecteer basis BIN", filetypes=[("BIN", "*.bin")])
        if not base_bin:
            return
        output = filedialog.asksaveasfilename(
            title="Output BIN", defaultextension=".bin",
            initialfile="modified.bin"
        )
        if output:
            self._run_command(["txt2bin", txt_file, base_bin, output], self.map_text)

    def _compare_bins(self):
        file1 = filedialog.askopenfilename(title="Eerste BIN", filetypes=[("BIN", "*.bin")])
        if not file1:
            return
        file2 = filedialog.askopenfilename(title="Tweede BIN", filetypes=[("BIN", "*.bin")])
        if not file2:
            return
        self._run_command(["bindiff", file1, file2], self.map_text)

    def _toggle_live(self):
        if self.live_running:
            self.live_running = False
            self.live_btn.configure(text="Start Live Data")
        else:
            port = self.serial_port.get()
            if not port or port == "Geen poorten gevonden":
                messagebox.showwarning("Geen port", "Selecteer eerst een serial port.")
                return
            self.live_running = True
            self.live_btn.configure(text="Stop Live Data")
            self._log("Live data gestart...")

    def _flash_ecu(self):
        # Check all safety boxes
        for i, var in self.flash_checks.items():
            if not var.get():
                messagebox.showerror("Safety Check",
                    f"Niet alle safety checks zijn afgevinkt.\n"
                    f"Vink alle 5 punten aan voordat je flasht.")
                return

        path = self.bin_file.get()
        port = self.serial_port.get()
        if not path or not port:
            messagebox.showerror("Ontbrekend", "Selecteer BIN bestand en serial port.")
            return

        if messagebox.askyesno("FLASH BEVESTIGING",
                "WAARSCHUWING: Dit overschrijft de ECU firmware.\n\n"
                "Zorg ervoor dat:\n"
                "- Batterij > 12.0V en stabiel\n"
                "- Contactsleutel AAN, motor UIT\n"
                "- NIET de stroom onderbreken tijdens flashen\n\n"
                "Doorgaan met flashen?",
                icon="warning"):
            self._log(f"FLASHEN: {path} naar {port}")
            self._run_command(["flash", port, path, "--force"], self.flash_text)

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Entry point for GUI."""
    app = GP800App()
    app.run()


if __name__ == "__main__":
    main()
