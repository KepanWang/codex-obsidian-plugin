---
name: obsidian-video-knowledge
description: Use when the user asks Codex to turn an already available video or audio source into Obsidian knowledge: transcribe, OCR slides/keyframes, summarize, curate artifacts, and save the result into the vault. This skill should trigger for local video files, Cat Catch/猫抓-downloaded media, MP4/MOV/M4A/WAV/MP3, “把视频转成知识”, “整理视频到知识库”, “视频总结”, “提取关键帧”, “转录视频”, and similar requests, even when the user does not explicitly mention Obsidian. This skill is not responsible for environment-specific video downloading; use or create a separate downloader skill for ordinary webpage/replay links.
---

# Obsidian Video Knowledge

Turn authorized video material into an Obsidian knowledge note with curated, traceable vault artifacts.

Use this skill together with `obsidian-vault` whenever the final result should be saved to the user's vault. If a dedicated local transcription skill is available, follow its transcription engine preference for Whisper/MLX/whisper.cpp.

## Scope

This is a video-to-knowledge skill. It owns:

- Local video/audio processing.
- Transcription.
- OCR and keyframe curation.
- Knowledge summarization.
- Obsidian note creation.
- Final artifact archival under the relevant Obsidian folder.

It does not own environment-specific downloading from arbitrary links. If the user gives a normal webpage or livestream replay URL, first use a downloader skill if available, or ask the user to download the media with Cat Catch/猫抓 and provide the resulting local file.

## Safety Boundary

- Do not bypass paywalls, login protections, DRM, browser security policy, private cookies, or app session boundaries.
- If the video page depends on the user's logged-in browser state, ask the user to download it manually with Cat Catch/猫抓, or hand off to a dedicated downloader skill that follows the user's authorization and platform constraints.
- Cat Catch can be used as a user-operated capture helper. Prefer: user opens the page, Cat Catch detects the resource, user downloads the file, Codex processes the local file.
- Do not store signed replay URLs, cookies, authorization headers, API keys, account screenshots, payment details, or other secrets in Obsidian notes.
- If the user provides a direct m3u8/mp4 URL and confirms they are authorized to download it, a downloader skill or `yt-dlp`/`ffmpeg` may produce the local source file before this skill continues.

## Recommended Inputs

Prefer these inputs, in order:

1. A local video/audio file path, such as `.mp4`, `.mov`, `.m4a`, `.wav`, `.mp3`.
2. A media file downloaded by Cat Catch/猫抓.
3. A local file produced by a downloader skill.
4. An authorized direct `.mp4` or `.m3u8` URL only as a pre-processing handoff into a local file.

## Environment Checks

Check tools before heavy work:

```bash
which ffmpeg
which ffprobe || true
which tesseract || true
which yt-dlp || true
```

For transcription, prefer:

1. `mlx-whisper` on Apple Silicon.
2. `whisper.cpp` with Metal/Core ML.
3. OpenAI Whisper CPU fallback only if needed.

For Chinese OCR, verify `chi_sim` is available:

```bash
tesseract --list-langs
```

If installing packages in mainland China, prefer temporary mirror settings rather than changing global config without the user's approval. Useful patterns:

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew install <package>
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

Prefer reusing local model caches over downloading large models.

## Processing Workflow

Use a temporary work directory for intermediate files. It can live beside the source file or under a system temp directory:

```text
<source-stem>_processing/
```

Final deliverables must be archived into the Obsidian vault, not left only beside the original source file.

After classifying the note with the user's Obsidian classification guide, create an artifact directory beside the note:

```text
<note-folder>/_video-assets/<YYYY-MM-DD-short-slug>/
```

For example, if the note is saved to:

```text
01 Sources/Development/2026-06-06 AI 工具配置扫盲.md
```

save curated artifacts to:

```text
01 Sources/Development/_video-assets/2026-06-06-ai-tooling-onboarding/
```

Use relative Obsidian links from the note to these archived artifacts when practical.

Generate these artifacts when feasible:

- `<stem>.audio.wav`: mono 16 kHz PCM audio for transcription.
- `<stem>.whisper-<model>.txt`: transcript.
- `<stem>.whisper-<model>.srt`: subtitle file when timestamps are useful.
- `<stem>.whisper-<model>.json`: structured transcript when supported.
- `<stem>.720p.compact.mp4`: compressed video for review/storage.
- `candidate_frames_60s/`: temporary one-frame-per-minute candidates, or `candidate_frames_30s/` for dense slide videos.
- `keyframes/`: curated frames worth keeping.
- `keyframes_index.md`: timestamps, OCR excerpts, and keep reasons for curated frames.
- `ocr_full_raw.md`: optional debug output only; do not archive by default.

Use stable ffmpeg commands:

```bash
ffmpeg -hide_banner -y -i "$VIDEO" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/$STEM.audio.wav"
```

```bash
ffmpeg -hide_banner -y -i "$VIDEO" -vf "fps=1/60,scale=1280:-2" -q:v 3 "$OUT/frames_60s/frame_%05d.jpg"
```

```bash
ffmpeg -hide_banner -y -i "$VIDEO" -vf "scale=1280:-2,fps=12" \
  -c:v h264_videotoolbox -b:v 500k -maxrate 700k -bufsize 1000k \
  -c:a aac -b:a 64k -movflags +faststart "$OUT/$STEM.720p.compact.mp4"
```

For screen recordings and slide-heavy videos, time-based candidate frames every 30-60 seconds are usually more reliable than scene detection alone. Scene detection can be an optional supplement:

```bash
ffmpeg -hide_banner -y -i "$VIDEO" -vf "select='gt(scene,0.08)',scale=1280:-2" -vsync vfr "$OUT/scene_frames/frame_%05d.jpg"
```

For OCR:

```bash
tesseract "$FRAME" stdout -l chi_sim+eng --psm 6
```

## Keyframe Curation

Do not archive every extracted frame by default. Treat candidate frames as temporary evidence.

Keep a frame only when it adds retrieval or understanding value:

- It contains a slide title, outline, checklist, diagram, table, code, URL, command, product name, or UI state that is useful later.
- Its OCR text has enough meaningful content. As a starting threshold, require at least 30 meaningful CJK/Latin/digit characters after removing whitespace and punctuation.
- It is not near-duplicate of the previous retained frame. Use OCR text similarity, perceptual image similarity, or both. As a starting rule, drop frames whose cleaned OCR text is more than 80% similar to a retained frame unless the image clearly changed.
- It has acceptable OCR quality. Drop frames dominated by UI chrome, watermark noise, chat overlays, empty screens, or broken OCR.
- It helps segment the video into chapters even if OCR is imperfect.

For long videos, prefer 12-40 curated frames unless the user asks for a denser visual archive. Keep `keyframes_index.md` with:

- Timestamp.
- Frame filename.
- Short OCR excerpt.
- Why it was kept.

After curation, delete or leave out the raw candidate frame directory from the final Obsidian archive unless the user asks for a debug bundle.

## Artifact Archival

Archive final text and curated visual artifacts into the Obsidian vault:

- Summary note.
- Transcript or transcript excerpts.
- Subtitle file when useful.
- Curated keyframes.
- `keyframes_index.md`.
- Clean OCR summary or OCR excerpts.

Compressed video archival is configurable because it can be large and may affect Obsidian Sync/iCloud/Git:

- If the compressed video is under the user's configured size limit, archive it into the same `_video-assets/<slug>/` folder.
- If no limit is configured, ask before copying files larger than 200 MB into the vault.
- If the user declines or the file is too large, keep the compressed video outside the vault and record its absolute local path in frontmatter and the artifact index.

## Knowledge Summary Rules

Summarize from the transcript first; use OCR as a secondary source for slide titles, outline recovery, product names, URLs, and keywords.

The Obsidian note should include:

- A concise title.
- Valid quoted YAML frontmatter.
- Category, series, and classification confidence from the user's classification guide.
- One-sentence summary.
- Core conclusions.
- Tool/process relationships when relevant.
- Actionable workflow or checklist.
- Risks and caveats.
- Relative vault artifact links for archived files.
- Absolute local paths only for large files intentionally kept outside the vault.

Do not paste the full transcript into the knowledge note by default. Store the summary and link to the archived transcript instead.

If the source language is English, write the saved note in Chinese unless the user asks otherwise.

## Frontmatter Pattern

Use this shape and adapt it to the source:

```yaml
---
title: "Readable Chinese title"
source: "Local video file"
source_url_status: "not archived; original URL may contain access tokens"
author: "unknown"
captured: "YYYY-MM-DD"
processed: "YYYY-MM-DD"
type: "video-summary"
language: "zh-CN"
original_language: "zh-CN"
category: "Development"
series: "Engineering"
classification_confidence: "high"
video_duration: "HH:MM:SS"
local_source_file: "/absolute/path/source.mp4"
artifact_folder: "01 Sources/Development/_video-assets/YYYY-MM-DD-short-slug/"
compressed_video_file: "01 Sources/Development/_video-assets/YYYY-MM-DD-short-slug/video.compact.mp4"
transcript_file: "01 Sources/Development/_video-assets/YYYY-MM-DD-short-slug/transcript.txt"
keyframes_index: "01 Sources/Development/_video-assets/YYYY-MM-DD-short-slug/keyframes_index.md"
tags:
  - "video-capture"
  - "transcription"
---
```

Validate frontmatter before writing when a local YAML parser is available.

## Completion Check

Before reporting success:

- Confirm all expected artifacts exist and have nonzero size.
- Confirm the Obsidian note can be read back through the Local REST API or MCP tool.
- Confirm final artifacts are archived under the Obsidian note's category folder, not only in the source/download directory.
- Confirm raw candidate frames were removed from the final archive unless the user asked to keep them.
- Report any degraded steps, such as OCR missing Chinese language data, transcription fallback model, or manual download required.
