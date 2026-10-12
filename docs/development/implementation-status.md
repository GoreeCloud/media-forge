# Prototype implementation status — verified locally

Version: **0.1.0-dev** | Status: prototype (not release candidate)

## Implemented and testable

- File-only source analysis via FFprobe.
- MKV stream-copy preservation of FFmpeg-supported video/audio/subtitle/attachment streams and chapters, with stream and chapter inventory verification.
- H.264/AAC transcoding with three CRF-based presets, MKV/MP4 output, verified resulting video codec.
- Preserve+Convert sequential pipeline sourced from the verified archival output.
- SQLite persistent sequential job queue and status/progress history.
- Cancel queued and active jobs; startup marks abandoned in-flight jobs as interrupted.
- Temporary outputs are removed on failure/cancel, final outputs never intentionally overwritten.
- Vanilla HTML/CSS/JS loopback-only UI; CSRF-like per-session header token and no external network calls.

## Known limitations and honest claims

- A lossless MKV title preservation is **not** a bit-for-bit optical-disc or filesystem backup.
- Verification checks metadata inventories, not bitstream-level cryptographic equality or complete playback integrity.
- Scan supports **files only**; DVD/BDMV directory navigation, automatic title identification, protected disc access absent.
- Preservation copies all compatible media streams instead of allowing selection.
- Conversion copies the first video stream, maps all audio streams, and deliberately drops subtitle streams; UI must not claim converted subtitles preserved.
- `libx264` availability depends on installed FFmpeg binary. No bundled FFmpeg.
- Not cross-platform packaged; runtime verified only in current Linux test environment.
- UI is a styling prototype only, not an implementation of the authoritative Glaze design tokens/components.
- Verified outputs are persisted stage-by-stage; if conversion fails after preservation, the job is marked `partial_success` with archive output retained.
- Existing verified archive outputs remain on disk if later conversion fails; early prototype UI may not list them on the failed job unless partial output tracking is enabled.
- Nine platform systems are unverified/integrations unimplemented.

## Validation evidence

Run `python3 -m unittest discover -s tests -v` to execute unit and FFmpeg synthetic-media integration tests. FFmpeg-generated test video represents only a narrow subset of codec/format cases. Manual cross-platform, disc and security testing remain outstanding.

## Protected-source scope

No AACS/BD+ or other encrypted commercial-disc decryption/circumvention implemented. Technical possibility and legality require separate review; jurisdiction-specific law may restrict circumvention even for personally owned media.
