"""JSONL data logger voor live ECU sensor frames."""
import json
import time
from datetime import datetime
from pathlib import Path


class DataLogger:
    """Schrijft sensor frames naar dagelijkse .jsonl bestanden.

    Formaat per regel: {"ts": 1234567890.123, "rpm": 1200, "tps": 5.2, ...}
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_date: str = ""
        self._fh = None

    def _get_path(self) -> Path:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / f"gp800-{today}.jsonl"

    def write(self, frame: dict) -> None:
        path = self._get_path()
        date_str = path.stem
        if date_str != self._current_date:
            if self._fh:
                self._fh.close()
            self._fh = open(path, "a", encoding="utf-8")
            self._current_date = date_str

        self._fh.write(json.dumps(frame) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None
