#!/usr/bin/env python3
"""Generate static marketing concept pages for the public repo."""
from __future__ import annotations

import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONCEPTS = DOCS / "concepts"
ASSETS = DOCS / "assets"
GRAPH = DOCS / "demo" / "graph.json"


CONCEPTS_DATA = [
    {
        "slug": "product-launch",
        "theme": "theme-product",
        "name": "Product Launch",
        "kicker": "MULTI-MACHINE MEMORY -> GALAXY VIEWER",
        "title": "Turn agent traces into a clickable memory galaxy.",
        "lead": "Collect agent_memory.md, safe session metadata, machine fragments, and live presence into graph.json, then inspect the result in a browser-based Galaxy Viewer.",
        "best": "Best for a clear public README-to-install conversion path.",
        "primary": "Open synthetic demo",
        "secondary": "Install the skill",
        "proof": ["Public framework", "Private memory", "125 synthetic nodes", "No build step"],
        "sections": [
            ("Data Path", "Contributor machines write fragments. The aggregator normalizes entries, facts, files, datasets, models, and live agents into one graph."),
            ("Viewer Interaction", "Search, filter by machine or node type, zoom, rotate, and click nodes for source-aware readouts."),
            ("Privacy Architecture", "Public repo for code and demo data. Private hub for real fragments, presence, graph.json, and standalone.html."),
        ],
    },
    {
        "slug": "graphite-console",
        "theme": "theme-graphite",
        "name": "Graphite Console",
        "kicker": "PUBLIC FRAMEWORK / PRIVATE MEMORY",
        "title": "A quiet control room for agent work memory.",
        "lead": "A dark technical launch page with the live synthetic galaxy as the product surface. No loud neon, just status, structure, and a graph you can inspect.",
        "best": "Best for developer-tool launch energy without looking like a generic cyber poster.",
        "primary": "Expand galaxy",
        "secondary": "View privacy model",
        "proof": ["Graph JSON truth", "Contributor -> aggregator", "Encrypted Pages option", "Live presence nodes"],
        "sections": [
            ("Agent Work Leaves Traces", "Sessions, files, datasets, W&B runs, Notion pages, and machines each carry context that future agents need."),
            ("Pipeline", "Collect, distill, merge, encrypt, view. The workflow stays static and auditable."),
            ("Operating Modes", "Contributors write machine fragments. Aggregators merge, inject presence, and publish encrypted viewer assets when needed."),
        ],
    },
    {
        "slug": "research-memo",
        "theme": "theme-lab",
        "name": "Research Memo",
        "kicker": "FIELD NOTES FOR MULTI-AGENT WORK",
        "title": "Not another notes folder. A graph your next agent can enter.",
        "lead": "A paper-and-ink research product page: concise lab memo, real interactive Figure 1, and a privacy model that keeps personal work out of the public repo.",
        "best": "Best for researchers and open-source builders who want technical credibility.",
        "primary": "Inspect Figure 1",
        "secondary": "Read runbook",
        "proof": ["Synthetic figure", "Node and edge model", "Session summaries only", "Private by default"],
        "sections": [
            ("Fragmented Agent Work", "One debugging trail is on a laptop, another training note is on a runner, and every tool remembers a different slice."),
            ("Method", "Normalize traces into project, entry, fact, agent, machine, dataset, server, model, method, file, wandb, tech, and notion nodes."),
            ("Privacy Model", "Plaintext stays local. Fragments live in private hubs. Public Pages should serve encrypted graph data only."),
        ],
    },
    {
        "slug": "bento-proof",
        "theme": "theme-bento",
        "name": "Bento Proof",
        "kicker": "OPEN-SOURCE DEVTOOL / INSTALLABLE SKILL",
        "title": "Understand the repo in ten seconds.",
        "lead": "A dense proof page that puts install commands, data policy, multi-machine roles, and the interactive galaxy in the first viewport.",
        "best": "Best default direction for open-source devtool promotion.",
        "primary": "Open synthetic demo",
        "secondary": "Install skill",
        "proof": ["Two install messages", "Plaintext gitignored", "Fragments sync privately", "Synthetic demo public"],
        "sections": [
            ("Install", "Add the plugin marketplace, install agent-memory-galaxy, then call the skill when connecting or aggregating memory."),
            ("Data Contract", "graph.json and standalone.html are local/private. docs/demo is synthetic. docs/galaxy is reserved for encrypted viewer assets."),
            ("Multi-Machine Sync", "Each contributor writes a fragment. The aggregator merges shared entities and produces the galaxy."),
        ],
    },
    {
        "slug": "spatial-orbit",
        "theme": "theme-orbit",
        "name": "Spatial Orbit",
        "kicker": "SPATIAL MEMORY INFRA",
        "title": "A private orbit map for the work your agents leave behind.",
        "lead": "A premium spatial page with restrained motion, titanium-dark surfaces, and the memory galaxy as the central object rather than decorative wallpaper.",
        "best": "Best for a polished AI-infrastructure brand impression.",
        "primary": "Open live preview",
        "secondary": "Compare concepts",
        "proof": ["Orbit graph", "Status pulses", "Machine clusters", "Client-side unlock"],
        "sections": [
            ("Spatial Context", "Projects, files, tools, machines, and live agents become navigable objects in the same space."),
            ("Infrastructure Credibility", "Static viewer, normalized graph.json, optional encrypted Pages publishing, and no frontend build step."),
            ("Public vs Private", "The public repo demonstrates the system with fictional data. Real work memory belongs in a private deployment."),
        ],
    },
]


CSS = r"""
:root {
  color-scheme: light;
  --bg: #f7f9fc;
  --surface: #ffffff;
  --surface-2: #edf2f7;
  --text: #111827;
  --muted: #64748b;
  --line: rgba(15, 23, 42, .13);
  --accent: #2f6fed;
  --accent-2: #00a6b2;
  --accent-3: #e9a825;
  --danger: #d84e63;
  --code-bg: #0b1020;
  --code-text: #e9eefc;
  --max: 1180px;
}

.theme-graphite {
  color-scheme: dark;
  --bg: #050506;
  --surface: #0f1014;
  --surface-2: #15171d;
  --text: #f4f4f5;
  --muted: #a1a1aa;
  --line: rgba(255, 255, 255, .11);
  --accent: #8fa6ff;
  --accent-2: #48b98c;
  --accent-3: #d6a451;
  --danger: #d36b7d;
  --code-bg: #08090d;
  --code-text: #f4f4f5;
}

.theme-lab {
  --bg: #f5efe5;
  --surface: #fffaf1;
  --surface-2: #eadfce;
  --text: #171717;
  --muted: #5f5a50;
  --line: rgba(76, 63, 42, .22);
  --accent: #245e8f;
  --accent-2: #43735b;
  --accent-3: #b34b3e;
  --danger: #8f2e2e;
  --code-bg: #171717;
  --code-text: #fff7e8;
}

.theme-bento {
  color-scheme: dark;
  --bg: #090a0c;
  --surface: #121417;
  --surface-2: #191c20;
  --text: #f3f0e8;
  --muted: #a7adb5;
  --line: rgba(255, 255, 255, .10);
  --accent: #f2b84b;
  --accent-2: #5ed6b3;
  --accent-3: #7ca7ff;
  --danger: #f06f79;
  --code-bg: #060708;
  --code-text: #fff3cf;
}

.theme-orbit {
  color-scheme: dark;
  --bg: #050608;
  --surface: #111418;
  --surface-2: #1b2027;
  --text: #f5f7fa;
  --muted: #9aa3b2;
  --line: rgba(216, 222, 233, .14);
  --accent: #f4b860;
  --accent-2: #4fd1c5;
  --accent-3: #7aa2ff;
  --danger: #f06f79;
  --code-bg: #07090c;
  --code-text: #f7f8fb;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--line) 40%, transparent) 1px, transparent 1px),
    linear-gradient(180deg, color-mix(in srgb, var(--line) 36%, transparent) 1px, transparent 1px),
    var(--bg);
  background-size: 56px 56px;
  color: var(--text);
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.5;
  text-rendering: optimizeLegibility;
}
a { color: inherit; }
button, input, select, textarea { font: inherit; }
code, pre, .mono { font-family: "JetBrains Mono", "Cascadia Code", "SFMono-Regular", Consolas, monospace; }

.nav {
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(14px);
}
.nav-inner {
  width: min(var(--max), calc(100% - 32px));
  margin: 0 auto;
  min-height: 58px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.brand {
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}
.nav-links {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--muted);
  font-size: 14px;
}
.nav-links a {
  text-decoration: none;
}
.nav-links a:hover { color: var(--text); }

.page {
  width: min(var(--max), calc(100% - 32px));
  margin: 0 auto;
}
.hero {
  min-height: calc(100vh - 58px);
  display: grid;
  grid-template-columns: minmax(0, .88fr) minmax(420px, 1.12fr);
  gap: 36px;
  align-items: center;
  padding: 48px 0 34px;
}
.hero-copy { min-width: 0; }
.kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--accent);
  font: 800 12px/1 "JetBrains Mono", "Cascadia Code", monospace;
  text-transform: uppercase;
}
.kicker::before {
  content: "";
  width: 28px;
  height: 2px;
  background: var(--accent);
}
h1 {
  max-width: 860px;
  margin: 18px 0 18px;
  font-size: 68px;
  line-height: .95;
  font-weight: 860;
  letter-spacing: 0;
}
.theme-lab h1 {
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 760;
}
.lead {
  max-width: 680px;
  margin: 0;
  color: var(--muted);
  font-size: 19px;
}
.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 26px;
}
.btn {
  min-height: 44px;
  border: 1px solid var(--line);
  border-radius: 7px;
  padding: 10px 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text);
  background: var(--surface);
  text-decoration: none;
  font-weight: 760;
  cursor: pointer;
}
.btn.primary {
  background: var(--accent);
  color: color-mix(in srgb, var(--bg) 8%, white);
  border-color: transparent;
}
.theme-bento .btn.primary,
.theme-orbit .btn.primary,
.theme-lab .btn.primary {
  color: #111827;
}
.btn:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--accent) 48%, var(--line));
}
.proof-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 28px;
}
.pill {
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 10px;
  background: color-mix(in srgb, var(--surface) 74%, transparent);
  color: var(--muted);
  font-size: 13px;
  white-space: nowrap;
}

.galaxy-card {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #060814;
  min-height: 430px;
  box-shadow: 0 22px 70px rgba(0, 0, 0, .24);
  cursor: zoom-in;
}
.galaxy-card.compact {
  min-height: 360px;
}
.framebar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 3;
  height: 38px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, .10);
  background: rgba(4, 8, 18, .86);
  color: #dfe8ff;
  font-size: 12px;
}
.lights {
  display: inline-flex;
  gap: 6px;
}
.lights i {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #8fa6ff;
}
.lights i:nth-child(2) { background: #48b98c; }
.lights i:nth-child(3) { background: #d6a451; }
.framebar .status {
  margin-left: auto;
  color: #9fb2da;
}
.galaxy-card iframe {
  position: absolute;
  inset: 38px 0 0;
  width: 100%;
  height: calc(100% - 38px);
  border: 0;
  background: #050714;
  pointer-events: none;
}
.expand-galaxy {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 4;
  border: 1px solid rgba(255, 255, 255, .18);
  border-radius: 7px;
  padding: 9px 12px;
  background: rgba(8, 13, 24, .82);
  color: #f6f8ff;
  cursor: pointer;
  font-weight: 760;
  backdrop-filter: blur(10px);
}
.expand-galaxy:hover {
  border-color: rgba(143, 166, 255, .62);
}
.preview-note {
  position: absolute;
  left: 12px;
  bottom: 12px;
  z-index: 4;
  max-width: 62%;
  color: #aab7d2;
  font-size: 12px;
  background: rgba(8, 13, 24, .72);
  border: 1px solid rgba(255, 255, 255, .10);
  border-radius: 7px;
  padding: 8px 10px;
}

.section {
  padding: 72px 0;
  border-top: 1px solid var(--line);
}
.section-head {
  display: grid;
  grid-template-columns: minmax(180px, 330px) 1fr;
  gap: 36px;
  align-items: start;
  margin-bottom: 28px;
}
.section h2 {
  margin: 0;
  font-size: 38px;
  line-height: 1.05;
  letter-spacing: 0;
}
.section-head p {
  margin: 0;
  color: var(--muted);
  font-size: 17px;
  max-width: 720px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.tile {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  padding: 22px;
}
.tile h3 {
  margin: 0 0 8px;
  font-size: 20px;
}
.tile p {
  margin: 0;
  color: var(--muted);
}
.pipeline {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.step {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  padding: 18px;
  min-height: 128px;
}
.step b {
  color: var(--accent);
  display: block;
  margin-bottom: 18px;
  font-size: 12px;
}
.step span {
  display: block;
  font-weight: 800;
  margin-bottom: 8px;
}
.step p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}
.install-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.code {
  position: relative;
  margin: 14px 0 0;
  padding: 16px;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--code-bg);
  color: var(--code-text);
  font-size: 13px;
}
.copy-btn {
  margin-top: 10px;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: var(--surface-2);
  color: var(--text);
  padding: 7px 10px;
  cursor: pointer;
}
.compare-hero {
  padding: 72px 0 42px;
}
.concept-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin: 30px 0 60px;
}
.concept-card {
  min-height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 20px;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  text-decoration: none;
}
.concept-card:hover {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
  transform: translateY(-2px);
}
.concept-card h2 {
  margin: 0 0 10px;
  font-size: 24px;
}
.concept-card p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}
.swatch {
  display: flex;
  gap: 5px;
  margin-top: 18px;
}
.swatch i {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 1px solid var(--line);
}

.modal {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: none;
  background: rgba(0, 0, 0, .72);
  padding: 28px;
}
.modal.open {
  display: grid;
  place-items: center;
}
.modal-panel {
  width: min(1280px, 96vw);
  height: min(860px, 90vh);
  border: 1px solid rgba(255, 255, 255, .16);
  border-radius: 8px;
  overflow: hidden;
  background: #050714;
  box-shadow: 0 30px 90px rgba(0, 0, 0, .48);
}
.modal-head {
  height: 44px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  background: #090e1a;
  color: #eff4ff;
  border-bottom: 1px solid rgba(255, 255, 255, .12);
}
.modal-head .muted {
  color: #93a1bd;
  font-size: 12px;
}
.modal-close {
  margin-left: auto;
  border: 1px solid rgba(255, 255, 255, .18);
  border-radius: 7px;
  background: transparent;
  color: #eff4ff;
  cursor: pointer;
  padding: 6px 9px;
}
.modal iframe {
  width: 100%;
  height: calc(100% - 44px);
  border: 0;
  background: #050714;
  pointer-events: auto;
}
.footer {
  padding: 36px 0;
  color: var(--muted);
  border-top: 1px solid var(--line);
}
.footer .page {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

@media (max-width: 1080px) {
  .hero { grid-template-columns: 1fr; min-height: auto; }
  .galaxy-card { min-height: 520px; }
  .concept-list { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 760px) {
  .nav-links { display: none; }
  h1 { font-size: 44px; }
  .lead { font-size: 17px; }
  .section { padding: 48px 0; }
  .section-head, .grid, .pipeline, .install-grid { grid-template-columns: 1fr; }
  .galaxy-card { min-height: 430px; }
  .preview-note { display: none; }
  .concept-list { grid-template-columns: 1fr; }
  .modal { padding: 0; }
  .modal-panel { width: 100vw; height: 100vh; border-radius: 0; border: 0; }
}
@media (max-width: 480px) {
  .page, .nav-inner { width: min(var(--max), calc(100% - 24px)); }
  h1 { font-size: 38px; }
  .actions { display: grid; }
  .galaxy-card { min-height: 380px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .btn:hover, .concept-card:hover { transform: none; }
}
"""



CSS += r"""
.hero.landing-hero {
  grid-template-columns: minmax(0, .92fr) minmax(440px, 1.08fr);
}
.hero-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: 24px;
  max-width: 760px;
}
.hero-stat {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: color-mix(in srgb, var(--surface) 82%, transparent);
  padding: 12px;
}
.hero-stat b { display: block; font-size: 24px; color: var(--accent); }
.hero-stat span { color: var(--muted); font-size: 12px; }
.domain-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: color-mix(in srgb, var(--surface) 90%, transparent);
}
.domain-table th,
.domain-table td {
  border-bottom: 1px solid var(--line);
  padding: 13px 14px;
  text-align: left;
  vertical-align: top;
}
.domain-table th { color: var(--accent); font-size: 12px; text-transform: uppercase; }
.domain-table tr:last-child td { border-bottom: 0; }
.callout-band {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.command-stack .code { margin-top: 10px; }
.mini-label { color: var(--accent); font: 800 11px/1.2 "JetBrains Mono", monospace; text-transform: uppercase; }
@media (max-width: 1080px) {
  .hero.landing-hero { grid-template-columns: 1fr; }
}
@media (max-width: 760px) {
  .hero-stat-grid, .callout-band { grid-template-columns: 1fr; }
  .domain-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .domain-table { min-width: 620px; }
  .modal-head .muted { display: none; }
}
"""

CSS += r"""
.lang-switch {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: color-mix(in srgb, var(--surface) 86%, transparent);
}
.lang-switch button {
  min-width: 42px;
  border: 0;
  border-radius: 5px;
  padding: 5px 8px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
}
.lang-switch button.active {
  color: #101318;
  background: var(--accent);
}
.galaxy-card {
  width: 100%;
  min-width: 0;
  min-height: 0;
  height: clamp(320px, 44vw, 540px);
  container-type: inline-size;
}
.galaxy-card.compact { height: clamp(300px, 38vw, 420px); min-height: 0; }
.framebar { overflow: hidden; }
.framebar .mono { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.framebar .status { flex: 0 1 auto; min-width: 0; }
/* --- Cinematic canvas mini galaxy. HTML panels stay on top; the SVG below is the
   static fallback for noscript / prefers-reduced-motion. --- */
.galaxy-card {
  transition: border-color .25s ease, box-shadow .25s ease;
}
.galaxy-card:hover,
.galaxy-card:focus-visible {
  border-color: rgba(143, 166, 255, .5);
  box-shadow: 0 22px 70px rgba(0, 0, 0, .34), 0 0 44px rgba(96, 128, 255, .16);
}
.framebar {
  background: linear-gradient(180deg, rgba(9, 15, 34, .94), rgba(5, 9, 22, .88));
  border-bottom: 1px solid rgba(120, 150, 255, .16);
}
.lights i { box-shadow: 0 0 8px rgba(143, 166, 255, .85); }
.lights i:nth-child(2) { box-shadow: 0 0 8px rgba(72, 185, 140, .85); }
.lights i:nth-child(3) { box-shadow: 0 0 8px rgba(214, 164, 81, .85); }
.mini-galaxy-preview {
  position: absolute;
  inset: 38px 0 0;
  overflow: hidden;
  background:
    radial-gradient(ellipse at 22% 26%, rgba(104, 66, 222, .32), transparent 54%),
    radial-gradient(ellipse at 78% 70%, rgba(40, 92, 214, .28), transparent 56%),
    radial-gradient(ellipse at 52% 46%, rgba(255, 196, 128, .10), transparent 42%),
    radial-gradient(circle at 50% 46%, #0a102e 0%, #05071c 55%, #02030e 100%);
}
.mini-galaxy-preview::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  background: radial-gradient(circle at 50% 48%, transparent 42%, rgba(1, 3, 12, .40) 88%);
  pointer-events: none;
}
.mini-galaxy-preview.canvas-on::after {
  background: radial-gradient(circle at 50% 48%, transparent 52%, rgba(1, 3, 12, .28) 94%);
}
.mini-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: none;
}
.canvas-on .mini-canvas { display: block; }
.canvas-on .mini-map { display: none; }

/* Static SVG fallback */
.mini-map {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}
.mini-orbit {
  fill: none;
  stroke: rgba(138,180,255,.16);
  stroke-width: 1;
  stroke-dasharray: 6 14;
  animation: mini-orbit-drift 24s linear infinite;
}
.mini-orbit.gold { stroke: rgba(255,207,107,.30); animation-duration: 18s; animation-direction: reverse; }
.mini-edge {
  fill: none;
  stroke: rgba(95,152,230,.36);
  stroke-width: 1.2;
  stroke-linecap: round;
  stroke-dasharray: 8 18;
  animation: mini-flow 4.8s linear infinite;
  filter: url(#mini-glow);
  transition: stroke .22s ease, stroke-width .22s ease, opacity .22s ease;
}
.mini-edge.warm { stroke: rgba(255,188,118,.78); stroke-width: 2.4; }
.mini-edge.live { stroke: rgba(255,64,82,.72); stroke-width: 2; animation-duration: 2.2s; }
.mini-edge.secure { stroke: rgba(125,243,196,.68); stroke-width: 1.8; }
.mini-edge.active { stroke-width: 3.2; opacity: 1; }
.mini-dust {
  fill: rgba(211,222,255,.42);
  animation: mini-twinkle 3.8s ease-in-out infinite;
}
.mini-dust:nth-of-type(2n) { animation-delay: -1.1s; opacity: .5; }
.mini-dust:nth-of-type(3n) { animation-delay: -2.4s; opacity: .36; }
.mini-star .halo { opacity: .34; filter: url(#mini-glow); }
.mini-star .core { filter: url(#mini-glow); animation: mini-pulse 2.8s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
.mini-star.project .core { fill: #ff5d73; }
.mini-star.server .core { fill: #ff5fa2; }
.mini-star.agent .core { fill: #ff3b4e; animation-duration: 1.55s; }
.mini-star.boundary .core { fill: #f5b642; }
.mini-star.artifact .core { fill: #7df3c4; }
.mini-star .spike { stroke: currentColor; stroke-width: 1.2; stroke-linecap: round; opacity: .72; filter: url(#mini-glow); }
.mini-star.project, .mini-star.agent { color: #ff7282; }
.mini-star.server { color: #ff6faa; }
.mini-star.boundary { color: #f5b642; }
.mini-star.artifact { color: #7df3c4; }
.mini-star .lock { fill: none; stroke: #ffcf6b; stroke-width: 1.3; opacity: 0; transition: opacity .22s ease; }
.mini-star.active .halo { opacity: .82; }
.mini-star.active .lock { opacity: .95; }
.mini-scan {
  fill: none;
  stroke: rgba(56,225,255,.50);
  stroke-width: 1.4;
  stroke-linecap: round;
  stroke-dasharray: 18 28;
  filter: url(#mini-glow);
  animation: mini-scan 5.8s linear infinite;
}
.mini-coreline {
  fill: none;
  stroke: rgba(255,220,165,.28);
  stroke-width: 20;
  stroke-linecap: round;
  filter: url(#mini-soft-glow);
}

/* HUD panels float above the canvas in plain HTML (never transformed, always crisp) */
.mini-side,
.mini-readout {
  position: absolute;
  z-index: 3;
  border: 1px solid rgba(148, 178, 255, .28);
  border-radius: 6px;
  background: linear-gradient(165deg, rgba(16, 24, 52, .84), rgba(5, 9, 24, .80));
  color: #dbe4ff;
  backdrop-filter: blur(9px);
  box-shadow: 0 12px 32px rgba(1, 4, 16, .45), inset 0 0 24px rgba(88, 128, 255, .08);
}
.mini-side {
  left: 12px;
  top: 12px;
  width: min(172px, 40cqw);
  padding: 10px;
  display: grid;
  gap: 6px;
  font: 10px/1.25 "JetBrains Mono", monospace;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.mini-side b { color: #9fc0ff; }
.mini-side span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #97acd8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mini-side span::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 10px currentColor, 0 0 20px color-mix(in srgb, currentColor 55%, transparent);
  flex: none;
}
.mini-side [data-mini-type="project"] { color: #ff7282; }
.mini-side [data-mini-type="server"] { color: #ff6faa; }
.mini-side [data-mini-type="agent"] { color: #ff3b4e; }
.mini-side [data-mini-type="boundary"] { color: #f5b642; }
.mini-side [data-mini-type="artifact"] { color: #7df3c4; }
.mini-readout {
  right: 12px;
  top: 12px;
  max-width: min(262px, 45cqw);
  padding: 10px 12px;
  font: 11px/1.5 "JetBrains Mono", monospace;
}
.mini-readout b {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #ffcf6b;
  margin-bottom: 5px;
  letter-spacing: .06em;
}
.mini-readout b::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ff4052;
  box-shadow: 0 0 10px #ff4052;
  flex: none;
  animation: mini-live-blink 1.6s ease-in-out infinite;
}
.mini-readout span {
  color: #9fb2da;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
  overflow: hidden;
  overflow-wrap: anywhere;
}
@keyframes mini-flow { to { stroke-dashoffset: -104; } }
@keyframes mini-pulse { 50% { transform: scale(1.18); opacity: .72; } }
@keyframes mini-twinkle { 50% { opacity: .88; } }
@keyframes mini-scan { to { stroke-dashoffset: -184; } }
@keyframes mini-orbit-drift { to { stroke-dashoffset: -160; } }
@keyframes mini-live-blink { 50% { opacity: .35; } }
@media (prefers-reduced-motion: reduce) {
  .mini-edge, .mini-scan, .mini-orbit, .mini-dust, .mini-star .core { animation: none !important; }
  .mini-canvas { display: none !important; }
  .canvas-on .mini-map { display: block !important; }
}
@container (max-width: 560px) {
  .framebar .status { display: none; }
  .mini-readout { display: none; }
  .mini-side { width: 138px; font-size: 9px; }
}
@container (max-width: 420px) {
  .mini-side { display: none; }
  .expand-galaxy { left: 12px; right: 12px; text-align: center; }
}

@media (max-width: 760px) {
  .nav-links { display: flex; margin-left: auto; gap: 8px; }
  .nav-links > a { display: none; }
  .lang-switch { display: inline-flex; }
}
"""


JS = r"""
(function () {
  var modal = document.querySelector('[data-galaxy-modal]');
  var frame = modal ? modal.querySelector('iframe') : null;
  var close = modal ? modal.querySelector('[data-modal-close]') : null;
  var lastFocus = null;
  var dict = {
    en: {
      navConcepts: 'Design archive', navDemo: 'Demo', navPrivacy: 'Privacy', navInstall: 'Install',
      previewTitle: 'synthetic graph preview', previewNote: 'Compressed public preview. Open the full demo for search, filters, zoom, and readouts.',
      expandGalaxy: 'Expand galaxy', miniSideTitle: 'NODE TYPES', miniProject: 'Project', miniServer: 'Server', miniAgent: 'Agent', miniBoundary: 'Boundary', miniArtifact: 'Artifact', miniReadoutTitle: 'ONLINE HUD', miniReadout: 'multi-server handoff / live agents / encrypted boundary',
      modalMuted: 'Synthetic demo. Drag, zoom, filter, and inspect nodes.', openFullDemo: 'Open full demo', close: 'Close', copied: 'Copied', copyFailed: 'Copy failed',
      status: function (n, e, m) { return n + ' nodes / ' + e + ' links / ' + m + ' machines'; },
      heroKicker: 'PUBLIC FRAMEWORK / PRIVATE MEMORY', heroTitle: 'Your agents remember together. Privately.',
      heroLead: 'Turn scattered agent traces across machines into one private, inspectable memory graph. Collect reviewed notes, safe session metadata, machine fragments, and live presence, then explore the result in a static Galaxy Viewer.',
      openDemo: 'Open synthetic demo', installSkill: 'Install as skill', syntheticNodes: 'synthetic nodes', syntheticLinks: 'synthetic links', fictionalProjects: 'fictional projects', fictionalMachines: 'fictional machines',
      previewHeading: 'Live synthetic demo. No real memory.', previewBody: 'The public graph demonstrates multi-server collaboration, currently-working agents, project inheritance, shared assets, and private/public/encrypted boundaries using fictional labels only.',
      searchLabel: 'Search', searchTitle: 'Find a project or artifact', searchBody: 'Search across projects, agents, files, models, servers, and derived facts.',
      filterLabel: 'Filter', filterTitle: 'Focus by machine or activity', filterBody: 'Switch from the full graph to one machine, one project, recent work, or live doing state.',
      inspectLabel: 'Inspect', inspectTitle: 'Click through evidence', inspectBody: 'Open a node readout, inspect neighbors, and follow inheritance or publishing edges.',
      installHeading: 'Install in two Claude Code messages.', installBody: 'The public repository carries a Claude Code plugin/skill package. Use it to set up private hubs, connect contributors, aggregate fragments, publish encrypted viewers, or review privacy before release.',
      pluginInstall: 'Plugin/skill install', copyMarketplace: 'Copy marketplace command', copyInstall: 'Copy install command', localDemo: 'Local demo fallback', copyDemo: 'Copy demo commands',
      workflowHeading: 'Collect, distill, merge, encrypt, view.', workflowBody: 'Contributor machines write private fragments. An aggregator merges shared entities, injects live presence, and optionally publishes an encrypted viewer shell.',
      stepCollect: 'Collect', stepCollectBody: 'Scan reviewed `agent_memory.md` notes from explicit project roots.', stepDistill: 'Distill', stepDistillBody: 'Extract safe structured metadata from agent sessions without copying raw text.', stepMerge: 'Merge', stepMergeBody: 'Connect projects through shared files, datasets, models, tools, and servers.', stepEncrypt: 'Encrypt', stepEncryptBody: 'Publish ciphertext only when deploying an encrypted viewer shell to Pages.', stepView: 'View', stepViewBody: 'Search, filter, zoom, and inspect the resulting memory galaxy.',
      privacyHeading: 'Public framework. Private memory.', privacyBody: 'GitHub Pages is not private access control. Public pages carry the framework and fake demo data. Real fragments and plaintext graphs belong in a private hub or local machine.',
      contributor: 'Contributor', contributorBody: 'Writes `fragments/<machine>.json` in a private hub. Does not need encryption passwords and should not touch `docs/galaxy/`.', aggregator: 'Aggregator', aggregatorBody: 'Merges all fragments, builds local `standalone.html`, and optionally creates `docs/galaxy/graph.enc.json` with strong passwords.',
      urlHeading: 'Know which URL you are sharing.', urlBody: 'The marketing site, synthetic demo, and optional encrypted runtime viewer are separate paths.', path: 'Path', purpose: 'Purpose', dataPolicy: 'Data policy',
      urlPromo: 'Public promo landing', urlNoReal: 'No real data', urlDemo: 'Synthetic interactive demo', urlFake: 'Fake graph only', urlConcepts: 'Design exploration archive', urlSecondary: 'Public, secondary', urlGalaxy: 'Optional encrypted viewer shell', urlCipher: 'Public shell, ciphertext only', urlStandalone: 'Local plaintext viewer', urlLocal: 'Local only, gitignored',
      footerPrivacy: 'Synthetic demo public. Real memory private.'
    },
    zh: {
      navConcepts: '设计存档', navDemo: '演示', navPrivacy: '隐私', navInstall: '安装',
      previewTitle: '合成图谱预览', previewNote: '压缩公开预览。打开完整 demo 后可搜索、过滤、缩放和查看读出面板。',
      expandGalaxy: '展开图谱', miniSideTitle: '节点类型', miniProject: '项目', miniServer: '机器', miniAgent: 'Agent', miniBoundary: '边界', miniArtifact: '产物', miniReadoutTitle: '在线 HUD', miniReadout: '多服务器交接 / 在线 agent / 加密边界',
      modalMuted: '合成 demo。可拖拽、缩放、过滤并点击节点读出。', openFullDemo: '打开完整 demo', close: '关闭', copied: '已复制', copyFailed: '复制失败',
      status: function (n, e, m) { return n + ' 节点 / ' + e + ' 连线 / ' + m + ' 机器'; },
      heroKicker: '公开框架 / 私有记忆', heroTitle: '让你的 agents 一起记住工作。并保持私有。',
      heroLead: '把分散在多台机器上的 agent 工作痕迹汇成一个私有、可检索、可检查的记忆图谱。它收集审阅后的笔记、安全会话元数据、机器 fragment 和在线状态，并在静态 Galaxy Viewer 中探索。',
      openDemo: '打开合成 demo', installSkill: '安装为 skill', syntheticNodes: '合成节点', syntheticLinks: '合成连线', fictionalProjects: '虚构项目', fictionalMachines: '虚构机器',
      previewHeading: '实时合成 demo，不含真实记忆。', previewBody: '公开图谱用虚构标签展示多服务器协作、正在工作的 agent、项目继承、共享资产，以及公开/私有/加密边界。',
      searchLabel: '搜索', searchTitle: '查找项目或产物', searchBody: '跨项目、agent、文件、模型、服务器和自动提炼事实搜索。',
      filterLabel: '过滤', filterTitle: '聚焦机器或活跃状态', filterBody: '从完整图谱切到单台机器、单个项目、近期工作或正在做的状态。',
      inspectLabel: '读出', inspectTitle: '点击查看证据链', inspectBody: '打开节点读出面板，检查邻居，并沿继承或发布边继续追踪。',
      installHeading: '两条 Claude Code 消息完成安装。', installBody: '公开仓库包含 Claude Code plugin/skill 包。可用于创建私有 hub、连接贡献机器、聚合 fragments、发布加密 viewer，或在公开前审阅隐私。',
      pluginInstall: 'Plugin/skill 安装', copyMarketplace: '复制 marketplace 命令', copyInstall: '复制 install 命令', localDemo: '本地 demo 备用路径', copyDemo: '复制 demo 命令',
      workflowHeading: '采集、提炼、合并、加密、查看。', workflowBody: '贡献机器写入私有 fragments。聚合端合并共享实体，注入在线状态，并可选择发布加密 viewer shell。',
      stepCollect: '采集', stepCollectBody: '从明确指定的项目根目录扫描已审阅的 `agent_memory.md`。', stepDistill: '提炼', stepDistillBody: '从 agent session 中提取安全结构化元数据，不复制原始对话。', stepMerge: '合并', stepMergeBody: '通过共享文件、数据集、模型、工具和服务器连接项目。', stepEncrypt: '加密', stepEncryptBody: '只有在部署加密 viewer shell 到 Pages 时才发布密文。', stepView: '查看', stepViewBody: '搜索、过滤、缩放并检查最终记忆图谱。',
      privacyHeading: '公开框架，私有记忆。', privacyBody: 'GitHub Pages 不是私有访问控制。公开页面只承载框架和虚构 demo 数据。真实 fragments 与明文图谱应保留在私有 hub 或本地机器。',
      contributor: '贡献机器', contributorBody: '在私有 hub 中写入 `fragments/<machine>.json`。不需要加密密码，也不应修改 `docs/galaxy/`。', aggregator: '聚合端', aggregatorBody: '合并所有 fragments，构建本地 `standalone.html`，并可用强密码创建 `docs/galaxy/graph.enc.json`。',
      urlHeading: '分清你正在分享哪个 URL。', urlBody: '宣传站、合成 demo 和可选加密运行 viewer 是不同路径。', path: '路径', purpose: '用途', dataPolicy: '数据策略',
      urlPromo: '公开宣传页', urlNoReal: '没有真实数据', urlDemo: '合成交互 demo', urlFake: '仅虚构图谱', urlConcepts: '设计探索存档', urlSecondary: '公开、次级页面', urlGalaxy: '可选加密 viewer shell', urlCipher: '公开 shell，仅密文', urlStandalone: '本地明文 viewer', urlLocal: '仅本地，已 gitignore',
      footerPrivacy: '合成 demo 公开，真实记忆私有。'
    }
  };

  function currentLang() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'zh' || q === 'en') return q;
    try { var stored = localStorage.getItem('amg_lang'); if (stored === 'zh' || stored === 'en') return stored; } catch (err) {}
    return 'en';
  }
  var lang = currentLang();
  function t(key) { return (dict[lang] && dict[lang][key]) || dict.en[key] || key; }
  function demoUrl(src) {
    var url = new URL(src || 'demo/', location.href);
    if (!url.searchParams.get('style')) url.searchParams.set('style', 'cosmos');
    url.searchParams.set('lang', lang);
    return url.pathname + url.search + url.hash;
  }
  function syncDemoLinks() {
    document.querySelectorAll('[data-demo-src]').forEach(function (el) {
      var base = el.getAttribute('data-demo-base') || el.getAttribute('data-demo-src') || 'demo/';
      el.setAttribute('data-demo-base', base);
      el.setAttribute('data-demo-src', demoUrl(base));
    });
    document.querySelectorAll('[data-demo-link]').forEach(function (el) {
      var base = el.getAttribute('data-demo-base') || el.getAttribute('href') || 'demo/';
      el.setAttribute('data-demo-base', base);
      el.setAttribute('href', demoUrl(base));
    });
  }
  function applyLang(next) {
    lang = next || lang;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    try { localStorage.setItem('amg_lang', lang); } catch (err) {}
    try { var u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState(null, '', u); } catch (err) {}
    document.querySelectorAll('[data-i18n]').forEach(function (el) { el.textContent = t(el.getAttribute('data-i18n')); });
    document.querySelectorAll('[data-preview-status]').forEach(function (el) { el.textContent = t('status')(el.dataset.nodes, el.dataset.edges, el.dataset.machines); });
    document.querySelectorAll('[data-lang-choice]').forEach(function (btn) { btn.classList.toggle('active', btn.getAttribute('data-lang-choice') === lang); });
    syncDemoLinks();
  }


  function hydrateMiniPreview() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('[data-mini-preview]').forEach(function (preview) {
      if (preview.dataset.hydrated || preview.dataset.canvasOn) return;
      preview.dataset.hydrated = '1';
      var nodes = Array.prototype.slice.call(preview.querySelectorAll('[data-mini-node]'));
      var edges = Array.prototype.slice.call(preview.querySelectorAll('[data-mini-edge]'));
      if (!nodes.length) return;
      var active = 0;
      function setActive() {
        nodes.forEach(function (node, idx) { node.classList.toggle('active', idx === active); });
        edges.forEach(function (edge) {
          var pair = (edge.getAttribute('data-pair') || '').split('-').map(function (x) { return parseInt(x, 10); });
          edge.classList.toggle('active', pair.indexOf(active) !== -1);
        });
        active = (active + 1) % nodes.length;
      }
      setActive();
      window.setInterval(setActive, 1400);
    });
  }

  /* Cinematic canvas mini galaxy: parallax starfields, log-spiral arms, nebulas,
     typed node constellation, golden reference streams, live pulses, meteors.
     All sprites are pre-rendered offscreen; per-frame work is drawImage + strokes.
     Falls back to the static SVG when reduced-motion is set or JS is unavailable. */
  function startMiniGalaxy() {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    Array.prototype.forEach.call(document.querySelectorAll('[data-mini-preview]'), function (preview) {
      var canvas = preview.querySelector('[data-mini-canvas]');
      if (!canvas || preview.dataset.canvasOn) return;
      var ctx = canvas.getContext('2d');
      if (!ctx) return;
      preview.dataset.canvasOn = '1';

      var TAU = Math.PI * 2;
      var SQ = 0.62;                    /* disc tilt: vertical squash */
      var ARM_TWIST = 3.6 * Math.PI;    /* how far each spiral arm winds */
      var seed = 20260706;
      function rand() {
        seed = seed + 0x6D2B79F5 | 0;
        var x = Math.imul(seed ^ seed >>> 15, 1 | seed);
        x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x;
        return ((x ^ x >>> 14) >>> 0) / 4294967296;
      }
      function armU(tt) { return Math.min(0.95, 0.05 * Math.exp(2.95 * tt)); }

      function glowSprite(color, size, midStop) {
        var c = document.createElement('canvas');
        c.width = c.height = size;
        var g = c.getContext('2d');
        var grad = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
        grad.addColorStop(0, color + 'e8');
        grad.addColorStop(midStop || 0.28, color + '55');
        grad.addColorStop(1, color + '00');
        g.fillStyle = grad;
        g.fillRect(0, 0, size, size);
        return c;
      }

      var TYPES = {
        project:  { color: '#ff6079', halo: glowSprite('#ff6079', 96, 0.22) },
        server:   { color: '#ff64a6', halo: glowSprite('#ff64a6', 64) },
        agent:    { color: '#ff4052', halo: glowSprite('#ff4052', 64) },
        boundary: { color: '#f5b642', halo: glowSprite('#f5b642', 64) },
        artifact: { color: '#7df3c4', halo: glowSprite('#7df3c4', 64) }
      };
      var goldHalo = glowSprite('#ffd27d', 64);
      var coreHalo = glowSprite('#ffe2b8', 256, 0.18);
      var nebulas = [
        { c: glowSprite('#6a48e0', 256, 0.34), k: 1.35, sx: 0.24, sy: 0.58, ph: 0.0, a: 0.32 },
        { c: glowSprite('#2b62d9', 256, 0.34), k: 1.10, sx: 0.84, sy: 0.80, ph: 2.1, a: 0.28 },
        { c: glowSprite('#b3487d', 256, 0.34), k: 0.85, sx: 0.58, sy: 0.22, ph: 4.2, a: 0.18 }
      ];

      var nodes = [];
      [['project', 6, 4.6, 6.6], ['server', 9, 2.3, 3.3], ['agent', 9, 2.2, 3.0],
       ['boundary', 9, 2.5, 3.5], ['artifact', 15, 2.0, 3.2]].forEach(function (def) {
        for (var i = 0; i < def[1]; i++) {
          var u, th;
          if (rand() < 0.7) {
            var tt = 0.1 + rand() * 0.82;
            th = (rand() < 0.5 ? 0 : Math.PI) + tt * ARM_TWIST + (rand() - 0.5) * 0.6;
            u = armU(tt) * (1 + (rand() - 0.5) * 0.18);
          } else {
            th = rand() * TAU;
            u = 0.12 + Math.sqrt(rand()) * 0.8;
          }
          if (def[0] === 'project') u = 0.18 + (u % 0.48);
          u = Math.max(0.07, Math.min(0.95, u));
          nodes.push({ type: def[0], u: u, th: th, size: def[2] + rand() * (def[3] - def[2]),
                       live: false, ph: rand() * TAU, sp: 0.5 + rand() * 1.2 });
        }
      });
      var liveLeft = 3;
      nodes.forEach(function (n) { if (n.type === 'agent' && liveLeft > 0) { n.live = true; liveLeft--; } });

      var all = [], projects = [], artifacts = [], boundaries = [];
      nodes.forEach(function (n, i) {
        all.push(i);
        if (n.type === 'project') projects.push(i);
        if (n.type === 'artifact') artifacts.push(i);
        if (n.type === 'boundary') boundaries.push(i);
      });
      var edges = [], used = {};
      function pick(list) { return list[(rand() * list.length) | 0]; }
      function addEdge(aList, bList, kind) {
        for (var tries = 0; tries < 14; tries++) {
          var a = pick(aList), b = pick(bList);
          if (a === b || used[a + '-' + b] || used[b + '-' + a]) continue;
          used[a + '-' + b] = 1;
          edges.push({ a: a, b: b, kind: kind, ph: rand() });
          return;
        }
      }
      addEdge(projects, artifacts, 'gold');
      addEdge(projects, artifacts, 'gold');
      addEdge(projects, boundaries, 'gold');
      nodes.forEach(function (n, i) { if (n.live) addEdge([i], projects, 'live'); });
      for (var eB = 0; eB < 8; eB++) addEdge(all, all, 'blue');

      var twinkles = [];
      for (var tw = 0; tw < 26; tw++) {
        twinkles.push({ x: rand(), y: rand(), ph: rand() * TAU, sp: 0.6 + rand() * 1.8, sz: 0.5 + rand() * 1.1 });
      }

      function buildStars(count, R, mul, tint) {
        var c = document.createElement('canvas');
        c.width = c.height = Math.max(2, Math.ceil(R * 2));
        var g = c.getContext('2d');
        for (var i = 0; i < count; i++) {
          var a = rand() * TAU;
          var rr = Math.sqrt(rand()) * R;
          var x = R + Math.cos(a) * rr;
          var y = R + Math.sin(a) * rr;
          var sz = (0.4 + rand() * 1.05) * mul;
          var col = '#ccd7ff';
          if (rand() < tint) col = ['#ffd9a6', '#a9c5ff', '#ffb3ca', '#b9f4de'][(rand() * 4) | 0];
          g.globalAlpha = 0.22 + rand() * 0.6;
          g.fillStyle = col;
          g.beginPath(); g.arc(x, y, sz, 0, TAU); g.fill();
          if (rand() < 0.05) {
            g.globalAlpha = 0.12;
            g.beginPath(); g.arc(x, y, sz * 3.4, 0, TAU); g.fill();
          }
        }
        return c;
      }

      function buildDisc(R) {
        var c = document.createElement('canvas');
        c.width = c.height = Math.max(2, Math.ceil(R * 2));
        var g = c.getContext('2d');
        g.translate(R, R);
        var haze = g.createRadialGradient(0, 0, 0, 0, 0, R);
        haze.addColorStop(0, 'rgba(120, 130, 255, 0.16)');
        haze.addColorStop(0.5, 'rgba(90, 100, 220, 0.07)');
        haze.addColorStop(1, 'rgba(60, 70, 180, 0)');
        g.fillStyle = haze;
        g.beginPath(); g.arc(0, 0, R, 0, TAU); g.fill();
        for (var arm = 0; arm < 2; arm++) {
          var a0 = arm * Math.PI;
          for (var i = 0; i < 520; i++) {
            var tt = i / 520;
            var th = a0 + tt * ARM_TWIST + (rand() - 0.5) * (0.14 + 0.5 * tt);
            var u = armU(tt) * (1 + (rand() - 0.5) * 0.17);
            var x = Math.cos(th) * u * R;
            var y = Math.sin(th) * u * R;
            var warm = Math.max(0, 1 - tt * 2.1);
            var pickC = rand(), col;
            if (pickC < warm) col = '#ffdfb4';
            else if (pickC < 0.62) col = '#c7d4ff';
            else if (pickC < 0.84) col = '#9fb4ff';
            else col = '#c39bff';
            g.globalAlpha = (0.16 + rand() * 0.5) * (1 - tt * 0.42);
            g.fillStyle = col;
            g.beginPath(); g.arc(x, y, 0.5 + rand() * 1.3, 0, TAU); g.fill();
            if (i % 13 === 0) {
              g.globalAlpha = 0.05;
              g.fillStyle = tt < 0.4 ? '#ffd9a6' : '#8fa4ff';
              g.beginPath(); g.arc(x, y, 7 + rand() * 13, 0, TAU); g.fill();
            }
          }
        }
        g.globalAlpha = 1;
        var core = g.createRadialGradient(0, 0, 0, 0, 0, R * 0.34);
        core.addColorStop(0, 'rgba(255, 240, 214, 0.85)');
        core.addColorStop(0.25, 'rgba(255, 214, 150, 0.38)');
        core.addColorStop(0.6, 'rgba(200, 150, 255, 0.10)');
        core.addColorStop(1, 'rgba(160, 120, 255, 0)');
        g.fillStyle = core;
        g.beginPath(); g.arc(0, 0, R * 0.34, 0, TAU); g.fill();
        return c;
      }

      var W = 0, H = 0, DPR = 1, sceneR = 120, discR = 140, starR = 300;
      var disc = null, starsFar = null, starsMid = null, starsNear = null, vignette = null;
      function rebuild() {
        var rect = preview.getBoundingClientRect();
        W = Math.max(80, rect.width);
        H = Math.max(80, rect.height);
        DPR = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(W * DPR);
        canvas.height = Math.round(H * DPR);
        sceneR = Math.max(90, Math.min((H * 0.5 - 26) / SQ, W * 0.5 - 34));
        discR = sceneR * 1.18;
        starR = Math.hypot(W, H) / 2 + 30;
        seed = 987654321;
        disc = buildDisc(discR);
        starsFar = buildStars(170, starR, 0.85, 0.16);
        starsMid = buildStars(120, starR, 1.1, 0.2);
        starsNear = buildStars(70, starR, 1.5, 0.25);
        vignette = document.createElement('canvas');
        vignette.width = Math.max(2, Math.round(W / 2));
        vignette.height = Math.max(2, Math.round(H / 2));
        var vg = vignette.getContext('2d');
        var grad = vg.createRadialGradient(
          vignette.width / 2, vignette.height * 0.48, Math.min(vignette.width, vignette.height) * 0.2,
          vignette.width / 2, vignette.height * 0.48, Math.max(vignette.width, vignette.height) * 0.72);
        grad.addColorStop(0, 'rgba(2, 3, 14, 0)');
        grad.addColorStop(1, 'rgba(1, 2, 10, 0.55)');
        vg.fillStyle = grad;
        vg.fillRect(0, 0, vignette.width, vignette.height);
      }

      function drawLayer(img, R, rot, sqz, alpha, cx, cy, zoom) {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.scale(zoom, zoom * sqz);
        ctx.rotate(rot);
        ctx.globalAlpha = alpha;
        ctx.drawImage(img, -R, -R);
        ctx.restore();
      }

      var px = [], py = [];
      var meteor = null, nextMeteor = 2.5;
      var rafId = 0, running = false, inView = true, motionOff = false;

      function draw(t) {
        if (!disc) return;
        ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#020310';
        ctx.fillRect(0, 0, W, H);

        var cx = W / 2 + Math.sin(t * 0.10) * W * 0.021;
        var cy = H * 0.52 + Math.cos(t * 0.084) * H * 0.02;
        var zoom = 1 + Math.sin(t * 0.047) * 0.022;
        var drot = t * 0.03;

        ctx.globalCompositeOperation = 'lighter';
        for (var nI = 0; nI < nebulas.length; nI++) {
          var nb = nebulas[nI];
          var nw = Math.min(W, H) * nb.k;
          var nx = W * nb.sx + Math.sin(t * 0.05 + nb.ph) * W * 0.04;
          var ny = H * nb.sy + Math.cos(t * 0.041 + nb.ph) * H * 0.05;
          ctx.globalAlpha = nb.a;
          ctx.drawImage(nb.c, nx - nw / 2, ny - nw / 2, nw, nw);
        }
        ctx.globalCompositeOperation = 'source-over';

        drawLayer(starsFar, starR, t * 0.006, 1.0, 0.7, cx, cy, zoom * 0.97);
        drawLayer(starsMid, starR, t * 0.011, 0.9, 0.85, cx, cy, zoom);
        drawLayer(starsNear, starR, t * 0.02, 0.78, 1, cx, cy, zoom * 1.03);
        drawLayer(disc, discR, drot, SQ, 1, cx, cy, zoom);

        ctx.globalCompositeOperation = 'lighter';
        var coreW = sceneR * (0.72 + 0.05 * Math.sin(t * 0.8));
        ctx.globalAlpha = 0.5;
        ctx.drawImage(coreHalo, cx - coreW / 2, cy - coreW * SQ / 2, coreW, coreW * SQ);
        ctx.globalCompositeOperation = 'source-over';

        var i, nd;
        var R = sceneR * zoom;
        for (i = 0; i < nodes.length; i++) {
          nd = nodes[i];
          var thN = nd.th + drot;
          px[i] = cx + Math.cos(thN) * nd.u * R;
          py[i] = cy + Math.sin(thN) * nd.u * R * SQ;
        }

        ctx.lineCap = 'round';
        var eI, ed, x1, y1, x2, y2, qx, qy;
        for (eI = 0; eI < edges.length; eI++) {
          ed = edges[eI];
          x1 = px[ed.a]; y1 = py[ed.a]; x2 = px[ed.b]; y2 = py[ed.b];
          qx = cx + ((x1 + x2) / 2 - cx) * 0.6;
          qy = cy + ((y1 + y2) / 2 - cy) * 0.6;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.quadraticCurveTo(qx, qy, x2, y2);
          if (ed.kind === 'gold') {
            ctx.strokeStyle = 'rgba(255, 205, 120, 0.4)';
            ctx.lineWidth = 1.4;
          } else if (ed.kind === 'live') {
            ctx.strokeStyle = 'rgba(255, 74, 92, ' + (0.3 + 0.18 * Math.sin(t * 2.4 + ed.ph * 6)).toFixed(3) + ')';
            ctx.lineWidth = 1.3;
          } else {
            ctx.strokeStyle = 'rgba(120, 160, 255, 0.2)';
            ctx.lineWidth = 1;
          }
          ctx.stroke();
        }

        ctx.globalCompositeOperation = 'lighter';
        for (eI = 0; eI < edges.length; eI++) {
          ed = edges[eI];
          if (ed.kind !== 'gold') continue;
          x1 = px[ed.a]; y1 = py[ed.a]; x2 = px[ed.b]; y2 = py[ed.b];
          qx = cx + ((x1 + x2) / 2 - cx) * 0.6;
          qy = cy + ((y1 + y2) / 2 - cy) * 0.6;
          var u0 = (t * 0.13 + ed.ph) % 1;
          for (var k = 0; k < 6; k++) {
            var uu = u0 - k * 0.022;
            if (uu < 0) continue;
            var iv = 1 - uu;
            var bx = iv * iv * x1 + 2 * iv * uu * qx + uu * uu * x2;
            var by = iv * iv * y1 + 2 * iv * uu * qy + uu * uu * y2;
            if (k === 0) {
              ctx.globalAlpha = 0.9;
              ctx.drawImage(goldHalo, bx - 10, by - 10, 20, 20);
            }
            ctx.globalAlpha = 0.85 * (1 - k / 6);
            ctx.fillStyle = '#ffe3ae';
            ctx.beginPath(); ctx.arc(bx, by, Math.max(0.4, 1.8 - k * 0.22), 0, TAU); ctx.fill();
          }
        }
        ctx.globalCompositeOperation = 'source-over';

        for (i = 0; i < nodes.length; i++) {
          nd = nodes[i];
          var spec = TYPES[nd.type];
          var x = px[i], y = py[i];
          var sz = nd.size * (0.82 + 0.18 * Math.sin(t * nd.sp + nd.ph));
          var haloW = sz * (nd.type === 'project' ? 9 : 6.5);
          ctx.globalAlpha = nd.type === 'project' ? 0.85 : 0.55;
          ctx.drawImage(spec.halo, x - haloW / 2, y - haloW / 2, haloW, haloW);
          if (nd.type === 'project' || nd.type === 'boundary') {
            ctx.globalAlpha = 0.6;
            ctx.strokeStyle = spec.color;
            ctx.lineWidth = 1;
            var spikeR = sz * 2.6;
            ctx.beginPath();
            ctx.moveTo(x - spikeR, y); ctx.lineTo(x + spikeR, y);
            ctx.moveTo(x, y - spikeR); ctx.lineTo(x, y + spikeR);
            ctx.stroke();
          }
          ctx.globalAlpha = 1;
          ctx.fillStyle = spec.color;
          ctx.beginPath(); ctx.arc(x, y, sz, 0, TAU); ctx.fill();
          ctx.globalAlpha = 0.95;
          ctx.fillStyle = '#fff7f2';
          ctx.beginPath(); ctx.arc(x, y, Math.max(0.6, sz * 0.38), 0, TAU); ctx.fill();
          if (nd.live) {
            ctx.strokeStyle = '#ff4052';
            ctx.lineWidth = 1.4;
            for (var pr = 0; pr < 2; pr++) {
              var pp = (t / 2.2 + nd.ph + pr * 0.5) % 1;
              ctx.globalAlpha = (1 - pp) * 0.5;
              ctx.beginPath(); ctx.arc(x, y, sz + 2 + pp * 24, 0, TAU); ctx.stroke();
            }
          }
        }

        for (i = 0; i < twinkles.length; i++) {
          var twk = twinkles[i];
          ctx.globalAlpha = 0.18 + 0.4 * (0.5 + 0.5 * Math.sin(t * twk.sp + twk.ph));
          ctx.fillStyle = '#e6edff';
          ctx.beginPath(); ctx.arc(twk.x * W, twk.y * H, twk.sz, 0, TAU); ctx.fill();
        }

        if (!meteor && t > nextMeteor) {
          meteor = { x: W * (0.15 + rand() * 0.6), y: H * (0.05 + rand() * 0.25),
                     dx: 0.55 + rand() * 0.4, dy: 0.45 + rand() * 0.35,
                     v: 210 + rand() * 140, born: t, life: 0.9 + rand() * 0.5 };
          var mm = Math.hypot(meteor.dx, meteor.dy);
          meteor.dx /= mm; meteor.dy /= mm;
          if (rand() < 0.5) { meteor.dx = -meteor.dx; meteor.x = W - meteor.x; }
        }
        if (meteor) {
          var age = t - meteor.born;
          if (age > meteor.life) {
            meteor = null;
            nextMeteor = t + 4 + rand() * 6;
          } else {
            var fade = 1 - age / meteor.life;
            var hx = meteor.x + meteor.dx * meteor.v * age;
            var hy = meteor.y + meteor.dy * meteor.v * age;
            for (var mk = 0; mk < 9; mk++) {
              var back = mk * 6;
              ctx.globalAlpha = fade * (1 - mk / 9) * 0.8;
              ctx.fillStyle = mk === 0 ? '#ffffff' : '#cfe0ff';
              ctx.beginPath();
              ctx.arc(hx - meteor.dx * back, hy - meteor.dy * back, Math.max(0.4, 1.9 - mk * 0.18), 0, TAU);
              ctx.fill();
            }
          }
        }

        ctx.globalAlpha = 1;
        ctx.drawImage(vignette, 0, 0, W, H);
      }

      function frame(now) {
        rafId = requestAnimationFrame(frame);
        draw(now / 1000);
      }

      function start() {
        if (running || motionOff) return;
        running = true;
        rafId = requestAnimationFrame(frame);
      }
      function stop() {
        running = false;
        cancelAnimationFrame(rafId);
      }

      /* Paint the first frame synchronously, then swap the static SVG out in the
         same task so no blank canvas ever flashes on slow devices/networks. */
      rebuild();
      draw(0);
      preview.classList.add('canvas-on');

      /* Runtime reduced-motion switch: stop the loop and free the offscreen
         sprites when it turns on; rebuild and resume when it turns off. */
      var motionMq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
      function onMotionChange() {
        if (motionMq.matches) {
          motionOff = true;
          stop();
          preview.classList.remove('canvas-on');
          disc = starsFar = starsMid = starsNear = vignette = null;
        } else {
          motionOff = false;
          rebuild();
          draw(0);
          preview.classList.add('canvas-on');
          if (inView && !document.hidden) start();
        }
      }
      if (motionMq) {
        if (motionMq.addEventListener) motionMq.addEventListener('change', onMotionChange);
        else if (motionMq.addListener) motionMq.addListener(onMotionChange);
      }

      function onResize() {
        if (motionOff) return;
        rebuild();
        if (!running) draw(0);
      }
      if (window.ResizeObserver) {
        new ResizeObserver(onResize).observe(preview);
      } else {
        window.addEventListener('resize', onResize);
      }
      document.addEventListener('visibilitychange', function () {
        if (document.hidden) stop(); else if (inView) start();
      });
      if (window.IntersectionObserver) {
        new IntersectionObserver(function (entries) {
          inView = entries[0].isIntersecting;
          if (inView && !document.hidden) start(); else stop();
        }, { threshold: 0.02 }).observe(preview);
      }
      start();
    });
  }

  function openModal(src) {
    if (!modal || !frame) return;
    lastFocus = document.activeElement;
    frame.src = demoUrl(src);
    modal.classList.add('open');
    modal.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
    if (close) close.focus();
  }

  function closeModal() {
    if (!modal || !frame) return;
    modal.classList.remove('open');
    modal.setAttribute('hidden', '');
    frame.src = 'about:blank';
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.querySelectorAll('[data-lang-choice]').forEach(function (btn) {
    btn.addEventListener('click', function () { applyLang(btn.getAttribute('data-lang-choice')); });
  });

  document.querySelectorAll('[data-demo-src]').forEach(function (card) {
    card.addEventListener('click', function (event) {
      if (event.target.closest('a, button')) return;
      openModal(card.getAttribute('data-demo-src') || 'demo/');
    });
    card.addEventListener('keydown', function (event) {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      openModal(card.getAttribute('data-demo-src') || 'demo/');
    });
  });

  document.querySelectorAll('[data-expand-galaxy]').forEach(function (button) {
    button.addEventListener('click', function () {
      var card = button.closest('[data-demo-src]');
      openModal(button.getAttribute('data-demo-src') || (card ? card.getAttribute('data-demo-src') : 'demo/'));
    });
  });

  if (modal) modal.addEventListener('click', function (event) { if (event.target === modal) closeModal(); });
  if (close) close.addEventListener('click', closeModal);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modal && modal.classList.contains('open')) closeModal();
  });

  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var text = button.getAttribute('data-copy') || '';
      var old = button.textContent;
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = t('copied');
        setTimeout(function () { button.textContent = old; }, 1200);
      } catch (err) {
        button.textContent = t('copyFailed');
        setTimeout(function () { button.textContent = old; }, 1200);
      }
    });
  });
  applyLang(lang);
  startMiniGalaxy();
  hydrateMiniPreview();
}());
"""



def graph_meta():
    if GRAPH.exists():
        with GRAPH.open("r", encoding="utf-8") as f:
            meta = json.load(f).get("meta", {})
        return {
            "nodes": meta.get("node_count", 0),
            "edges": meta.get("edge_count", 0),
            "projects": len(meta.get("projects", [])),
            "machines": len(meta.get("machines", [])),
        }
    return {"nodes": 125, "edges": 445, "projects": 6, "machines": 5}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def modal_markup(prefix: str) -> str:
    return f"""
<div class="modal" data-galaxy-modal hidden>
  <div class="modal-panel" role="dialog" aria-modal="true" aria-label="Expanded synthetic galaxy demo">
    <div class="modal-head">
      <strong>Agent Memory Galaxy</strong>
      <span class="muted" data-i18n="modalMuted">Synthetic demo. Drag, zoom, filter, and inspect nodes.</span>
      <a class="btn" href="{prefix}demo/?style=cosmos" data-demo-link data-i18n="openFullDemo">Open full demo</a>
      <button class="modal-close" type="button" data-modal-close data-i18n="close">Close</button>
    </div>
    <iframe title="Expanded Agent Memory Galaxy synthetic demo" src="about:blank"></iframe>
  </div>
</div>
"""



MINI_PREVIEW_NODES = [
    (0, "project", 384, 252, 12),
    (1, "project", 505, 178, 10),
    (2, "server", 232, 180, 8),
    (3, "server", 586, 338, 8),
    (4, "agent", 330, 354, 7),
    (5, "agent", 468, 302, 7),
    (6, "boundary", 190, 342, 9),
    (7, "artifact", 632, 220, 9),
]
MINI_PREVIEW_LINKS = [
    (0, 1, "warm"),
    (0, 2, ""),
    (0, 4, "live"),
    (0, 5, "live"),
    (1, 7, "secure"),
    (2, 6, "secure"),
    (3, 5, ""),
    (4, 6, "warm"),
    (5, 7, "secure"),
    (1, 3, ""),
]
MINI_DUST = [(120,130,1.4),(152,398,1.1),(286,114,1.2),(368,422,1.4),(430,126,1.1),(690,150,1.5),(706,386,1.1),(88,276,1.0),(548,92,1.0),(610,420,1.2),(254,444,1.0),(742,264,1.2)]


def mini_preview_markup(stats: dict) -> str:
    nodes_by_id = {idx: (kind, x, y, r) for idx, kind, x, y, r in MINI_PREVIEW_NODES}
    dust = "\n".join(f'<circle class="mini-dust" cx="{x}" cy="{y}" r="{r}" />' for x, y, r in MINI_DUST)
    links = []
    for source, target, tone in MINI_PREVIEW_LINKS:
        _, x1, y1, _ = nodes_by_id[source]
        _, x2, y2, _ = nodes_by_id[target]
        cls = f"mini-edge {tone}".strip()
        links.append(f'<line class="{cls}" data-mini-edge data-pair="{source}-{target}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />')
    node_markup = []
    for idx, kind, x, y, r in MINI_PREVIEW_NODES:
        spike = ""
        if kind in {"project", "boundary"}:
            spike = f'<path class="spike" d="M {-r*2.2:.1f} 0 H {r*2.2:.1f} M 0 {-r*2.2:.1f} V {r*2.2:.1f} M {-r*1.55:.1f} {-r*1.55:.1f} L {r*1.55:.1f} {r*1.55:.1f} M {-r*1.55:.1f} {r*1.55:.1f} L {r*1.55:.1f} {-r*1.55:.1f}" />'
        elif kind in {"server", "agent", "artifact"}:
            spike = f'<path class="spike" d="M {-r*1.7:.1f} 0 H {r*1.7:.1f} M 0 {-r*1.7:.1f} V {r*1.7:.1f}" />'
        node_markup.append(f"""<g class="mini-star {kind}" data-mini-node data-index="{idx}" transform="translate({x} {y})">
        <circle class="halo" r="{r * 3}" fill="currentColor" />
        {spike}
        <circle class="core" r="{r}" />
        <circle class="lock" r="{r + 8}" />
      </g>""")
    return f"""
  <div class="mini-galaxy-preview" data-mini-preview aria-hidden="true">
    <canvas class="mini-canvas" data-mini-canvas></canvas>
    <svg class="mini-map" viewBox="0 0 800 520" preserveAspectRatio="xMidYMid meet">
      <defs>
        <filter id="mini-glow" x="-120%" y="-120%" width="340%" height="340%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="mini-soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="8" /></filter>
      </defs>
      <ellipse class="mini-orbit gold" cx="400" cy="260" rx="244" ry="126" />
      <ellipse class="mini-orbit" cx="400" cy="260" rx="310" ry="166" transform="rotate(-17 400 260)" />
      <path class="mini-coreline" d="M 148 332 C 248 198 350 154 472 204 S 620 356 704 210" />
      <g class="mini-dust-layer">{dust}</g>
      <g class="mini-links">{"".join(links)}</g>
      <path class="mini-scan" d="M 146 394 C 264 222 406 146 570 206 C 650 236 702 286 724 342" />
      <g class="mini-nodes">{"".join(node_markup)}</g>
    </svg>
    <div class="mini-side"><b data-i18n="miniSideTitle">NODE TYPES</b><span data-mini-type="project" data-i18n="miniProject">Project</span><span data-mini-type="server" data-i18n="miniServer">Server</span><span data-mini-type="agent" data-i18n="miniAgent">Agent</span><span data-mini-type="boundary" data-i18n="miniBoundary">Boundary</span><span data-mini-type="artifact" data-i18n="miniArtifact">Artifact</span></div>
    <div class="mini-readout"><b data-i18n="miniReadoutTitle">ONLINE HUD</b><span data-i18n="miniReadout">multi-server handoff / live agents / encrypted boundary</span></div>
  </div>"""


def galaxy_card(prefix: str, stats: dict, compact: bool = False, element_id: str = "preview") -> str:
    demo = f"{prefix}demo/?style=cosmos"
    compact_class = " compact" if compact else ""
    return f"""
<div class="galaxy-card{compact_class}" id="{element_id}" data-demo-src="{demo}" role="button" tabindex="0" aria-label="Expand the interactive synthetic Agent Memory Galaxy demo">
  <div class="framebar">
    <span class="lights"><i></i><i></i><i></i></span>
    <span class="mono" data-i18n="previewTitle">synthetic graph preview</span>
    <span class="status mono" data-preview-status data-nodes="{stats['nodes']}" data-edges="{stats['edges']}" data-machines="{stats['machines']}">{stats['nodes']} nodes / {stats['edges']} links / {stats['machines']} machines</span>
  </div>
{mini_preview_markup(stats)}
  <p class="preview-note" data-i18n="previewNote">Compressed public preview. Open the full demo for search, filters, zoom, and readouts.</p>
  <button class="expand-galaxy" type="button" data-expand-galaxy data-i18n="expandGalaxy">Expand galaxy</button>
</div>
"""


def nav(prefix: str, compare_href: str) -> str:
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a class="brand" href="{prefix}index.html">Agent Memory Galaxy</a>
    <div class="nav-links">
      <a href="{compare_href}" data-i18n="navConcepts">Design archive</a>
      <a href="#preview" data-i18n="navDemo">Demo</a>
      <a href="#privacy" data-i18n="navPrivacy">Privacy</a>
      <a href="#install" data-i18n="navInstall">Install</a>
      <a href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
      <div class="lang-switch" aria-label="Language">
        <button type="button" data-lang-choice="en">EN</button>
        <button type="button" data-lang-choice="zh">中文</button>
      </div>
    </div>
  </div>
</nav>
"""


def concept_html(concept: dict, stats: dict) -> str:
    prefix = "../"
    title = esc(concept["name"])
    proof = "\n".join(f'<span class="pill">{esc(item)}</span>' for item in concept["proof"])
    tiles = "\n".join(
        f'<article class="tile"><h3>{esc(name)}</h3><p>{esc(body)}</p></article>'
        for name, body in concept["sections"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Agent Memory Galaxy marketing concept: {title}.">
<title>{title} | Agent Memory Galaxy</title>
<link rel="stylesheet" href="../assets/landing.css">
</head>
<body class="{esc(concept['theme'])}">
{nav(prefix, "index.html")}
<main class="page">
  <section class="hero">
    <div class="hero-copy">
      <div class="kicker">{esc(concept['kicker'])}</div>
      <h1>{esc(concept['title'])}</h1>
      <p class="lead">{esc(concept['lead'])}</p>
      <div class="actions">
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="../demo/?style=cosmos">{esc(concept['primary'])}</button>
        <a class="btn" href="#install">{esc(concept['secondary'])}</a>
        <a class="btn" href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
      </div>
      <div class="proof-row">{proof}</div>
    </div>
{galaxy_card(prefix, stats)}
  </section>

  <section class="section">
    <div class="section-head">
      <h2>{esc(concept['name'])}</h2>
      <p>{esc(concept['best'])}</p>
    </div>
    <div class="grid">{tiles}</div>
  </section>

  <section class="section">
    <div class="section-head">
      <h2 data-i18n="workflowHeading">Collect, distill, merge, encrypt, view.</h2>
      <p>Each page keeps the same product story and changes only the visual system, so you can compare style without losing the core message.</p>
    </div>
    <div class="pipeline">
      <div class="step"><b>01</b><span>Collect</span><p>Scan memory notes, safe session metadata, fragments, and presence.</p></div>
      <div class="step"><b>02</b><span>Distill</span><p>Extract structured facts without publishing raw conversation text.</p></div>
      <div class="step"><b>03</b><span>Merge</span><p>Connect shared projects, files, models, datasets, and tools.</p></div>
      <div class="step"><b>04</b><span>Encrypt</span><p>Publish ciphertext only when deploying a public viewer.</p></div>
      <div class="step"><b>05</b><span>Explore</span><p>Search, filter, zoom, and click through the memory galaxy.</p></div>
    </div>
  </section>

  <section class="section" id="privacy">
    <div class="section-head">
      <h2 data-i18n="privacyHeading">Public framework. Private memory.</h2>
      <p>Public pages use fictional graph data. Real fragments, presence files, graph.json, and standalone.html belong in a private hub or local machine.</p>
    </div>
    <div class="grid">
      <article class="tile"><h3>Public repo</h3><p>Code, docs, plugin packaging, and synthetic demo graph.</p></article>
      <article class="tile"><h3>Private hub</h3><p>Real fragments, presence, graph.json, and local standalone viewer.</p></article>
      <article class="tile"><h3>Encrypted Pages</h3><p>Optional docs/galaxy viewer shell plus graph.enc.json only.</p></article>
    </div>
  </section>

  <section class="section" id="install">
    <div class="section-head">
      <h2>Install as a skill.</h2>
      <p>Same two-message flow as a Claude Code plugin marketplace skill, with a direct CLI fallback for local use.</p>
    </div>
    <div class="install-grid">
      <article class="tile">
        <h3>Claude Code skill</h3>
        <pre class="code"><code>/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy</code></pre>
        <button class="copy-btn" type="button" data-copy="/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy"><span data-i18n="copyMarketplace">Copy marketplace command</span></button>
        <pre class="code"><code>/plugin install agent-memory-galaxy@agent-memory-galaxy</code></pre>
        <button class="copy-btn" type="button" data-copy="/plugin install agent-memory-galaxy@agent-memory-galaxy"><span data-i18n="copyInstall">Copy install command</span></button>
      </article>
      <article class="tile">
        <h3>Local CLI</h3>
        <pre class="code"><code>git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
./contribute.sh workstation-a codex ~/projects</code></pre>
        <button class="copy-btn" type="button" data-copy="git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git&#10;cd agent-memory-galaxy&#10;./contribute.sh workstation-a codex ~/projects">Copy CLI example</button>
      </article>
    </div>
  </section>
</main>
<footer class="footer"><div class="page"><span>Agent Memory Galaxy</span><span data-i18n="footerPrivacy">Synthetic demo public. Real memory private.</span></div></footer>
{modal_markup(prefix)}
<script src="../assets/landing.js"></script>
</body>
</html>
"""


def gallery_html(prefix: str, concept_prefix: str, stats: dict, out_title: str) -> str:
    cards = []
    colors = {
        "theme-product": ["#f7f9fc", "#2f6fed", "#00a6b2"],
        "theme-graphite": ["#050506", "#8fa6ff", "#48b98c"],
        "theme-lab": ["#f5efe5", "#245e8f", "#b34b3e"],
        "theme-bento": ["#090a0c", "#f2b84b", "#5ed6b3"],
        "theme-orbit": ["#050608", "#f4b860", "#7aa2ff"],
    }
    for concept in CONCEPTS_DATA:
        href = f"{concept_prefix}{concept['slug']}.html"
        swatches = "".join(f'<i style="background:{c}"></i>' for c in colors[concept["theme"]])
        cards.append(
            f'<a class="concept-card" href="{href}">'
            f'<div><h2>{esc(concept["name"])}</h2><p>{esc(concept["best"])}</p></div>'
            f'<div class="swatch">{swatches}</div></a>'
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Agent Memory Galaxy marketing concept gallery.">
<title>{esc(out_title)} | Agent Memory Galaxy</title>
<link rel="stylesheet" href="{prefix}assets/landing.css">
</head>
<body class="theme-bento">
{nav(prefix, f"{concept_prefix}index.html")}
<main class="page">
  <section class="compare-hero">
    <div class="kicker">STYLE EXPLORATION</div>
    <h1>Five launch-page directions for Agent Memory Galaxy.</h1>
    <p class="lead">Each concept keeps the same public-safe product story: installable skill, synthetic live demo, private memory boundary, and an expandable interactive galaxy preview.</p>
    <div class="actions">
      <a class="btn primary" href="{concept_prefix}bento-proof.html">Open recommended concept</a>
      <button class="btn" type="button" data-expand-galaxy data-demo-src="{prefix}demo/?style=cosmos">Expand synthetic galaxy</button>
      <a class="btn" href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
    </div>
    <div class="proof-row">
      <span class="pill">{stats['nodes']} synthetic nodes</span>
      <span class="pill">{stats['edges']} synthetic links</span>
      <span class="pill">{stats['projects']} fictional projects</span>
      <span class="pill">{stats['machines']} fictional machines</span>
    </div>
  </section>
{galaxy_card(prefix, stats, compact=True)}
  <section class="section">
    <div class="section-head">
      <h2>Pick visually, then refine.</h2>
      <p>This mirrors the frontend-slides workflow: show concrete alternatives first, then converge after you react to what you see.</p>
    </div>
    <div class="concept-list">{''.join(cards)}</div>
  </section>
</main>
<footer class="footer"><div class="page"><span>Agent Memory Galaxy concepts</span><span>Generated static pages. No frontend build step.</span></div></footer>
{modal_markup(prefix)}
<script src="{prefix}assets/landing.js"></script>
</body>
</html>
"""


def landing_html(stats: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Agent Memory Galaxy turns scattered AI-agent work traces into a private, inspectable memory graph.">
<title>Agent Memory Galaxy</title>
<link rel="stylesheet" href="assets/landing.css">
</head>
<body class="theme-bento">
{nav("", "concepts/index.html")}
<main class="page">
  <section class="hero landing-hero">
    <div class="hero-copy">
      <div class="kicker" data-i18n="heroKicker">PUBLIC FRAMEWORK / PRIVATE MEMORY</div>
      <h1 data-i18n="heroTitle">Your agents remember together. Privately.</h1>
      <p class="lead" data-i18n="heroLead">Turn scattered agent traces across machines into one private, inspectable memory graph. Collect reviewed notes, safe session metadata, machine fragments, and live presence, then explore the result in a static Galaxy Viewer.</p>
      <div class="actions">
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos" data-i18n="openDemo">Open synthetic demo</button>
        <a class="btn" href="#install" data-i18n="installSkill">Install as skill</a>
        <a class="btn" href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
      </div>
      <div class="hero-stat-grid">
        <div class="hero-stat"><b>{stats['nodes']}</b><span data-i18n="syntheticNodes">synthetic nodes</span></div>
        <div class="hero-stat"><b>{stats['edges']}</b><span data-i18n="syntheticLinks">synthetic links</span></div>
        <div class="hero-stat"><b>{stats['projects']}</b><span data-i18n="fictionalProjects">fictional projects</span></div>
        <div class="hero-stat"><b>{stats['machines']}</b><span data-i18n="fictionalMachines">fictional machines</span></div>
      </div>
    </div>
{galaxy_card("", stats, element_id="hero-demo")}
  </section>

  <section class="section" id="preview">
    <div class="section-head">
      <h2 data-i18n="previewHeading">Live synthetic demo. No real memory.</h2>
      <p data-i18n="previewBody">The public graph demonstrates multi-server collaboration, currently-working agents, project inheritance, shared assets, and private/public/encrypted boundaries using fictional labels only.</p>
    </div>
    <div class="grid">
      <article class="tile"><div class="mini-label" data-i18n="searchLabel">Search</div><h3 data-i18n="searchTitle">Find a project or artifact</h3><p data-i18n="searchBody">Search across projects, agents, files, models, servers, and derived facts.</p></article>
      <article class="tile"><div class="mini-label" data-i18n="filterLabel">Filter</div><h3 data-i18n="filterTitle">Focus by machine or activity</h3><p data-i18n="filterBody">Switch from the full graph to one machine, one project, recent work, or live doing state.</p></article>
      <article class="tile"><div class="mini-label" data-i18n="inspectLabel">Inspect</div><h3 data-i18n="inspectTitle">Click through evidence</h3><p data-i18n="inspectBody">Open a node readout, inspect neighbors, and follow inheritance or publishing edges.</p></article>
    </div>
  </section>

  <section class="section" id="install">
    <div class="section-head">
      <h2 data-i18n="installHeading">Install in two Claude Code messages.</h2>
      <p data-i18n="installBody">The public repository carries a Claude Code plugin/skill package. Use it to set up private hubs, connect contributors, aggregate fragments, publish encrypted viewers, or review privacy before release.</p>
    </div>
    <div class="install-grid">
      <article class="tile command-stack">
        <h3 data-i18n="pluginInstall">Plugin/skill install</h3>
        <pre class="code"><code>/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy</code></pre>
        <button class="copy-btn" type="button" data-copy="/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy"><span data-i18n="copyMarketplace">Copy marketplace command</span></button>
        <pre class="code"><code>/plugin install agent-memory-galaxy@agent-memory-galaxy</code></pre>
        <button class="copy-btn" type="button" data-copy="/plugin install agent-memory-galaxy@agent-memory-galaxy"><span data-i18n="copyInstall">Copy install command</span></button>
      </article>
      <article class="tile command-stack">
        <h3 data-i18n="localDemo">Local demo fallback</h3>
        <pre class="code"><code>git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
python3 scripts/build-public-demo.py
python3 -m http.server 8765 --directory docs</code></pre>
        <button class="copy-btn" type="button" data-copy="git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git&#10;cd agent-memory-galaxy&#10;python3 scripts/build-public-demo.py&#10;python3 -m http.server 8765 --directory docs"><span data-i18n="copyDemo">Copy demo commands</span></button>
      </article>
    </div>
  </section>

  <section class="section" id="workflow">
    <div class="section-head">
      <h2 data-i18n="workflowHeading">Collect, distill, merge, encrypt, view.</h2>
      <p data-i18n="workflowBody">Contributor machines write private fragments. An aggregator merges shared entities, injects live presence, and optionally publishes an encrypted viewer shell.</p>
    </div>
    <div class="pipeline">
      <div class="step"><b>01</b><span data-i18n="stepCollect">Collect</span><p data-i18n="stepCollectBody">Scan reviewed `agent_memory.md` notes from explicit project roots.</p></div>
      <div class="step"><b>02</b><span data-i18n="stepDistill">Distill</span><p data-i18n="stepDistillBody">Extract safe structured metadata from agent sessions without copying raw text.</p></div>
      <div class="step"><b>03</b><span data-i18n="stepMerge">Merge</span><p data-i18n="stepMergeBody">Connect projects through shared files, datasets, models, tools, and servers.</p></div>
      <div class="step"><b>04</b><span data-i18n="stepEncrypt">Encrypt</span><p data-i18n="stepEncryptBody">Publish ciphertext only when deploying an encrypted viewer shell to Pages.</p></div>
      <div class="step"><b>05</b><span data-i18n="stepView">View</span><p data-i18n="stepViewBody">Search, filter, zoom, and inspect the resulting memory galaxy.</p></div>
    </div>
  </section>

  <section class="section" id="privacy">
    <div class="section-head">
      <h2 data-i18n="privacyHeading">Public framework. Private memory.</h2>
      <p data-i18n="privacyBody">GitHub Pages is not private access control. Public pages carry the framework and fake demo data. Real fragments and plaintext graphs belong in a private hub or local machine.</p>
    </div>
    <div class="callout-band">
      <article class="tile"><h3 data-i18n="contributor">Contributor</h3><p data-i18n="contributorBody">Writes `fragments/&lt;machine&gt;.json` in a private hub. Does not need encryption passwords and should not touch `docs/galaxy/`.</p></article>
      <article class="tile"><h3 data-i18n="aggregator">Aggregator</h3><p data-i18n="aggregatorBody">Merges all fragments, builds local `standalone.html`, and optionally creates `docs/galaxy/graph.enc.json` with strong passwords.</p></article>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <h2 data-i18n="urlHeading">Know which URL you are sharing.</h2>
      <p data-i18n="urlBody">The marketing site, synthetic demo, and optional encrypted runtime viewer are separate paths.</p>
    </div>
    <div class="domain-scroll">
      <table class="domain-table">
        <thead><tr><th data-i18n="path">Path</th><th data-i18n="purpose">Purpose</th><th data-i18n="dataPolicy">Data policy</th></tr></thead>
        <tbody>
          <tr><td><code>/agent-memory-galaxy/</code></td><td data-i18n="urlPromo">Public promo landing</td><td data-i18n="urlNoReal">No real data</td></tr>
          <tr><td><code>/agent-memory-galaxy/demo/</code></td><td data-i18n="urlDemo">Synthetic interactive demo</td><td data-i18n="urlFake">Fake graph only</td></tr>
          <tr><td><code>/agent-memory-galaxy/concepts/</code></td><td data-i18n="urlConcepts">Design exploration archive</td><td data-i18n="urlSecondary">Public, secondary</td></tr>
          <tr><td><code>/agent-memory-galaxy/galaxy/</code></td><td data-i18n="urlGalaxy">Optional encrypted viewer shell</td><td data-i18n="urlCipher">Public shell, ciphertext only</td></tr>
          <tr><td><code>standalone.html</code></td><td data-i18n="urlStandalone">Local plaintext viewer</td><td data-i18n="urlLocal">Local only, gitignored</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</main>
<footer class="footer"><div class="page"><span>Agent Memory Galaxy</span><span data-i18n="footerPrivacy">Synthetic demo public. Real memory private.</span></div></footer>
{modal_markup("")}
<script src="assets/landing.js"></script>
</body>
</html>
"""


def main():
    stats = graph_meta()
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "landing.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (ASSETS / "landing.js").write_text(JS.strip() + "\n", encoding="utf-8")
    (DOCS / "index.html").write_text(landing_html(stats), encoding="utf-8")
    (CONCEPTS / "index.html").write_text(
        gallery_html("../", "", stats, "Concept Gallery"), encoding="utf-8"
    )
    for concept in CONCEPTS_DATA:
        (CONCEPTS / f"{concept['slug']}.html").write_text(concept_html(concept, stats), encoding="utf-8")
    print(f"wrote {DOCS / 'index.html'}")
    print(f"wrote {CONCEPTS}")
    print(f"wrote {ASSETS}")


if __name__ == "__main__":
    main()
