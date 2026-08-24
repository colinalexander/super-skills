# Expected decisions

- Set prediction time before the retention intervention and exclude later events.
- Identify `cancellation_reason` and `closed_account_at` as post-outcome leakage.
- Treat `support_tickets_next_30d` as unavailable future information.
- Replace random row splitting with a time-based cohort split that matches deployment.
- Compare against a simple base-rate or rules baseline.
- Select ranking or classification metrics from intervention capacity and error cost.
- Define segment error analysis, drift monitoring, fallback, and retirement conditions.
