import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from loguru import logger
from ai.report_hasher import ReportHasher


TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates", "dossier_en.html"
)


class DossierGenerator:

    def __init__(self, driver=None):
        self.driver  = driver
        self.hasher  = ReportHasher()
        self._jinja  = None
        self._weasy  = None
        self._load_libs()

    def _load_libs(self):
        try:
            import jinja2
            self._jinja = jinja2
            logger.success("[Dossier] Jinja2 loaded")
        except ImportError:
            logger.error("[Dossier] jinja2 not installed. Run: pip install jinja2")

        try:
            import weasyprint
            self._weasy = weasyprint
            logger.success("[Dossier] WeasyPrint loaded")
        except Exception as e:
            logger.warning(f"[Dossier] WeasyPrint not available: {e}")
            logger.info("[Dossier] HTML output available. Install weasyprint for PDF.")

    def assemble_dossier_data(self, entity_id: str,
                               multi_report: dict = None) -> dict:
        generated_at = datetime.now().isoformat()
        report_hash  = self.hasher.generate_hash(entity_id, generated_at)

        overview     = {}
        entity_type  = "Unknown"
        entity_name  = entity_id

        if self.driver:
            try:
                with self.driver.session() as session:
                    row = session.run(
                        """
                        MATCH (n {id: $id})
                        RETURN n.name AS name, labels(n)[0] AS type,
                               n.party AS party, n.state AS state,
                               n.total_assets AS assets,
                               n.risk_score AS risk_score,
                               n.risk_level AS risk_level
                        """,
                        id=entity_id
                    ).single()
                    if row:
                        entity_name = row["name"] or entity_id
                        entity_type = row["type"] or "Unknown"
                        overview = {
                            "party":      row.get("party"),
                            "state":      row.get("state"),
                            "assets":     row.get("assets"),
                            "risk_score": row.get("risk_score", 0),
                            "risk_level": row.get("risk_level", "UNKNOWN"),
                        }
            except Exception as e:
                logger.warning(f"[Dossier] Neo4j query failed: {e}")

        if multi_report:
            entity_name = multi_report.get("entity_name", entity_name)

        agreed_findings      = []
        doubts               = []
        positive_contributions = []
        timeline             = []
        evidence_locker      = []
        investigator_count   = 12

        if multi_report:
            agreed_findings        = multi_report.get("agreed_findings", [])
            doubts                 = multi_report.get("doubts", [])
            positive_contributions = multi_report.get("positive_contributions", [])
            timeline               = multi_report.get("timeline", [])
            evidence_locker        = multi_report.get("evidence_locker", [])
            investigator_count     = multi_report.get("investigator_count", 12)

        if self.driver and not self.hasher.store_hash(
            report_hash, entity_id, generated_at, self.driver
        ):
            logger.info("[Dossier] Hash storage skipped — no live driver")

        risk_score = int(overview.get("risk_score") or 0)
        risk_level = overview.get("risk_level") or "UNKNOWN"

        return {
            "entity_id":           entity_id,
            "entity_name":         entity_name,
            "entity_type":         entity_type,
            "report_hash":         report_hash,
            "generated_at":        generated_at[:19].replace("T", " "),
            "investigator_count":  investigator_count,
            "evidence_count":      len(evidence_locker),
            "overview":            overview,
            "risk_score":          risk_score,
            "risk_level":          risk_level,
            "agreed_findings":     agreed_findings,
            "doubts":              doubts,
            "positive_contributions": positive_contributions,
            "timeline":            timeline,
            "evidence_locker":     evidence_locker,
        }

    def render_html(self, dossier_data: dict) -> str:
        if not self._jinja:
            logger.error("[Dossier] Jinja2 not available — cannot render HTML")
            return ""

        if not os.path.exists(TEMPLATE_PATH):
            logger.error(f"[Dossier] Template not found: {TEMPLATE_PATH}")
            return ""

        env      = self._jinja.Environment(
            loader=self._jinja.FileSystemLoader(
                os.path.dirname(TEMPLATE_PATH)
            )
        )
        template = env.get_template(os.path.basename(TEMPLATE_PATH))
        html     = template.render(**dossier_data)
        logger.success(
            f"[Dossier] HTML rendered for {dossier_data['entity_name']} "
            f"({len(html):,} chars)"
        )
        return html

    def render_pdf(self, html: str, output_path: str) -> bool:
        if not self._weasy:
            logger.warning(
                "[Dossier] WeasyPrint not available — "
                "saving HTML instead of PDF"
            )
            html_path = output_path.replace(".pdf", ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"[Dossier] HTML saved to: {html_path}")
            return True

        try:
            self._weasy.HTML(string=html).write_pdf(output_path)
            size_kb = os.path.getsize(output_path) // 1024
            logger.success(
                f"[Dossier] PDF saved: {output_path} ({size_kb} KB)"
            )
            return True
        except Exception as e:
            logger.error(f"[Dossier] PDF generation failed: {e}")
            return False

    def generate(self, entity_id: str, multi_report: dict = None,
                  output_dir: str = "data/processed") -> dict:
        os.makedirs(output_dir, exist_ok=True)
        dossier_data = self.assemble_dossier_data(entity_id, multi_report)
        html         = self.render_html(dossier_data)

        result = {
            "entity_id":   entity_id,
            "entity_name": dossier_data["entity_name"],
            "report_hash": dossier_data["report_hash"],
            "generated_at":dossier_data["generated_at"],
            "html_ready":  bool(html),
            "pdf_path":    None,
            "html_path":   None,
        }

        if html:
            ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name  = "".join(
                c if c.isalnum() else "_"
                for c in dossier_data["entity_name"]
            )[:30]
            pdf_path    = os.path.join(
                output_dir, f"dossier_{clean_name}_{ts}.pdf"
            )
            success     = self.render_pdf(html, pdf_path)
            if success:
                actual_path = pdf_path if os.path.exists(pdf_path) \
                              else pdf_path.replace(".pdf", ".html")
                result["pdf_path"]  = actual_path
                result["html_path"] = pdf_path.replace(".pdf", ".html") \
                                      if not os.path.exists(pdf_path) else None

        return result


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph - Dossier Generator Test")
    print("=" * 55)

    generator = DossierGenerator(driver=None)

    sample_report = {
        "entity_name":     "Sample Politician",
        "investigator_count": 12,
        "agreed_findings": [
            {
                "type":        "contract_financial_flow",
                "description": "Entity linked to 3 contracts totalling Rs 150 Cr.",
                "severity":    "HIGH",
                "confidence":  "HIGH",
                "evidence":    ["Contract order from GeM"],
            }
        ],
        "doubts": [
            {
                "hypothesis": "Company directorships exist but no matching contracts found.",
                "gap":        "Possible CPPP data coverage gap",
                "action":     "Cross-reference with CPPP tender awards",
            }
        ],
        "positive_contributions": [
            "Party affiliation recorded providing public accountability.",
            "No matches found in ICIJ Offshore Leaks database.",
        ],
        "timeline": [
            {
                "date":   "2022-04-15",
                "event":  "Contract Awarded",
                "detail": "Rs 50 Cr from Ministry of Rural Development",
                "source": "GeM",
            }
        ],
        "evidence_locker": [
            {
                "institution": "Government e-Marketplace",
                "document":    "Contract Order Records",
                "url":         "https://gem.gov.in",
                "date":        "2022-04-15",
            },
            {
                "institution": "Election Commission of India",
                "document":    "Candidate Affidavit",
                "url":         "https://myneta.info",
                "date":        "2024-04-01",
            },
        ],
    }

    result = generator.generate(
        "sample_entity_001",
        multi_report=sample_report,
        output_dir="data/processed",
    )

    print(f"\n  Entity:       {result['entity_name']}")
    print(f"  Report hash:  {result['report_hash'][:32]}...")
    print(f"  HTML ready:   {result['html_ready']}")
    print(f"  Output path:  {result.get('pdf_path') or result.get('html_path')}")

    print("\nDone!")
