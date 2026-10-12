"""Safe and bounded media inspection through ffprobe."""
import json
import shutil
import subprocess
from pathlib import Path


class MediaError(Exception):
    """A media operation could not be safely completed."""


def check_executables():
    return {tool: shutil.which(tool) for tool in ("ffmpeg", "ffprobe")}


def inspect_media(source: str) -> dict:
    path = Path(source).expanduser().resolve(strict=False)
    if not path.is_file():
        if path.is_dir():
            raise MediaError("Disc directories are planned but not yet supported by this prototype. Select a media file (such as VOB or M2TS) instead.")
        raise MediaError("Source is not an accessible file.")
    if shutil.which("ffprobe") is None:
        raise MediaError("ffprobe was not found in PATH.")
    try:
        process = subprocess.run(
            ["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe,crypto,data", "-show_format", "-show_streams", "-show_chapters", "-of", "json", str(path)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MediaError("Media scanning timed out after 30 seconds.") from exc
    if process.returncode != 0:
        raise MediaError("ffprobe could not inspect this source. It may be unreadable or unsupported.")
    try:
        data = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise MediaError("ffprobe returned malformed metadata.") from exc
    streams = []
    for s in data.get("streams", []):
        streams.append({
            "index": s.get("index"), "type": s.get("codec_type"),
            "codec": s.get("codec_name", "unknown"),
            "width": s.get("width"), "height": s.get("height"),
            "language": (s.get("tags") or {}).get("language", "und"),
            "channels": s.get("channels"),
        })
    if not any(s["type"] == "video" for s in streams):
        raise MediaError("No video stream was detected in this source.")
    fmt = data.get("format") or {}
    try:
        duration = float(fmt.get("duration") or 0)
    except (ValueError, TypeError):
        duration = 0.0
    return {
        "path": str(path), "name": path.name, "size": path.stat().st_size,
        "duration": duration, "format": fmt.get("format_name", "unknown"),
        "streams": streams, "chapters": len(data.get("chapters") or []),
    }


def validate_preservation(source: dict, dest: dict) -> None:
    """Detect lost streams and changed codec identities; this is NOT a bit-exact proof."""
    for typ in ("video", "audio", "subtitle", "attachment"):
        src = [s["codec"] for s in source["streams"] if s["type"] == typ]
        dst = [s["codec"] for s in dest["streams"] if s["type"] == typ]
        if sorted(src) != sorted(dst):
            raise MediaError(f"Preservation verification failed: {typ} codec/stream inventory changed ({src} → {dst}).")
    unsupported = sorted({s["type"] for s in source["streams"] if s["type"] not in ("video", "audio", "subtitle", "attachment")})
    if unsupported:
        raise MediaError(f"Preservation validation found unsupported source stream types: {unsupported}. These cannot be silently dropped.")
    if source["chapters"] != dest["chapters"]:
        raise MediaError("Preservation verification failed: chapter count changed.")
