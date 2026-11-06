# Your first AnimeLab contribution

[Français](first-contribution.md) | [English](first-contribution.en.md)

Choose one task below and comment on its issue with your idea, platform and the
help you need. Read recent comments before starting to avoid duplicate work.
These three issues are the highlighted entry points; the
[tracker #12](https://github.com/loeuf237/animelab/issues/12) lists other tasks too.

The maintainer can help narrow the scope, identify relevant files and select
checks. A report or mockup is enough to get started. Target for an initial reply:
two working days, subject to availability. See [CONTRIBUTING](../CONTRIBUTING.en.md).

Baseline as of **6 November 2026**: **v0.1.6-beta.5** for installed-app tests;
`main` for documentation and design. Always record the actual tag or
`git rev-parse HEAD`. One device test does not certify all devices or sources.

## Android

**Task:** document a cold start and airplane-mode playback on one phone in
[#32](https://github.com/loeuf237/animelab/issues/32). No Kotlin change or Android
build is required.

**Preparation:** Android 10+ ARM64 device, [beta.5 APK](https://github.com/loeuf237/animelab/releases/tag/v0.1.6-beta.5)
and a short video you can use. Prepare a completed AnimeLab download using test
data; do not clean or replace a personal library. If preparation fails, report
that blocker without claiming offline playback failed. The APK extension runtime
remains experimental.

1. Record app version, phone model, Android version, video format and private/exported location.
2. Fully close AnimeLab, enable airplane mode and reopen the app.
3. Open available local media, play the video and seek to another position.
4. Close and reopen; check position restoration. Test subtitles/audio tracks
   only when they are actually present locally.
5. Restore the network setting and record at most three reproducible blockers.

**Deliverable:** an issue comment or small documentation PR with this matrix,
numbered reproduction steps and useful screenshots:

| Stage | Passed / failed / blocked / not tested | Observation and evidence |
| --- | --- | --- |
| Airplane-mode cold start | Fill in | |
| Access to local media | Fill in | |
| Playback and seeking | Fill in | |
| Close and restore position | Fill in | |

**Validation:** describe the observed outcome, including success or a blocker,
without sharing cookies, signed URLs or a personal database. Starting points:
[Android storage](android-distribution.md), [player](../frontend/src/stores/player.ts)
and [library](../frontend/src/views/LibraryView.vue).

## Linux

**Task:** follow the existing instructions and propose a short illustrated FR/EN
walkthrough in [#21](https://github.com/loeuf237/animelab/issues/21).

**Preparation:** Linux, Git, Python 3.12/3.13, uv 0.13.1, Node.js 22.13+ in the
22.x line and FFmpeg/ffprobe. Use a test account/profile without a personal AnimeLab
library. Installation downloads dependencies; a documentation review or FR/EN
correction can be proposed without installing the complete toolchain.

1. Record distribution, architecture and checkout commit.
2. Follow [CONTRIBUTING](../CONTRIBUTING.en.md#setting-up-your-environment) and
   [development setup](development.md) to install dependencies, build the interface
   and open the launcher with `uv run --locked --group desktop python desktop.py`.
3. Explain how this checkout differs from a release archive containing the
   `AnimeLab` executable. Do not invent an executable in the source directory.
4. Capture the actual launcher/interface, any error and browser fallback when
   the native WebView is unavailable.
5. Stop the test server using the launcher's **Stop** button.

**Deliverable:** a PR limited to the guide and its FR/EN README links, with two or
three screenshots, commands followed and missing prerequisites identified.
An installation difficulty reported in the issue is useful too.

**Validation:** check links, matching FR/EN captions and the exact tested platform.
Markdown validation alone does not demonstrate a real launch. Reuse
[desktop.py](../desktop.py) and the [desktop guide](desktop-distribution.md);
no launcher implementation change is required.

## Design

**Task:** propose one extra palette in [#28](https://github.com/loeuf237/animelab/issues/28)
with three previews. No backend, Android build or new theme picker is required.

**Preparation:** four palettes and light/dark modes already exist. Read
[themes.css](../frontend/src/themes.css),
[ThemePicker.vue](../frontend/src/components/ThemePicker.vue),
[appearance.ts](../frontend/src/stores/appearance.ts) and [branding](branding/README.md).
Static mockups can be produced without installing the app.

1. Name the palette and map colors to existing variables, including `--bg`,
   `--panel`, `--text`, `--muted`, `--accent` and `--line`.
2. Show library, extensions and player, with at least one narrow-screen preview.
3. Show text, focus, selection and errors using cues beyond color alone.
4. Record text/background contrast and limitations of light/dark variants;
   measurements or screenshots are more useful than a broad accessibility claim.

**Deliverable:** a documented palette and three annotated images in #28 or a PR.
Identify the origin/license of reused assets. Picker integration is a separate
step to discuss in #23.

**Validation:** colors reference actual tokens, labels remain readable, focus is
visible and a mobile preview is included. A mockup does not prove integration.

## Proposals and review

In your comment or PR, state the chosen task, proposed result, version/platform,
checks performed and help needed. A draft PR can be reviewed early. Keep changes
limited to the agreed deliverable.

Use [Discussions](https://github.com/loeuf237/animelab/discussions) for open questions.
Keep technical decisions in the issue or PR. Accepted contributions are credited
in release notes, including design, testing and documentation.
