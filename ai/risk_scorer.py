import os
import sys
import json
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger

from ai.indicators import (
    indicator_politician_company_overlap,
    indicator_contract_concentration,
    indicator_audit_mention_frequency,
    indicator_asset_growth_anomaly,
    indicator_criminal_case_presence,
)
from ai.explainer import score_to_level, generate_explanation, validate_language


class RiskScorer:

    def __init__(self):
        self.driver = None
        self._connect()

    def _connect(self):
        try:
            from neo4j import GraphDatabase
            from dotenv import load_dotenv
            load_dotenv()
            uri  = os.getenv("NEO4J_URI", "")
            user = os.getenv("NEO4J_USER", "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "")
            if not uri or not pwd:
                raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set in .env")
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
            self.driver.verify_connectivity()
            logger.success("[RiskScorer] Connected to Neo4j")
        except Exception as e:
            logger.error(f"[RiskScorer] Connection failed: {e}")
            raise

    def score_entity(self, entity_id: str) -> dict:
        with self.driver.session() as session:
            entity = session.run(
                "MATCH (n {id: $id}) RETURN n.name AS name, labels(n)[0] AS type",
                id=entity_id
            ).single()

            if not entity:
                return {
                    "entity_id":    entity_id,
                    "entity_name":  entity_id,
                    "entity_type":  "unknown",
                    "risk_score":   0,
                    "risk_level":   "UNKNOWN",
                    "factors":      [],
                    "explanation":  "Entity not found in graph.",
                    "scored_at":    datetime.now().isoformat(),
                }

            entity_name = entity["name"] or entity_id
            entity_type = entity["type"] or "unknown"

            factors = [
                indicator_politician_company_overlap(entity_id, session),
                indicator_contract_concentration(entity_id, session),
                indicator_audit_mention_frequency(entity_id, entity_name, session),
                indicator_asset_growth_anomaly(entity_id, session),
                indicator_criminal_case_presence(entity_id, session),
            ]

            total = sum(f["raw_score"] for f in factors)
            score = min(total, 100)
            level = score_to_level(score)
            explanation = validate_language(
                generate_explanation(entity_name, score, factors)
            )

            logger.info(
                f"[RiskScorer] {entity_name}: score={score} level={level} "
                f"factors={len([f for f in factors if f['raw_score'] > 0])}"
            )

            return {
                "entity_id":   entity_id,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "risk_score":  score,
                "risk_level":  level,
                "factors":     factors,
                "explanation": explanation,
                "sources": list({
                    f["source_institution"]: f["source_url"]
                    for f in factors
                }.items()),
                "scored_at": datetime.now().isoformat(),
            }

    def score_all_politicians(self, limit: int = 50) -> list:
        with self.driver.session() as session:
            rows = session.run(
                "MATCH (p:Politician) RETURN p.id AS id LIMIT $limit",
                limit=limit
            ).data()

        results = []
        for row in rows:
            try:
                result = self.score_entity(row["id"])
                results.append(result)
            except Exception as e:
                logger.error(f"[RiskScorer] Failed to score {row['id']}: {e}")

        results.sort(key=lambda x: x["risk_score"], reverse=True)
        logger.success(f"[RiskScorer] Scored {len(results)} politicians")
        return results

    def score_all_companies(self, limit: int = 50) -> list:
        with self.driver.session() as session:
            rows = session.run(
                "MATCH (c:Company) RETURN c.id AS id LIMIT $limit",
                limit=limit
            ).data()

        results = []
        for row in rows:
            try:
                result = self.score_entity(row["id"])
                results.append(result)
            except Exception as e:
                logger.error(f"[RiskScorer] Failed to score {row['id']}: {e}")

        results.sort(key=lambda x: x["risk_score"], reverse=True)
        logger.success(f"[RiskScorer] Scored {len(results)} companies")
        return results

    def save_scores(self, scores: list, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
        logger.success(f"[RiskScorer] Saved {len(scores)} scores to {filepath}")

    def write_scores_to_graph(self, scores: list):
        with self.driver.session() as session:
            for s in scores:
                session.run(
                    """
                    MATCH (n {id: $id})
                    SET n.risk_score = $score,
                        n.risk_level = $level,
                        n.scored_at  = $at
                    """,
                    id=s["entity_id"],
                    score=s["risk_score"],
                    level=s["risk_level"],
                    at=s["scored_at"],
                )
        logger.success(f"[RiskScorer] Wrote {len(scores)} scores to Neo4j nodes")

    def close(self):
        if self.driver:
            self.driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BharatGraph Risk Scorer")
    parser.add_argument("--entity-id", type=str, default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write-graph", action="store_true")
    args = parser.parse_args()

    print("=" * 55)
    print("BharatGraph - Risk Scoring Engine")
    print("=" * 55)

    scorer = RiskScorer()

    if args.entity_id:
        result = scorer.score_entity(args.entity_id)
        print(f"\nEntity:      {result['entity_name']}")
        print(f"Type:        {result['entity_type']}")
        print(f"Risk Score:  {result['risk_score']} / 100")
        print(f"Risk Level:  {result['risk_level']}")
        print(f"\nExplanation:\n  {result['explanation']}")
        print(f"\nFactors:")
        for f in result["factors"]:
            if f["raw_score"] > 0:
                print(f"  {f['name']}: {f['raw_score']} pts")
                print(f"    {f['description']}")

    elif args.all:
        politicians = scorer.score_all_politicians(limit=100)
        companies   = scorer.score_all_companies(limit=100)
        all_scores  = politicians + companies

        if args.write_graph:
            scorer.write_scores_to_graph(all_scores)

        from datetime import datetime as dt
        ts = dt.now().strftime("%Y%m%d_%H%M%S")
        scorer.save_scores(all_scores, f"data/processed/risk_scores_{ts}.json")

        print(f"\nTotal scored: {len(all_scores)}")
        print(f"High or above: {len([s for s in all_scores if s['risk_score'] >= 61])}")
        print(f"With any indicator: {len([s for s in all_scores if s['risk_score'] > 0])}")

        if all_scores:
            print(f"\nTop results:")
            for s in all_scores[:5]:
                print(f"  {s['entity_name']:30s} {s['risk_score']:3d}  {s['risk_level']}")
    else:
        print("\nUsage:")
        print("  python -m ai.risk_scorer --entity-id <id>")
        print("  python -m ai.risk_scorer --all")
        print("  python -m ai.risk_scorer --all --write-graph")

    scorer.close()
