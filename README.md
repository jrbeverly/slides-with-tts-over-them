# Slides with TTS Over

> [!WARNING]
> **AI-authored:** This change was autonomously planned and implemented by an AI software factory from a human-authored specification, with possible subsequent human review or modification.

Transforms `slides.json` into slide images, then combines equal-duration slides with a copied Chatterbox `Corporate Female 01` narration to produce an MP4. `assets/demo.mp4` is spliced into the result where the narration says "Here is that demo now."

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
```

The output is written to `build/acme-sprint-report.mp4`.

## Notes

- Concept: programmatically generated slide decks from structured JSON status data; TTS/video is one test output, not the primary goal.
- Define reusable slide templates for status updates, bullets, metrics, progress, etc.; populate them automatically from team-work artifacts already summarized by AI.
- Pipeline idea: work artifacts → distilled status-update JSON → templated slides/report outputs.
- Same JSON could drive multiple presentation surfaces: PowerPoint, rendered slide images, galleries, report pages, and narrated/TTS versions.
- Value is in separating the underlying structured reporting data from the final presentation format; one source can produce many delivery modes.
- Fits with existing AI processes that already determine what was completed during a period; this becomes the presentation/rendering layer on top.
- Significant uncertainty remains around how the pieces should connect and what rendering/polish stages are needed to reach acceptable visual quality.
- Main risk: technically functional automation producing ugly, generic, or “AI-generated” presentation output; aesthetic/quality pipeline needs more investigation.
