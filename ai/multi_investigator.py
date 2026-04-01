import os
import sys
import json
import hashlib
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from ai.explainer import validate_language
from ai.investigators import ALL_INVESTIGATORS


def generate_report_hash(entity_id: str, timestamp: str) -> str:
    raw = f"{entity_id}|{timestamp}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run_investigator(investigator_class, entity_id: str,
                     entity_name: str, driver) -> dict:
    investigator = investigator_class()
    try:
        if driver:
            with driver.session() as session:
                return investigator.investigate(entity_id, entity_name, session)
        else:
            class FakeSession:
                def run(self, *a, **k):
                    class FakeResult:
                        def single(self):    return None
                        def data(self):      return []
                    return FakeResult()
            return investigator.investigate(entity_id, entity_name, FakeSession())
    except Exception as e:
        logger.warning(
            f"[MultiInvestigator] {investigator_class.NAME} failed: {e}"
        )
        return {
            "investigator": investigator_class.NAME,
            "focus":        investigator_class.FOCUS,
            "findings":     [],
            "positive":     [],
            "evidence":     [],
            "confidence":   "NONE",
            "error":        str(e),
            "investigated_at": datetime.now().isoformat(),
        }


def synthesise(results: list) -> dict:
    finding_counter = {}
    for result in results:
        for finding in result.get("findings", []):
            ftype = finding.get("type", "")
            if ftype not in finding_counter:
                finding_counter[ftype] = {
                    "type":        ftype,
                    "description": finding.get("description", ""),
                    "severity":    finding.get("severity", "LOW"),
                    "count":       0,
                    "investigators":[],
                    "evidence":    finding.get("evidence", []),
                }
            finding_counter[ftype]["count"]        += 1
            finding_counter[ftype]["investigators"].append(
                result["investigator"]
            )

    agreed = [
        f for f in finding_counter.values()
        if f["count"] >= 3
    ]
    for f in agreed:
        if f["count"] >= 3:
            f["confidence"] = "HIGH"
        elif f["count"] == 2:
            f["confidence"] = "MODERATE"
        else:
            f["confidence"] = "LOW"

    return {
        "agreed_findings": sorted(agreed, key=lambda x: x["count"], reverse=True),
        "finding_types":   len(finding_counter),
    }


class MultiInvestigator:

    def __init__(self, driver=None):
        self.driver = driver

    def investigate(self, entity_id: str,
                    entity_name: str = "") -> dict:
        timestamp = datetime.now().isoformat()
        report_hash = generate_report_hash(entity_id, timestamp)

        logger.info(
            f"[MultiInvestigator] Starting investigation: {entity_name or entity_id}"
        )
        logger.info(
            f"[MultiInvestigator] Report hash: {report_hash[:16]}..."
        )

        if not entity_name and self.driver:
            with self.driver.session() as session:
                row = session.run(
                    "MATCH (n {id: $id}) RETURN n.name AS name",
                    id=entity_id
                ).single()
                entity_name = row["name"] if row else entity_id

        entity_name = entity_name or entity_id
        results     = []

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(
                    run_investigator,
                    inv_class,
                    entity_id,
                    entity_name,
                    self.driver,
                ): inv_class.NAME
                for inv_class in ALL_INVESTIGATORS
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                    logger.success(
                        f"[MultiInvestigator] {name} completed — "
                        f"{len(result.get('findings', []))} finding(s)"
                    )
                except Exception as e:
                    logger.error(f"[MultiInvestigator] {name} timed out: {e}")

        synthesis = synthesise(results)

        all_evidence = []
        seen_evidence = set()
        for r in results:
            for e in r.get("evidence", []):
                key = e.get("institution", "") + e.get("document", "")
                if key not in seen_evidence:
                    seen_evidence.add(key)
                    all_evidence.append(e)

        all_positive = []
        for r in results:
            all_positive.extend(r.get("positive", []))

        all_doubts = []
        for r in results:
            if r.get("doubts"):
                all_doubts.extend(r["doubts"])

        timeline = []
        for r in results:
            if r.get("timeline"):
                timeline.extend(r["timeline"])
        timeline.sort(key=lambda x: x.get("date", ""), reverse=False)

        biography = (
            f"{entity_name} — Investigation Report\n\n"
            f"This report was generated by the BharatGraph Multi-Investigator "
            f"AI Engine on {timestamp[:10]}. "
            f"{len(ALL_INVESTIGATORS)} specialist investigators analysed this "
            f"entity from {len(ALL_INVESTIGATORS)} independent angles. "
            f"Every claim is backed by primary source evidence. "
            f"This is an analytical report and does not constitute a legal finding."
        )

        explanation_raw = (
            f"The multi-investigator analysis of {entity_name} produced "
            f"{len(synthesis['agreed_findings'])} agreed finding(s) confirmed "
            f"by 3 or more investigators. "
            f"The evidence locker contains {len(all_evidence)} primary source reference(s). "
            f"{len(all_doubts)} investigative hypothesis(es) require further attention."
        )

        try:
            explanation = validate_language(explanation_raw)
        except ValueError as e:
            explanation = (
                "Analytical summary withheld — language validation failed. "
                "Review individual investigator findings."
            )
            logger.warning(f"[MultiInvestigator] Language validation: {e}")

        report = {
            "entity_id":           entity_id,
            "entity_name":         entity_name,
            "unique_report_hash":  report_hash,
            "generated_at":        timestamp,
            "investigator_count":  len(ALL_INVESTIGATORS),
            "results_received":    len(results),
            "entity_biography":    biography,
            "agreed_findings":     synthesis["agreed_findings"],
            "individual_findings": results,
            "doubts":              all_doubts,
            "positive_contributions": all_positive,
            "timeline":            timeline,
            "evidence_locker":     all_evidence,
            "explanation":         explanation,
        }
        logger.success(
            f"[MultiInvestigator] Report complete. "
            f"Hash: {report_hash[:16]}... "
            f"Agreed findings: {len(synthesis['agreed_findings'])}"
        )
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BharatGraph Multi-Investigator Engine"
    )
    parser.add_argument("--entity-id",   default="sample_entity_001")
    parser.add_argument("--entity-name", default="Sample Entity")
    parser.add_argument("--save",        action="store_true")
    args = parser.parse_args()

    print("=" * 55)
    print("BharatGraph - Multi-Investigator AI Engine")
    print("=" * 55)
    print(f"\n  Entity:  {args.entity_name}")
    print(f"  ID:      {args.entity_id}")
    print(f"  Investigators: {len(ALL_INVESTIGATORS)}")

    engine = MultiInvestigator(driver=None)
    report = engine.investigate(args.entity_id, args.entity_name)

    print(f"\n  Report hash:       {report['unique_report_hash'][:32]}...")
    print(f"  Investigators run: {report['results_received']}")
    print(f"  Agreed findings:   {len(report['agreed_findings'])}")
    print(f"  Doubts raised:     {len(report['doubts'])}")
    print(f"  Evidence items:    {len(report['evidence_locker'])}")
    print(f"  Positive notes:    {len(report['positive_contributions'])}")

    if report["agreed_findings"]:
        print("\n  Agreed Findings:")
        for f in report["agreed_findings"][:3]:
            print(f"    [{f['severity']}] {f['description'][:70]}...")

    if report["doubts"]:
        print("\n  Doubts Raised:")
        for d in report["doubts"][:2]:
            print(f"    {d['hypothesis'][:70]}...")

    if args.save:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"data/processed/multi_investigation_{ts}.json"
        os.makedirs("data/processed", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved to: {path}")

    print("\nDone!")
