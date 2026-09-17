# Vision Provider Reliability Notes

## Evidence

Hermes issue #8120 documents intermittent `vision_analyze` timeouts for local images, especially in Windows/WSL2 workflows and larger PNG payloads. The issue identifies short timeouts, image encoding/upload overhead, and lack of retry as compounding factors. Related PR #8168 proposed proactive compression, a longer configured timeout, and a timeout retry; the PR was closed after unrelated test changes were found, so use the technique, not the closed PR as an installed patch.

Hermes documentation states that images are sent as base64 data URLs in an OpenAI-compatible `image_url` content block, and that text-only main models use the auxiliary vision route. Auxiliary vision settings are configured under `auxiliary.vision`, including `provider`, `model`, `timeout`, and `download_timeout`.

## Validated Windows Case

Observed configuration before repair:

- Main provider: custom Yue88 OpenAI-compatible relay.
- `auxiliary.vision.provider`: `auto`.
- `auxiliary.vision.timeout`: `120` seconds.
- OpenRouter credential entry existed but `OPENROUTER_API_KEY` was not present in the process environment.

Observed outcomes:

- Automatic/custom route: repeated `Request timed out`.
- Explicit OpenRouter route: immediate `401 Missing Authentication header`; this was an authentication/configuration failure, not a timeout solution.
- Explicit `custom:agnes` with `agnes-2.5-flash`: successful image analysis on a local review image.

The working configuration for that profile became:

```yaml
auxiliary:
  vision:
    provider: custom:agnes
    model: agnes-2.5-flash
    timeout: 180
    download_timeout: 60
```

This is a case-specific validated route, not a universal default. Verify the credential and model in the active profile before applying it elsewhere.

## Review Image Handling

Keep the source image unchanged. Create a temporary review copy with the longest edge near 1568 pixels. For spatial plans or other detail-sensitive images, crop meaningful regions after the full-image request. Delete review copies after the QC decision.

## Interpretation Boundary

A successful provider response proves transport only. It does not prove the image satisfies the requested layout. Conversely, a vision model may confidently misread symbolic marks in a procedural plan. When exact topology matters, verify geometry deterministically and avoid arrows, labels, or decorative symbols that can be mistaken for rooms or objects.
