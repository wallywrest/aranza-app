# Aranza v1.99

- Added full research-record editing with an automatic pre-edit snapshot.
- Added restoration of a selected historical version; current state is snapshotted before restore, making restoration reversible.
- Preserved account scoping for both edit and restore operations.
- Reuses the existing `historial_investigacion` table; no schema migration required.
- Added regression tests for round-trip restoration and cross-account isolation.
