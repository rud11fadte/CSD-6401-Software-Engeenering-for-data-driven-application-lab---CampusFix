from pathlib import Path
import configparser
from threading import Lock

# 1. SINGLETON: one thread-safe shared application configuration instance.
class AppConfig:
    _instance = None
    _lock = Lock()
    def __new__(cls, config_path=None):
        with cls._lock:
            if cls._instance is None:
                obj = super().__new__(cls)
                obj._load(config_path)
                cls._instance = obj
        return cls._instance
    def _load(self, config_path=None):
        path = Path(config_path) if config_path else Path(__file__).resolve().parents[2] / "campusfix.ini"
        parser = configparser.ConfigParser()
        if path.exists(): parser.read(path)
        defaults = {"daily_complaint_limit":"5","duplicate_window_hours":"24","notification_retries":"3"}
        self.settings = {k:parser.get("campusfix",k,fallback=v) for k,v in defaults.items()}
    def get_int(self, key, default):
        try: return int(self.settings.get(key,default))
        except (ValueError,TypeError): return default
