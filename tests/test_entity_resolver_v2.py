"""
Tests for EntityResolverV2 -- Phase 32.
Pure ASCII.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestJaroWinkler:

    def test_identical_strings(self):
        from processing.entity_resolver_v2 import jaro_winkler
        assert jaro_winkler("modi", "modi") == 1.0

    def test_empty_strings(self):
        from processing.entity_resolver_v2 import _jaro
        assert _jaro("", "test") == 0.0
        assert _jaro("test", "") == 0.0

    def test_similar_names(self):
        from processing.entity_resolver_v2 import jaro_winkler
        score = jaro_winkler("rahulkumar", "rahul kumar")
        assert score > 0.85

    def test_different_names(self):
        from processing.entity_resolver_v2 import jaro_winkler
        score = jaro_winkler("priya", "rajesh")
        assert score < 0.7


class TestNormaliseIndianName:

    def test_honorific_removal_person(self):
        from processing.entity_resolver_v2 import normalise_indian_name
        assert normalise_indian_name("Sh. Ram Kumar", "person") == "ram kumar"
        assert normalise_indian_name("Smt. Priya Devi", "person") == "priya devi"
        assert normalise_indian_name("Dr. Manmohan Singh", "person") == "manmohan singh"
        assert normalise_indian_name("Late Shri Rajiv Gandhi", "person") == "rajiv gandhi"

    def test_company_suffix_normalisation(self):
        from processing.entity_resolver_v2 import normalise_indian_name
        a = normalise_indian_name("Sample Private Limited", "company")
        b = normalise_indian_name("Sample Pvt Ltd", "company")
        assert a == b

    def test_ms_prefix_stripped(self):
        from processing.entity_resolver_v2 import normalise_indian_name
        result = normalise_indian_name("M/S. Delhi Roads Ltd", "company")
        assert "m/s" not in result.lower()

    def test_uppercase_lowercased(self):
        from processing.entity_resolver_v2 import normalise_indian_name
        result = normalise_indian_name("NARENDRA MODI", "person")
        assert result == result.lower()


class TestEntityResolverV2:

    def test_exact_cin_match_returns_one(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2()
        rec1 = {"name": "Adani Enterprises", "cin": "L51100GJ1988PLC013248"}
        rec2 = {"name": "Adani Ltd",          "cin": "L51100GJ1988PLC013248"}
        assert r.combined_score("Adani Enterprises", "Adani Ltd", rec1, rec2) == 1.0

    def test_different_cin_returns_zero(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2()
        rec1 = {"name": "Company A", "cin": "L51100GJ1988PLC013248"}
        rec2 = {"name": "Company A", "cin": "U12345MH2010PLC123456"}
        assert r.combined_score("Company A", "Company A", rec1, rec2) == 0.0

    def test_same_name_after_normalise_returns_one(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        score = r.combined_score("RAHUL KUMAR", "Rahul Kumar")
        assert score == 1.0

    def test_honorific_variant_matches(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        assert r.is_same_entity("Sh. Ram Kumar Gupta", "Ram Kumar Gupta")

    def test_clearly_different_names_no_match(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        assert not r.is_same_entity("Priya Sharma", "Rajesh Gupta")

    def test_resolve_dataset_merges_duplicates(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        records = [
            {"name": "RAHUL KUMAR",  "_source": "myneta"},
            {"name": "Rahul Kumar",  "_source": "wikidata"},
            {"name": "Priya Sharma", "_source": "myneta"},
        ]
        resolved = r.resolve_dataset(records, "name")
        assert len(resolved) == 2

    def test_resolve_dataset_backward_compat_keys(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        records = [
            {"name": "RAHUL KUMAR", "_source": "myneta"},
            {"name": "Rahul Kumar", "_source": "wikidata"},
        ]
        resolved = r.resolve_dataset(records, "name")
        assert "aliases" in resolved[0]
        assert "duplicates" in resolved[0]   # backward compat key
        assert resolved[0]["_resolved_v2"] is True

    def test_cross_dataset_match_finds_link(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        politicians = [{"name": "Rahul Kumar", "_source": "myneta"}]
        directors   = [{"director_name": "RAHUL KUMAR", "_source": "mca"}]
        matches = r.cross_dataset_match(politicians, directors,
                                         "name", "director_name")
        assert len(matches) == 1
        assert matches[0]["score"] >= 0.72

    def test_cross_dataset_match_has_canonical_id(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        politicians = [{"name": "Rahul Kumar", "_source": "myneta"}]
        directors   = [{"director_name": "RAHUL KUMAR", "_source": "mca"}]
        matches = r.cross_dataset_match(politicians, directors,
                                         "name", "director_name")
        assert "canonical_id" in matches[0]
        assert len(matches[0]["canonical_id"]) == 20

    def test_build_alias_graph(self):
        from processing.entity_resolver_v2 import EntityResolverV2
        r = EntityResolverV2(threshold=0.72)
        records = [
            {"name": "RAHUL KUMAR",  "id": "abc123",
             "_source": "myneta",
             "aliases": [{"name": "Rahul Kumar", "id": "def456", "score": 1.0,
                           "source": "wikidata"}]},
        ]
        graph = r.build_alias_graph(records, "name")
        assert "rahul kumar" in graph
        assert graph["rahul kumar"] == "abc123"

    def test_entity_resolver_alias(self):
        # EntityResolver must still work as an alias
        from processing.entity_resolver_v2 import EntityResolver, EntityResolverV2
        assert EntityResolver is EntityResolverV2


class TestAliasGraph:

    def test_add_and_resolve(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        ag.add("RAHUL KUMAR", "abc123")
        assert ag.resolve("rahul kumar") == "abc123"
        assert ag.resolve("RAHUL KUMAR") == "abc123"

    def test_not_found_returns_empty(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        assert ag.resolve("nobody") == ""

    def test_contains(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        ag.add("Priya Sharma", "xyz789")
        assert "priya sharma" in ag

    def test_bulk_add(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        records = [
            {"alias_name": "Modi",           "canonical": "pol_001"},
            {"alias_name": "Narendra Modi",  "canonical": "pol_001"},
        ]
        ag.bulk_add(records, "alias_name", "canonical")
        assert ag.resolve("modi")          == "pol_001"
        assert ag.resolve("Narendra Modi") == "pol_001"

    def test_merge(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        ag.merge({"Amit Shah": "pol_002", "amit shah": "pol_002"})
        assert ag.resolve("amit shah") == "pol_002"
        assert len(ag) == 1   # both normalise to "amit shah"

    def test_stats(self):
        from processing.alias_graph import AliasGraph
        ag = AliasGraph()
        ag.add("Modi", "pol_001")
        ag.add("Narendra Modi", "pol_001")
        ag.add("Rahul Gandhi", "pol_002")
        stats = ag.stats()
        assert stats["total_aliases"] == 3
        assert stats["unique_canonical_ids"] == 2


class TestCanonicalId:

    def test_deterministic(self):
        from processing.canonical_id import canonical_id
        assert canonical_id("narendra modi", "gujarat") == \
               canonical_id("narendra modi", "gujarat")

    def test_case_insensitive(self):
        from processing.canonical_id import canonical_id
        assert canonical_id("MODI", "GUJARAT") == \
               canonical_id("modi", "gujarat")

    def test_length(self):
        from processing.canonical_id import canonical_id
        assert len(canonical_id("test")) == 20

    def test_cin_shortcut(self):
        from processing.canonical_id import canonical_id_for_company
        by_cin  = canonical_id_for_company(cin="L51100GJ1988PLC013248")
        by_name = canonical_id_for_company(name="adani",  state="gj")
        assert by_cin != by_name   # CIN and name-based IDs differ
        assert len(by_cin) == 20
