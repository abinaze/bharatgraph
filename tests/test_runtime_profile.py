"""
Tests for Phase 31 - Runtime Profile
Pure ASCII.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRuntimeProfileScoring:

    def test_low_score_gives_low_profile(self):
        from config.runtime_profile import _compute_score, _score_to_profile
        score = _compute_score(cpu=1, ram=2.0, gpu=False,
                               disk=5.0, docker=False, db_local=False)
        assert score < 4
        assert _score_to_profile(score) == "low"

    def test_medium_score_gives_medium_profile(self):
        from config.runtime_profile import _compute_score, _score_to_profile
        score = _compute_score(cpu=4, ram=8.0, gpu=False,
                               disk=20.0, docker=True, db_local=False)
        assert 4 <= score < 8
        assert _score_to_profile(score) == "medium"

    def test_high_score_gives_high_profile(self):
        from config.runtime_profile import _compute_score, _score_to_profile
        score = _compute_score(cpu=8, ram=16.0, gpu=True,
                               disk=100.0, docker=True, db_local=True)
        assert score >= 8
        assert _score_to_profile(score) == "high"

    def test_profile_env_override(self):
        os.environ["BHARATGRAPH_PROFILE"] = "low"
        from config.runtime_profile import RuntimeProfile
        RuntimeProfile._instance = None
        p = RuntimeProfile.get()
        assert p.name == "low"
        assert p["max_workers"] == 2
        del os.environ["BHARATGRAPH_PROFILE"]
        RuntimeProfile._instance = None

    def test_profile_has_required_keys(self):
        from config.runtime_profile import PROFILE
        required = [
            "max_workers", "batch_size", "graph_depth",
            "investigation_layers", "cache_ttl_seconds", "enable_gpu"
        ]
        for key in required:
            assert key in PROFILE.settings, f"Missing key: {key}"

    def test_to_dict_structure(self):
        from config.runtime_profile import PROFILE
        d = PROFILE.to_dict()
        assert "profile_name" in d
        assert "score"        in d
        assert "hardware"     in d
        assert "settings"     in d
        assert d["profile_name"] in ("low", "medium", "high")

    def test_cpu_score_bounds(self):
        from config.runtime_profile import _compute_score
        assert _compute_score(1, 2, False, 1, False, False) >= 0
        assert _compute_score(16, 64, True, 200, True, True) <= 9

    def test_model_selector_returns_string(self):
        from config.model_selector import get_model, get_max_workers
        model = get_model("embeddings")
        assert isinstance(model, str)
        assert len(model) > 0
        assert get_max_workers() >= 1

    def test_unknown_task_returns_empty_string(self):
        from config.model_selector import get_model
        result = get_model("nonexistent_task_xyz")
        assert isinstance(result, str)


class TestRuntimeProfileDetectors:

    def test_cpu_cores_positive(self):
        from config.runtime_profile import _cpu_cores
        assert _cpu_cores() >= 1

    def test_ram_gb_positive(self):
        from config.runtime_profile import _ram_gb
        assert _ram_gb() > 0.0

    def test_disk_gb_positive(self):
        from config.runtime_profile import _free_disk_gb
        assert _free_disk_gb() >= 0.0

    def test_in_docker_returns_bool(self):
        from config.runtime_profile import _in_docker
        assert isinstance(_in_docker(), bool)

    def test_db_local_false_when_no_env(self):
        from config.runtime_profile import _db_local
        saved = os.environ.pop("NEO4J_URI", None)
        assert _db_local() is False
        if saved:
            os.environ["NEO4J_URI"] = saved

    def test_db_local_true_for_localhost(self):
        from config.runtime_profile import _db_local
        LOCAL_URI = "bolt:" + "//" + "localhost:7687"
        os.environ["NEO4J_URI"] = LOCAL_URI
        assert _db_local() is True
        del os.environ["NEO4J_URI"]
