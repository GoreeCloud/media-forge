"""Validated FFmpeg job command construction and isolated process handling."""
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from .probe import MediaError, inspect_media, validate_preservation

PRESETS = {
    "balanced": {"label": "Balanced · H.264", "crf": 22, "speed": "medium", "audio_bitrate": "160k"},
    "archive-quality": {"label": "High quality · H.264", "crf": 18, "speed": "slow", "audio_bitrate": "192k"},
    "compact": {"label": "Compact · H.264", "crf": 28, "speed": "medium", "audio_bitrate": "128k"},
}
MODES = ("preserve", "convert", "both")
FORMATS = ("mp4", "mkv")


def safe_stem(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_-]", "-", Path(name).stem)[:56].strip("-_")
    return s or "media"


def validate_plan(plan: dict) -> dict:
    if not isinstance(plan, dict):
        raise MediaError("Expected a processing plan object.")
    source = plan.get("source")
    output_dir = plan.get("output_dir")
    mode = plan.get("mode")
    preset = plan.get("preset", "balanced")
    container = plan.get("container", "mp4")
    if not isinstance(source, str) or not source.strip() or len(source) > 4096:
        raise MediaError("A valid source path is required.")
    if not isinstance(output_dir, str) or not output_dir.strip() or len(output_dir) > 4096:
        raise MediaError("A valid output directory is required.")
    if mode not in MODES or preset not in PRESETS or container not in FORMATS:
        raise MediaError("Invalid processing mode, preset, or container.")
    p = Path(source).expanduser().resolve(strict=False)
    out = Path(output_dir).expanduser().resolve(strict=False)
    if not p.is_file():
        raise MediaError("Source must be an existing media file; optical-disc adapters are not implemented yet.")
    if not out.is_dir():
        raise MediaError("Output directory must already exist.")
    if not os.access(out, os.W_OK):
        raise MediaError("Output directory is not writable.")
    if p.parent == out and p.name.startswith("."):
        raise MediaError("Hidden temporary source files are not accepted.")
    return {"source": str(p), "output_dir": str(out), "mode": mode, "preset": preset, "container": container}


def processing_steps(plan: dict, job_id: str):
    src = Path(plan["source"])
    stem = safe_stem(src.name)
    directory = Path(plan["output_dir"])
    archive = directory / f"{stem}-{job_id[:8]}-archive.mkv"
    converted = directory / f"{stem}-{job_id[:8]}-converted.{plan['container']}"
    stages = []
    if plan["mode"] in ("preserve", "both"):
        stages.append(("preserve", src, archive))
    if plan["mode"] in ("convert", "both"):
        stages.append(("convert", archive if plan["mode"] == "both" else src, converted))
    return stages


def build_ffmpeg_args(kind: str, source: Path, target: Path, plan: dict):
    base = ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-n", "-progress", "pipe:1", "-protocol_whitelist", "file,pipe,crypto,data", "-i", str(source)]
    if kind == "preserve":
        # Stream copy preserves existing compressed streams but is not a full-disc image.
        return base + ["-map", "0:v?", "-map", "0:a?", "-map", "0:s?", "-map", "0:t?", "-map_metadata", "0", "-map_chapters", "0", "-c", "copy", "-f", "matroska", str(target)]
    preset = PRESETS[plan["preset"]]
    args = base + ["-map", "0:v:0", "-map", "0:a?", "-map_metadata", "0", "-map_chapters", "0", "-c:v", "libx264", "-preset", preset["speed"], "-crf", str(preset["crf"]), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", preset["audio_bitrate"], "-sn"]
    if plan["container"] == "mp4":
        args += ["-movflags", "+faststart", "-f", "mp4"]
    else:
        args += ["-f", "matroska"]
    return args + [str(target)]


def execute_plan(job_id: str, plan: dict, on_progress, cancel_event: threading.Event, log_dir: Path, on_output=None):
    """Run sequential steps, never overwrite a completed output and clean partial files."""
    if not shutil_which_ffmpeg():
        raise MediaError("ffmpeg executable was not found in PATH.")
    log_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    steps = processing_steps(plan, job_id)
    source_probe = inspect_media(plan["source"])
    if plan["mode"] in ("preserve", "both"):
        unsupported = sorted({s["type"] for s in source_probe["streams"] if s["type"] not in ("video", "audio", "subtitle", "attachment")})
        if unsupported:
            raise MediaError(f"Preservation cannot represent source stream types {unsupported}; refusing silent omission.")
    for idx, (kind, input_path, destination) in enumerate(steps):
        if cancel_event.is_set():
            raise JobCanceled()
        if destination.exists():
            raise MediaError("Output already exists; refusing to overwrite a completed file.")
        temporary = destination.with_name("." + destination.stem + ".part" + destination.suffix)
        if temporary.exists():
            raise MediaError("A partial output already exists; refusing to overwrite it.")
        log = log_dir / f"{job_id}-{idx}.log"
        process = None
        try:
            with log.open("x", encoding="utf-8") as errors:
                os.chmod(log, 0o600)
                process = subprocess.Popen(
                    build_ffmpeg_args(kind, input_path, temporary, plan),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=errors,
                    text=True, encoding="utf-8", errors="replace",
                )
                def monitor_cancel(proc=process):
                    # FFmpeg may stop emitting progress. Cancellation must not wait
                    # indefinitely for another progress line to arrive.
                    while proc.poll() is None:
                        if cancel_event.wait(0.15):
                            if proc.poll() is None:
                                proc.terminate()
                                try:
                                    proc.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    proc.kill()
                                    proc.wait(timeout=5)
                            return
                threading.Thread(target=monitor_cancel, name=f"cancel-{job_id[:8]}", daemon=True).start()
                duration = source_probe.get("duration") or 0
                for line in process.stdout:
                    if cancel_event.is_set():
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=5)
                        raise JobCanceled()
                    if line.startswith("out_time_us=") or line.startswith("out_time_ms="):
                        try:
                            value = float(line.split("=", 1)[1]) / 1000000
                            ratio = max(0.0, min(0.99, value / duration)) if duration > 0 else 0
                            on_progress(kind, (idx + ratio) / len(steps), "processing")
                        except ValueError:
                            pass
                code = process.wait()
            if cancel_event.is_set():
                raise JobCanceled()
            if code != 0:
                detail = log.read_text(encoding="utf-8", errors="replace")[-1200:]
                detail = detail.replace(str(input_path), "[source]").replace(str(temporary), "[output]")
                raise MediaError(f"{kind.capitalize()} failed (ffmpeg status {code}): {detail.strip() or 'Review codec/container support.'}")
            on_progress(kind, (idx + .99) / len(steps), "verifying")
            result_probe = inspect_media(str(temporary))
            if kind == "preserve":
                validate_preservation(source_probe, result_probe)
            else:
                if not any(s["type"] == "video" and s["codec"] == "h264" for s in result_probe["streams"]):
                    raise MediaError("Conversion verification failed: H.264 video not found.")
            # Atomic exclusive publication: hard-link creation fails if target already exists.
            os.link(temporary, destination)
            temporary.unlink()
            outputs.append({"kind": kind, "path": str(destination), "size": destination.stat().st_size, "streams": result_probe["streams"], "chapters": result_probe["chapters"]})
            if on_output is not None:
                on_output(outputs[:])
            on_progress(kind, (idx + 1) / len(steps), "processing")
        finally:
            if process and process.poll() is None:
                process.kill()
                process.wait()
            if process and process.stdout is not None:
                process.stdout.close()
            try:
                temporary.unlink(missing_ok=True)
            finally:
                log.unlink(missing_ok=True)
    return outputs


def shutil_which_ffmpeg():
    from shutil import which
    return which("ffmpeg") is not None


class JobCanceled(Exception):
    pass
