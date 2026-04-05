"""Custom Tk widgets — ArcGauge, HeatmapCanvas, LogPanel."""
import math
import tkinter as tk
from tkinter import ttk, scrolledtext

from . import (BG, BG_PANEL, BG_CARD, BG_INPUT, BORDER, TEXT, TEXT_DIM,
               ACCENT, GREEN, RED, YELLOW, ORANGE, CYAN, FONT, FONT_MONO)


# ---------------------------------------------------------------------------
# Color utilities
# ---------------------------------------------------------------------------

def value_color(val: float, lo: float, hi: float) -> str:
    """Map a value to a blue-green-yellow-red gradient."""
    if hi == lo:
        return GREEN
    t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    if t < 0.25:
        r, g, b = 0, int(t * 4 * 255), 255
    elif t < 0.5:
        r, g, b = 0, 255, int((1 - (t - 0.25) * 4) * 255)
    elif t < 0.75:
        r, g, b = int((t - 0.5) * 4 * 255), 255, 0
    else:
        r, g, b = 255, int((1 - (t - 0.75) * 4) * 255), 0
    return f"#{r:02x}{g:02x}{b:02x}"


# ---------------------------------------------------------------------------
# ArcGauge
# ---------------------------------------------------------------------------

class ArcGauge(tk.Canvas):
    """Circular arc gauge with value display."""

    ARC_START = 225   # degrees (bottom-left)
    ARC_EXTENT = -270  # sweep clockwise

    def __init__(self, parent, label: str, unit: str,
                 min_val: float = 0, max_val: float = 100,
                 color: str = GREEN, warn: float | None = None,
                 danger: float | None = None, size: int = 160, **kw):
        super().__init__(parent, width=size, height=size + 30,
                         bg=BG_CARD, highlightthickness=0, **kw)
        self.label = label
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.color = color
        self.warn = warn
        self.danger = danger
        self.size = size
        self._value = None
        self._draw_base()
        self.set_value(None)

    def _draw_base(self):
        """Draw the static background arc and labels."""
        s = self.size
        pad = 18
        # Label at top
        self.create_text(s // 2, 10, text=self.label, fill=TEXT_DIM,
                         font=(FONT, 9), anchor="n")
        # Background arc (track)
        self.create_arc(pad, 24, s - pad, s - pad + 24,
                        start=self.ARC_START, extent=self.ARC_EXTENT,
                        style="arc", outline=BORDER, width=10, tags="track")

    def set_value(self, value: float | None):
        """Update the displayed value."""
        self._value = value
        self.delete("val_arc", "val_text", "unit_text")

        s = self.size
        pad = 18

        if value is None:
            display = "---"
            arc_color = BORDER
            extent = 0
        else:
            clamped = max(self.min_val, min(self.max_val, value))
            ratio = (clamped - self.min_val) / max(1, self.max_val - self.min_val)
            extent = self.ARC_EXTENT * ratio

            # Color based on thresholds
            if self.danger is not None and value >= self.danger:
                arc_color = RED
            elif self.warn is not None and value >= self.warn:
                arc_color = YELLOW
            else:
                arc_color = self.color

            display = f"{value:.0f}" if value == int(value) else f"{value:.1f}"

        # Value arc
        if extent != 0:
            self.create_arc(pad, 24, s - pad, s - pad + 24,
                            start=self.ARC_START, extent=extent,
                            style="arc", outline=arc_color, width=10,
                            tags="val_arc")

        # Value text (center)
        cy = (24 + s - pad + 24) // 2
        self.create_text(s // 2, cy - 4, text=display, fill=TEXT,
                         font=(FONT_MONO, 22, "bold"), tags="val_text")
        # Unit text
        self.create_text(s // 2, cy + 22, text=self.unit, fill=TEXT_DIM,
                         font=(FONT, 9), tags="unit_text")


# ---------------------------------------------------------------------------
# HeatmapCanvas
# ---------------------------------------------------------------------------

class HeatmapCanvas(tk.Frame):
    """Scrollable heatmap grid for ECU map tables."""

    CELL_W = 42
    CELL_H = 22
    LABEL_W = 55
    LABEL_H = 22

    def __init__(self, parent, on_hover=None, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        self.on_hover = on_hover
        self._data = None
        self._lo = self._hi = 0

        # Canvas + scrollbars
        self.canvas = tk.Canvas(self, bg=BG_CARD, highlightthickness=0)
        self.xscroll = ttk.Scrollbar(self, orient="horizontal",
                                     command=self.canvas.xview)
        self.yscroll = ttk.Scrollbar(self, orient="vertical",
                                     command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.xscroll.set,
                              yscrollcommand=self.yscroll.set)

        self.xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Motion>", self._on_motion)

    def set_data(self, values: list[list[float | int]],
                 x_labels: list[str] | None = None,
                 y_labels: list[str] | None = None,
                 title: str = ""):
        """Draw heatmap from 2D value array."""
        self.canvas.delete("all")
        if not values or not values[0]:
            return

        self._data = values
        rows = len(values)
        cols = len(values[0])

        flat = [v for row in values for v in row]
        self._lo = min(flat)
        self._hi = max(flat)

        cw, ch = self.CELL_W, self.CELL_H
        lw, lh = self.LABEL_W, self.LABEL_H
        ox, oy = lw, lh  # origin offset for labels

        # Title
        if title:
            self.canvas.create_text(ox + cols * cw // 2, 4, text=title,
                                    fill=TEXT, font=(FONT, 10, "bold"),
                                    anchor="n")

        # X-axis labels
        if x_labels:
            for c, lbl in enumerate(x_labels[:cols]):
                x = ox + c * cw + cw // 2
                self.canvas.create_text(x, oy - 4, text=str(lbl)[:5],
                                        fill=TEXT_DIM, font=(FONT_MONO, 7),
                                        anchor="s")

        # Y-axis labels
        if y_labels:
            for r, lbl in enumerate(y_labels[:rows]):
                y = oy + r * ch + ch // 2
                self.canvas.create_text(ox - 4, y, text=str(lbl)[:6],
                                        fill=TEXT_DIM, font=(FONT_MONO, 7),
                                        anchor="e")

        # Cells
        for r, row in enumerate(values):
            for c, val in enumerate(row):
                x1 = ox + c * cw
                y1 = oy + r * ch
                x2 = x1 + cw
                y2 = y1 + ch
                color = value_color(float(val), self._lo, self._hi)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             outline=BG_CARD, width=1,
                                             tags=f"cell_{r}_{c}")
                # Value text (small)
                self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                        text=str(int(val)), fill="#000000",
                                        font=(FONT_MONO, 7),
                                        tags=f"txt_{r}_{c}")

        # Scroll region
        total_w = ox + cols * cw + 10
        total_h = oy + rows * ch + 10
        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _on_motion(self, event):
        """Report cell under cursor."""
        if not self._data or not self.on_hover:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        col = int((cx - self.LABEL_W) / self.CELL_W)
        row = int((cy - self.LABEL_H) / self.CELL_H)
        if 0 <= row < len(self._data) and 0 <= col < len(self._data[0]):
            self.on_hover(row, col, self._data[row][col])


# ---------------------------------------------------------------------------
# LogPanel
# ---------------------------------------------------------------------------

class LogPanel(tk.Frame):
    """Collapsible log output panel."""

    def __init__(self, parent, height: int = 8, **kw):
        super().__init__(parent, bg=BG, **kw)

        header = tk.Frame(self, bg=BG_PANEL)
        header.pack(fill=tk.X)
        tk.Label(header, text="Log", fg=TEXT_DIM, bg=BG_PANEL,
                 font=(FONT, 9)).pack(side=tk.LEFT, padx=8)
        tk.Button(header, text="Wissen", fg=TEXT_DIM, bg=BG_PANEL,
                  bd=0, font=(FONT, 8), activebackground=BG_PANEL,
                  command=self.clear).pack(side=tk.RIGHT, padx=8)

        self.text = scrolledtext.ScrolledText(
            self, height=height, bg="#010409", fg=GREEN,
            font=(FONT_MONO, 9), insertbackground=GREEN,
            selectbackground=ACCENT, relief="flat", bd=0)
        self.text.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))

        # Tag colors
        self.text.tag_configure("error", foreground=RED)
        self.text.tag_configure("warn", foreground=YELLOW)
        self.text.tag_configure("info", foreground=CYAN)
        self.text.tag_configure("ok", foreground=GREEN)

    def log(self, msg: str, level: str = ""):
        """Append a log line. level: error, warn, info, ok, or empty."""
        tag = level if level in ("error", "warn", "info", "ok") else ""
        self.text.insert(tk.END, msg + "\n", tag)
        self.text.see(tk.END)

    def clear(self):
        self.text.delete("1.0", tk.END)


# ---------------------------------------------------------------------------
# StatusBar
# ---------------------------------------------------------------------------

class StatusBar(tk.Frame):
    """Bottom status bar with connection and file info."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)

        self._conn_dot = tk.Canvas(self, width=10, height=10,
                                   bg=BG_PANEL, highlightthickness=0)
        self._conn_dot.pack(side=tk.LEFT, padx=(8, 2), pady=3)
        self._dot = self._conn_dot.create_oval(1, 1, 9, 9, fill=RED,
                                                outline="")

        self._conn_label = tk.Label(self, text="Niet verbonden",
                                    fg=TEXT_DIM, bg=BG_PANEL,
                                    font=(FONT, 9))
        self._conn_label.pack(side=tk.LEFT, padx=(0, 15))

        self._file_label = tk.Label(self, text="Geen bestand",
                                    fg=TEXT_DIM, bg=BG_PANEL,
                                    font=(FONT, 9))
        self._file_label.pack(side=tk.LEFT)

        self._status_label = tk.Label(self, text="", fg=TEXT_DIM,
                                      bg=BG_PANEL, font=(FONT, 9))
        self._status_label.pack(side=tk.RIGHT, padx=8)

    def set_connected(self, port: str = ""):
        self._conn_dot.itemconfig(self._dot, fill=GREEN)
        self._conn_label.configure(text=f"Verbonden ({port})", fg=GREEN)

    def set_disconnected(self):
        self._conn_dot.itemconfig(self._dot, fill=RED)
        self._conn_label.configure(text="Niet verbonden", fg=TEXT_DIM)

    def set_file(self, path: str):
        name = path.split("/")[-1].split("\\")[-1] if path else "Geen bestand"
        self._file_label.configure(text=name, fg=TEXT if path else TEXT_DIM)

    def set_status(self, msg: str, color: str = TEXT_DIM):
        self._status_label.configure(text=msg, fg=color)
