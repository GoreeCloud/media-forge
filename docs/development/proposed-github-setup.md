# Proposed repository setup — requires separate GitHub write authorization

Repository: `GoreeCloud/media-forge` (created; publicly accessible)
Description: "Open-source media preservation and video transcoding application for GoreeCloud."
Visibility: propose public after licensing, legal and security review; otherwise private during prototype development.
Default branch: `main`.
Topics: `media-processing`, `mkv`, `transcoding`, `archiving`, `video`, `desktop`, `goreecloud`.

## Initial repo checklist

- [ ] Approve repository creation and official product naming.
- [ ] Approve public source license; add complete LICENSE and notices.
- [ ] Upload this code only after removing local/proprietary data and reviewing provenance.
- [ ] Enforce branch rules, code owners, PR reviews, security scanning and required CI.
- [ ] Verify `goreecloud.platform.yaml` against applicable actual machine-readable contract; current file is only a planning placeholder.
- [ ] Add issue/PR templates from approved central governance source.
- [ ] Add release/version metadata, CODEOWNERS, changelog and dependency update policy.
- [ ] Set protected secret policy and native build/signing controls.
- [ ] Create backlog issues from `mvp-roadmap.md` after explicit authorization.

## Proposed first issues

1. `MF-001` — Approve architecture, boundaries and license.
2. `MF-002` — Build Rust core and source inventory/FFprobe adapter.
3. `MF-003` — Build native Tauri/Glaze desktop UI and OS file chooser.
4. `MF-004` — DVD title and chapter discovery.
5. `MF-005` — BDMV/MPLS title discovery.
6. `MF-006` — Track selection + preservation engine + strict validation.
7. `MF-007` — H.264/AAC transcoding presets + selectable audio/subtitles.
8. `MF-008` — Persistent queue + resumability and partial success.
9. `MF-009` — Integration security/quality tests + portable packaging.
10. `MF-010` — Applicable nine-system platform conformance with runtime evidence.
