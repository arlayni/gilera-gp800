"""GP800 Tool v2 — GUI Package.

Direct Python API integration, canvas gauges, heatmap visualization.
No extra dependencies — Tkinter only.
"""

# Theme colors (GitHub Dark inspired)
BG = "#0d1117"
BG_PANEL = "#161b22"
BG_CARD = "#1c2128"
BG_INPUT = "#21262d"
BORDER = "#30363d"
TEXT = "#e6edf3"
TEXT_DIM = "#7d8590"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#d29922"
ORANGE = "#db6d28"
CYAN = "#39d2c0"

FONT = "Segoe UI"
FONT_MONO = "Consolas"


def main():
    """Entry point for GUI (gp800-gui command)."""
    from .app import GP800App
    app = GP800App()
    app.run()
