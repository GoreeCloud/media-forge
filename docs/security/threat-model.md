# Security and privacy threat model — initial draft

## Protected assets

User media, disc inventory and viewing history, local media paths, output files, processing presets, debug logs, external video library credentials (future), downloaded metadata (future), OS/user permissions.

## Trust boundaries

1. Source file/disc supplied by a local user may be malformed or malicious.
2. UI controls must not become arbitrary shell execution or a remote HTTP administration surface.
3. Third-party FFmpeg codecs/demuxers parse untrusted media; isolation and patch cadence matter.
4. Destination filesystem may contain valuable existing data and symlinks.
5. Optional network integrations must not become mandatory or bypass privacy/policy settings.

## Prototype safeguards implemented

- HTTP binds `127.0.0.1` only. No external auth service.
- Mutation requests require random in-memory header token; Origin validated if present.
- Strict JSON body size and fixed API endpoints; no CORS headers and no generic static-file server.
- `subprocess.Popen` uses direct argument vector, never `shell=True`.
- Inputs must be regular accessible files and output must exist already.
- Temporary outputs are staged with a distinct name and published with an exclusive link creation (no overwrite).
- Worker failures do not crash queue; on restart in-progress jobs become `interrupted`.
- FFmpeg local stderr logs are chmod 0600 and removed at job completion/failure.

## Prototype gaps / must-fix before wider testing

- Browser endpoint design is development-only; implement native Tauri invoke commands and native permission-scoped file picker.
- No per-path allowlist, user consent-grant persistence, sandbox or seccomp/AppContainer isolation.
- No resource quotas/CPU limits, fuzz testing, FFmpeg CVE tracking or secure binary provenance enforcement.
- Error records may include sensitive media details; add structured redaction and retention limits.
- No egress blocker for unusual demuxers/protocols; media inputs should reject network protocols and configure protocol allowlists.
- No multipart upload; UI currently requires an explicit path, which is poor UX but avoids introducing media upload bugs.
- No FFmpeg sandboxing, crash isolation beyond subprocess separation.
- No native Glaze qualification, Wardveil/Privacy Shield/Policy/Observability integration evidence.
- No approved retention, deletion, backup, export, and audit contract for job database.

## Critical risks

- Malicious disc or file vulnerabilities in native codecs and parsers: mitigate via trusted pinned binaries, updates, fuzz corpora, OS sandbox, least privilege.
- Symlink/hardlink/path races at publication: assess and implement platform-specific atomic publish semantics.
- Localhost cross-origin request and DNS rebinding: prototype token protects mutations, but native security boundary strongly preferred.
- Filesystem exhaustion: perform disk-space preflight, job constraints and partial cleanup.
- Unencrypted/protected source misclassification: fail closed and present truthful errors.

## Gates

Security review, accessibility review, license/SBOM, privacy retention policy, cross-platform tests, GoreeCloud nine-system contract review and signed release evidence are required before any Stable claim.
