import pytest


class TestGraphAnalyticsOffline:
    """Test GraphAnalytics with in-memory sample data (no Neo4j required)."""

    SAMPLE_NODES = [
        ("P001", {"name": "Politician A", "type": "Politician"}),
        ("P002", {"name": "Politician B", "type": "Politician"}),
        ("C001", {"name": "Company X",    "type": "Company"}),
        ("C002", {"name": "Company Y",    "type": "Company"}),
        ("C003", {"name": "Company Z",    "type": "Company"}),
        ("CT01", {"name": "Contract 1",   "type": "Contract"}),
        ("CT02", {"name": "Contract 2",   "type": "Contract"}),
        ("M001", {"name": "Ministry A",   "type": "Ministry"}),
    ]
    SAMPLE_EDGES = [
        ("P001", "C001", {"rel": "DIRECTOR_OF"}),
        ("P001", "C002", {"rel": "DIRECTOR_OF"}),
        ("P002", "C003", {"rel": "DIRECTOR_OF"}),
        ("C001", "CT01", {"rel": "WON_CONTRACT"}),
        ("C002", "CT01", {"rel": "WON_CONTRACT"}),
        ("C003", "CT02", {"rel": "WON_CONTRACT"}),
        ("M001", "CT01", {"rel": "AWARDED_BY"}),
        ("M001", "CT02", {"rel": "AWARDED_BY"}),
        ("P001", "P002", {"rel": "MEMBER_OF"}),
    ]

    @pytest.fixture
    def analytics(self):
        from ai.graph_analytics import GraphAnalytics
        return GraphAnalytics(driver=None)

    def test_betweenness_returns_list(self, analytics):
        results = analytics.compute_betweenness_centrality(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        assert isinstance(results, list)
        assert len(results) > 0

    def test_betweenness_has_required_keys(self, analytics):
        results = analytics.compute_betweenness_centrality(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        required = {"entity_id", "name", "type", "betweenness_centrality"}
        for r in results:
            assert required.issubset(r.keys()), f"Missing keys in {r}"

    def test_betweenness_scores_between_0_and_1(self, analytics):
        results = analytics.compute_betweenness_centrality(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        for r in results:
            assert 0.0 <= r["betweenness_centrality"] <= 1.0

    def test_betweenness_too_few_nodes_returns_empty(self, analytics):
        tiny_nodes = [("A", {}), ("B", {})]
        tiny_edges = [("A", "B", {})]
        result = analytics.compute_betweenness_centrality(tiny_nodes, tiny_edges)
        assert result == []

    def test_pagerank_returns_list(self, analytics):
        results = analytics.compute_pagerank(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        assert isinstance(results, list)
        assert len(results) > 0

    def test_pagerank_scores_positive(self, analytics):
        results = analytics.compute_pagerank(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        for r in results:
            assert r["pagerank"] > 0

    def test_pagerank_sum_approximately_one(self, analytics):
        results = analytics.compute_pagerank(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        total = sum(r["pagerank"] for r in results)
        assert abs(total - 1.0) < 0.01, f"PageRank sum={total} (expected ~1.0)"

    def test_communities_returns_list(self, analytics):
        results = analytics.detect_communities(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        assert isinstance(results, list)
        assert len(results) > 0

    def test_communities_have_members(self, analytics):
        results = analytics.detect_communities(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        for c in results:
            assert "members" in c
            assert len(c["members"]) >= 2

    def test_communities_have_interpretation(self, analytics):
        results = analytics.detect_communities(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        for c in results:
            assert "interpretation" in c
            assert len(c["interpretation"]) > 0

    def test_too_few_nodes_communities_empty(self, analytics):
        result = analytics.detect_communities(
            [("A", {}), ("B", {})],
            [("A", "B", {})]
        )
        assert result == []

    def test_run_full_analysis_no_driver(self, analytics):
        """With driver=None, _fetch_graph_from_neo4j returns empty."""
        result = analytics.run_full_analysis()
        assert result.get("status") == "no_data" or "analyzed_at" in result

    def test_ministry_is_highest_betweenness(self, analytics):
        """Ministry A bridges both contracts -- should have high betweenness."""
        results = analytics.compute_betweenness_centrality(
            self.SAMPLE_NODES, self.SAMPLE_EDGES
        )
        top_name = results[0]["name"] if results else ""
        # Ministry or Politician A should be top broker
        assert top_name in ("Ministry A", "Politician A"), (
            f"Expected Ministry A or Politician A at top, got {top_name}"
        )


class TestTimelineHelpers:
    """Test timeline helper functions without Neo4j."""

    def test_label_to_category_contract(self):
        from api.routes.timeline import _label_to_category
        assert _label_to_category("Contract") == "contract"
        assert _label_to_category("Tender")   == "contract"

    def test_label_to_category_legal(self):
        from api.routes.timeline import _label_to_category
        assert _label_to_category("CourtCase")      == "legal"
        assert _label_to_category("InsolvencyOrder") == "legal"

    def test_label_to_category_unknown(self):
        from api.routes.timeline import _label_to_category
        assert _label_to_category("SomethingNew") == "other"

    def test_extract_date_order_date_preferred(self):
        from api.routes.timeline import _extract_date
        props = {"order_date": "2023-04-01", "scraped_at": "2024-01-01"}
        assert _extract_date(props) == "2023-04-01"

    def test_extract_date_fallback_scraped_at(self):
        from api.routes.timeline import _extract_date
        props = {"scraped_at": "2024-01-15", "source": "cag"}
        assert _extract_date(props) == "2024-01-15"

    def test_extract_date_none_when_no_date(self):
        from api.routes.timeline import _extract_date
        assert _extract_date({"name": "test", "source": "mca"}) is None
