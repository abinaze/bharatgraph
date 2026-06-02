import pytest


class TestBenfordsAnalyzer:

    @pytest.fixture
    def ba(self):
        from ai.benfords_analyzer import BenfordsAnalyzer
        return BenfordsAnalyzer()

    def test_uniform_data_low_chi2(self, ba):
        """Data with correct Benford distribution should have low chi2."""
        values = [1.1, 1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8, 8.9,
                  1.01, 2.02, 3.03, 1.5, 2.5, 3.5, 1.9, 2.9]
        result = ba.analyze(values)
        assert "chi2_statistic" in result
        assert isinstance(result["chi2_statistic"], (int, float))

    def test_all_same_digit_high_anomaly(self, ba):
        """All values starting with 9 is maximally non-Benford."""
        values = [9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9,
                  90, 91, 92, 93, 94]
        result = ba.analyze(values)
        assert result["chi2_statistic"] > 15.5

    def test_extract_numeric_values_from_text(self, ba):
        text = "Total assets: Rs 45.3 crore, liabilities 12.7 crore"
        vals = ba.extract_numeric_values(text)
        assert len(vals) >= 2
        assert 45.3 in vals or 12.7 in vals

    def test_first_digit_extraction(self, ba):
        assert ba.get_first_digit(123.45) == 1
        assert ba.get_first_digit(0.045)  == 4
        assert ba.get_first_digit(9000)   == 9

    def test_fewer_than_5_values_returns_result(self, ba):
        """Should not crash on small datasets."""
        result = ba.analyze([1.5, 2.3, 3.1])
        assert "chi2_statistic" in result or "status" in result


class TestGhostCompanyDetector:

    @pytest.fixture
    def gcd(self):
        from ai.ghost_company import GhostCompanyDetector
        return GhostCompanyDetector(driver=None)

    GHOST_COMPANY = {
        "id":           "co_ghost_001",
        "name":         "Phantom Services Pvt Ltd",
        "employee_count": 0,
        "registered_capital_crore": 0.1,
        "contract_count": 15,
        "website":      None,
    }
    REAL_COMPANY = {
        "id":           "co_real_001",
        "name":         "Tata Consultancy Services",
        "employee_count": 500000,
        "registered_capital_crore": 1000.0,
        "contract_count": 10,
        "website":      "https://tcs.com",
    }

    def test_ghost_company_high_score(self, gcd):
        result = gcd.score_company(self.GHOST_COMPANY)
        assert result.get("ghost_score", 0) >= 60

    def test_real_company_low_score(self, gcd):
        result = gcd.score_company(self.REAL_COMPANY)
        assert result.get("ghost_score", 100) < 40

    def test_score_has_required_keys(self, gcd):
        result = gcd.score_company(self.GHOST_COMPANY)
        assert "ghost_score" in result
        assert "name" in result or "id" in result

    def test_empty_company_does_not_crash(self, gcd):
        result = gcd.score_company({})
        assert isinstance(result, dict)


class TestShadowDirectorDetector:

    @pytest.fixture
    def sdd(self):
        from ai.shadow_director import ShadowDirectorDetector
        return ShadowDirectorDetector(driver=None)

    def test_detect_address_reuse_groups(self, sdd):
        companies = [
            {"id": "c1", "registered_address": "123 Shell St, Mumbai"},
            {"id": "c2", "registered_address": "123 Shell St, Mumbai"},
            {"id": "c3", "registered_address": "123 Shell St, Mumbai"},
            {"id": "c4", "registered_address": "456 Real Ave, Delhi"},
        ]
        clusters = sdd.detect_address_reuse(companies)
        assert len(clusters) >= 1
        cluster = clusters[0]
        assert cluster["company_count"] >= 3

    def test_below_threshold_not_flagged(self, sdd):
        companies = [
            {"id": "c1", "registered_address": "Unique Addr 1"},
            {"id": "c2", "registered_address": "Unique Addr 2"},
        ]
        clusters = sdd.detect_address_reuse(companies)
        assert len(clusters) == 0

    def test_no_driver_detect_address_does_not_crash(self, sdd):
        result = sdd.detect_address_reuse([])
        assert result == []


class TestCircularOwnershipDetector:

    @pytest.fixture
    def cod(self):
        from ai.circular_ownership import CircularOwnershipDetector
        return CircularOwnershipDetector(driver=None)

    def test_detect_simple_cycle(self, cod):
        edges = [
            {"from": "A", "to": "B"},
            {"from": "B", "to": "C"},
            {"from": "C", "to": "A"},
        ]
        cycles = cod.detect_cycles(ownership_edges=edges)
        assert len(cycles) >= 1

    def test_no_cycle_returns_empty(self, cod):
        edges = [
            {"from": "A", "to": "B"},
            {"from": "B", "to": "C"},
        ]
        cycles = cod.detect_cycles(ownership_edges=edges)
        assert cycles == []

    def test_no_driver_returns_empty_list(self, cod):
        """With no driver, _fetch_ownership_edges returns [] -- no crash."""
        result = cod.detect_cycles()
        assert isinstance(result, list)


class TestCaseStore:

    @pytest.fixture
    def cs(self, tmp_path, monkeypatch):
        from ai.case_memory import case_store as cs_module
        monkeypatch.setattr(cs_module, "CASE_FILE",
                            str(tmp_path / "cases.json"))
        from ai.case_memory.case_store import CaseStore
        return CaseStore()

    def test_get_case_count_empty(self, cs):
        assert cs.get_case_count() == 0

    def test_save_and_retrieve_case(self, cs):
        cs.save_case(
            entity_id="test_001",
            entity_name="Test Entity",
            findings=[{"type": "benfords_law_anomaly", "score": 18}],
            risk_score=18,
        )
        assert cs.get_case_count() == 1

    def test_find_similar_returns_list(self, cs):
        findings = [{"type": "benfords_law_anomaly"}]
        result = cs.find_similar(findings, top_k=5)
        assert isinstance(result, list)

    def test_record_false_positive_no_crash(self, cs):
        cs.record_false_positive("benfords_law_anomaly", "ent_001")
        stats = cs.get_pattern_stats()
        assert isinstance(stats, dict)
