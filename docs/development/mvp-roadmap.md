# MVP implementation roadmap and backlog v0.1

**Status:** proposed. No dates, staffing commitments, or remote tracking tickets have been created.

## Phase 0 — Governance and baseline (P0)

| Task | Acceptance evidence |
|---|---|
| Approve product boundary, name, owner, repository class | Signed ADR and repo metadata |
| Select open-source app license, dependency policy and packaging | Approved legal/license inventory and SBOM |
| Inventory current Stable Glaze/9-system contracts | Versioned applicability matrix, validators and blockers |
| Establish fixture repository and CI test machines | Repeatable reproducible fixtures |
| Define media schema v1 and compatibility/error contracts | JSON schema, migration tests, API docs |

## Phase 1 — Native application foundation (P0)

| Task | Acceptance evidence |
|---|---|
| Create original Rust workspace + Tauri v2 desktop package | `cargo test`, packaged smoke-test, installation proof |
| Move prototype plan/queue/worker into Rust modules | Differential tests against Python prototype fixtures |
| Glaze UI conformant shell, source chooser, processing modes | Rendered visual, accessibility and navigation acceptance |
| SQLite durable journal + recovery and non-clobber semantics | crash/restart/cancel integration tests |
| FFmpeg/ffprobe capability probe, provenance, version pinning | Runtime reports with verified features |

## Phase 2 — Disc preservation (P0; equal priority)

| Task | Acceptance evidence |
|---|---|
| DVD adapter: title, angle, track and chapter metadata | Fixture-based test for DVD-Video structure |
| Blu-ray adapter: MPLS title / seamless branching | Test with legal unencrypted sample BDMV fixtures |
| Track selector, map, subtitles, chapter preservation | exact selected-track inventory assertions |
| MKV archive with no video re-encode | codec/stream-content verification, error matrix |
| Read errors, destination preflight, optical device lock | failure-injection tests |

## Phase 3 — Transcoding (P0; equal priority)

| Task | Acceptance evidence |
|---|---|
| Video: H.264 presets, CRF and bitrate modes | objective metadata + playback sample suite |
| Audio track selection and conversion | channel/layout/language matrix |
| Subtitle copy/burn-in compatibility checks | no silent loss tests |
| Resolution, crop, rate/frame controls | pixel dimension/rate verification |
| MP4/MKV outputs and device profiles | profile compatibility tests |

## Phase 4 — Unified pipeline & quality (P0)

| Task | Acceptance evidence |
|---|---|
| Source fingerprint and shared scan model | deterministic plans, stale-source detection |
| Preserve+Convert with one optical read when possible | archive survives subsequent encoding failure |
| Separate output verification and durable manifests | `partial_success` with correct preserved results |
| Persistent jobs, retries, queue limits and cancellation | interrupted/recovery load tests |
| User-facing progress/status and error explanations | accessibility and UX test |

## Phase 5 — Qualification & release (P0)

| Task | Acceptance evidence |
|---|---|
| Windows/Linux packaging with hardware fixtures | verified installers, smoke tests |
| macOS packaging/entitlements if in scope | platform validation evidence |
| Security, privacy, dependency and platform system audits | accepted gates + documented blocks |
| End-to-end tests on legal test media | published test results; pass thresholds |
| Documentation, support/runbooks, changelog, migration | release package with non-placeholder version |

## Phase 6 — Post-MVP (P1/P2)

- HEVC/AV1/hardware transcoding, including quality comparisons.
- More complete BD/UHD and menu/ISO preservation where legally supported.
- Multi-drive and worker concurrency, distributed services where appropriate.
- Advanced subtitle editing, OCR only where justified and lawful, HDR/Dolby Vision paths.
- Optional GoreeCloud Video handoff and further approved integrations.

## Release gates

`G0: governance` → `G1: supported file modes work` → `G2: both disc formats work unencrypted` → `G3: native UX and three workflows work` → `G4: threat/license/dependency controls` → `G5: cross-platform, Glaze, nine-system evidence` → `release candidate`.

No phase completion may be inferred from a passing unit test alone. The current prototype passes only a subset of **G1**.

## Assumptions / risks

- Runtime FFmpeg must have required encoders; x264 support is not guaranteed in all distributable builds.
- Blu-ray navigation and read errors may require OS-specific privileged/device APIs.
- Physical discs and multi-angle content demand representative legal fixtures; synthetic FFmpeg file tests are insufficient.
- Vendor-account-free packaging and license independence may affect codec availability.
- Native UI qualification requires authoritative current Stable Glaze contract: not determined by this proposal alone.

## Resource and effort planning

Use milestone exit criteria instead of invented calendar dates. Assign one architecture/backend owner, one native UI owner, and explicit QA/security/license reviewers; one person may perform multiple roles, but reviews and test evidence remain necessary. Rough effort and schedules should be estimated only after platforms, legal scope, fixtures and staffing are confirmed.
