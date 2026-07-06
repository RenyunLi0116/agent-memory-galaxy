# Agent Memory Galaxy - Repository Memory

This file is both a lightweight project log and an example of the `agent_memory.md` format.

## 2026-07-03 - Public framework scaffold (codex)
- What changed: Prepared a public-safe framework for multi-machine agent memory graphs, including a marketing page, runtime viewer separation, synthetic demo generation, and skill/plugin packaging.
- Why: Public repositories should explain the system and provide install paths without exposing real memory fragments, machines, projects, or private graph data.
- Status: done
- Verification: Run the public demo builder and privacy leak scan before release.
- Files: README.md, AGENTS.md, ONBOARDING.md, PORTABILITY.md, docs/index.html, viewer/index.html, scripts/build-public-demo.py, plugins/agent-memory-galaxy/skills/agent-memory-galaxy/SKILL.md

## 2026-07-06 - Public demo visual alignment and bilingual launch polish (codex)
- What changed: Synchronized the public demo viewer closer to the private viewer visual baseline by restoring the default `cosmos` style, making demo URLs explicit with `style=cosmos`, adding public demo edge labels, and extending galaxy glyph mapping for `boundary` and `artifact` nodes. Reworked the promotional hero thumbnail from a static mini layout into a public-safe animated SVG micro-galaxy with glowing nodes, flowing edges, scan motion, responsive panels, and reduced-motion support. Added bilingual README/demo URL updates and kept the promo/demo language switching intact.
- Why: The public repository is intended for promotion and skill adoption, so the demo needs to look consistent with the private viewer while remaining synthetic, attractive, bilingual, and safe to publish.
- Status: done
- Verification: Regenerated `docs/demo` and landing assets, checked Python syntax, JS syntax, JSON validity, `git diff --check`, local HTTP routes, Chrome headless layout and canvas rendering, private artifact tracking, secret/path leak scan, and live GitHub Pages URLs. Pushed commit `5972c50` and confirmed online pages returned 200 with latest content.
- Files: README.md, README.zh-CN.md, viewer/index.html, docs/demo/index.html, docs/galaxy/index.html, scripts/build-landing-concepts.py, docs/index.html, docs/assets/landing.css, docs/assets/landing.js, docs/concepts/*.html
