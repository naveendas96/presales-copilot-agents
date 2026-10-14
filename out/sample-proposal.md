# Solution Proposal (draft)

## Executive summary
The proposed architecture is a governed lakehouse with medallion layers, a certified semantic layer and governed GenAI access, delivered in two phases.

## Requirements traceability matrix
| Req | Priority | Requirement | Capability | Component | Effort (d) |
|---|---|---|---|---|---|
| R01 | Must | The solution must ingest data from SAP ERP, Salesforce CRM and the Oracle warehouse on a daily batch schedule. | Batch ingestion | Managed ELT connectors -> Bronze layer | 25.0 |
| R02 | Must | The platform must support near real-time ingestion of e-commerce clickstream events with latency under 5 minutes. | Streaming ingestion | Event streaming (Kafka/Kinesis) -> Structured Streaming | 20.0 |
| R03 | Must | The vendor shall migrate 8 years of historical sales data from the Oracle warehouse. | Data migration | Bulk unload + reconciliation framework | 30.0 |
| R04 | Must | The solution must provide a governed semantic layer with certified KPIs for finance and merchandising. | Semantic layer | Governed semantic layer / metric store on Gold | 20.0 |
| R05 | Must | The platform must implement role-based access control and column-level masking of customer PII. | Security & governance | Unity Catalog / Snowflake RBAC + masking policies | 12.0 |
| R06 | Should | The solution should deliver 15 executive and operational dashboards. | BI dashboards | BI tool on certified semantic layer | 30 |
| R07 | Must | The vendor shall build a demand forecasting machine learning model at store and SKU level. | ML forecasting | Feature store + MLflow-managed forecasting pipeline | 35.0 |
| R08 | Should | The solution should provide a natural language assistant so business users can query sales data in plain English. | GenAI assistant | Governed text-to-SQL agent over semantic layer | 25.0 |
| R09 | Must | The platform must comply with data residency requirements and keep all data in-region. | Compliance | Single-region deployment + policy-as-code | 5.0 |
| R10 | Must | The vendor must provide data quality monitoring with alerting on pipeline failures. | Data quality & observability | Expectations framework + alerting to ITSM | 10.0 |
| R11 | Must | The vendor shall provide knowledge transfer and training for 40 internal users. | Enablement | Role-based training curriculum | 10.0 |
| R12 | Must | The solution must support disaster recovery with an RPO of 4 hours. | Resilience / DR | Cross-zone replication + tested runbooks | 8.0 |

## Solution outline
- **BI dashboards**: BI tool on certified semantic layer
- **Batch ingestion**: Managed ELT connectors -> Bronze layer
- **Compliance**: Single-region deployment + policy-as-code
- **Data migration**: Bulk unload + reconciliation framework
- **Data quality & observability**: Expectations framework + alerting to ITSM
- **Enablement**: Role-based training curriculum
- **GenAI assistant**: Governed text-to-SQL agent over semantic layer
- **ML forecasting**: Feature store + MLflow-managed forecasting pipeline
- **Resilience / DR**: Cross-zone replication + tested runbooks
- **Security & governance**: Unity Catalog / Snowflake RBAC + masking policies
- **Semantic layer**: Governed semantic layer / metric store on Gold
- **Streaming ingestion**: Event streaming (Kafka/Kinesis) -> Structured Streaming

## Effort estimate
- Delivery effort: 230.0 person-days
- Project management (12%): 27.6 person-days
- Contingency: 15%
- **Total: 296.2 person-days (~$177,720 at $600/day blended)**

## Risks
| Area | Risk | Linked reqs |
|---|---|---|
| Batch ingestion | Source-system API limits and SAP extractor licensing | R01 |
| Streaming ingestion | Latency SLA depends on client network and event volume | R02 |
| Data migration | Historical data quality unknown; reconciliation effort may grow | R03 |
| Semantic layer | KPI definitions need business sign-off | R04 |
| Security & governance | Role model must be agreed with InfoSec early | R05 |
| BI dashboards | Dashboard scope creep | R06 |
| ML forecasting | Forecast accuracy depends on history depth and promotions data | R07 |
| GenAI assistant | Hallucinated SQL; needs guardrails and eval harness | R08 |
| Compliance | Some managed AI services may not be available in-region | R09 |
| Data quality & observability | Alert fatigue without ownership model | R10 |
| Enablement | Availability of client staff | R11 |
| Resilience / DR | DR tests require production change windows | R12 |

## Open review items
- None: all Must requirements are covered.
