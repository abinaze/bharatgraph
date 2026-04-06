import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

SOURCE_PRIORITY = {
    "ECI":         1,
    "MyNeta":      1,
    "LokSabha":    2,
    "CAG":         2,
    "GeM":         3,
    "MCA":         3,
    "SEBI":        3,
    "ED":          3,
    "PIB":         4,
    "Wikidata":    4,
    "ICIJ":        5,
    "OpenSanctions": 5,
}


class TimelineBuilder:

    def build(self, entity_id: str, entity_name: str,
              driver=None) -> dict:
        logger.info(f"[TimelineBuilder] Building timeline: {entity_name}")

        events = []

        if driver:
            events.extend(self._fetch_election_events(entity_id, driver))
            events.extend(self._fetch_contract_events(entity_id, driver))
            events.extend(self._fetch_audit_events(entity_id, driver))
            events.extend(self._fetch_court_events(entity_id, driver))
            events.extend(self._fetch_press_events(entity_id, driver))
            events.extend(self._fetch_corporate_events(entity_id, driver))
        else:
            events = self._sample_events(entity_name)

        events = [e for e in events if e.get("date")]
        events.sort(key=lambda e: e.get("date", ""))

        grouped = {}
        for e in events:
            year = e["date"][:4]
            grouped.setdefault(year, []).append(e)

        logger.success(
            f"[TimelineBuilder] {entity_name}: "
            f"{len(events)} events across {len(grouped)} years"
        )
        return {
            "entity_id":   entity_id,
            "entity_name": entity_name,
            "event_count": len(events),
            "year_count":  len(grouped),
            "events":      events,
            "by_year":     grouped,
            "built_at":    datetime.now().isoformat(),
        }

    def _fetch_election_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p:Politician {id:$id})
                    RETURN p.year AS year, p.constituency AS seat,
                           p.party AS party, p.state AS state
                    """, id=entity_id
                ).data()
                return [{
                    "date":     str(r.get("year","")) + "-01-01",
                    "type":     "election",
                    "category": "political",
                    "title":    f"Contested election from {r.get('seat','?')}",
                    "detail":   f"Party: {r.get('party','?')} | State: {r.get('state','?')}",
                    "source":   "ECI",
                    "priority": SOURCE_PRIORITY["ECI"],
                } for r in rows if r.get("year")]
        except Exception as e:
            logger.warning(f"[Timeline] Election fetch failed: {e}")
            return []

    def _fetch_contract_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    RETURN ct.order_date AS date, ct.amount_crore AS amount,
                           ct.buyer_org AS buyer, c.name AS company,
                           ct.order_id AS cid
                    ORDER BY ct.order_date LIMIT 50
                    """, id=entity_id
                ).data()
                return [{
                    "date":     r.get("date",""),
                    "type":     "contract",
                    "category": "financial",
                    "title":    f"Company won contract — Rs {r.get('amount',0):.1f} Cr",
                    "detail":   f"{r.get('company','?')} → {r.get('buyer','?')}",
                    "source":   "GeM",
                    "priority": SOURCE_PRIORITY["GeM"],
                    "amount":   r.get("amount"),
                } for r in rows if r.get("date")]
        except Exception as e:
            logger.warning(f"[Timeline] Contract fetch failed: {e}")
            return []

    def _fetch_audit_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (a:AuditReport)
                    WHERE toLower(a.title) CONTAINS toLower($name)
                    RETURN a.year AS year, a.title AS title,
                           a.irregularity_amount_crore AS amount
                    LIMIT 10
                    """, name=entity_id
                ).data()
                return [{
                    "date":     str(r.get("year","")) + "-01-01",
                    "type":     "audit",
                    "category": "regulatory",
                    "title":    "CAG audit mention",
                    "detail":   (r.get("title","") or "")[:100],
                    "source":   "CAG",
                    "priority": SOURCE_PRIORITY["CAG"],
                } for r in rows if r.get("year")]
        except Exception as e:
            logger.warning(f"[Timeline] Audit fetch failed: {e}")
            return []

    def _fetch_court_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (c:CourtCase)-[:INVOLVES]->(n {id:$id})
                    RETURN c.filing_date AS date, c.case_type AS ctype,
                           c.court AS court, c.status AS status
                    LIMIT 20
                    """, id=entity_id
                ).data()
                return [{
                    "date":     r.get("date",""),
                    "type":     "court",
                    "category": "legal",
                    "title":    f"Court case — {r.get('ctype','?')}",
                    "detail":   f"{r.get('court','?')} | Status: {r.get('status','?')}",
                    "source":   "NJDG",
                    "priority": 3,
                } for r in rows if r.get("date")]
        except Exception as e:
            return []

    def _fetch_press_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (pr:PressRelease)
                    WHERE toLower(pr.title) CONTAINS toLower($name)
                    RETURN pr.date AS date, pr.title AS title
                    ORDER BY pr.date DESC LIMIT 10
                    """, name=entity_id
                ).data()
                return [{
                    "date":     r.get("date",""),
                    "type":     "press",
                    "category": "media",
                    "title":    "PIB press mention",
                    "detail":   (r.get("title","") or "")[:100],
                    "source":   "PIB",
                    "priority": SOURCE_PRIORITY["PIB"],
                } for r in rows if r.get("date")]
        except Exception as e:
            return []

    def _fetch_corporate_events(self, entity_id: str, driver) -> list:
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                    RETURN c.registration_date AS date, c.name AS name,
                           c.cin AS cin
                    """, id=entity_id
                ).data()
                return [{
                    "date":     r.get("date",""),
                    "type":     "company",
                    "category": "corporate",
                    "title":    f"Director of {r.get('name','?')}",
                    "detail":   f"CIN: {r.get('cin','?')}",
                    "source":   "MCA",
                    "priority": SOURCE_PRIORITY["MCA"],
                } for r in rows if r.get("date")]
        except Exception as e:
            return []

    def _sample_events(self, name: str) -> list:
        return [
            {"date":"2004-04-15","type":"election","category":"political",
             "title":f"{name} contested Lok Sabha 2004",
             "detail":"First national election","source":"ECI","priority":1},
            {"date":"2009-04-23","type":"election","category":"political",
             "title":f"{name} re-elected Lok Sabha 2009",
             "detail":"Second consecutive term","source":"ECI","priority":1},
            {"date":"2011-03-12","type":"company","category":"corporate",
             "title":"Appointed director of associated company",
             "detail":"MCA21 directorship record","source":"MCA","priority":3},
            {"date":"2014-05-16","type":"election","category":"political",
             "title":f"{name} contested Lok Sabha 2014",
             "detail":"National election cycle","source":"ECI","priority":1},
            {"date":"2016-08-01","type":"contract","category":"financial",
             "title":"Associated company won government contract",
             "detail":"GeM procurement record","source":"GeM","priority":3,
             "amount":12.5},
            {"date":"2019-05-23","type":"election","category":"political",
             "title":f"{name} contested Lok Sabha 2019",
             "detail":"National election cycle","source":"ECI","priority":1},
            {"date":"2021-02-28","type":"audit","category":"regulatory",
             "title":"CAG audit mention",
             "detail":"Audit report flagged associated scheme",
             "source":"CAG","priority":2},
            {"date":"2024-06-04","type":"election","category":"political",
             "title":f"{name} contested Lok Sabha 2024",
             "detail":"Most recent national election","source":"ECI","priority":1},
        ]
