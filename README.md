# GoreeCloud Media Forge

**Status: runnable prototype / pre-MVP. NOT a production application.**

A new GoreeCloud-owned project for **lossless MKV stream preservation**, **H.264 video transcoding**, and a **combined preservation + conversion** workflow. The prototype runs entirely on the local computer through a loopback-only browser interface. It does not inherit HandBrake or MakeMKV product source code.

## Run the prototype

Requires Python 3.10+, `ffmpeg`, and `ffprobe` installed and available on PATH. No Python third-party dependencies are required.

```bash
python3 -m media_forge --port 8765
```

Open `http://127.0.0.1:8765` (the application also attempts to open a browser).

Provide an absolute path to a **local video file** and a directory that already exists. Select **Preserve**, **Convert**, or **Both**. Click Scan and then Queue Job. Wait for verified outputs; processing runs locally.

```bash
python3 -m unittest discover -s tests -v
```

## Implemented now

- FFprobe source scanning: container, duration, codec inventory, audio languages, chapters.
- MKV stream copy with explicit selected-format validation (not a disc-image backup).
- H.264 + AAC transcoding into MP4/MKV with three presets.
- Combined sequence: preserve and verify MKV, then transcode from it.
- Persistent SQLite job queue; cancel queued or active job; interrupted-state recovery.
- Progress reporting, no-clobber publishing, partial-file cleanup, structured job history.
- Loopback-only UI, per-process CSRF token, no shell command interpolation, no account or cloud requirement.

## Not implemented (do not claim as working)

- Disc navigation and automatic DVD/Blu-ray title selection; encryption/AACS/BD+ handling.
- Complete disc image backups, menu structures, UHD full support.
- Selectable tracks, multi-angle handling, subtitle conversion or burn-in; conversion intentionally drops subtitles in this prototype.
- Hardware encoding, HEVC, AV1, HDR processing, distributed processing.
- Native Glaze interface or final Rust/Tauri desktop packaging.
- Full GoreeCloud platform system integration or Stable release gates.

**Current source limitation:** Files only. For an unprotected optical source a directly readable media file such as `.vob` or `.m2ts` may work, but directory/playlist scanning is not implemented.

## Repository

Repository: `GoreeCloud/media-forge`. This developer prototype is not a released desktop application. See [architecture](docs/architecture/overview.md), [product specification](docs/specifications/product-spec.md), [MVP plan](docs/development/mvp-roadmap.md), [security review](docs/security/threat-model.md), and [status](docs/development/implementation-status.md).

## Licensing

**No distribution license has been approved yet.** This prototype bundle is provided for internal technical evaluation. A governing open-source license, complete notices, dependency-SBOM, and an FFmpeg distribution/compliance review must be approved before public distribution. See `docs/decisions/0002-license-and-distribution.md`.
