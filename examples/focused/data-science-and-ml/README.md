# Data science and ML: churn leakage review

This example audits a churn-model proposal whose strongest feature is recorded after the prediction decision.

- **Trigger:** target definition, temporal validation, leakage, baseline, metrics, and deployment behavior determine validity.
- **Non-trigger:** an ordinary CRUD API does not require an ML workflow.
- **Fixture:** [`fixture/model-proposal.md`](fixture/model-proposal.md) and [`fixture/sample.csv`](fixture/sample.csv).
- **Reference artifact:** [`reference-output/analysis.md`](reference-output/analysis.md).
- **Verification:** reconstruct the deployment-time feature boundary and show why the proposed random split cannot estimate production performance.
