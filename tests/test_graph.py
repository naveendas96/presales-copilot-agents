from pathlib import Path

from copilot.graph import build
from copilot.llm import MockLLM

RFP = (Path(__file__).parents[1] / "samples" / "rfp-retail-analytics.md").read_text()


def run(rfp=RFP):
    return build().invoke({"rfp": rfp})


def test_extracts_all_requirements():
    s = run()
    assert len(s["requirements"]) == 12
    assert s["requirements"][5]["priority"] == "Should"


def test_full_traceability_coverage():
    s = run()
    assert all(d["capability"] != "UNMAPPED" for d in s["design"])
    assert s["critique"] == []


def test_estimate_is_consistent():
    e = run()["estimate"]
    assert e["base_days"] == sum(l["days"] for l in e["lines"])
    assert e["total_days"] > e["base_days"]
    dash = next(l for l in e["lines"] if l["capability"] == "BI dashboards")
    assert dash["days"] == 30  # 15 dashboards x 2 days


def test_unmapped_requirement_flagged_by_critic():
    s = run("## Req\n1. The vendor must provide quantum teleportation.\n")
    assert s["critique"] and s["iterations"] == 2  # critic looped once, then stopped
    assert "Open review items" in s["proposal"]


def test_proposal_sections():
    md = run()["proposal"]
    for h in ["Requirements traceability matrix", "Solution outline", "Effort estimate", "Risks"]:
        assert f"## {h}" in md


def test_llm_is_pluggable():
    llm = MockLLM(lambda p, s: '[{"id":"R01","text":"Build dashboards","priority":"Must"}]' if p.startswith("EXTRACT") else "custom summary")
    s = build(llm).invoke({"rfp": "x"})
    assert "custom summary" in s["proposal"] and len(llm.calls) == 2


def test_cost_matches_total_days_and_rate():
    from copilot.graph import RATE_PER_DAY_USD
    e = run()["estimate"]
    assert e["cost_usd"] == round(e["total_days"] * RATE_PER_DAY_USD)
    assert e["pm_days"] == round(e["base_days"] * 0.12, 1)


def test_cli_writes_proposal(tmp_path, monkeypatch):
    import sys
    from copilot.cli import main
    out = tmp_path / "p.md"
    rfp = Path(__file__).parents[1] / "samples" / "rfp-retail-analytics.md"
    monkeypatch.setattr(sys, "argv", ["copilot", str(rfp), "-o", str(out)])
    main()
    assert out.read_text().startswith("# Solution Proposal (draft)")
