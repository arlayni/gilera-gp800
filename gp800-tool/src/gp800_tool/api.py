"""Flask server voor GP800 ECU — live data, DTC, validatie, logging.

Start via CLI: gp800-tool serve COM3
"""
import json
import tempfile
import threading
import time
from pathlib import Path

try:
    from flask import Flask, Response, jsonify, request, stream_with_context
except ImportError:
    raise ImportError("flask vereist. pip install flask")

from .ecucomm import ECUConnection
from .datalogger import DataLogger

# ---------------------------------------------------------------------------
# App state
# ---------------------------------------------------------------------------

class AppState:
    def __init__(self, port: str, log_dir: Path):
        self.port = port
        self.ecu: ECUConnection | None = None
        self.logger = DataLogger(log_dir)
        self.connected = False
        self.last_frame: dict = {}
        self.ecu_info: dict = {}
        self._lock = threading.Lock()
        self._poll_thread: threading.Thread | None = None

    def connect(self) -> bool:
        self.disconnect()
        try:
            self.ecu = ECUConnection(self.port)
            info = self.ecu.connect()
            self.connected = True
            self.ecu_info = {
                "software_id": info.software_id,
                "hardware_id": info.hardware_id,
                "homologation": info.homologation,
                "port": self.port,
            }
            return True
        except Exception as e:
            self.connected = False
            self.ecu = None
            raise ConnectionError(str(e))

    def disconnect(self):
        self.connected = False
        if self.ecu:
            try:
                self.ecu.disconnect()
            except Exception:
                pass
            self.ecu = None

    def start_polling(self, interval: float = 1.0):
        if self._poll_thread and self._poll_thread.is_alive():
            return
        self._poll_thread = threading.Thread(
            target=self._poll_loop, args=(interval,), daemon=True
        )
        self._poll_thread.start()

    def _poll_loop(self, interval: float):
        pids = [
            (0x0C, "rpm",     "rpm", 1),
            (0x11, "tps",     "%",   1),
            (0x05, "coolant", "°C",  1),
            (0x14, "lambda",  "",    0.01),
        ]
        while True:
            if self.ecu and self.connected:
                frame: dict = {"ts": time.time()}
                try:
                    with self._lock:
                        for pid, key, _unit, scale in pids:
                            raw = self.ecu.read_live_data(pid)
                            frame[key] = round(raw * scale, 2) if raw is not None else None
                    self.last_frame = frame
                    self.logger.write(frame)
                except Exception:
                    self.connected = False
            time.sleep(interval)


_state: AppState | None = None


def get_state() -> AppState:
    if _state is None:
        raise RuntimeError("API niet gestart via gp800-tool serve")
    return _state


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(port: str, log_dir: Path | None = None) -> Flask:
    global _state
    log_dir = log_dir or Path.home() / "gp800-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _state = AppState(port, log_dir)

    # Auto-connect bij start
    try:
        _state.connect()
        _state.start_polling()
        print(f"[GP800] Verbonden op {port}")
    except Exception as e:
        print(f"[GP800] Verbinding mislukt: {e}")
        print("[GP800] Open /connect in het dashboard om opnieuw te proberen.")

    app = Flask(__name__)

    @app.after_request
    def cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------

    @app.route("/")
    def dashboard():
        html = (Path(__file__).parent / "dashboard.html").read_text(encoding="utf-8")
        return Response(html, mimetype="text/html")

    @app.route("/status")
    def status():
        s = get_state()
        return jsonify({
            "connected": s.connected,
            "port": s.port,
            "ecu": s.ecu_info,
            "last_frame_ts": s.last_frame.get("ts"),
        })

    @app.route("/connect", methods=["POST"])
    def connect():
        s = get_state()
        try:
            s.connect()
            s.start_polling()
            return jsonify({"ok": True, "ecu": s.ecu_info})
        except ConnectionError as e:
            return jsonify({"ok": False, "error": str(e)}), 503

    @app.route("/disconnect", methods=["POST"])
    def disconnect():
        get_state().disconnect()
        return jsonify({"ok": True})

    @app.route("/live")
    def live_data():
        s = get_state()
        if not s.connected:
            return jsonify({"error": "Niet verbonden met ECU"}), 503
        return jsonify(s.last_frame)

    @app.route("/live/stream")
    def live_stream():
        s = get_state()

        def generate():
            while True:
                if s.last_frame:
                    yield f"data: {json.dumps(s.last_frame)}\n\n"
                time.sleep(1.0)

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.route("/dtcs")
    def read_dtcs():
        s = get_state()
        if not s.connected or not s.ecu:
            return jsonify({"error": "Niet verbonden met ECU"}), 503
        try:
            with s._lock:
                dtcs = s.ecu.read_dtcs()
            return jsonify({
                "count": len(dtcs),
                "dtcs": [{"code": d.code_hex, "status": hex(d.status)} for d in dtcs],
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/dtcs", methods=["DELETE"])
    def clear_dtcs():
        s = get_state()
        if not s.connected or not s.ecu:
            return jsonify({"error": "Niet verbonden met ECU"}), 503
        try:
            with s._lock:
                ok = s.ecu.clear_dtcs()
            return jsonify({"ok": ok})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/logs")
    def list_logs():
        s = get_state()
        files = sorted(s.logger.log_dir.glob("*.jsonl"), reverse=True)
        return jsonify({
            "files": [
                {
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "modified": f.stat().st_mtime,
                }
                for f in files[:20]
            ]
        })

    @app.route("/logs/<filename>")
    def download_log(filename: str):
        s = get_state()
        path = s.logger.log_dir / filename
        if not path.exists() or path.suffix != ".jsonl":
            return jsonify({"error": "Niet gevonden"}), 404
        return Response(
            open(path, "rb"),
            mimetype="application/x-ndjson",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @app.route("/validate", methods=["POST"])
    def validate_map():
        from .binary_parser import parse_binary
        from .parser import parse_txt_file
        from .validator import validate_map_file
        from .schemas import load_safe_ranges, find_schemas_dir

        schemas_dir = find_schemas_dir()
        if not schemas_dir:
            return jsonify({"error": "Schemas directory niet gevonden"}), 500

        ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")
        f = request.files.get("file")
        if not f:
            return jsonify({"error": "Geen bestand meegestuurd"}), 400

        suffix = Path(f.filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            f.save(tmp.name)
            tmp_path = Path(tmp.name)

        try:
            if suffix == ".bin":
                dump = parse_binary(tmp_path)
                from .validator import validate_binary
                results = validate_binary(dump, ranges)
            else:
                mf = parse_txt_file(tmp_path)
                results = validate_map_file(mf, ranges)
        finally:
            tmp_path.unlink(missing_ok=True)

        blockers = [r for r in results if r.severity == "BLOCKER"]
        warnings = [r for r in results if r.severity == "WARNING"]

        return jsonify({
            "verdict": "RED" if blockers else ("YELLOW" if warnings else "GREEN"),
            "blockers": [r.message for r in blockers],
            "warnings": [r.message for r in warnings],
            "passed": len([r for r in results if r.passed]),
        })

    return app


# ---------------------------------------------------------------------------
# Directe run helper (gebruikt door cli.py serve commando)
# ---------------------------------------------------------------------------

def serve(port: str, host: str = "0.0.0.0", api_port: int = 8000,
          log_dir: Path | None = None) -> None:
    app = create_app(port, log_dir)
    print(f"\n[GP800] Dashboard: http://localhost:{api_port}")
    print(f"[GP800] iPhone:    http://<laptop-ip>:{api_port}")
    print("[GP800] Stoppen:   Ctrl+C\n")
    app.run(host=host, port=api_port, threaded=True)
