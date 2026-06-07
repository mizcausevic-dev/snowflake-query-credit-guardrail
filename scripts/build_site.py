from __future__ import annotations

import html
from pathlib import Path

from snowflake_query_credit_guardrail import analyze_queries, load_rows


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "snowflake-query-credit-sample.json"
OUT_DIR = ROOT / "site"


def main() -> None:
    summary = analyze_queries(load_rows(FIXTURE))
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(render(summary), encoding="utf-8")


def render(summary: dict) -> str:
    findings = "\n".join(
        f"""
        <article class="finding">
          <div>
            <span class="eyebrow">{html.escape(item['severity'])} / {item['risk_score']}</span>
            <h3>{html.escape(item['query_hash'])}</h3>
            <p>{html.escape(item['warehouse'])} / {html.escape(item['owner'])}</p>
          </div>
          <strong>{item['credits']} credits</strong>
          <p>{html.escape(item['recommendation'])}</p>
        </article>
        """
        for item in summary["top_findings"][:5]
    )
    warehouses = "\n".join(
        f"<li><span>{html.escape(row['name'])}</span><strong>{row['credits']} credits</strong><em>risk {row['risk']}</em></li>"
        for row in summary["warehouse_pressure"][:5]
    )
    owners = "\n".join(
        f"<li><span>{html.escape(row['name'])}</span><strong>{row['credits']} credits</strong><em>risk {row['risk']}</em></li>"
        for row in summary["owner_pressure"][:5]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Snowflake Query Credit Guardrail</title>
  <meta name="description" content="Offline Snowflake query credit guardrail for warehouse burn, cache misses, owner gaps, and remediation sequencing." />
  <style>
    :root {{
      color-scheme: dark;
      --ink: #f5f1e9;
      --muted: #9aa7ba;
      --bg: #05080f;
      --panel: #0d1624;
      --line: rgba(125, 229, 207, 0.22);
      --cyan: #28d9ff;
      --mint: #46f0af;
      --violet: #a78bfa;
      --warn: #ffd166;
    }}
    * {{ box-sizing: border-box; }}
    html {{ width: 100%; overflow-x: hidden; background: var(--bg); }}
    body {{
      margin: 0;
      font-family: "Geist", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 80% 10%, rgba(167, 139, 250, 0.16), transparent 34rem),
        radial-gradient(circle at 12% 18%, rgba(40, 217, 255, 0.13), transparent 30rem),
        linear-gradient(135deg, #05080f 0%, #080b17 55%, #061521 100%);
    }}
    main {{ width: min(1180px, calc(100% - 36px)); margin: 0 auto; padding: 42px 0 56px; }}
    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: clamp(28px, 5vw, 58px);
      background: linear-gradient(145deg, rgba(13, 22, 36, 0.96), rgba(6, 12, 22, 0.92));
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
      border-top: 5px solid var(--cyan);
    }}
    .eyebrow {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      color: var(--mint);
      text-transform: uppercase;
      letter-spacing: .18em;
      font-size: .75rem;
      font-weight: 800;
    }}
    h1 {{
      max-width: 940px;
      margin: 18px 0;
      font-size: clamp(3.4rem, 10vw, 8rem);
      line-height: .88;
      letter-spacing: -0.08em;
    }}
    p {{ color: var(--muted); font-size: 1.1rem; line-height: 1.7; max-width: 780px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-top: 34px;
    }}
    .metric, .card, .finding {{
      border: 1px solid rgba(255,255,255,.1);
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.045);
      padding: 20px;
    }}
    .metric strong {{ display:block; font-size: clamp(2rem, 4vw, 3.4rem); letter-spacing: -.05em; }}
    .grid {{ display: grid; grid-template-columns: 1.15fr .85fr; gap: 18px; margin-top: 18px; }}
    h2 {{ font-size: clamp(2.2rem, 5vw, 4.6rem); line-height: .95; letter-spacing: -.06em; margin: 0 0 18px; }}
    .finding {{ display: grid; gap: 12px; margin-bottom: 12px; border-left: 4px solid var(--mint); }}
    .finding h3 {{ margin: 8px 0 2px; font-family: "JetBrains Mono", ui-monospace, monospace; }}
    .finding strong {{ color: var(--warn); font-size: 1.2rem; }}
    ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }}
    li {{ display: grid; grid-template-columns: 1fr auto auto; gap: 14px; align-items: center; color: var(--muted); }}
    li strong {{ color: var(--ink); }}
    li em {{ color: var(--cyan); font-style: normal; font-family: ui-monospace, monospace; }}
    footer {{ margin-top: 28px; color: var(--muted); font-size: .9rem; }}
    a {{ color: var(--cyan); }}
    @media (max-width: 820px) {{
      main {{ width: min(100% - 24px, 1180px); padding-top: 18px; }}
      .metrics, .grid {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: clamp(3rem, 16vw, 5rem); }}
      li {{ grid-template-columns: 1fr; gap: 4px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <span class="eyebrow">Snowflake / credit guardrail</span>
      <h1>Which queries are turning warehouse power into avoidable spend?</h1>
      <p>Snowflake Query Credit Guardrail converts exported query-history rows into owner-visible remediation lanes for cache reuse, warehouse sizing, tagging hygiene, and spend-review sequencing.</p>
      <div class="metrics">
        <div class="metric"><span class="eyebrow">Queries</span><strong>{summary['total_queries']}</strong></div>
        <div class="metric"><span class="eyebrow">Credits</span><strong>{summary['total_credits']}</strong></div>
        <div class="metric"><span class="eyebrow">Avoidable</span><strong>{summary['avoidable_credits']}</strong></div>
        <div class="metric"><span class="eyebrow">High risk</span><strong>{summary['high_risk_queries']}</strong></div>
      </div>
    </section>

    <section class="grid">
      <div class="card">
        <h2>Query findings</h2>
        {findings}
      </div>
      <div class="card">
        <h2>Pressure map</h2>
        <p><strong>Primary recommendation:</strong> {html.escape(summary['primary_recommendation'])}</p>
        <h3>Warehouse pressure</h3>
        <ul>{warehouses}</ul>
        <h3>Owner pressure</h3>
        <ul>{owners}</ul>
      </div>
    </section>
    <footer>
      <a href="https://github.com/mizcausevic-dev/snowflake-query-credit-guardrail">GitHub</a> /
      <a href="https://portfolio.kineticgain.com/">Kinetic Gain Portfolio</a>
    </footer>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    main()

