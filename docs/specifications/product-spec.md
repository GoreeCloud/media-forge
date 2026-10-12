# Media Forge — Product Requirements Document v0.1 (proposed)

## Vision

One application supporting equal first-class workflows for (1) **preservation of compatible compressed disc/file streams** without video re-encoding and (2) **video transcoding**, plus a combined sequential process. User owned, local-first, fully open-source, privacy-forward, no mandatory subscription or hosted control plane.

## Users and jobs-to-be-done

- Media archivist: extract selected titles, video/audio/subtitles/chapters into verified archival MKV without intentional quality reduction.
- Everyday user: shrink or convert video for compatible playback devices while selecting quality and audio tracks.
- Batch user: queue multiple discs and videos, track outputs, retry failures, and recover after a crash.
- GoreeCloud ecosystem user: place approved output into an existing media library through an optional integration.

## Core workflows

**W1 Preserve:** source -> scan -> select title/tracks -> stream-copy to supported archival container -> validate -> publish + manifest.

**W2 Convert:** source -> scan -> select title/tracks + preset -> decode/encode -> verify -> publish + report.

**W3 Both:** source -> scan -> archive -> verify -> convert from verified archive -> independently verify each; verified archive persists on conversion failure.

## Requirements and traceability

| ID | Requirement | Priority | Prototype | MVP |
|---|---|---|---|---|
| MF-SRC-001 | Import accessible media file | P0 | Working | Required |
| MF-SRC-002 | Enumerate DVD-Video titles and chapters | P0 | Missing | Required |
| MF-SRC-003 | Enumerate unencrypted Blu-ray playlists/titles | P0 | Missing | Required |
| MF-SRC-004 | Import supported DVD/BDMV directories | P0 | Missing | Required |
| MF-SRC-005 | Detect unreadable, unsupported and protected sources safely | P0 | Partial | Required |
| MF-PR-001 | MKV preservation with no video re-encoding | P0 | Working on files | Required on supported titles |
| MF-PR-002 | Select multiple audio/subtitle streams and chapters | P0 | Copy all compatible streams | Required |
| MF-PR-003 | Validate selected stream inventory and chapter counts | P0 | Partial | Required |
| MF-PR-004 | Full-disc structure/ISO backup | P2 | Missing | Later |
| MF-CV-001 | H.264 + AAC -> MP4/MKV | P0 | Working | Required |
| MF-CV-002 | Configurable constant quality / bitrate, scale, crop | P0 | Presets only | Required |
| MF-CV-003 | Select audio tracks and handling of compatible subtitles | P0 | Missing | Required |
| MF-CV-004 | H.265 and hardware encoding | P1 | Missing | Evaluate by MVP build |
| MF-CV-005 | HDR/AV1/advanced filters | P2 | Missing | Later |
| MF-CMB-001 | Preserve + Convert via one queued job | P0 | Working on files | Required |
| MF-CMB-002 | Independent success/partial-success states and outputs | P0 | Partial | Required |
| MF-Q-001 | Persistent, cancelable queue | P0 | Working | Required |
| MF-Q-002 | Crash-safe partial outputs and retries | P0 | Partial | Required |
| MF-VER-001 | Output probe, codec and track inventory comparison | P0 | Working, basic | Required |
| MF-VER-002 | Stronger packet/hash/decoded-content validation options | P1 | Missing | Desirable |
| MF-UX-001 | Accessible Glaze compliant native app | P0 | Only conceptual UI | Required for release |
| MF-SEC-001 | Offline/local first with no mandatory account | P0 | Working | Required |
| MF-SEC-002 | Versioned SBOM/license/security gates | P0 | Missing | Required for release |
| MF-INT-001 | Optional GoreeCloud Video integration | P2 | Missing | Later |
| MF-INT-002 | Nine-system applicability and compliance evidence | P0 | Missing | Required when applicable |

`Working` means tests or direct code inspection establish the specified *prototype scope*, not Stable or product-wide readiness. `Partial` signals important gaps.

## Functional details

- **Source import:** explicit source path or OS file picker; available volumes/disc drives; title preview thumbnails only with user permission. The app must identify encrypted discs as unsupported unless a compliant adapter is present.
- **Preservation:** default copy of selected video/audio/subtitles and chapters into MKV, reject incompatible streams and report precisely what cannot be preserved. Do not advertise MKV as a 1:1 replacement for full disc/menu structures.
- **Transcoding:** H.264 baseline, H.265 optional after verified redistribution decisions, preset profiles, CRF/bitrate and scaling, device profile compatibility, stream mapping, subtitle compatibility / burn-in where suitable.
- **Queue:** states `scanning / queued / preparing / processing / verifying / completed / partial_success / blocked / canceled / interrupted / failed`, durable state transitions, progress based on processed media time, cancel and retry safe idempotence.
- **Verification:** no silent drop of required streams, output playable/probeable, correct declared codecs and chapters, corruption checks, actual time range, verified vs merely presumed bitstream identity distinguished in manifest.
- **Privacy:** no telemetry by default, no uploading media content, opt-in metadata lookup, store filenames/path in minimum necessary local database, redact diagnostics and honor platform privacy/policy authorities.
- **Usability:** three top-level choices (Preserve, Convert, Both) after scan; novice and advanced settings; keyboard/screen-reader support and appropriate semantic Glaze controls.

## Nonfunctional release targets (proposed; subject to testing)

- No output clobber without explicit user action.
- No unresolved partial outputs presented as completed.
- Repeatable tests across supported operating systems with representative optical devices.
- Installer/uninstaller, structured diagnostics, recovery instructions, verifiable packages, no mandatory internet.
- Clear warnings about legal rights and technical restrictions, without making claims of permitted circumvention.

## Defined exclusions for the first MVP

Commercial-disc decryption parity, UHD encrypted content, full-disc ISO, simultaneous multi-drive extraction, GPU parity, HDR fidelity, remote processing, AI metadata enrichment, and cloud control planes.

## Product decisions pending approval

- Product brand final sign-off and official Glaze assets.
- Public source license, provenance/SPDX and FFmpeg packaging model.
- Windows/Linux/macOS sequencing and native installer requirements.
- Disc compatibility fixtures and exact minimum-supported hardware.
- Final contract and policy interpretation for the nine GoreeCloud platform systems.
