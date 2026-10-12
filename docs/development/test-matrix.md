# Quality & acceptance test matrix

| Test ID | Scenario | Expected result | Status |
|---|---|---|---|
| UT-01 | Sanitize suspicious filename | No traversal/name injection | Automated pass |
| UT-02 | Invalid plan mode/container | Reject without spawning FFmpeg | Automated pass |
| UT-03 | Missing audio in archive inventory | Verification fails | Automated pass |
| IT-01 | Synthetic H.264/MPEG-4 file -> MKV stream copy | Archive preserves source codec inventory | Automated pass |
| IT-02 | Synthetic source -> H.264/AAC MP4 | Converted H.264 video verified | Automated pass |
| IT-03 | Synthetic source -> combined outputs | Two outputs with sequential stages | Automated pass |
| IT-04 | Queue persists and completes job | Completed job stored with output paths | Automated pass |
| IT-05 | Restart with running queue | Marked interrupted, not completed | Automated pass |
| IT-06 | Cancel active FFmpeg job | Job canceled and partial files removed | Manual/pending |
| IT-07 | Converter fails after valid archive | Archive retained; partial success recorded | Automated pass |
| DR-01 | DVD unencrypted fixture | Correct titles, angles and chapters | Pending |
| DR-02 | BDMV with branching | Correct playlist/chapters and track mapping | Pending |
| DR-03 | Encrypted Blu-ray without legal adapter | Typed unsupported protection error | Pending |
| PR-01 | Video stream data unchanged in remux | Strong stream-hash comparison | Pending |
| CV-01 | Subtitle handling MP4 vs MKV | No silently lost required subtitle | Pending |
| CV-02 | CRF/scale/crop set by UI | Verified output properties | Pending |
| QA-01 | Windows and Linux optical drives | Installer/device-specific smoke pass | Pending |
| QA-02 | Screen readers, keyboard, Glaze current Stable | Acceptance evidence | Pending |
| SEC-01 | Crafted media, path/race and isolation fuzz | No privileged escape/data loss | Pending |
| GOV-01 | Nine-system applicability + license/SBOM | Approved release evidence | Pending |

The automated test statuses are scoped to the prototype and generated fixtures. They are not proof of release readiness.
