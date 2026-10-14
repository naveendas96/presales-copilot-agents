"""LangGraph workflow: analyst -> architect -> estimator -> critic (-> architect on gaps) -> writer."""
from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from .kb import PATTERNS, match
from .llm import LLM, get_llm

RATE_PER_DAY_USD = 600
CONTINGENCY = 0.15


class State(TypedDict, total=False):
    rfp: str
    requirements: list[dict]
    design: list[dict]
    estimate: dict
    risks: list[dict]
    critique: list[str]
    iterations: int
    proposal: str


def mock_handler(prompt: str, _system: str) -> str:
    """Deterministic stand-in: the analyst prompt gets regex extraction as JSON; others get a summary line."""
    if prompt.startswith("EXTRACT"):
        rows = []
        for m in re.finditer(r"^\s*(\d+)\.\s+(.*)$", prompt, re.M):
            txt = m.group(2).strip()
            pr = "Must" if re.search(r"\b(must|shall)\b", txt, re.I) else "Should"
            rows.append({"id": f"R{int(m.group(1)):02d}", "text": txt, "priority": pr})
        return json.dumps(rows)
    return "The proposed architecture is a governed lakehouse with medallion layers, a certified semantic layer and governed GenAI access, delivered in two phases."


def analyst(llm: LLM):
    def node(s: State) -> State:
        out = llm.complete("EXTRACT numbered requirements as JSON list of {id,text,priority}.\n" + s["rfp"],
                           "You are a requirements analyst.")
        m = re.search(r"\[.*\]", out, re.S)
        reqs = json.loads(m.group(0)) if m else []
        return {"requirements": reqs, "iterations": 0}
    return node


def architect(s: State) -> State:
    design = []
    for r in s["requirements"]:
        p = match(r["text"])
        design.append({"req": r["id"], "capability": p["cap"] if p else "UNMAPPED",
                       "component": p["component"] if p else "Needs solution architect review"})
    return {"design": design, "iterations": s.get("iterations", 0) + 1}


def estimator(s: State) -> State:
    lines = []
    for d, r in zip(s["design"], s["requirements"]):
        p = next((x for x in PATTERNS if x["cap"] == d["capability"]), None)
        if not p:
            days = 10.0
        elif p.get("per_unit"):
            n = re.search(r"\b(\d+)\b\s+(?:\w+\s+){0,3}(?:dashboards|users|reports)", r["text"])
            days = p["days"] * (int(n.group(1)) if n else 10)
        else:
            days = float(p["days"])
        lines.append({"req": r["id"], "capability": d["capability"], "days": round(days, 1)})
    base = sum(x["days"] for x in lines)
    pm = round(base * 0.12, 1)
    total = round((base + pm) * (1 + CONTINGENCY), 1)
    return {"estimate": {"lines": lines, "base_days": base, "pm_days": pm,
                         "contingency_pct": CONTINGENCY * 100, "total_days": total,
                         "cost_usd": round(total * RATE_PER_DAY_USD)}}


def critic(s: State) -> State:
    issues = [f"{d['req']} has no mapped capability" for d in s["design"] if d["capability"] == "UNMAPPED"]
    musts = {r["id"] for r in s["requirements"] if r["priority"] == "Must"}
    covered = {d["req"] for d in s["design"] if d["capability"] != "UNMAPPED"}
    issues += [f"Must-have {m} not covered" for m in sorted(musts - covered)]
    risks, seen = [], set()
    for d in s["design"]:
        p = next((x for x in PATTERNS if x["cap"] == d["capability"]), None)
        if p and p["cap"] not in seen:
            seen.add(p["cap"])
            risks.append({"area": p["cap"], "risk": p["risk"], "reqs": [x["req"] for x in s["design"] if x["capability"] == p["cap"]]})
    if re.search(r"6 months", s["rfp"]) and s["estimate"]["total_days"] > 300:
        risks.append({"area": "Timeline", "risk": f"{s['estimate']['total_days']} person-days in 6 months needs a team of ~{round(s['estimate']['total_days'] / 110)}+ FTE; phase scope", "reqs": []})
    return {"critique": issues, "risks": risks}


def route(s: State) -> str:
    return "architect" if s["critique"] and s["iterations"] < 2 else "writer"


def writer(llm: LLM):
    def node(s: State) -> State:
        summary = llm.complete("SUMMARISE solution for executive summary:\n" + json.dumps(s["design"]),
                               "You are a principal solution architect.")
        e = s["estimate"]
        md = ["# Solution Proposal (draft)", "", "## Executive summary", summary, "",
              "## Requirements traceability matrix", "| Req | Priority | Requirement | Capability | Component | Effort (d) |", "|---|---|---|---|---|---|"]
        for r, d, l in zip(s["requirements"], s["design"], e["lines"]):
            md.append(f"| {r['id']} | {r['priority']} | {r['text']} | {d['capability']} | {d['component']} | {l['days']} |")
        caps = sorted({d["capability"] for d in s["design"]})
        md += ["", "## Solution outline", *[f"- **{c}**: " + next(d["component"] for d in s["design"] if d["capability"] == c) for c in caps],
               "", "## Effort estimate", f"- Delivery effort: {e['base_days']} person-days",
               f"- Project management (12%): {e['pm_days']} person-days",
               f"- Contingency: {e['contingency_pct']:.0f}%", f"- **Total: {e['total_days']} person-days (~${e['cost_usd']:,} at ${RATE_PER_DAY_USD}/day blended)**",
               "", "## Risks", "| Area | Risk | Linked reqs |", "|---|---|---|",
               *[f"| {r['area']} | {r['risk']} | {', '.join(r['reqs'])} |" for r in s["risks"]],
               "", "## Open review items", *([f"- {c}" for c in s["critique"]] or ["- None: all Must requirements are covered."])]
        return {"proposal": "\n".join(md) + "\n"}
    return node


def build(llm: LLM | None = None) -> Any:
    llm = llm or get_llm(mock_handler)
    g = StateGraph(State)
    g.add_node("analyst", analyst(llm))
    g.add_node("architect", architect)
    g.add_node("estimator", estimator)
    g.add_node("critic", critic)
    g.add_node("writer", writer(llm))
    g.set_entry_point("analyst")
    g.add_edge("analyst", "architect")
    g.add_edge("architect", "estimator")
    g.add_edge("estimator", "critic")
    g.add_conditional_edges("critic", route, {"architect": "architect", "writer": "writer"})
    g.add_edge("writer", END)
    return g.compile()
