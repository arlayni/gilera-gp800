"""FastAPI layer voor GP800 ECU — live data, DTC, validatie, logging.

Start met: uvicorn gp800_tool.api:app --host 0.0.0.0 --port 8000
Of via CLI: gp800-tool serve /dev/ttyUSB0
"""
import asyncio
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    raise ImportError("fastapi en uvicorn vereist. pip install 'gp800-tool[api]'")

from .ecucomm import ECUConnection, ECUInfo, DTC
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
        self.live_task: asyncio.Task | None = None
        self.last_frame: dict = {}
        self.ecu_info: dict = {}

    async def connect(self) -> bool:
        if self.ecu and self.connected:
            return True
        try:
            self.ecu = ECUConnection(self.port)
            info = await asyncio.to_thread(self.ecu.connect)
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
        if self.ecu:
            try:
                self.ecu.disconnect()
            except Exception:
                pass
        self.ecu = None
        self.connected = False

    async def poll_live(self, interval: float = 1.0):
        """Achtergrondtaak: polt ECU en schrijft naar logger."""
        pids = [
            (0x0C, "rpm", "rpm", 1),
            (0x11, "tps", "%", 1),
            (0x05, "coolant", "°C", 1),
            (0x14, "lambda", "", 0.01),
        ]
        while True:
            if self.ecu and self.connected:
                frame: dict = {"ts": time.time()}
                try:
                    for pid, key, unit, scale in pids:
                        raw = await asyncio.to_thread(self.ecu.read_live_data, pid)
                        frame[key] = round(raw * scale, 2) if raw is not None else None
                    self.last_frame = frame
                    self.logger.write(frame)
                except Exception:
                    self.connected = False
            await asyncio.sleep(interval)


_state: AppState | None = None


def get_state() -> AppState:
    if _state is None:
        raise RuntimeError("API niet gestart via gp800-tool serve")
    return _state


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(port: str, log_dir: Path | None = None) -> FastAPI:
    global _state
    log_dir = log_dir or Path.home() / "gp800-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _state = AppState(port, log_dir)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Auto-connect bij start
        try:
            await _state.connect()
            _state.live_task = asyncio.create_task(_state.poll_live())
        except Exception as e:
            print(f"[GP800] Verbinding mislukt bij start: {e}")
            print("[GP800] Gebruik /connect om opnieuw te verbinden.")
        yield
        # Cleanup
        if _state.live_task:
            _state.live_task.cancel()
        _state.disconnect()

    app = FastAPI(
        title="GP800 ECU API",
        description="Raspberry Pi API voor Gilera GP800 IAW 5AM ECU",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def dashboard():
        html = (Path(__file__).parent / "dashboard.html").read_text()
        return HTMLResponse(html)

    @app.get("/status")
    async def status():
        s = get_state()
        return {
            "connected": s.connected,
            "port": s.port,
            "ecu": s.ecu_info,
            "last_frame_ts": s.last_frame.get("ts"),
        }

    @app.post("/connect")
    async def connect():
        s = get_state()
        s.disconnect()
        try:
            await s.connect()
            if not s.live_task or s.live_task.done():
                s.live_task = asyncio.create_task(s.poll_live())
            return {"ok": True, "ecu": s.ecu_info}
        except ConnectionError as e:
            raise HTTPException(503, detail=str(e))

    @app.post("/disconnect")
    async def disconnect():
        s = get_state()
        if s.live_task:
            s.live_task.cancel()
        s.disconnect()
        return {"ok": True}

    @app.get("/live")
    async def live_data():
        """Huidig live sensor frame (polling)."""
        s = get_state()
        if not s.connected:
            raise HTTPException(503, detail="Niet verbonden met ECU")
        return s.last_frame

    @app.get("/live/stream")
    async def live_stream():
        """Server-Sent Events stream van live sensor data."""
        s = get_state()

        async def event_generator():
            while True:
                if s.last_frame:
                    data = json.dumps(s.last_frame)
                    yield f"data: {data}\n\n"
                await asyncio.sleep(1.0)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/dtcs")
    async def read_dtcs():
        s = get_state()
        if not s.connected or not s.ecu:
            raise HTTPException(503, detail="Niet verbonden met ECU")
        try:
            dtcs = await asyncio.to_thread(s.ecu.read_dtcs)
            return {
                "count": len(dtcs),
                "dtcs": [{"code": d.code_hex, "status": hex(d.status)} for d in dtcs],
            }
        except Exception as e:
            raise HTTPException(500, detail=str(e))

    @app.delete("/dtcs")
    async def clear_dtcs():
        s = get_state()
        if not s.connected or not s.ecu:
            raise HTTPException(503, detail="Niet verbonden met ECU")
        try:
            ok = await asyncio.to_thread(s.ecu.clear_dtcs)
            return {"ok": ok}
        except Exception as e:
            raise HTTPException(500, detail=str(e))

    @app.get("/logs")
    async def list_logs():
        s = get_state()
        files = sorted(s.logger.log_dir.glob("*.jsonl"), reverse=True)
        return {
            "files": [
                {
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "modified": f.stat().st_mtime,
                }
                for f in files[:20]
            ]
        }

    @app.get("/logs/{filename}")
    async def download_log(filename: str):
        s = get_state()
        path = s.logger.log_dir / filename
        if not path.exists() or path.suffix != ".jsonl":
            raise HTTPException(404)
        return StreamingResponse(
            open(path, "rb"),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @app.post("/validate")
    async def validate_map(file: UploadFile = File(...)):
        """Upload een .bin of .txt map file en valideer hem."""
        from .binary_parser import parse_binary
        from .parser import parse_txt_file
        from .validator import validate_map_file, validate_binary
        from .schemas import load_safe_ranges, find_schemas_dir

        schemas_dir = find_schemas_dir()
        if not schemas_dir:
            raise HTTPException(500, detail="Schemas directory niet gevonden op Pi")

        ranges = load_safe_ranges(schemas_dir / "safe-ranges.json")

        # Sla tijdelijk op
        tmp = Path("/tmp") / file.filename
        tmp.write_bytes(await file.read())

        try:
            if tmp.suffix == ".bin":
                dump = parse_binary(tmp)
                results = validate_binary(dump, ranges)
            else:
                mf = parse_txt_file(tmp)
                results = validate_map_file(mf, ranges)
        finally:
            tmp.unlink(missing_ok=True)

        blockers = [r for r in results if r.severity == "BLOCKER"]
        warnings = [r for r in results if r.severity == "WARNING"]

        return {
            "verdict": "RED" if blockers else ("YELLOW" if warnings else "GREEN"),
            "blockers": [r.message for r in blockers],
            "warnings": [r.message for r in warnings],
            "passed": len([r for r in results if r.passed]),
        }

    return app


# ---------------------------------------------------------------------------
# Directe run helper (gebruikt door cli.py serve commando)
# ---------------------------------------------------------------------------

def serve(port: str, host: str = "0.0.0.0", api_port: int = 8000,
          log_dir: Path | None = None) -> None:
    app = create_app(port, log_dir)
    uvicorn.run(app, host=host, port=api_port, log_level="info")
