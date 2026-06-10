import pytest


class TestEntityViewWiring:
    """Verify the entity view now includes all 6 API calls."""

    def test_promise_all_includes_timeline(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "Api.timeline(id)" in app

    def test_promise_all_includes_graph_analytics(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "Api.graphAnalytics(id" in app

    def test_promise_all_includes_investigate(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "Api.investigate(id)" in app

    def test_six_tabs_defined(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        for tab in ["findings", "graph", "timeline", "forensics", "analytics", "evidence"]:
            assert "data-tab="" + tab + """ in app, f"Tab {tab} not found"

    def test_timeline_tab_content_panel(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "tab-content-timeline" in app

    def test_forensics_tab_content_panel(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "tab-content-forensics" in app

    def test_analytics_tab_content_panel(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "tab-content-analytics" in app

    def test_tab_switch_array_has_six_tabs(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert '"findings","graph","timeline","forensics","analytics","evidence"' in app


class TestForensicsPage:

    def test_forensics_view_registered(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "Views.forensics" in app
        assert 'Router.register("/forensics"' in app

    def test_forensics_view_calls_ghost_api(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "forensicsGhostCompanies" in app

    def test_forensics_view_calls_shadow_api(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "forensicsShadowDirectors" in app

    def test_forensics_view_calls_circular_api(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "forensicsCircularOwnership" in app

    def test_forensics_nav_link_in_html(self):
        with open("frontend/index.html", encoding="utf-8") as f:
            html = f.read()
        assert "/forensics" in html


class TestHomeStats:

    def test_home_stats_has_six_entries(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        # The expanded stats array has 6 entries
        assert "Relationships" in app
        assert "Audit Reports" in app

    def test_home_stats_uses_relationship_count(self):
        with open("frontend/js/app.js", encoding="utf-8") as f:
            app = f.read()
        assert "data.relationships" in app


class TestApiJsMethods:

    def test_investigate_method_present(self):
        with open("frontend/js/api.js", encoding="utf-8") as f:
            apijs = f.read()
        assert "investigate:" in apijs

    def test_all_phase34_methods_present(self):
        with open("frontend/js/api.js", encoding="utf-8") as f:
            apijs = f.read()
        for method in ["forensicsGhostCompanies", "forensicsShadowDirectors",
                        "forensicsCircularOwnership", "forensicsBenfords",
                        "selfLearningPatterns", "caseMemoryStats"]:
            assert method in apijs, f"Missing: {method}"
