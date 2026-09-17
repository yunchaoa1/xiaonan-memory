---
name: vision-analysis-reliability
description: "Use when vision calls fail or images need independent QC."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    category: software-development
    tags: [vision, image-analysis, timeout, routing, provider, qc]
    related_skills: [hermes-agent, scene-image-generation]
---

# Vision Analysis Reliability

## When to Use

Use this skill when an image-analysis call is slow, repeatedly times out, returns an authentication or provider error, or when a generated image must be independently checked before being marked usable.

## Core Principle

Treat vision analysis as two separate systems:

1. **Transport and routing:** image preparation, provider selection, authentication, request timeout, and fallback behavior.
2. **Visual judgment:** what the image visibly contains and whether it satisfies the acceptance criteria.

A successful image-generation call does not prove that the image is structurally correct. A successful API call does not prove that the requested provider or model is correctly routed. Record both results separately.

## Procedure

1. **State the acceptance questions first.** Convert the task into a short checklist of visible facts. For a spatial template, check projection, scene boundary, object counts, portals, circulation, forbidden extras, and readability.

2. **Inspect the live configuration before retrying.** Read the active main provider, `auxiliary.vision.provider`, `auxiliary.vision.model`, vision timeout, download timeout, and credential source. Do not infer provider capability from the model name alone.

3. **Classify the failure from the returned error.**
   - `Request timed out`: investigate image size, request timeout, provider latency, and whether the route is a custom or incompatible endpoint.
   - `401` or missing authentication header: stop retrying that route; verify the credential source and environment variable before any new request.
   - Fast `400` format/model errors: verify the model is a vision-understanding model and that the endpoint accepts OpenAI-compatible image content blocks.
   - Successful response: continue to visual QC; never stop at transport success.

4. **Use evidence before changing configuration.** Check the current Hermes documentation and public issue/PR history for the reported failure pattern. Known durable mitigations include a configurable vision timeout, bounded retry, proactive image compression, and an explicitly selected vision-capable provider. Preserve the main model unless the user asks to change it.

5. **Prepare a review copy for large local images.** Keep the original artifact unchanged. For visual inspection, create a temporary copy with the longest edge around 1568 pixels and a reasonable file-size budget. If the image contains tiny details, inspect targeted crops after the full image. Remove temporary copies after the decision.

6. **Choose one verified route and run a minimal probe.** Prefer a provider/model already authenticated in the current Hermes profile and known to accept image inputs. Use a small crop first when the full image is expensive. Do not fan out repeated calls against an unverified route.

7. **Run visual QC against the checklist.** Ask for visible facts and uncertainty, not creative interpretation. When the model reports a mismatch, classify it as a real artifact defect, a model misread, or insufficient resolution. If the distinction matters, inspect a crop or use a deterministic/procedural representation.

8. **Use a deterministic fallback for exact topology.** If a generative image repeatedly violates exact counts, portals, or room boundaries, switch to a programmatic floor plan or approved 3D blockout. Remove ambiguous symbols, arrows, labels, and decorative marks when they could be mistaken for scene content. A fallback is acceptable only after its own visual or geometric verification.

9. **Report status precisely.** Use separate statuses such as `TRANSPORT_VERIFIED`, `VISION_QC_FAILED`, `VISION_QC_PASSED`, and `NEEDS_REVIEW`. Never label an artifact customer-ready when a required criterion was not independently verified.

## Provider and Timeout Rules

- `auxiliary.vision` should be explicit for a production or test run when the main provider is a custom relay.
- A longer timeout can address slow inference, but it cannot repair missing credentials or an endpoint that does not support image input.
- Base64 image input is widely compatible, but large payloads increase processing and upload time; resize a review copy rather than modifying the source.
- Provider-specific settings belong in configuration, while provider quirks and research evidence belong in `references/vision-provider-reliability.md`.

## Pitfalls

- Do not retry the same failing provider repeatedly without reading the error and configuration.
- Do not treat a connectivity health check as proof that the selected auxiliary route has a valid credential.
- Do not assume `auto` routing will choose a vision-capable path behind a custom OpenAI-compatible relay.
- Do not use an image-generation model for image understanding.
- Do not let a vision model's confident description override the actual acceptance checklist.
- Do not expand a portal into a destination room merely because the prompt mentions that room as metadata.
- Do not turn a programmatic plan's decorative arrows or symbols into semantic room objects.

## Rendering a Generated Artifact So It Can Be QC'd

A written file is not a verified render. For generated HTML/SVG/vector artifacts, rasterize first, then judge the raster:

- **SVG → PNG:** `pip install resvg-py` (single-file renderer, no native deps) then `resvg_py.svg_to_bytes(svg_string=..., width=…)`. On Windows `cairosvg` also needs a `libcairo-2.dll` that is often absent, so `resvg-py` is the lower-friction route there. Render a CJK sample too and confirm the glyphs are not tofu — set an explicit `font-family` (e.g. `Microsoft YaHei`) rather than relying on the default.
- **Local HTML page → PNG:** `chrome --headless=new --disable-gpu --hide-scrollbars --window-size=W,H --screenshot=out.png "file:///<percent-encoded path>"`. Percent-encode the path; non-ASCII (e.g. Chinese) directories require it.
- **A generated SVG can silently drop malformed elements.** Bare path data placed outside `<path d="…">` renders as nothing and raises no error. An empty-looking render is usually a markup bug, not a renderer failure — inspect the generated markup (or the diff of it) before concluding the renderer is broken.
- For icon/mark work, include the small-size render (16–64 px) in the acceptance checklist; a mark that only reads at 512 px has not passed QC.

## Verification

A completed run must include:

- the active provider/model and timeout values;
- the exact error classification, if any;
- confirmation that the source image was preserved;
- the visual QC result for every acceptance criterion;
- the final artifact status and path;
- cleanup of temporary review files.

See `references/vision-provider-reliability.md` for the documented issue pattern, the Hermes configuration shape, and the validated troubleshooting sequence from the September 2026 Windows case.
