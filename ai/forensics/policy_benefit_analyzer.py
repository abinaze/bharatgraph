import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from loguru import logger

GRANGER_LAG        = 2
GRANGER_THRESHOLD  = 2.5
CACA_WINDOW_DAYS   = 180
ENTROPY_THRESHOLD  = 0.15


class PolicyBenefitAnalyzer:
    """
    Three causal analysis methods applied to policy events and entity benefits:

    1. Granger causality: tests whether policy time series improves prediction
       of contract award series beyond lagged contract values alone.

    2. Transfer entropy: measures directional information flow from policy
       event series to contract award series.

    3. Cumulative Abnormal Contract Award (CACA): computes difference between
       actual contract awards post-policy versus pre-event baseline.
    """

    def analyze(self, entity_id: str, entity_name: str,
                driver=None) -> dict:
        logger.info(f"[PolicyBenefitAnalyzer] Analyzing {entity_name}")

        events    = self._fetch_policy_events(entity_id, driver)
        contracts = self._fetch_contracts(entity_id, driver)

        if not events or not contracts:
            return {
                "entity_id":      entity_id,
                "entity_name":    entity_name,
                "status":         "insufficient_data",
                "event_count":    len(events),
                "contract_count": len(contracts),
                "analyzed_at":    datetime.now().isoformat(),
            }

        policy_series   = self._build_series(events,    "date")
        contract_series = self._build_series(contracts, "date")

        granger = self._granger_causality(policy_series, contract_series)
        entropy = self._transfer_entropy(policy_series, contract_series)
        caca    = self._caca(events, contracts)

        findings = []
        positive = []

        if granger.get("significant"):
            findings.append({
                "type":     "granger_causality",
                "severity": "HIGH",
                "description": (
                    f"Granger causality test indicates that policy events "
                    f"associated with {entity_name} have statistically significant "
                    f"predictive power over subsequent contract award volumes "
                    f"(F-statistic {granger['f_stat']:.2f}, threshold "
                    f"{GRANGER_THRESHOLD}). This indicates a directional "
                    f"statistical relationship between policy activity and "
                    f"procurement outcomes."
                ),
                "evidence": [
                    f"F-statistic: {granger['f_stat']:.4f}",
                    f"Lag order: {GRANGER_LAG}",
                    f"Policy events in series: {len(events)}",
                ],
            })

        if entropy.get("significant"):
            findings.append({
                "type":     "transfer_entropy",
                "severity": "MODERATE",
                "description": (
                    f"Transfer entropy of {entropy['te_value']:.3f} nats from "
                    f"the policy event series to the contract series indicates "
                    f"directional information flow. Policy events carry predictive "
                    f"information about future contract patterns beyond historical "
                    f"contract data alone."
                ),
                "evidence": [
                    f"Transfer entropy: {entropy['te_value']:.4f} nats",
                    f"Threshold: {ENTROPY_THRESHOLD} nats",
                ],
            })

        if caca.get("significant"):
            findings.append({
                "type":     "cumulative_abnormal_award",
                "severity": "HIGH" if caca["caca_score"] > 2.0 else "MODERATE",
                "description": (
                    f"Cumulative Abnormal Contract Award score of "
                    f"{caca['caca_score']:.2f}x indicates that contract values "
                    f"in the {CACA_WINDOW_DAYS}-day window after policy events "
                    f"are significantly above the pre-event baseline. "
                    f"Expected: Rs {caca['expected_crore']:.1f} Cr. "
                    f"Actual: Rs {caca['actual_crore']:.1f} Cr."
                ),
                "evidence": [
                    f"Expected (baseline): Rs {caca['expected_crore']:.1f} Cr",
                    f"Actual (post-event): Rs {caca['actual_crore']:.1f} Cr",
                    f"CACA ratio: {caca['caca_score']:.2f}x",
                    f"Events analysed: {caca['events_count']}",
                ],
            })

        if not findings:
            positive.append(
                "Policy-benefit causal analysis found no statistically significant "
                "relationship between policy events and contract award patterns for "
                "this entity in the available data."
            )

        logger.success(
            f"[PolicyBenefitAnalyzer] {entity_name}: {len(findings)} findings"
        )

        return {
            "entity_id":      entity_id,
            "entity_name":    entity_name,
            "event_count":    len(events),
            "contract_count": len(contracts),
            "granger":        granger,
            "entropy":        entropy,
            "caca":           caca,
            "findings":       findings,
            "positive":       positive,
            "analyzed_at":    datetime.now().isoformat(),
        }

    def _granger_causality(self, x: list, y: list) -> dict:
        n = min(len(x), len(y))
        if n < GRANGER_LAG * 3 + 2:
            return {"significant": False, "f_stat": 0.0, "reason": "insufficient_data"}
        x, y = x[:n], y[:n]
        rss_r = self._ar_residuals(y, GRANGER_LAG)
        rss_u = self._var_residuals(x, y, GRANGER_LAG)
        denom = rss_u / max(n - 2 * GRANGER_LAG - 1, 1)
        if denom == 0:
            return {"significant": False, "f_stat": 0.0}
        f_stat = max(0.0, ((rss_r - rss_u) / GRANGER_LAG) / denom)
        return {
            "significant":        f_stat > GRANGER_THRESHOLD,
            "f_stat":             round(f_stat, 4),
            "rss_restricted":     round(rss_r, 4),
            "rss_unrestricted":   round(rss_u, 4),
        }

    def _ar_residuals(self, y: list, lag: int) -> float:
        rss = 0.0
        for t in range(lag, len(y)):
            y_hat = sum(y[t - k - 1] for k in range(lag)) / lag
            rss  += (y[t] - y_hat) ** 2
        return rss

    def _var_residuals(self, x: list, y: list, lag: int) -> float:
        rss = 0.0
        for t in range(lag, len(y)):
            y_hat = (
                sum(y[t - k - 1] for k in range(lag)) +
                sum(x[t - k - 1] for k in range(lag))
            ) / (2 * lag)
            rss += (y[t] - y_hat) ** 2
        return rss

    def _transfer_entropy(self, x: list, y: list) -> dict:
        n = min(len(x), len(y))
        if n < 8:
            return {"significant": False, "te_value": 0.0}
        x, y = x[:n], y[:n]

        def discretise(series, bins=4):
            mn, mx = min(series), max(series)
            rng = mx - mn or 1.0
            return [min(int((v - mn) / rng * bins), bins - 1) for v in series]

        dx, dy = discretise(x), discretise(y)
        h_y   = self._conditional_entropy(dy[1:], dy[:-1])
        h_yyx = self._conditional_entropy(dy[1:], list(zip(dy[:-1], dx[:-1])))
        te    = max(0.0, h_y - h_yyx)
        return {"significant": te > ENTROPY_THRESHOLD, "te_value": round(te, 5)}

    def _conditional_entropy(self, y: list, x: list) -> float:
        from collections import Counter
        joint    = Counter(zip(x, y))
        marginal = Counter(x)
        n        = len(y)
        if n == 0:
            return 0.0
        h = 0.0
        for (xi, yi), cnt in joint.items():
            p_joint = cnt / n
            p_x     = marginal[xi] / n
            if p_joint > 0 and p_x > 0:
                h -= p_joint * math.log2(p_joint / p_x)
        return h

    def _caca(self, events: list, contracts: list) -> dict:
        if not events or not contracts:
            return {"significant": False, "caca_score": 0.0}
        from datetime import date as date_cls
        total_expected = 0.0
        total_actual   = 0.0
        events_counted = 0
        for event in events:
            ev_str = event.get("date", "")
            if not ev_str:
                continue
            try:
                ev_date = date_cls.fromisoformat(ev_str[:10])
            except ValueError:
                continue
            pre, post = [], []
            for c in contracts:
                c_str = c.get("date", "") or c.get("order_date", "")
                if not c_str:
                    continue
                try:
                    c_date = date_cls.fromisoformat(c_str[:10])
                except ValueError:
                    continue
                gap    = (c_date - ev_date).days
                amount = float(c.get("amount_crore") or c.get("amount") or 0)
                if -CACA_WINDOW_DAYS <= gap < 0:
                    pre.append(amount)
                elif 0 <= gap <= CACA_WINDOW_DAYS:
                    post.append(amount)
            if not pre:
                continue
            expected        = (sum(pre) / CACA_WINDOW_DAYS) * CACA_WINDOW_DAYS
            total_expected += expected
            total_actual   += sum(post)
            events_counted += 1
        if total_expected == 0 or events_counted == 0:
            return {"significant": False, "caca_score": 0.0, "events_count": 0}
        caca_score = total_actual / total_expected
        return {
            "significant":    caca_score > 1.5,
            "caca_score":     round(caca_score, 3),
            "expected_crore": round(total_expected, 2),
            "actual_crore":   round(total_actual, 2),
            "events_count":   events_counted,
        }

    def _fetch_policy_events(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {"date": "2018-06-01", "title": "Roads policy A"},
                {"date": "2019-03-15", "title": "Infrastructure bill"},
                {"date": "2021-09-10", "title": "Procurement rule change"},
                {"date": "2023-02-28", "title": "Budget allocation update"},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (pr:PressRelease)
                    WHERE toLower(pr.title) CONTAINS toLower($id)
                    RETURN pr.published AS date, pr.title AS title
                    ORDER BY pr.published LIMIT 20
                    """, id=entity_id
                ).data()
                return [{"date": r.get("date",""), "title": r.get("title","")}
                        for r in rows if r.get("date")]
        except Exception as e:
            logger.warning(f"[PolicyBenefit] Event fetch failed: {e}")
            return []

    def _fetch_contracts(self, entity_id: str, driver) -> list:
        if not driver:
            return [
                {"date": "2018-04-01", "amount_crore": 8.0},
                {"date": "2018-07-15", "amount_crore": 22.5},
                {"date": "2019-01-20", "amount_crore": 9.0},
                {"date": "2019-05-10", "amount_crore": 31.0},
                {"date": "2021-10-05", "amount_crore": 28.0},
                {"date": "2023-04-01", "amount_crore": 35.0},
            ]
        try:
            with driver.session() as s:
                rows = s.run(
                    """
                    MATCH (p {id:$id})-[:DIRECTOR_OF]->(c:Company)
                          -[:WON_CONTRACT]->(ct:Contract)
                    RETURN ct.order_date AS date,
                           ct.amount_crore AS amount_crore
                    ORDER BY ct.order_date
                    """, id=entity_id
                ).data()
                return [dict(r) for r in rows if r.get("date")]
        except Exception as e:
            logger.warning(f"[PolicyBenefit] Contract fetch failed: {e}")
            return []

    def _build_series(self, records: list, date_field: str) -> list:
        sorted_recs = sorted(
            [r for r in records if r.get(date_field)],
            key=lambda r: r[date_field]
        )
        return [float(r.get("amount_crore") or r.get("amount") or 1.0)
                for r in sorted_recs]


if __name__ == "__main__":
    print("=" * 55)
    print("BharatGraph — Policy Benefit Analyzer Test")
    print("=" * 55)
    a = PolicyBenefitAnalyzer()
    r = a.analyze("pol_001", "Test Entity", driver=None)
    print(f"\n  Events:    {r['event_count']}")
    print(f"  Contracts: {r['contract_count']}")
    print(f"  Granger:   F={r['granger']['f_stat']:.3f} sig={r['granger']['significant']}")
    print(f"  Entropy:   TE={r['entropy']['te_value']:.4f} sig={r['entropy']['significant']}")
    print(f"  CACA:      {r['caca'].get('caca_score',0):.2f}x sig={r['caca']['significant']}")
    print(f"  Findings:  {len(r['findings'])}")
    for f in r["findings"]:
        print(f"  [{f['severity']}] {f['type']}: {f['description'][:70]}")
    print("\nDone!")
