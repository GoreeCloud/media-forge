# Media Forge architecture — proposed production design v0.1

## Architecture decision

Media Forge is a **new native GoreeCloud application**, not a fork of HandBrake/MakeMKV and not part of GoreeCloud Video. It uses bounded media libraries and codecs, with a future **Rust + Tauri + current Stable Glaze** desktop application and a native Rust orchestration core. The included Python/vanilla-JS runtime is a deliberately limited *testable prototype* of the orchestration contract, not the approved final runtime.

## Component diagram

```
Desktop UI (Glaze via Tauri) ------ status/events ------+--------------------------+
    |                                                  | GoreeCloud owned core    |
    +---- validated user commands --------------------->|                          |
                                                       | Source registry          |
Local media file ------> Media probes ----------------->| Title / track inventory  |
DVD / Blu-ray ---------> Disc adapters* -------------->| ProcessingPlan compiler  |
                                                       | Job scheduler / journal  |
                                                       | Output validator         |
                                                       +------------+-------------+
                                                                    |
                                           +------------------------+-----------------+
                                           v                                          v
                                 Preservation worker                          Transcode worker
                                 stream copy / remux                          decode/filter/encode
                                           |                                          |
                                           +----------------------+-------------------+
                                                                  v
                                                       Verified local output
                                                                  |
                                                       Optional integration adapter*
                                                       (GoreeCloud Video, etc.)

* Planned, not implemented in the prototype.
```

## Isolation rules

- UI never directly constructs or executes FFmpeg shell commands.
- Local-source paths and destination paths are validated before processing.
- `ProcessingPlan` is a versioned data structure; source, title, track, and output descriptors are separate.
- Source adapters own DVD/Blu-ray device-specific behavior; unsupported/encrypted sources have typed errors.
- Preservation must not call a video encoder. Stream-copy errors are surfaced; never silently change mode.
- Transcode may re-encode video/audio; container limitations are preflighted.
- Verified archive output remains intact if its subsequent conversion fails.
- Media payloads remain authoritative files. Queue DB, thumbnails, manifests, and cached metadata can be rebuilt or exported.
- Backend operations use filesystem constraints, limited worker concurrency, sanitized logs, no shell interpolation, and atomic publication.

## Disc source model (planned)

```
Source: {id, kind: file|dvd|bluray|folder, locator, device_capabilities, protection_status}
Title:  {title_id, playlist_id?, duration, streams[], chapters[], angles[], warnings[]}
Stream: {index, kind, codec, language, channels, role, compatibility}
Plan:   {schema_version, input, title_selection[], stream_selection[], outputs[], validation_policy}
Output: {kind: archive|transcode|full_disc_image, container, codec_policy, destination}
Job:    {id, state, stage, progress, artifacts[], warnings[], errors[]}
```

The current code uses a reduced v0 prototype plan (`source`, `output_dir`, `mode`, `preset`, `container`) and can process ordinary media files only.

## Future disc processing

- DVD: build device/folder adapter around mature open-source disc-navigation libraries (`libdvdread`, `libdvdnav`) and FFmpeg decoders. Implement IFO title/chapter/angle handling; use read errors and verification events.
- Blu-ray: use `libbluray` for playlists, MPLS/CLPI metadata, title and stream discovery. Handle seamless branching and distinguish physical disc layout from playlist titles.
- Protected discs: separate legal and technical investigation; do not imply support from `libbluray` alone.
- Full-disc image and original menu preservation: separate output type, not equivalent to the current MKV remux mode.

## Combined processing plan

1. Scan title and tracks and freeze a source fingerprint; user selects mode and destinations.
2. Preflight disk space, codec support, source readability, permission and legal-policy gates.
3. Stage 1 writes an archive output to a temporary path, stream-copies and verifies selected streams, then atomically publishes.
4. Stage 2 transcodes the verified archive where possible; errors do not roll back archive.
5. Emit independent manifests, per-output verification details, jobs/events and provenance/version metadata.

## Concurrency and performance

Start with one optical-drive read per drive, optional separate worker for file transcodes, configurable CPU/IO budgets; cap memory, queued jobs, log size, output staging, and thread counts. Only allow parallel transcodes after throughput and thermal behavior are benchmarked. Avoid simultaneous read jobs on one optical device.

## GoreeCloud platform contracts — evaluation required

The verified active instruction defines nine systems: Manager, Privacy Shield, Wardveil Security, Everkeep, Glaze UI, Mesh, Identity, Policy, Observability. Every system requires explicit applicability, authoritative contract/version, adapter, evidence, tests, blockers, and an honest state. None are implemented merely by labeling the UI or a YAML field. On standalone local use, an offline fallback must retain essential processing without bypassing enforced security/privacy policy.

## Relationship to `GoreeCloud/video`

Video owns streaming, discovery, playback and its metadata index. Media Forge owns source acquisition, preservation, conversion, and validation. A future handoff adapter may request import/indexing of *already verified, user-approved* output files without making Video the authoritative holder of the original media or requiring it for conversion.

## Sources reviewed

GoreeCloud Drive: `Requirement — Open-Source Software`, `Requirement — Fork-to-Native Integration and Distinct GoreeCloud Identity`, `Instructions — Native Application Development, Migration, and Platform Compliance`, `Instructions — Integral Platform Systems`, `Instructions — System-Wide Platform Contract`, `Standard — Repository Architecture, Boundaries, and Organization`. GitHub: `GoreeCloud/video` README and `docs/goreecloud/PRODUCT_BOUNDARY.md`. Scope: direct examination of these specific records, not a complete audit of GoreeCloud.
