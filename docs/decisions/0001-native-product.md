# ADR-0001 — Build Native Media Forge (proposed)

Status: proposed. Date: 2026-10-12.

## Context

The product combines a first-class MKV preservation engine, a first-class transcode engine, and a unified workflow. Existing GoreeCloud Video is a separate Jellyfin-derived streaming application; a direct application fork would complicate ownership, Glaze differentiation, and licensing.

## Decision proposed

Create an **original GoreeCloud/media-forge** repository with an owned application data model, UX, policy boundary and processing orchestration. Reuse bounded FFmpeg, libdvdread/libdvdnav, libbluray components under reviewed licenses. Long-term app target: Rust/Tauri + approved Stable Glaze; use a self-contained Python proof-of-concept solely for early engine testing.

## Alternatives

- HandBrake fork: useful encoding baseline but large inherited application shell and not a preservation-centric product.
- MakeMKV wrapper: incompatible with fully open-source default and reproduces dependency on external proprietary software.
- Extend GoreeCloud Video: couples streaming service release/security boundary to local disc acquisition and desktop UI.
- Native orchestration with bounded libraries (chosen proposal): more engineering work initially, best control over experience and interfaces.

## Consequences

Build DVD/Blu-ray adapters rather than claiming existing support. Maintain licensing reviews and test fixtures. Preserve useful upstream library history/attribution without importing whole-product architecture.
