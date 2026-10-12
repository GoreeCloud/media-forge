# ADR-0002 — Public license and dependency distribution (pending)

Status: **decision required before external distribution**.

## Licensing boundary

GoreeCloud's documented policy requires open-source software for long-term use absent explicit approved exception. The Python prototype source is delivered as an internal evaluation artifact; no public project code license is approved in this package.

FFmpeg itself is normally LGPL with optional GPL components. `libx264` and optional encoders may trigger GPL requirements for the FFmpeg binary build, and packaging/distribution arrangements matter. Official guidance: https://www.ffmpeg.org/legal.html

## Proposed evaluation

1. Choose and approve GPL-compatible open-source license for GoreeCloud-controlled app code (evaluate GPL-3.0-or-later vs AGPL-3.0-or-later vs MPL-2.0, with distribution and linking assessment).
2. Decide system-installed FFmpeg versus separately packaged, sourced and reproducible binaries.
3. Record full FFmpeg `-buildconf` and license flags; validate available encoders for supported platforms.
4. Review `libdvdread`, `libdvdnav`, `libbluray`, SQLite, Tauri, Rust crates and all transitive dependencies.
5. Generate SPDX SBOM, notices and reproducible release artifacts; audit patent/codec obligations by jurisdiction.
6. Do not bundle MakeMKV proprietary binaries into the mandatory feature set.

This document is engineering decision support, not legal advice.
