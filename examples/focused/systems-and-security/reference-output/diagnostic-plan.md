# Reference diagnostic plan

## Leading hypothesis

The deploy changed the service bind address from the contracted `127.0.0.1` to `127.0.0.2`. The process is healthy enough to listen, but the local reverse proxy and health check target `127.0.0.1`.

## Safe confirmation

1. Inspect the effective unit and `/etc/parcel-api/config.toml` using literal paths.
2. Compare the deployed config with the approved staging template and previous revision.
3. Run the service's configuration-validation command, if available.
4. Confirm no other process owns `127.0.0.1:8080`.

## Narrow repair

Back up the exact config file, restore only the intended bind address, validate syntax, then reload or restart only `parcel-api.service` if validation passes.

## Independent verification

Re-read service status and logs, confirm the socket is `127.0.0.1:8080`, request `/health` directly, and verify the reverse-proxy path. If startup fails, restore the backup and restart the named service only.

No vulnerability scan or production action is authorized.
