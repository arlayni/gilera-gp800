"""Thread-safe background task runner for GUI operations."""
import queue
import threading


class Worker:
    """Runs tasks in background threads, delivers results to Tk main loop."""

    def __init__(self, root):
        self.root = root
        self._queue = queue.Queue()
        self._poll()

    def submit(self, task, on_done=None, on_error=None, on_progress=None):
        """Run task(progress_cb?) in a daemon thread.

        Callbacks fire on the main thread via Tk's event loop.
        If on_progress is set, task receives a progress(cur, total, msg) callback.
        """
        def _run():
            try:
                if on_progress:
                    def _progress(cur, total, msg):
                        self._queue.put(("progress", on_progress, (cur, total, msg)))
                    result = task(_progress)
                else:
                    result = task()
                self._queue.put(("done", on_done, result))
            except Exception as e:
                self._queue.put(("error", on_error, e))

        threading.Thread(target=_run, daemon=True).start()

    def _poll(self):
        """Drain the queue and dispatch callbacks on the main thread."""
        try:
            for _ in range(20):  # max 20 per poll to stay responsive
                kind, callback, data = self._queue.get_nowait()
                if callback:
                    if kind == "progress":
                        callback(*data)
                    else:
                        callback(data)
        except queue.Empty:
            pass
        self.root.after(50, self._poll)
