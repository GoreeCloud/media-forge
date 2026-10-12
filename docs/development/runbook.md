# Local prototype runbook

1. Ensure Python 3.10+ and an FFmpeg distribution with `ffprobe` and `libx264` support.
2. Inspect capabilities: `ffmpeg -hide_banner -encoders | grep libx264` on Linux (Windows users can inspect `ffmpeg -encoders`).
3. Run `python3 -m media_forge --port 8765 --db ./media-forge-dev.sqlite3` from repo root.
4. Open `http://127.0.0.1:8765`, submit an absolute media-file path and an existing output directory.
5. Select Preserve, Convert, or Both; choose preset/container; scan; then queue.
6. Watch progress in Queue; completed outputs are displayed as absolute paths.
7. For automated validation: `python3 -m unittest discover -s tests -v`.

## Recovery

Interrupted jobs are marked `interrupted` on restart. Review source path and destination before resubmitting; previous verified outputs are not overwritten. Cancel removes temporary output files where practical. If a job fails after archival output is created, inspect output directory: the archive may already exist and be verified despite later-stage failure. Do not delete old outputs automatically.

## Handling private data

Job DB contains absolute file paths and names; protect the local state directory, avoid sharing DB or screenshots publicly. The Python prototype intentionally does not collect external telemetry.

## Diagnostics

- `ffprobe` scan fails: confirm readable actual file, not DVD/BDMV folder.
- Conversion fails: confirm `libx264` is compiled into FFmpeg and codec supports selected source.
- Preservation fails: container may not support all source tracks/attachments; choose compatible fixture and review unsupported format.
- Missing permissions: choose an existing writable destination directory.
- Port busy: pass another `--port`, e.g. 8766.
