"""Solution-pattern knowledge base: keyword triggers -> capability, component, base effort, risk."""
from __future__ import annotations

PATTERNS: list[dict] = [
    {"cap": "Batch ingestion", "keys": ["ingest", "batch", "erp", "crm"], "component": "Managed ELT connectors -> Bronze layer", "days": 25, "risk": "Source-system API limits and SAP extractor licensing"},
    {"cap": "Streaming ingestion", "keys": ["real-time", "real time", "streaming", "clickstream", "latency"], "component": "Event streaming (Kafka/Kinesis) -> Structured Streaming", "days": 20, "risk": "Latency SLA depends on client network and event volume"},
    {"cap": "Data migration", "keys": ["migrate", "migration", "historical"], "component": "Bulk unload + reconciliation framework", "days": 30, "risk": "Historical data quality unknown; reconciliation effort may grow"},
    {"cap": "Semantic layer", "keys": ["semantic", "kpi", "metric"], "component": "Governed semantic layer / metric store on Gold", "days": 20, "risk": "KPI definitions need business sign-off"},
    {"cap": "Security & governance", "keys": ["access control", "masking", "pii", "rbac"], "component": "Unity Catalog / Snowflake RBAC + masking policies", "days": 12, "risk": "Role model must be agreed with InfoSec early"},
    {"cap": "BI dashboards", "keys": ["dashboard", "report"], "component": "BI tool on certified semantic layer", "days": 2, "per_unit": True, "risk": "Dashboard scope creep"},
    {"cap": "ML forecasting", "keys": ["forecast", "machine learning", "ml model"], "component": "Feature store + MLflow-managed forecasting pipeline", "days": 35, "risk": "Forecast accuracy depends on history depth and promotions data"},
    {"cap": "GenAI assistant", "keys": ["natural language", "plain english", "assistant", "genai"], "component": "Governed text-to-SQL agent over semantic layer", "days": 25, "risk": "Hallucinated SQL; needs guardrails and eval harness"},
    {"cap": "Compliance", "keys": ["residency", "comply", "compliance", "in-region"], "component": "Single-region deployment + policy-as-code", "days": 5, "risk": "Some managed AI services may not be available in-region"},
    {"cap": "Data quality & observability", "keys": ["data quality", "monitoring", "alert"], "component": "Expectations framework + alerting to ITSM", "days": 10, "risk": "Alert fatigue without ownership model"},
    {"cap": "Enablement", "keys": ["training", "knowledge transfer"], "component": "Role-based training curriculum", "days": 0.25, "per_unit": True, "risk": "Availability of client staff"},
    {"cap": "Resilience / DR", "keys": ["disaster recovery", "rpo", "rto", "backup"], "component": "Cross-zone replication + tested runbooks", "days": 8, "risk": "DR tests require production change windows"},
]


def match(text: str) -> dict | None:
    t = text.lower()
    best, score = None, 0
    for p in PATTERNS:
        s = sum(k in t for k in p["keys"])
        if s > score:
            best, score = p, s
    return best
