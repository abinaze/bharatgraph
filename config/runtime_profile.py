"""
BharatGraph - Phase 31: Runtime Profile Auto-Detector
Detects hardware at startup and assigns LOW / MEDIUM / HIGH profile.
All downstream modules read from PROFILE rather than hardcoding limits.
Pure ASCII - no Unicode characters.
"""
import os
import multiprocessing
import platform
import shutil
from loguru import logger


# ---- Profile presets --------------------------------------------------

PROFILES = {
    "low": {
        "max_workers":          2,
        "batch_size":           25,
        "graph_depth":          2,
        "investigation_layers": 3,
        "cache_ttl_seconds":    300,
        "enable_gpu":           False,
        "description": "Minimal footprint - laptop or free-tier cloud",
    },
    "medium": {
        "max_workers":          4,
        "batch_size":           100,
        "graph_depth":          3,
        "investigation_layers": 4,
        "cache_ttl_seconds":    120,
        "enable_gpu":           False,
        "description": "Standard server - 4 CPU / 8 GB RAM",
    },
    "high": {
        "max_workers":          8,
        "batch_size":           500,
        "graph_depth":          5,
        "investigation_layers": 6,
        "cache_ttl_seconds":    60,
        "enable_gpu":           True,
        "description": "High-performance server - 8+ CPU / 16+ GB RAM",
    },
}


# ---- Hardware detection -----------------------------------------------

def _cpu_cores() -> int:
    try:
        return multiprocessing.cpu_count()
    except Exception:
        return 1


def _ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        return kb / (1024 ** 2)
        except Exception:
            pass
        return 2.0


def _gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        pass
    try:
        result = shutil.which("nvidia-smi")
        if result:
            import subprocess
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        pass
    return False


def _free_disk_gb() -> float:
    try:
        usage = shutil.disk_usage(".")
        return usage.free / (1024 ** 3)
    except Exception:
        return 10.0


def _in_docker() -> bool:
    try:
        with open("/proc/1/cgroup") as f:
            return "docker" in f.read() or "kubepods" in f.read()
    except Exception:
        pass
    return os.path.exists("/.dockerenv")


def _db_local() -> bool:
    """True when Neo4j URI points to localhost (low-latency)."""
    uri = os.getenv("NEO4J_URI", "")
    return "localhost" in uri or "127.0.0.1" in uri or "bolt://" in uri


# ---- Profile scoring --------------------------------------------------
# Score >= 8 -> high, >= 4 -> medium, else low

def _compute_score(cpu: int, ram: float, gpu: bool,
                   disk: float, docker: bool, db_local: bool) -> int:
    score = 0
    score += 2 if cpu >= 8  else (1 if cpu >= 4 else 0)
    score += 2 if ram >= 16 else (1 if ram >= 8  else 0)
    score += 2 if gpu       else 0
    score += 1 if disk >= 20 else 0
    score += 1 if docker     else 0
    score += 1 if db_local   else 0
    return score


def _score_to_profile(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


# ---- Public API -------------------------------------------------------

class RuntimeProfile:
    """
    Singleton - call RuntimeProfile.get() anywhere to read settings.

    Usage:
        from config.runtime_profile import PROFILE
        workers = PROFILE["max_workers"]
    """

    _instance = None

    def __init__(self):
        self.cpu     = _cpu_cores()
        self.ram_gb  = _ram_gb()
        self.gpu     = _gpu_available()
        self.disk_gb = _free_disk_gb()
        self.docker  = _in_docker()
        self.db_loc  = _db_local()
        self.os      = platform.system()

        self.score = _compute_score(
            self.cpu, self.ram_gb, self.gpu,
            self.disk_gb, self.docker, self.db_loc
        )
        self.name = os.getenv("BHARATGRAPH_PROFILE", "").lower()
        if self.name not in PROFILES:
            self.name = _score_to_profile(self.score)

        self.settings = dict(PROFILES[self.name])

        logger.info(
            f"[RuntimeProfile] Detected: CPU={self.cpu} cores, "
            f"RAM={self.ram_gb:.1f}GB, GPU={self.gpu}, "
            f"Disk={self.disk_gb:.1f}GB, Docker={self.docker}, "
            f"DB-local={self.db_loc}, OS={self.os}"
        )
        logger.success(
            f"[RuntimeProfile] Score={self.score} -> Profile: {self.name.upper()} "
            f"({self.settings['description']})"
        )

    @classmethod
    def get(cls) -> "RuntimeProfile":
        if cls._instance is None:
            cls._instance = RuntimeProfile()
        return cls._instance

    def __getitem__(self, key):
        return self.settings[key]

    def to_dict(self) -> dict:
        return {
            "profile_name": self.name,
            "score":        self.score,
            "hardware": {
                "cpu_cores": self.cpu,
                "ram_gb":    round(self.ram_gb, 1),
                "gpu":       self.gpu,
                "disk_gb":   round(self.disk_gb, 1),
                "in_docker": self.docker,
                "db_local":  self.db_loc,
                "os":        self.os,
            },
            "settings":    self.settings,
            "overridable": "Set BHARATGRAPH_PROFILE=low|medium|high to force a profile",
        }


# Module-level singleton - import this in all modules
PROFILE = RuntimeProfile.get()
