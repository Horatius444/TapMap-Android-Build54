import os
import threading
from pathlib import Path

_lock = threading.RLock()
_app = None
_runtime = None

def start(data_dir, port=8765):
    global _app, _runtime

    with _lock:
        if _app is not None:
            return f"http://127.0.0.1:{port}/"

        data_path = Path(data_dir) / "tapmap"
        data_path.mkdir(parents=True, exist_ok=True)

        os.environ["TAPMAP_ANDROID"] = "1"
        os.environ["TAPMAP_DATA_DIR"] = str(data_path)
        os.environ["TAPMAP_HOST"] = "127.0.0.1"
        os.environ["TAPMAP_PORT"] = str(port)
        os.environ["TAPMAP_LAUNCH_BROWSER"] = "0"

        from tapmap.app import APP_META, TapMap
        from tapmap.runtime import build_runtime

        _runtime = build_runtime(APP_META, no_browser=True)
        _app = TapMap(_runtime)
        _app.run()

        return f"http://127.0.0.1:{port}/"

def stop():
    global _app, _runtime

    with _lock:
        app = _app
        _app = None
        _runtime = None

    if app is not None:
        app.close()

def status():
    return "running" if _app is not None else "stopped"
