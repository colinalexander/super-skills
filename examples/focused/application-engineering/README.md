# Application engineering: inventory reservation

This example designs an API that reserves scarce inventory for ten minutes under concurrent demand.

- **Trigger:** state ownership, transaction semantics, idempotency, expiry, and API boundaries determine correctness.
- **Non-trigger:** visual presentation and implementation workflow are secondary skills.
- **Fixture:** [`fixture/system-brief.md`](fixture/system-brief.md).
- **Reference artifacts:** [`reference-output/adr.md`](reference-output/adr.md) and [`reference-output/openapi.yaml`](reference-output/openapi.yaml).
- **Verification:** test the reservation invariant at the persistence/API boundary, including duplicate requests, expiry, and concurrency.
