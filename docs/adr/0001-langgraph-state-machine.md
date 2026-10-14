# ADR 0001: LangGraph with explicit state, not a free-form agent chat
**Status:** Accepted
**Context:** Presales output has to be reproducible and auditable. Agents talking to each other freely is hard to test and drifts between runs.
**Decision:** Model the copilot as a typed `StateGraph`: analyst -> architect -> estimator -> critic, with a conditional loop back to the architect when the critic finds gaps (at most 2 iterations), then the writer.
**Consequences:** Each agent is a pure function of the state, so each one can be unit-tested. The loop is bounded, so it can't cause runaway cost.
