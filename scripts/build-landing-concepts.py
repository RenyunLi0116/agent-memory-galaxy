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
  .actions { display: grid; grid-template-columns: 1fr 1fr; }
  .actions > :first-child { grid-column: 1 / -1; }
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

CSS += r"""
/* === Landing v2: contrast-impact launch (docs/index.html only; concepts untouched) === */
.landing-v2 .hero-intro { padding: 56px 0 4px; }
.landing-v2 .hero-intro h1 {
  max-width: 1060px;
  margin: 16px 0 18px;
  font-size: clamp(46px, 6.6vw, 94px);
  line-height: .96;
}
.landing-v2 h1, .landing-v2 h2 { text-wrap: balance; }
.landing-v2 .hero-intro .lead { max-width: 840px; font-size: 19px; }
.landing-v2 .hero-intro .hero-def {
  max-width: 860px;
  color: var(--text);
  font-size: 20px;
  font-weight: 650;
  line-height: 1.55;
}
.landing-v2 .hero-intro .hero-scene {
  max-width: 720px;
  margin-top: 12px;
  font-size: 16.5px;
}
.landing-v2 .demo-note {
  margin: 10px 0 0;
  color: var(--muted);
  font: 500 12.5px/1.5 "JetBrains Mono", "Cascadia Code", monospace;
}
.hero-spec {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px 20px;
  margin-top: 26px;
}
.hero-spec .spec-num {
  color: var(--accent);
  font: 800 16px/1.5 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .02em;
  white-space: nowrap;
}
.hero-spec .spec-privacy {
  color: var(--muted);
  font: 600 12.5px/1.6 "JetBrains Mono", "Cascadia Code", monospace;
}

/* zh typography: no orphan glyphs in display text, no shouting latin in zh labels */
html[lang="zh-CN"] h1, html[lang="zh-CN"] h2, html[lang="zh-CN"] h3,
html[lang="zh-CN"] .hero-def, html[lang="zh-CN"] .evidence-lead,
html[lang="zh-CN"] .aud-lead { word-break: keep-all; line-break: strict; }
/* zh body text: keep-all avoids single-glyph orphans / mid-word breaks
   (verified: no CJK run here exceeds the narrowest 390px container). */
html[lang="zh-CN"] .hero-scene, html[lang="zh-CN"] .section-head p,
html[lang="zh-CN"] .pillar-how, html[lang="zh-CN"] .aud-list li,
html[lang="zh-CN"] .privacy-team, html[lang="zh-CN"] .gh-body,
html[lang="zh-CN"] .tl-item p, html[lang="zh-CN"] .stat-honest,
html[lang="zh-CN"] .contrast-caption,
html[lang="zh-CN"] .mini-readout span { word-break: keep-all; line-break: strict; }
html[lang="zh-CN"] .kicker,
html[lang="zh-CN"] .contrast-tag,
html[lang="zh-CN"] .mini-label,
html[lang="zh-CN"] .tl-step { text-transform: none; }

/* horizontal-scroll hint: edge fade appears only while more code hides off-screen */
.code {
  background:
    linear-gradient(90deg, var(--code-bg) 45%, transparent) 0 0 / 48px 100% no-repeat,
    linear-gradient(270deg, var(--code-bg) 45%, transparent) 100% 0 / 48px 100% no-repeat,
    radial-gradient(farthest-side at 0 50%, rgba(226, 232, 255, .26), transparent) 0 0 / 16px 100% no-repeat,
    radial-gradient(farthest-side at 100% 50%, rgba(226, 232, 255, .26), transparent) 100% 0 / 16px 100% no-repeat,
    var(--code-bg);
  background-attachment: local, local, scroll, scroll;
}

.contrast { padding: 40px 0 14px; }
.contrast-grid {
  display: grid;
  grid-template-columns: minmax(0, .86fr) 44px minmax(0, 1.14fr);
  gap: 14px;
  align-items: stretch;
}
.contrast-side { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.contrast-tag {
  display: flex; align-items: center; gap: 10px;
  color: #878d97;
  font: 800 11px/1.3 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .1em;
  text-transform: uppercase;
}
.contrast-tag::before {
  content: ""; width: 9px; height: 9px; border-radius: 50%;
  background: #62666e; flex: none;
}
.contrast-tag.gold { color: var(--accent); }
.contrast-tag.gold::before { background: var(--accent); box-shadow: 0 0 12px rgba(242, 184, 75, .85); }
.contrast-tag em {
  font-style: normal; font-weight: 650; letter-spacing: .02em; text-transform: none;
  border: 1px solid var(--line); border-radius: 999px; padding: 2px 9px;
  color: var(--muted); font-size: 10.5px; white-space: nowrap;
}
.contrast-caption { margin: 0; color: var(--muted); font-size: 13.5px; line-height: 1.55; max-width: 62ch; }
.contrast-arrow {
  display: flex; align-items: center; justify-content: center;
  color: var(--accent); font-size: 38px; font-weight: 800;
  text-shadow: 0 0 20px rgba(242, 184, 75, .7);
}
.contrast-grid .galaxy-still { flex: 1; height: auto; min-height: 420px; }

.chaos-board {
  position: relative; flex: 1; min-height: 420px; overflow: hidden;
  border: 1px dashed rgba(255, 255, 255, .17);
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, .028) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 255, 255, .028) 1px, transparent 1px),
    radial-gradient(circle at 50% 36%, #101114 0%, #0a0b0d 74%);
  background-size: 34px 34px, 34px 34px, 100% 100%;
  box-shadow: inset 0 0 80px rgba(0, 0, 0, .55);
}
.chaos-lines { position: absolute; inset: 0; width: 100%; height: 100%; }
.chaos-lines path {
  fill: none; stroke: rgba(255, 255, 255, .15); stroke-width: 1.3;
  stroke-dasharray: 5 9; stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.chaos-chip {
  position: absolute; z-index: 2;
  transform: rotate(var(--rot, 0deg));
  border: 1px solid rgba(255, 255, 255, .15);
  border-radius: 6px; padding: 5px 9px 5px 8px;
  background: #131417; color: #989ea7;
  font: 600 11px/1.3 "JetBrains Mono", "Cascadia Code", monospace;
  white-space: nowrap;
  box-shadow: 0 8px 18px rgba(0, 0, 0, .45);
}
.chaos-chip::before {
  content: ""; display: inline-block; width: 7px; height: 7px;
  border-radius: 50%; background: #53575e; margin-right: 7px;
}
.chaos-term {
  position: absolute; z-index: 1;
  transform: rotate(var(--rot, 0deg));
  border: 1px solid rgba(255, 255, 255, .12); border-radius: 7px;
  background: #0b0c0e; overflow: hidden;
  box-shadow: 0 14px 30px rgba(0, 0, 0, .5);
}
.chaos-term b {
  display: block; padding: 6px 10px;
  background: #15161a; color: #767c86;
  font: 700 10px/1.4 "JetBrains Mono", "Cascadia Code", monospace;
  border-bottom: 1px solid rgba(255, 255, 255, .07);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.chaos-term b::before {
  content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: #3e424a; box-shadow: 10px 0 0 #3e424a, 20px 0 0 #3e424a;
  margin-right: 28px;
}
.chaos-term code {
  display: block; padding: 4px 12px; color: #7c828b; font-size: 12.5px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.chaos-term code:last-child { padding-bottom: 10px; }
.chaos-term code.q { color: #dfe4ec; font-size: 15px; font-weight: 700; }
.chaos-note {
  position: absolute; z-index: 2;
  transform: rotate(var(--rot, 0deg));
  max-width: 34%;
  background: #17150f;
  border: 1px solid rgba(242, 184, 75, .3);
  border-radius: 3px;
  padding: 8px 10px;
  color: #ac9a6d;
  font-size: 11.5px; line-height: 1.4; font-weight: 600;
  box-shadow: 0 10px 22px rgba(0, 0, 0, .45);
}
.chaos-q {
  position: absolute; z-index: 0;
  color: rgba(255, 255, 255, .12);
  font-weight: 860; font-size: 44px; line-height: 1;
  transform: rotate(var(--rot, 0deg));
}

.pain-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.pain-card {
  min-width: 0;
  border: 1px solid var(--line); border-radius: 8px; padding: 20px;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
}
.pain-num {
  display: block; margin-bottom: 12px;
  color: var(--danger);
  font: 800 11px/1 "JetBrains Mono", "Cascadia Code", monospace; letter-spacing: .12em;
}
.pain-fig {
  width: 100%; height: 116px; display: block; margin-bottom: 14px;
  border-radius: 6px; background: #0b0c10; border: 1px solid rgba(255, 255, 255, .06);
}
.pain-card h3 { margin: 0 0 8px; font-size: 19px; }
.pain-card p { margin: 0; color: var(--muted); font-size: 14.5px; }

.stat-band {
  border: 1px solid color-mix(in srgb, var(--accent) 26%, var(--line));
  border-radius: 10px;
  padding: 24px 22px 16px;
  background:
    radial-gradient(circle at 12% 0%, rgba(242, 184, 75, .09), transparent 52%),
    color-mix(in srgb, var(--surface) 94%, transparent);
}
.stat-band .mini-label { display: block; margin-bottom: 16px; }
.stat-band-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.stat-cell { min-width: 0; }
.stat-cell b { display: block; font-size: clamp(26px, 2.6vw, 38px); font-weight: 860; color: var(--accent); line-height: 1.1; }
.stat-cell span { color: var(--muted); font-size: 12.5px; }
.stat-honest { margin: 18px 0 0; padding-top: 12px; border-top: 1px dashed var(--line); color: var(--muted); font-size: 12.5px; }

.timeline { position: relative; padding-left: 40px; display: grid; gap: 30px; max-width: 880px; }
.timeline::before {
  content: ""; position: absolute; left: 9px; top: 8px; bottom: 8px; width: 2px;
  background: linear-gradient(180deg, var(--accent), rgba(242, 184, 75, .08));
}
.tl-item { position: relative; }
.tl-item::before {
  content: ""; position: absolute; left: -36px; top: 2px;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--bg); border: 3px solid var(--accent);
  box-shadow: 0 0 14px rgba(242, 184, 75, .5);
}
.tl-item.live::before { border-color: var(--danger); box-shadow: 0 0 14px rgba(240, 111, 121, .65); }
.tl-step { display: block; color: var(--accent); font: 800 11px/1.3 "JetBrains Mono", "Cascadia Code", monospace; letter-spacing: .12em; }
.tl-item.live .tl-step { color: var(--danger); }
.tl-item h3 { margin: 8px 0 6px; font-size: 21px; }
.tl-item p { margin: 0; color: var(--muted); font-size: 15px; max-width: 76ch; }

.demo-wide { margin-bottom: 26px; }

/* Evidence readout card: plain HTML, styled after the viewer's detail panel */
.evidence-row {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(0, .88fr);
  gap: 30px;
  align-items: center;
  margin-bottom: 30px;
}
.evidence-card {
  margin: 0;
  overflow: hidden;
  border: 1px solid rgba(148, 178, 255, .28);
  border-radius: 8px;
  background: linear-gradient(165deg, rgba(16, 24, 52, .92), rgba(5, 9, 24, .96));
  box-shadow: 0 18px 50px rgba(1, 4, 16, .4), inset 0 0 28px rgba(88, 128, 255, .07);
  font-family: "JetBrains Mono", "Cascadia Code", monospace;
}
.ev-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(120, 150, 255, .16);
  background: rgba(9, 15, 34, .8);
}
.ev-kind { color: #ffcf6b; font-size: 11px; font-weight: 800; letter-spacing: .1em; flex: none; }
.ev-title { color: #dbe4ff; font-size: 12.5px; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ev-fields { margin: 0; padding: 14px 16px 16px; display: grid; gap: 9px; }
.ev-field { display: grid; grid-template-columns: 84px minmax(0, 1fr); gap: 12px; }
.ev-field dt { color: #9fc0ff; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; padding-top: 2px; }
.ev-field dd { margin: 0; color: #dbe4ff; font-size: 13px; line-height: 1.55; overflow-wrap: anywhere; }
.ev-field dd.ev-ok { color: #7df3c4; }
.evidence-aside .evidence-lead { margin: 0 0 10px; font-size: clamp(22px, 2.2vw, 28px); font-weight: 800; line-height: 1.2; }
.evidence-aside .evidence-sub { margin: 0 0 18px; color: var(--muted); font-size: 15px; max-width: 46ch; }
.evidence-aside .actions { margin-top: 0; }

.privacy-team { margin: 16px 0 0; color: var(--muted); font-size: 15px; line-height: 1.6; max-width: 760px; }
.privacy-more { margin: 12px 0 0; font-size: 15px; }
.privacy-more a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
}
.privacy-more a:hover { border-bottom-color: var(--accent); }

.cta-band {
  margin: 76px 0;
  border: 1px solid color-mix(in srgb, var(--accent) 40%, var(--line));
  border-radius: 12px;
  padding: 58px 26px;
  text-align: center;
  background:
    radial-gradient(circle at 50% -10%, rgba(242, 184, 75, .16), transparent 58%),
    #0b0c10;
}
.cta-band h2 { margin: 0 0 12px; font-size: clamp(30px, 4vw, 50px); line-height: 1.02; }
.cta-band > p { margin: 0 auto; max-width: 680px; color: var(--muted); font-size: 16px; }
.cta-band .actions { justify-content: center; }

@media (max-width: 1080px) {
  .contrast-grid { grid-template-columns: 1fr; }
  .contrast-arrow { transform: rotate(90deg); min-height: 42px; }
  .stat-band-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .pain-grid { grid-template-columns: 1fr; }
  .pain-fig { height: 104px; }
  .evidence-row { grid-template-columns: 1fr; gap: 18px; }
}
@media (max-width: 760px) {
  .landing-v2 .hero-intro { padding-top: 36px; }
  .landing-v2 .hero-intro h1 { margin: 12px 0 14px; font-size: clamp(40px, 11vw, 56px); }
  .landing-v2 .hero-intro .hero-def { font-size: 17px; }
  .landing-v2 .hero-intro .hero-scene { margin-top: 10px; font-size: 15px; }
  .landing-v2 .hero-intro .actions { margin-top: 18px; }
  .hero-spec { margin-top: 16px; gap: 6px 16px; }
  .hero-spec .spec-num { white-space: normal; font-size: 14px; }
  .landing-v2 .section { padding: 36px 0; }
  .landing-v2 .section-head { gap: 12px; margin-bottom: 20px; }
  .stat-band-grid { grid-template-columns: repeat(3, 1fr); gap: 14px 10px; }
  .stat-cell b { font-size: 22px; }
  .chaos-board { min-height: 380px; }
  .contrast-grid .galaxy-still { min-height: 380px; }
  .contrast-arrow { min-height: 26px; font-size: 30px; }
  .timeline { gap: 20px; }
  .timeline { padding-left: 32px; }
  .timeline::before { left: 7px; }
  .tl-item::before { left: -28px; }
  .tl-item h3 { margin: 6px 0 4px; font-size: 19px; }
  .tile { padding: 16px; }
  .pain-card { padding: 16px; }
  .code { padding: 12px; font-size: 12px; }
  .ev-fields { padding: 12px 14px 14px; gap: 7px; }
  .cta-band { padding: 40px 16px; margin: 36px 0; }
  .footer { padding: 28px 0; }
  .nav-links > a[data-nav-install] { display: inline-flex; }
}
/* Narrow chaos board: tighter type so the two question terminals stay readable. */
@media (max-width: 600px) {
  .chaos-board { min-height: 280px; }
  .chaos-chip { font-size: 9.5px; padding: 4px 7px; }
  .chaos-term code { font-size: 11px; }
  .chaos-term code.q { font-size: 13px; }
  .chaos-q { font-size: 34px; }
  .pain-fig { display: none; }
  .contrast-grid .galaxy-still { min-height: 330px; }
}
"""

CSS += r"""
/* === Landing round-5: value-prop pillars, dual audience, GitHub callout === */
.pillars .pillar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.pillar {
  position: relative;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  padding: 22px 22px 24px;
  transition: border-color .25s ease, transform .25s ease, box-shadow .25s ease;
}
.pillar:hover {
  border-color: color-mix(in srgb, var(--accent) 48%, var(--line));
  transform: translateY(-2px);
  box-shadow: 0 16px 42px rgba(0, 0, 0, .28);
}
.pillar-ico {
  display: grid; place-items: center;
  width: 46px; height: 46px; margin-bottom: 16px;
  border-radius: 12px;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 32%, var(--line));
}
.pillar-ico svg { width: 24px; height: 24px; display: block; }
.pillar h3 { margin: 0 0 8px; font-size: 19px; line-height: 1.25; }
.pillar-how { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.58; }
.pillar-tag {
  position: absolute; top: 16px; right: 16px;
  color: var(--accent-2);
  font: 800 9.5px/1 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .09em; text-transform: uppercase;
  border: 1px solid color-mix(in srgb, var(--accent-2) 44%, var(--line));
  border-radius: 999px; padding: 5px 8px;
  background: color-mix(in srgb, var(--accent-2) 12%, transparent);
}
html[lang="zh-CN"] .pillar-tag { text-transform: none; letter-spacing: .02em; }

.audiences .audience-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.audience {
  min-width: 0;
  display: flex; flex-direction: column; gap: 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 26px 26px 24px;
  background: color-mix(in srgb, var(--surface) 92%, transparent);
}
.audience.pm {
  border-color: color-mix(in srgb, var(--accent) 26%, var(--line));
  background:
    radial-gradient(120% 90% at 100% 0%, color-mix(in srgb, var(--accent) 11%, transparent), transparent 56%),
    color-mix(in srgb, var(--surface) 92%, transparent);
}
.audience-tag {
  display: inline-flex; align-items: center; gap: 9px;
  color: var(--muted);
  font: 800 11px/1.3 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .1em; text-transform: uppercase;
}
.audience-tag::before { content: ""; width: 9px; height: 9px; border-radius: 50%; background: currentColor; flex: none; }
.audience.res .audience-tag { color: var(--accent-3); }
.audience.pm .audience-tag { color: var(--accent); }
.audience.pm .audience-tag::before { box-shadow: 0 0 12px color-mix(in srgb, var(--accent) 70%, transparent); }
html[lang="zh-CN"] .audience-tag { text-transform: none; letter-spacing: .02em; }
.audience h3 { margin: 0; font-size: 23px; line-height: 1.2; }
.aud-list { list-style: none; margin: 4px 0 0; padding: 0; display: grid; gap: 13px; }
.aud-list li {
  position: relative; padding-left: 24px;
  color: var(--muted); font-size: 14.5px; line-height: 1.55;
}
.aud-list li::before {
  content: ""; position: absolute; left: 2px; top: 7px;
  width: 8px; height: 8px; border-radius: 2px; transform: rotate(45deg);
  background: var(--accent-3);
}
.audience.pm .aud-list li::before { background: var(--accent); }
.aud-legend {
  margin-top: auto; padding-top: 16px;
  border-top: 1px dashed var(--line);
  display: flex; flex-wrap: wrap; gap: 9px 18px;
}
.aud-legend .leg { display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12.5px; }
.aud-legend .sw { flex: none; display: inline-flex; }
.aud-legend .sw.dot { width: 10px; height: 10px; border-radius: 50%; }
.aud-legend .sw.dot.red { background: var(--danger); box-shadow: 0 0 9px color-mix(in srgb, var(--danger) 70%, transparent); }
.aud-legend .sw.line { width: 22px; height: 2px; border-radius: 2px; background: var(--accent); align-self: center; }
.aud-legend .sw.users { gap: 2px; }
.aud-legend .sw.users span { width: 7px; height: 12px; border-radius: 2px; display: block; }

.gh-band {
  margin: 6px 0 4px;
  border: 1px solid color-mix(in srgb, var(--accent) 34%, var(--line));
  border-radius: 14px;
  padding: 52px 28px;
  text-align: center;
  background:
    radial-gradient(circle at 50% -20%, color-mix(in srgb, var(--accent) 16%, transparent), transparent 60%),
    color-mix(in srgb, var(--surface) 90%, transparent);
}
.gh-band h2 { margin: 0 auto; max-width: 17ch; font-size: clamp(30px, 4.6vw, 56px); line-height: 1.04; }
.gh-band .gh-body { margin: 16px auto 0; max-width: 62ch; color: var(--muted); font-size: 16px; line-height: 1.6; }
.gh-chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 24px 0 0; }
.gh-chips span {
  display: inline-flex; align-items: center;
  border: 1px solid var(--line); border-radius: 999px;
  padding: 8px 13px;
  color: var(--text);
  background: color-mix(in srgb, var(--surface) 70%, transparent);
  font: 700 12.5px/1 "JetBrains Mono", "Cascadia Code", monospace;
}
.gh-chips span::before { content: "\2715"; color: var(--danger); font-weight: 800; margin-right: 8px; }
.gh-foot {
  margin: 22px auto 0; max-width: 66ch;
  color: var(--muted);
  font: 600 12.5px/1.6 "JetBrains Mono", "Cascadia Code", monospace;
}

@media (max-width: 1080px) {
  .pillars .pillar-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 900px) {
  .audiences .audience-grid { grid-template-columns: 1fr; }
}
@media (max-width: 760px) {
  .pillars .pillar-grid { grid-template-columns: 1fr; }
  .pillar { padding: 18px; }
  .audience { padding: 20px; }
  .gh-band { padding: 38px 18px; }
  .gh-foot { font-size: 12px; }
}
"""

CSS += r"""
/* === Team monitoring console (ported from bid B) — static illustration inside the
   PM/team-lead audience column; NOT the canvas galaxy (galaxy_card stays the single
   interactive surface). Member colours match docs/demo team.json (ada/kael/mira). === */
.audience.pm .aud-lead { margin: 0; color: var(--muted); font-size: 14.5px; line-height: 1.55; }
.audience.pm .team-console { margin-top: 4px; }

.team-console {
  overflow: hidden; border-radius: 10px;
  border: 1px solid rgba(148, 178, 255, .24);
  background: linear-gradient(165deg, rgba(12, 18, 40, .94), rgba(5, 8, 20, .97));
  box-shadow: 0 24px 60px rgba(1, 4, 16, .45), inset 0 0 30px rgba(88, 128, 255, .06);
  font-family: "JetBrains Mono", "Cascadia Code", monospace;
}
.tc-bar {
  display: flex; align-items: center; flex-wrap: wrap; gap: 4px 10px;
  min-height: 37px; padding: 7px 12px;
  border-bottom: 1px solid rgba(120, 150, 255, .16);
  background: rgba(7, 11, 26, .85); color: #cdd8ff; font-size: 11.5px;
}
.tc-bar .lights { display: inline-flex; gap: 6px; flex: none; }
.tc-bar .lights i { width: 9px; height: 9px; border-radius: 50%; background: #2f3652; }
.tc-title { font-weight: 700; color: #dbe4ff; white-space: nowrap; }
.tc-status { margin-left: auto; color: #8ea6e8; white-space: nowrap; }
.tc-body { padding: 13px 13px 14px; }
.tc-filter { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 12px; }
.tc-chip {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid rgba(150, 175, 255, .2); border-radius: 999px;
  padding: 4px 10px; color: #b9c6ee; font-size: 11.5px; background: rgba(20, 28, 54, .55);
}
.tc-chip.active { border-color: rgba(242, 184, 75, .6); color: #ffe6b0; background: rgba(242, 184, 75, .1); }
.tc-chip i { width: 8px; height: 8px; border-radius: 50%; background: var(--u, #8ea6e8); flex: none; }
.tc-rows { display: grid; gap: 7px; }
.tc-row {
  display: grid; grid-template-columns: 11px minmax(0, 1fr) auto; gap: 11px; align-items: center;
  padding: 9px 11px; border: 1px solid rgba(120, 150, 255, .12); border-radius: 7px;
  background: rgba(12, 18, 40, .5);
}
.tc-row .u {
  width: 10px; height: 10px; border-radius: 50%; flex: none;
  background: var(--u, #8ea6e8);
  box-shadow: 0 0 8px color-mix(in srgb, var(--u, #8ea6e8) 70%, transparent);
}
.tc-main { min-width: 0; }
.tc-main .n { color: #e6ecff; font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tc-main .d { color: #8fa0cc; font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tc-st { font-size: 10.5px; letter-spacing: .05em; color: #7f8fbc; white-space: nowrap; }
.tc-row.live { border-color: rgba(240, 111, 121, .38); background: rgba(30, 16, 24, .45); }
.tc-row.live .tc-st { color: #ff9199; }
.tc-row.live .tc-st::before {
  content: ""; display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background: var(--danger); margin-right: 6px; vertical-align: baseline;
  box-shadow: 0 0 8px rgba(240, 111, 121, .85);
  animation: tcPulse 1.9s ease-in-out infinite;
}
@keyframes tcPulse { 0%, 100% { opacity: 1; } 50% { opacity: .32; } }
.tc-legend {
  margin-top: 12px; padding-top: 10px; border-top: 1px dashed rgba(120, 150, 255, .16);
  display: flex; flex-wrap: wrap; gap: 8px 16px; color: #8291bd; font-size: 11px;
}
.tc-legend span { display: inline-flex; align-items: center; gap: 6px; }
.tc-legend b { color: #b9c6ee; font-weight: 600; }
.tc-legend i.lg { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.tc-legend i.lg.red { background: var(--danger); box-shadow: 0 0 7px rgba(240, 111, 121, .7); }
.tc-legend i.lg.gold { background: var(--accent); box-shadow: 0 0 7px rgba(242, 184, 75, .7); }
.tc-legend i.lg.user { background: conic-gradient(#7dd3fc, #f0abfc, #fde68a, #7dd3fc); }
.tc-demo { margin: 10px 0 0; color: #6f7ba6; font-size: 10.5px; }
.audience.pm .tc-bridge { margin: 12px 2px 0; color: var(--muted); font-size: 13px; line-height: 1.55; }

@media (prefers-reduced-motion: reduce) {
  .tc-row.live .tc-st::before { animation: none; }
}
@media (max-width: 760px) {
  .tc-status { font-size: 10.5px; }
  .tc-row { grid-template-columns: 11px minmax(0, 1fr) auto; gap: 9px; }
}
"""

CSS += r"""
/* === Round-6 V2: demo-first hero (interactive galaxy in the fold) + in-place reveal ===
   The one interactive galaxy_card moves into the hero so the demo is the first thing on
   screen, immediately interactive, with no blocking splash. On load it does a single
   in-place "unveil" (galaxy settles first, copy staggers in). The before/after keeps its
   punch via a decorative, non-interactive .galaxy-still twin. */
.landing-v2 .hero-intro.hero-split {
  display: grid;
  grid-template-columns: minmax(0, 0.94fr) minmax(430px, 1.06fr);
  gap: 44px;
  align-items: center;
  min-height: calc(100vh - 58px);
  padding: 40px 0 30px;
}
.hero-split .hero-copy { min-width: 0; }
.landing-v2 .hero-split h1 { font-size: clamp(40px, 4.7vw, 72px); margin: 14px 0 16px; }
.landing-v2 .hero-split .hero-def { max-width: 42ch; font-size: 18.5px; }
.landing-v2 .hero-split .hero-scene { max-width: 46ch; margin-top: 12px; font-size: 15.5px; }
.landing-v2 .hero-split .hero-spec { margin-top: 22px; }

.hero-split .hero-stage {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stage-frame { position: relative; width: 100%; min-width: 0; }
.stage-frame .galaxy-card { height: clamp(380px, 42vw, 560px); }
.stage-hint {
  position: absolute;
  left: 0; right: 0; bottom: -26px;
  text-align: center;
  color: var(--muted);
  font: 600 12px/1.4 "JetBrains Mono", "Cascadia Code", monospace;
  pointer-events: none;
}

/* === Round-7: cinematic FLIP intro — galaxy shrinks + flies into the demo slot ==
   A one-time opening. The DEMO galaxy (the inert galaxy_still — no canvas, no data
   hooks, no role=button) fades in BIG and centered on a deep-space veil, holds, then
   SHRINKS and FLIES (a runtime FLIP transform the head script measures against the
   live hero galaxy_card) precisely onto that card's slot, where it crossfades into
   the real interactive card. The veil background dissolves as it flies so the settled
   hero arrives underneath —打开页面像电影一样先展示 demo 银河，随后它淡化+缩小+平移落到 demo 卡槽位.
   The overlay is the still, so the single interactive-galaxy rule holds. Base (no
   html.intro-cine) = no overlay + settled hero: no-JS, reduced-motion, repeat visits
   and ?intro=skip all get the finished hero with zero motion, nothing ever covering
   it. Orchestration + FLIP math + safety timers live in the head script, so content
   is never permanently covered even if landing.js never loads or throws. */

/* Skip: high-contrast gold pill, top-right, rendered from the first frame. */
.intro-skip {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 90;
  display: none;
  align-items: center;
  gap: 8px;
  border: 1.5px solid var(--accent);
  border-radius: 999px;
  padding: 9px 18px;
  background: color-mix(in srgb, #05060f 76%, transparent);
  color: #ffdd94;
  font: 800 12.5px/1 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .04em;
  cursor: pointer;
  backdrop-filter: blur(8px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, .5), 0 0 20px color-mix(in srgb, var(--accent) 42%, transparent);
}
.intro-skip::before {
  content: "";
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 10px var(--accent);
}
.intro-skip:hover {
  color: #fff;
  border-color: #ffdd94;
  box-shadow: 0 8px 30px rgba(0, 0, 0, .5), 0 0 28px color-mix(in srgb, var(--accent) 62%, transparent);
}
html.intro-cine .intro-skip { display: inline-flex; }

/* Deep-space veil. The opaque background lives on ::before so it can dissolve
   without fading the flying galaxy that sits above it. Shown only under
   html.intro-cine; the gate class rides on <html>, so a bare `.intro-cine{display:none}`
   would blank the page — hence the veil carries its own class. */
.intro-veil {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: none;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.intro-veil::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 1;
  background:
    radial-gradient(ellipse at 24% 28%, rgba(104, 66, 222, .30), transparent 55%),
    radial-gradient(ellipse at 78% 72%, rgba(40, 92, 214, .26), transparent 58%),
    radial-gradient(ellipse at 52% 46%, rgba(255, 196, 128, .08), transparent 44%),
    radial-gradient(circle at 50% 46%, #0a102e 0%, #05071c 55%, #01020a 100%);
  transition: opacity 1.5s ease;
}
html.intro-cine .intro-veil { display: flex; }
/* Veil dissolves as the galaxy begins to fly, so the settled hero arrives beneath it. */
html.intro-flying .intro-veil::before,
html.intro-landed .intro-veil::before { opacity: 0; }

/* Keep the settled page hidden while the veil is up, then reveal it the instant the
   galaxy starts flying. visibility (not display) preserves layout so the head script
   can measure the live card's real rect while it is still hidden. */
html.intro-cine body > :not(.intro-veil) { visibility: hidden; }
html.intro-cine.intro-flying body > :not(.intro-veil) { visibility: visible; }
/* The one interactive card stays hidden until the flown galaxy lands on its slot and
   crossfades in — so exactly one galaxy is ever on screen. */
html.intro-cine #after-galaxy { visibility: hidden; }
html.intro-cine.intro-landed #after-galaxy { visibility: visible; }

.cine-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  width: min(760px, 82vw);
}
.cine-galaxy {
  width: 100%;
  container-type: inline-size;
  transform-origin: 50% 50%;
  will-change: transform, opacity;
}
/* Cinematic fade-in of the big centered galaxy. fill: backwards ONLY — it must not
   hold forwards or it would out-rank the inline FLIP transform the head script sets
   for the fly; once it ends the element rests at its base (transform none) — the "hold". */
html.intro-cine .cine-galaxy { animation: cineShowGalaxy 1s cubic-bezier(.2, .65, .2, 1) backwards; }
.cine-galaxy .galaxy-still { box-shadow: 0 30px 90px rgba(0, 0, 0, .5), 0 0 60px rgba(96, 128, 255, .14); }
.cine-caption { position: relative; z-index: 1; text-align: center; }
html.intro-cine .cine-caption { animation: cineShowCap 1.1s ease backwards; }
html.intro-flying .cine-caption,
html.intro-landed .cine-caption { opacity: 0; transition: opacity .5s ease; }
.cine-brand {
  display: block;
  color: var(--accent);
  font: 800 11px/1.2 "JetBrains Mono", "Cascadia Code", monospace;
  letter-spacing: .42em;
  text-indent: .42em;
  margin-bottom: 8px;
  opacity: .92;
}
.cine-tagline {
  display: block;
  color: #eaf0ff;
  font-size: clamp(18px, 2.6vw, 26px);
  font-weight: 600;
  letter-spacing: .01em;
}

@keyframes cineShowGalaxy {
  0%   { opacity: 0; transform: scale(.9); }
  100% { opacity: 1; transform: none; }
}
@keyframes cineShowCap {
  0%   { opacity: 0; transform: translateY(10px); }
  32%  { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Decorative before/after still: mirrors the galaxy_card frame but is inert. */
.galaxy-still {
  position: relative;
  width: 100%;
  flex: 1;
  min-width: 0;
  min-height: 420px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #060814;
  box-shadow: 0 22px 70px rgba(0, 0, 0, .24);
}
.contrast-actions { margin-top: 4px; }

@media (prefers-reduced-motion: reduce) {
  /* Honesty + a11y: never play the intro for reduced-motion visitors. Base state is the
     settled hero, so this is a belt-and-braces guard on top of the head script never
     adding intro-cine — it hides the veil and forces every hidden element back to
     visible even if the gate class somehow lands. */
  html.intro-cine .intro-veil { display: none !important; }
  html.intro-cine body > :not(.intro-veil) { visibility: visible !important; }
  html.intro-cine #after-galaxy { visibility: visible !important; }
  .intro-skip { display: none !important; }
}

/* Mobile: single column, galaxy pulled up right under the definition so the demo (or at
   least the "Open the demo" CTA beside it) is in the phone's first screen. */
@media (max-width: 900px) {
  .landing-v2 .hero-intro.hero-split {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    min-height: auto;
    gap: 14px;
    padding: 32px 0 20px;
  }
  .hero-split .hero-copy { display: contents; }
  .hero-split .kicker     { order: 1; }
  .hero-split h1          { order: 2; }
  .hero-split .hero-def   { order: 3; }
  .hero-split .hero-stage { order: 4; margin: 2px 0 20px; }
  .hero-split .actions    { order: 5; }
  .hero-split .demo-note  { order: 6; }
  .hero-split .hero-spec  { order: 7; }
  .hero-split .hero-scene { order: 8; }
  .stage-frame .galaxy-card { height: clamp(320px, 76vw, 400px); }
  .landing-v2 .hero-split .hero-def { max-width: none; }
  .landing-v2 .hero-split .hero-scene { max-width: none; }
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
      previewTitle: 'demo graph preview', previewNote: 'Compressed preview. Open the full demo for search, filters, zoom, and node details.',
      expandGalaxy: 'Expand galaxy', miniSideTitle: 'NODE TYPES', miniProject: 'Project', miniServer: 'Server', miniAgent: 'Agent', miniBoundary: 'Boundary', miniArtifact: 'Artifact', miniReadoutTitle: 'PRESENCE LAYER', miniReadout: 'multi-user hub / agent status / encrypted boundary',
      modalMuted: 'Demo galaxy. Drag, zoom, filter, and inspect nodes.', openFullDemo: 'Open full demo', close: 'Close', copied: 'Copied', copyFailed: 'Copy failed',
      status: function (n, e, m) { return n + ' nodes / ' + e + ' links / ' + m + ' machines'; },
      heroKicker: 'FOR RESEARCHERS AND TEAMS RUNNING MANY AGENTS', heroTitle: 'Which agent did that?',
      heroDef: 'See what every teammate’s agents shipped today: a Claude Code skill that merges every machine’s agent_memory.md into one private, searchable map — a single static HTML page.',
      heroLead: 'Claude on your laptop, a trainer on the GPU node, Codex on CI. By 11 pm none of them knows what the others did.',
      openDemo: 'Open the demo', installSkill: 'Install as skill',
      demoNote: 'Demo uses fictional data.',
      heroSpec: '0 daemons · 1 static HTML file · 2 commands',
      heroSpecPrivacy: 'Private by default — publishing ships ciphertext only.',
      previewHeading: 'Search, filter, click through evidence.', previewBody: 'The demo runs the same viewer as the real thing — search, filters, and node details, in your browser.',
      searchLabel: 'Search', searchTitle: 'Find a project or artifact', searchBody: 'Search across projects, agents, files, models, servers, and derived facts.',
      filterLabel: 'Filter', filterTitle: 'Focus by machine or activity', filterBody: 'Switch from the full graph to one machine, one project, recent work, or what agents are doing right now.',
      inspectLabel: 'Inspect', inspectTitle: 'Click through evidence', inspectBody: 'Open a node’s detail panel, inspect neighbors, and follow inheritance or publishing edges.',
      evWho: 'who', evWhen: 'when', evMachine: 'machine', evFiles: 'files', evWhy: 'why', evStatus: 'status',
      evidenceCaption: 'This is what evidence looks like.',
      evidenceCaptionSub: 'Click any node in the demo and a panel like this opens — who, when, on which machine, which files, and why.',
      installHeading: 'Install with two Claude Code commands.', installBody: 'The repo ships a Claude Code plugin. The skill sets up a private hub, pulls in each machine, merges their memory into one graph, and runs a privacy review before anything is published.',
      pluginInstall: 'Plugin/skill install', copyMarketplace: 'Copy marketplace command', copyInstall: 'Copy install command', localDemo: 'Try the demo locally', copyDemo: 'Copy demo commands',
      workflowHeading: 'Collect, distill, merge, encrypt, view.',
      privacyHeading: 'Public framework. Private memory.', privacyBody: 'Working solo, your agent_memory.md and fragments never leave your machine — nothing phones home. GitHub Pages carries only the open framework and this demo.',
      privacyTeam: 'On a team, distilled fragments — safe session metadata, never raw conversations — sync as plaintext inside your private GitHub repo, readable only by the collaborators you add. The only thing that ever leaves that repo is a public Pages deploy, and that ships AES-256-GCM ciphertext, unlocked in the browser.',
      privacyMore: 'Full privacy model, roles, and URL map — see the README.',
      footerPrivacy: 'Demo data fictional. Real memory private.',
      skipIntro: 'Skip intro', cineTag: 'One galaxy. Every agent.', stageHint: 'Interactive demo — drag, zoom, click a node.', stillTitle: 'one graph, settled',
      beforeTag: 'WITHOUT SHARED MEMORY', afterTag: 'WITH AGENT MEMORY GALAXY',
      beforeCaption: 'Five machines, zero shared context. Every window remembers a different slice of the day, and it all evaporates when the terminal closes.',
      afterCaption: 'One day of work across five machines, resolved into one graph — the same interactive map you can open at the top of the page.',
      chaosNote1: 'who changed dataloader.py?', chaosNote4: 'was this fix already merged?',
      whyHeading: 'Why teams pick it', whyBody: 'One private graph of everything your agents remember — built to be trusted, cheap to run, and readable at a glance by the whole team.',
      p1Title: 'Your whole team’s memory, one graph', p1How: 'Every teammate’s machines push fragments into one private hub; filter and color by user to see who did what, on which machine.', p1Badge: 'New this week',
      p2Title: 'Plaintext stays local or in your private hub', p2How: 'Plaintext lives on your machines, or in a private repo only your collaborators can read; only a public Pages deploy is encrypted — client-side AES-256-GCM with PBKDF2 and a dual password, and nothing phones home.',
      p3Title: 'Works with the coding agents you already run', p3How: 'Native today for Claude Code, Codex, and Cursor. agent_memory.md is plain markdown, so any tool that writes it joins the graph too.',
      p4Title: 'The memory layer barely adds tokens', p4How: 'The graph is built by zero-dependency Python — heuristics by default, LLM optional and off. Indexing your agents’ work doesn’t burn tokens.',
      p5Title: 'It refreshes itself and lights up live work', p5How: 'A cron job rebuilds the graph on a schedule; auto-presence detects working agents and pulses them red — no manual heartbeat.',
      p6Title: 'A live map for team leads', p6How: 'See who’s on which machine and project at a glance — red means working now, gold lines mean cross-project references.',
      audHeading: 'One map, two jobs.', audBody: 'The same graph answers a different question depending on who is looking at it.',
      audResTag: 'FOR RESEARCHERS', audResTitle: 'Stop losing track of your own agents',
      r1: 'Who changed what — every entry carries the agent, machine, files, and the reason, so “why did this change?” always has an answer.',
      r2: 'No duplicate afternoons — spot a fix that already landed on another machine before you chase the same bug again.',
      r3: 'Real handoff — the next session, and the next agent, start from what already happened instead of a cold terminal.',
      audPmTag: 'FOR TEAM LEADS & PM', audPmTitle: 'Monitor the whole team from one map',
      audPmLead: 'Open the page and read the whole team in seconds — who is on which machine and project, and what is live right now.',
      tcTitle: 'team-orbit · live view', tcStatus: '3 users · 5 machines · 6 projects', tcAll: 'All', tcWorking: 'working', tcIdle: 'idle',
      tcTask1: 'merging a fragment dedupe fix', tcTask2: 'sweeping a learning-rate schedule', tcTask3: 'queuing an eval run', tcTask4: 'prism cache notes, wrapped up',
      tcLegendRed: 'working now', tcLegendGold: 'shared across projects', tcLegendUser: 'colour = teammate', tcDemo: 'Illustrative demo — a sample team, not live data.',
      tcBridge: 'The live product renders this same team data as an interactive galaxy — the demo opens that map, not a list like this.',
      ghHeading: 'All you need is a GitHub account.', ghBody: 'No server to run, no database, no SaaS to sign up for — just a git repo and the Python standard library. Collaborate by adding a teammate as a GitHub collaborator and pushing.',
      ghNoServer: 'No server', ghNoDb: 'No database', ghNoSaas: 'No SaaS signup', ghNoKey: 'No API key',
      ghFoot: 'You’ll need git and python3 on the machine — most dev machines already have both.',
      statBandTitle: 'The demo graph, by the numbers', statNodes: 'nodes', statLinks: 'links', statEntries: 'memory entries', statProjects: 'projects', statMachines: 'machines', statLive: 'simulated agents active',
      statHonest: 'The numbers above come straight from the demo’s graph.json. Every project, machine, agent, and file in it is fictional — no real memory is published here.',
      howHeading: 'From scattered traces to one galaxy.', howBody: 'Plain files and static HTML — here’s how one day of agent work becomes one graph.',
      tl1Tag: 'STEP 01 · IN EVERY PROJECT', tl1Title: 'Agents write memory as they work', tl1Body: 'Each project keeps an agent_memory.md: what changed, why, and which files. Agents read it when a session starts and append after meaningful changes.',
      tl2Tag: 'STEP 02 · ON EVERY MACHINE', tl2Title: 'Each machine contributes a fragment', tl2Body: 'contribute.sh scans reviewed notes and safe session metadata — never raw conversations — into fragments/<machine>.json.',
      tl3Tag: 'STEP 03 · ON THE AGGREGATOR', tl3Title: 'One aggregator merges the graph', tl3Body: 'Shared files, datasets, models, and servers connect projects across machines. A gold reference skeleton emerges between project hubs.',
      tl4Tag: 'STEP 04 · LIVE, EVERY FEW MINUTES', tl4Title: 'Working agents light up red', tl4Body: 'Agents that are mid-task show a red pulse plus a one-line status of what they’re working on — so you and every other agent see the overlap before it happens.',
      tl5Tag: 'STEP 05 · ONLY IF YOU PUBLISH', tl5Title: 'Encryption before anything leaves', tl5Body: 'Plaintext graphs stay local or in a private hub. A public Pages deploy ships the viewer shell plus ciphertext only, unlocked client-side.',
      ctaTitle: 'Stop asking “which agent did that?”', ctaBody: 'Install the skill and point it at your projects. Tomorrow, you — and every agent — look in one place.'
    },
    zh: {
      navConcepts: '设计存档（英文）', navDemo: '演示', navPrivacy: '隐私', navInstall: '安装',
      previewTitle: '演示图谱预览', previewNote: '压缩预览。打开完整 demo 可搜索、过滤、缩放、查看节点详情。',
      expandGalaxy: '展开图谱', miniSideTitle: '节点类型', miniProject: '项目', miniServer: '机器', miniAgent: 'Agent', miniBoundary: '边界', miniArtifact: '产物', miniReadoutTitle: '存在感图层', miniReadout: '多 user 私有 hub / agent 状态 / 加密边界',
      modalMuted: '演示图谱：可拖拽、缩放、过滤，点击节点查看详情。', openFullDemo: '打开完整 demo', close: '关闭', copied: '已复制', copyFailed: '复制失败',
      status: function (n, e, m) { return n + ' 节点 / ' + e + ' 连线 / ' + m + ' 机器'; },
      heroKicker: '写给同时跑一堆 agent 的研究者和团队', heroTitle: '昨天是哪个 agent 改的？',
      heroDef: '一眼看清全队的 agent 今天都产出了什么：一个 Claude Code skill，把每台机器的 agent_memory.md 汇成一张私有、可搜索的图——就一个静态 HTML 页面。',
      heroLead: '笔记本上的 Claude、GPU 节点上的训练 agent、CI 上的 Codex。到晚上 11 点，谁也不知道别人干了什么。',
      openDemo: '打开在线演示', installSkill: '安装为 skill',
      demoNote: '演示为虚构数据。',
      heroSpec: '0 常驻进程 · 1 个静态 HTML · 2 条命令安装',
      heroSpecPrivacy: '默认私有——发布出门的只有密文。',
      previewHeading: '搜索、过滤，点开证据链。', previewBody: 'demo 用的就是真实产品的 viewer：搜索、过滤、查看节点详情，浏览器里直接跑。',
      searchLabel: '搜索', searchTitle: '查找项目或产物', searchBody: '可按项目、agent、文件、模型、服务器，以及自动提炼出的事实进行搜索。',
      filterLabel: '过滤', filterTitle: '聚焦机器或活跃状态', filterBody: '从完整图谱切到单台机器、单个项目、近期工作，或只看正在进行的任务。',
      inspectLabel: '查看', inspectTitle: '点击查看证据链', inspectBody: '打开节点详情面板，查看相邻节点，并沿继承或发布关系继续追踪。',
      evWho: '谁', evWhen: '何时', evMachine: '机器', evFiles: '文件', evWhy: '为什么', evStatus: '状态',
      evidenceCaption: '证据长这样。',
      evidenceCaptionSub: '在 demo 里点开任意节点，就会展开这样一张卡：谁、何时、在哪台机器、改了哪些文件、为什么。',
      installHeading: '敲两条命令，装进 Claude Code。', installBody: '公开仓库自带 Claude Code 插件。装好后，skill 会帮你搭私有聚合端、接入每台机器、把记忆合并成一张图，公开前还会先做隐私审查。',
      pluginInstall: 'Plugin/skill 安装', copyMarketplace: '复制 marketplace 命令', copyInstall: '复制 install 命令', localDemo: '本地先跑 demo', copyDemo: '复制 demo 命令',
      workflowHeading: '采集、提炼、合并、加密、查看。',
      privacyHeading: '公开框架，私有记忆。', privacyBody: '独自使用时，你的 agent_memory.md 和 fragments 不会离开你的机器，也没有任何联网上报；GitHub Pages 上只有公开框架和这个演示。',
      privacyTeam: '在团队里，提炼出的 fragment（只含安全的会话元数据，绝不含原始对话）会以明文形式同步进你的私有 GitHub 仓库，只有你添加的协作者能读到。真正会离开这个仓库的，只有公开的 Pages 部署，而它携带的只有 AES-256-GCM 密文，在浏览器端解锁。',
      privacyMore: '完整的隐私模型、角色分工与 URL 对照表见 README。',
      footerPrivacy: '演示数据均为虚构，真实记忆保持私有。',
      skipIntro: '跳过', cineTag: '一张银河，容纳每个 agent。', stageHint: '可交互 demo——拖拽、缩放、点击节点。', stillTitle: '一张图，已汇合',
      beforeTag: '没有共享记忆的一天', afterTag: '接入 Agent Memory Galaxy 之后',
      beforeCaption: '五台机器，零共享上下文。每个窗口只记得这一天的一个切片，终端一关就全部蒸发。',
      afterCaption: '五台机器一天的工作，汇成一张图——就是页面顶部你能打开的那张可交互地图。',
      chaosNote1: 'dataloader.py 是谁改的？', chaosNote4: '这个 fix 是不是已经改过一次了？',
      whyHeading: '团队为什么选它', whyBody: '把 agent 记住的一切汇成一张私有图——可信、省钱、一眼看懂，整个团队都能用。',
      p1Title: '全队的记忆，汇成同一张图', p1How: '每个成员的机器把 fragment 推进同一个私有 hub；可按 user 筛选、着色，看清谁在哪台机器做了什么。', p1Badge: '本周上线',
      p2Title: '明文只留在本地或你的私有 hub', p2How: '明文只留在你的机器，或只有协作者能读的私有仓库里；只有公开的 Pages 部署才加密——客户端 AES-256-GCM（PBKDF2、双密码），且没有任何联网上报。',
      p3Title: '兼容你已经在用的编码 agent', p3How: '今天已原生支持 Claude Code、Codex、Cursor。agent_memory.md 是纯 markdown，任何会写它的工具也都能进图。',
      p4Title: '这层记忆几乎不额外烧 token', p4How: '图谱由零依赖的 Python 标准库构建——默认启发式，LLM 可选且默认关闭。给 agent 的工作建索引本身不烧 token。',
      p5Title: '自动刷新，自动点亮在线工作', p5How: 'cron 定时重建图谱；auto-presence 自动检测正在工作的 agent 并亮起红色脉冲，无需手动心跳。',
      p6Title: '给负责人的一张实时地图', p6How: '一眼看清谁在哪台机器、哪个项目——红色代表正在工作，金线代表跨项目引用。',
      audHeading: '一张图，两种用法。', audBody: '同一张图，谁来看，回答的就是谁最关心的问题。',
      audResTag: '写给研究者', audResTitle: '别再跟丢自己的 agent',
      r1: '谁改了什么——每条记录都带着 agent、机器、文件和原因，「这里为什么改了」永远有答案。',
      r2: '不再重复劳动——在你追同一个 bug 之前，就能看到修复早已落在另一台机器上。',
      r3: '真正的交接——下一个会话、下一个 agent，都从已经发生的事接着做，而不是面对一个空终端。',
      audPmTag: '写给负责人 / PM', audPmTitle: '一张图俯瞰全队进展',
      audPmLead: '打开页面，几秒就能读完整个团队——谁在哪台机器、哪个项目，此刻什么正在跑。',
      tcTitle: 'team-orbit · 实时视图', tcStatus: '3 位成员 · 5 台机器 · 6 个项目', tcAll: '全部', tcWorking: '工作中', tcIdle: '空闲',
      tcTask1: '正在合并 fragment 去重的修复', tcTask2: '正在扫学习率调度', tcTask3: '排队跑一次 eval', tcTask4: 'prism cache 的笔记，已收尾',
      tcLegendRed: '正在工作', tcLegendGold: '跨项目共享', tcLegendUser: '颜色 = 成员', tcDemo: '示意 demo——示例团队，非实时数据。',
      tcBridge: '真实产品把同一份团队数据渲染成一张可交互的星图——演示打开的是那张图，而不是这样一份列表。',
      ghHeading: '有个 GitHub 账号就够了。', ghBody: '不用跑服务器、不用数据库、不用注册 SaaS——一个 git 仓库加 Python 标准库即可。协作就是把成员加为 GitHub collaborator，然后 push。',
      ghNoServer: '无需服务器', ghNoDb: '无需数据库', ghNoSaas: '无需注册 SaaS', ghNoKey: '无需 API key',
      ghFoot: '机器上要有 git 和 python3——开发机通常本来就装了。',
      statBandTitle: '演示数据规模一览', statNodes: '个节点', statLinks: '条连线', statEntries: '条记忆', statProjects: '个项目', statMachines: '台机器', statLive: '个模拟 agent 在工作',
      statHonest: '以上数字直接取自 demo 的 graph.json；里面的项目、机器、agent 和文件均为虚构，这里不发布任何真实工作记忆。',
      howHeading: '从零散痕迹，到一张星图。', howBody: '纯文件加静态 HTML——一天的 agent 工作，是这样变成一张图的。',
      tl1Tag: '步骤 01 · 在每个项目里', tl1Title: 'agent 边工作边写记忆', tl1Body: '每个项目维护一份 agent_memory.md：改了什么、为什么、涉及哪些文件。agent 在会话开始时读取，在有意义的改动后追加。',
      tl2Tag: '步骤 02 · 在每台机器上', tl2Title: '每台机器贡献一个 fragment', tl2Body: 'contribute.sh 扫描已审阅的笔记与安全会话元数据——绝不包含原始对话——写入 fragments/<machine>.json。',
      tl3Tag: '步骤 03 · 在聚合端', tl3Title: '聚合端合并成一张图', tl3Body: '共享的文件、数据集、模型和服务器把跨机器的项目连接起来，项目枢纽之间浮现出金色引用骨架。',
      tl4Tag: '步骤 04 · 实时，每隔几分钟', tl4Title: '正在工作的 agent 亮起红光', tl4Body: '正在干活的 agent 显示红色脉冲和一行『正在做什么』——你和其他 agent 都能提前看到，赶在重复劳动之前。',
      tl5Tag: '步骤 05 · 仅在发布时', tl5Title: '任何东西出门前先加密', tl5Body: '明文图谱只留在本地或私有 hub。公开的 Pages 部署只携带 viewer shell 和密文，在浏览器端解锁。',
      ctaTitle: '别再问「是哪个 agent 改的」。', ctaBody: '装上 skill，指向你的项目。明天，你和每个 agent 都只看这一个地方。'
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
  /* The cinematic intro is orchestrated entirely by the head script (self-contained,
     always completes, and already delegates the Skip click). This is a belt-and-braces
     binding so Skip still tears the overlay down even if the delegated listener is gone.
     Idempotent: __amgIntroEnd only fires once. */
  function wireIntroSkip() {
    var d = document.documentElement;
    var btn = document.querySelector('[data-intro-skip]');
    if (!btn) return;
    btn.addEventListener('click', function () {
      if (typeof d.__amgIntroEnd === 'function') d.__amgIntroEnd();
      else d.classList.remove('intro-cine');
    });
  }

  applyLang(lang);
  startMiniGalaxy();
  hydrateMiniPreview();
  wireIntroSkip();
}());
"""



def graph_meta():
    if GRAPH.exists():
        with GRAPH.open("r", encoding="utf-8") as f:
            meta = json.load(f).get("meta", {})
        type_counts = meta.get("type_counts", {})
        return {
            "nodes": meta.get("node_count", 0),
            "edges": meta.get("edge_count", 0),
            "projects": len(meta.get("projects", [])),
            "machines": len(meta.get("machines", [])),
            "entries": type_counts.get("entry", 0),
            "live": type_counts.get("liveagent", 0),
        }
    return {"nodes": 125, "edges": 445, "projects": 6, "machines": 5, "entries": 0, "live": 0}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def modal_markup(prefix: str) -> str:
    return f"""
<div class="modal" data-galaxy-modal hidden>
  <div class="modal-panel" role="dialog" aria-modal="true" aria-label="Expanded galaxy demo">
    <div class="modal-head">
      <strong>Agent Memory Galaxy</strong>
      <span class="muted" data-i18n="modalMuted">Demo galaxy. Drag, zoom, filter, and inspect nodes.</span>
      <a class="btn" href="{prefix}demo/?style=cosmos" data-demo-link data-i18n="openFullDemo">Open full demo</a>
      <button class="modal-close" type="button" data-modal-close data-i18n="close">Close</button>
    </div>
    <iframe title="Expanded Agent Memory Galaxy demo" src="about:blank"></iframe>
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


def mini_preview_markup(stats: dict, still: bool = False) -> str:
    """Star-map preview. Default = the single interactive surface (canvas + data-mini-preview,
    hydrated by landing.js into the cinematic galaxy, click opens the demo modal).
    still=True = a decorative, non-interactive CSS-only twin (no canvas, no data-mini-preview,
    no click target) used for the before/after panel once the live demo moved into the hero.
    The still reuses the hero SVG's filter defs by id, so it omits its own <defs>."""
    nodes_by_id = {idx: (kind, x, y, r) for idx, kind, x, y, r in MINI_PREVIEW_NODES}
    dust = "\n".join(f'<circle class="mini-dust" cx="{x}" cy="{y}" r="{r}" />' for x, y, r in MINI_DUST)
    links = []
    for source, target, tone in MINI_PREVIEW_LINKS:
        _, x1, y1, _ = nodes_by_id[source]
        _, x2, y2, _ = nodes_by_id[target]
        cls = f"mini-edge {tone}".strip()
        edge_attr = "" if still else " data-mini-edge"
        links.append(f'<line class="{cls}"{edge_attr} data-pair="{source}-{target}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />')
    node_markup = []
    for idx, kind, x, y, r in MINI_PREVIEW_NODES:
        spike = ""
        if kind in {"project", "boundary"}:
            spike = f'<path class="spike" d="M {-r*2.2:.1f} 0 H {r*2.2:.1f} M 0 {-r*2.2:.1f} V {r*2.2:.1f} M {-r*1.55:.1f} {-r*1.55:.1f} L {r*1.55:.1f} {r*1.55:.1f} M {-r*1.55:.1f} {r*1.55:.1f} L {r*1.55:.1f} {-r*1.55:.1f}" />'
        elif kind in {"server", "agent", "artifact"}:
            spike = f'<path class="spike" d="M {-r*1.7:.1f} 0 H {r*1.7:.1f} M 0 {-r*1.7:.1f} V {r*1.7:.1f}" />'
        node_attr = "" if still else " data-mini-node"
        node_markup.append(f"""<g class="mini-star {kind}"{node_attr} data-index="{idx}" transform="translate({x} {y})">
        <circle class="halo" r="{r * 3}" fill="currentColor" />
        {spike}
        <circle class="core" r="{r}" />
        <circle class="lock" r="{r + 8}" />
      </g>""")
    # The interactive twin owns the canvas, the data-mini-preview hook, and the shared
    # filter defs; the still is inert markup that borrows those defs from the DOM.
    canvas = "" if still else '\n    <canvas class="mini-canvas" data-mini-canvas></canvas>'
    hook = "" if still else " data-mini-preview"
    defs = "" if still else """
      <defs>
        <filter id="mini-glow" x="-120%" y="-120%" width="340%" height="340%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="mini-soft-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="8" /></filter>
      </defs>"""
    return f"""
  <div class="mini-galaxy-preview"{hook} aria-hidden="true">{canvas}
    <svg class="mini-map" viewBox="0 0 800 520" preserveAspectRatio="xMidYMid meet">{defs}
      <ellipse class="mini-orbit gold" cx="400" cy="260" rx="244" ry="126" />
      <ellipse class="mini-orbit" cx="400" cy="260" rx="310" ry="166" transform="rotate(-17 400 260)" />
      <path class="mini-coreline" d="M 148 332 C 248 198 350 154 472 204 S 620 356 704 210" />
      <g class="mini-dust-layer">{dust}</g>
      <g class="mini-links">{"".join(links)}</g>
      <path class="mini-scan" d="M 146 394 C 264 222 406 146 570 206 C 650 236 702 286 724 342" />
      <g class="mini-nodes">{"".join(node_markup)}</g>
    </svg>
    <div class="mini-side"><b data-i18n="miniSideTitle">NODE TYPES</b><span data-mini-type="project" data-i18n="miniProject">Project</span><span data-mini-type="server" data-i18n="miniServer">Server</span><span data-mini-type="agent" data-i18n="miniAgent">Agent</span><span data-mini-type="boundary" data-i18n="miniBoundary">Boundary</span><span data-mini-type="artifact" data-i18n="miniArtifact">Artifact</span></div>
    <div class="mini-readout"><b data-i18n="miniReadoutTitle">PRESENCE LAYER</b><span data-i18n="miniReadout">multi-user hub / agent status / encrypted boundary</span></div>
  </div>"""


def galaxy_card(prefix: str, stats: dict, compact: bool = False, element_id: str = "preview") -> str:
    demo = f"{prefix}demo/?style=cosmos"
    compact_class = " compact" if compact else ""
    return f"""
<div class="galaxy-card{compact_class}" id="{element_id}" data-demo-src="{demo}" role="button" tabindex="0" aria-label="Expand the interactive Agent Memory Galaxy demo">
  <div class="framebar">
    <span class="lights"><i></i><i></i><i></i></span>
    <span class="mono" data-i18n="previewTitle">demo graph preview</span>
    <span class="status mono" data-preview-status data-nodes="{stats['nodes']}" data-edges="{stats['edges']}" data-machines="{stats['machines']}">{stats['nodes']} nodes / {stats['edges']} links / {stats['machines']} machines</span>
  </div>
{mini_preview_markup(stats)}
  <p class="preview-note" data-i18n="previewNote">Compressed public preview. Open the full demo for search, filters, zoom, and readouts.</p>
  <button class="expand-galaxy" type="button" data-expand-galaxy data-i18n="expandGalaxy">Expand galaxy</button>
</div>
"""


def galaxy_still_markup(stats: dict) -> str:
    """Decorative before/after still. NOT a galaxy_card and NOT interactive: no data-demo-src,
    no role=button, no canvas, no data-mini-preview. The one interactive galaxy lives in the
    hero; this is the CSS-only 'settled graph' twin for the WITHOUT/WITH contrast."""
    return f"""
<div class="galaxy-still" aria-hidden="true">
  <div class="framebar">
    <span class="lights"><i></i><i></i><i></i></span>
    <span class="mono" data-i18n="stillTitle">one graph, settled</span>
    <span class="status mono" data-preview-status data-nodes="{stats['nodes']}" data-edges="{stats['edges']}" data-machines="{stats['machines']}">{stats['nodes']} nodes / {stats['edges']} links / {stats['machines']} machines</span>
  </div>
{mini_preview_markup(stats, still=True)}
</div>
"""


def intro_cine_markup(stats: dict) -> str:
    """Cinematic FLIP opening overlay. The demo galaxy — the inert galaxy_still (no
    canvas, no data hooks, no role=button, aria-hidden) — fades in big & center-stage on
    a deep-space veil, holds, then shrinks and flies (a runtime FLIP transform the head
    script measures against the live hero galaxy_card) onto that card's slot, crossfading
    into the real card. data-cine-galaxy is the element the head script transforms. A
    high-contrast gold Skip pill is present from the first frame. The overlay is
    display:none by default, so no-JS / reduced-motion / repeat visits / ?intro=skip never
    render it; only the head script's intro-cine class turns it on. Placed last in <body>
    so it reuses the hero galaxy_card's SVG filter defs by id (backward reference, like the
    contrast still), and adds no second interactive galaxy."""
    return f"""
<div class="intro-veil" data-intro-cine>
  <div class="cine-inner">
    <div class="cine-galaxy" data-cine-galaxy>
{galaxy_still_markup(stats)}
    </div>
    <div class="cine-caption">
      <span class="cine-brand">AGENT MEMORY GALAXY</span>
      <span class="cine-tagline" data-i18n="cineTag">One galaxy. Every agent.</span>
    </div>
  </div>
  <button class="intro-skip" type="button" data-intro-skip data-i18n="skipIntro" aria-label="Skip the intro animation">Skip intro</button>
</div>
"""


def nav(prefix: str, compare_href: str, archive: bool = True) -> str:
    archive_link = (
        f'\n      <a href="{compare_href}" data-i18n="navConcepts">Design archive</a>' if archive else ""
    )
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a class="brand" href="{prefix}index.html">Agent Memory Galaxy</a>
    <div class="nav-links">{archive_link}
      <a href="#preview" data-i18n="navDemo">Demo</a>
      <a href="#install" data-i18n="navInstall" data-nav-install>Install</a>
      <a href="#privacy" data-i18n="navPrivacy">Privacy</a>
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


CHAOS_LINE_PATHS = [
    "M 28 12 L 39 19",
    "M 36 23 L 45 30",
    "M 47 41 L 56 47",
    "M 30 57 L 39 64",
    "M 63 52 L 70 57",
    "M 20 73 L 29 80",
]

CHAOS_CHIPS = [
    ("left:4%;top:4%;--rot:-3deg", "claude · demo-laptop-b", " c1"),
    ("right:4%;top:7%;--rot:2deg", "train-loop · demo-gpu-node-c", " c2"),
    ("left:5%;top:43%;--rot:2deg", "codex · demo-workstation-a", " c3"),
    ("right:5%;top:49%;--rot:-2deg", "sweep-agent · demo-gpu-node-c", " c4"),
    ("left:5%;top:90%;--rot:2deg", "eval-runner · demo-ci-runner-d", " c5"),
]

CHAOS_TERMS = [
    ("left:8%;top:15%;width:84%;--rot:-.7deg", "demo-workstation-a",
     [(None, "$ git log --oneline -1"), ("chaosNote1", "who changed dataloader.py?")]),
    ("left:10%;top:60%;width:84%;--rot:.7deg", "demo-ci-runner-d",
     [(None, "$ ls patches/ | tail -3"), ("chaosNote4", "was this fix already merged?")]),
]

CHAOS_QMARKS = [
    "left:46%;top:4%;--rot:-8deg",
    "right:12%;top:36%;--rot:6deg",
    "left:40%;top:82%;--rot:-6deg",
]


def chaos_board_markup() -> str:
    lines = "".join(f'<path d="{d}" />' for d in CHAOS_LINE_PATHS)
    chips = "".join(
        f'<span class="chaos-chip{cls}" style="{style}">{esc(label)}</span>'
        for style, label, cls in CHAOS_CHIPS
    )
    terms = []
    for style, host, rows in CHAOS_TERMS:
        row_html = ""
        for key, text in rows:
            if key:
                row_html += f'<code class="q" data-i18n="{key}">{esc(text)}</code>'
            else:
                row_html += f"<code>{esc(text)}</code>"
        terms.append(f'<div class="chaos-term" style="{style}"><b>{esc(host)}</b>{row_html}</div>')
    qmarks = "".join(f'<span class="chaos-q" style="{style}">?</span>' for style in CHAOS_QMARKS)
    return (
        '<div class="chaos-board" aria-hidden="true">'
        f'<svg class="chaos-lines" viewBox="0 0 100 100" preserveAspectRatio="none">{lines}</svg>'
        f'{"".join(terms)}{chips}{qmarks}'
        "</div>"
    )


PAIN_FIGS = {
    1: """<svg class="pain-fig" viewBox="0 0 240 116" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <g stroke="#565b63" stroke-dasharray="4 7" fill="none" stroke-width="1.4">
    <path d="M 40 30 L 82 48" /><path d="M 202 28 L 154 47" /><path d="M 48 90 L 88 72" />
  </g>
  <circle cx="33" cy="27" r="7" fill="#767c86" /><circle cx="208" cy="25" r="7" fill="#767c86" /><circle cx="42" cy="93" r="7" fill="#767c86" />
  <rect x="98" y="32" width="46" height="54" rx="6" fill="#15171b" stroke="#3e424a" />
  <path d="M 106 44 H 136 M 106 52 H 130" stroke="#3e424a" fill="none" />
  <text x="121" y="78" fill="#f06f79" font-size="26" font-weight="800" text-anchor="middle" font-family="Inter,sans-serif">?</text>
</svg>""",
    2: """<svg class="pain-fig" viewBox="0 0 240 116" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <circle cx="34" cy="56" r="8" fill="#767c86" /><circle cx="206" cy="56" r="8" fill="#767c86" />
  <path d="M 44 56 H 90" stroke="#565b63" stroke-width="1.4" /><path d="M 196 56 H 150" stroke="#565b63" stroke-width="1.4" />
  <rect x="92" y="34" width="34" height="34" rx="5" fill="#15171b" stroke="#767c86" />
  <rect x="112" y="46" width="34" height="34" rx="5" fill="#15171b" stroke="#767c86" />
  <path d="M 100 51 L 118 51 M 100 58 L 112 58" stroke="#3e424a" fill="none" />
  <path d="M 120 63 L 138 63 M 120 70 L 132 70" stroke="#3e424a" fill="none" />
  <text x="120" y="104" fill="#f2b84b" font-size="13" font-weight="800" text-anchor="middle" font-family="JetBrains Mono,monospace">x2</text>
</svg>""",
    3: """<svg class="pain-fig" viewBox="0 0 240 116" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
  <g fill="#767c86">
    <circle cx="44" cy="34" r="5" /><circle cx="118" cy="72" r="5" /><circle cx="164" cy="30" r="5" />
    <circle cx="208" cy="72" r="5" /><circle cx="70" cy="92" r="5" />
  </g>
  <g stroke="#565b63" stroke-dasharray="3 6" fill="none">
    <circle cx="44" cy="34" r="15" /><circle cx="118" cy="72" r="15" /><circle cx="164" cy="30" r="15" />
    <circle cx="208" cy="72" r="15" /><circle cx="70" cy="92" r="15" />
  </g>
  <path d="M 60 42 L 84 56" stroke="#565b63" stroke-dasharray="3 7" fill="none" />
  <path d="M 178 38 L 194 52" stroke="#565b63" stroke-dasharray="3 7" fill="none" />
</svg>""",
}


_ICO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">')
PILLAR_ICONS = {
    # multi-user team memory as one connected graph
    "team": _ICO + '<circle cx="12" cy="12" r="2.6"/><circle cx="5" cy="5" r="1.7"/>'
            '<circle cx="19" cy="6" r="1.7"/><circle cx="6" cy="19" r="1.7"/><circle cx="18" cy="18" r="1.7"/>'
            '<path d="M6.6 6.6 10 10M17.2 7.2 14 10M7.2 17.4 10.2 14M16.8 16.8 13.8 14"/></svg>',
    # client-side encryption / privacy padlock
    "lock": _ICO + '<rect x="5" y="10.5" width="14" height="9" rx="2.2"/>'
            '<path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/><circle cx="12" cy="14.4" r="1.15"/>'
            '<path d="M12 15.4v1.8"/></svg>',
    # two source tools merging into one target — works with any coding agent
    "plug": _ICO + '<rect x="3.2" y="4" width="6" height="5.6" rx="1.4"/>'
            '<rect x="3.2" y="14.4" width="6" height="5.6" rx="1.4"/>'
            '<rect x="14.8" y="9.2" width="6" height="5.6" rx="1.4"/>'
            '<path d="M9.2 6.8H12a2 2 0 0 1 2 2v1.6h0.8M9.2 17.2H12a2 2 0 0 0 2-2v-1.6h0.8"/></svg>',
    # lightning — light, near-zero token overhead
    "bolt": _ICO + '<path d="M13 2.5 5.5 13.2H11l-1 8.3L18.5 10H13z"/></svg>',
    # circular refresh — automatic cron + presence
    "auto": _ICO + '<path d="M4.5 12a7.5 7.5 0 0 1 12.8-5.3"/><path d="M13.8 6.7H17.3V3.2"/>'
            '<path d="M19.5 12a7.5 7.5 0 0 1-12.8 5.3"/><path d="M10.2 17.3H6.7V20.8"/></svg>',
    # monitor with trend line — dashboard for team leads
    "dash": _ICO + '<rect x="3.3" y="4.4" width="17.4" height="12" rx="2.2"/>'
            '<path d="M6.6 12.2 9.4 9.4l2.4 2.4 4-4.6"/><path d="M9.2 20h5.6M12 16.4V20"/></svg>',
}


def team_console_markup() -> str:
    """Static, illustrative team-lead console (ported from bid B). NOT the canvas
    galaxy (galaxy_card stays the single interactive surface). Users/colours match
    the synthetic demo (ada/kael/mira in team.json.example and docs/demo/graph.json).
    Carries an explicit non-live / illustrative disclaimer."""
    rows = [
        ("live", "#7dd3fc", "Ada &middot; demo-workstation-a", "tcTask1", "merging a fragment dedupe fix", "tcWorking", "working"),
        ("live", "#f0abfc", "Kael &middot; demo-gpu-node-c", "tcTask2", "sweeping a learning-rate schedule", "tcWorking", "working"),
        ("live", "#fde68a", "Mira &middot; demo-ci-runner-d", "tcTask3", "queuing an eval run", "tcWorking", "working"),
        ("", "#7dd3fc", "Ada &middot; demo-laptop-b", "tcTask4", "prism cache notes, wrapped up", "tcIdle", "idle"),
    ]
    row_html = "".join(
        f'<div class="tc-row {live}" style="--u:{color}">'
        f'<span class="u"></span>'
        f'<div class="tc-main"><div class="n">{who}</div>'
        f'<div class="d" data-i18n="{task_key}">{task_txt}</div></div>'
        f'<span class="tc-st" data-i18n="{st_key}">{st_txt}</span>'
        "</div>"
        for live, color, who, task_key, task_txt, st_key, st_txt in rows
    )
    return f"""
        <div class="team-console" aria-label="Illustrative team-monitoring console with sample data">
          <div class="tc-bar">
            <span class="lights"><i></i><i></i><i></i></span>
            <span class="tc-title" data-i18n="tcTitle">team-orbit &middot; live view</span>
            <span class="tc-status" data-i18n="tcStatus">3 users &middot; 5 machines &middot; 6 projects</span>
          </div>
          <div class="tc-body">
            <div class="tc-filter" aria-hidden="true">
              <span class="tc-chip active" data-i18n="tcAll">All</span>
              <span class="tc-chip"><i style="--u:#7dd3fc"></i>Ada</span>
              <span class="tc-chip"><i style="--u:#f0abfc"></i>Kael</span>
              <span class="tc-chip"><i style="--u:#fde68a"></i>Mira</span>
            </div>
            <div class="tc-rows">{row_html}</div>
            <div class="tc-legend" aria-hidden="true">
              <span><i class="lg red"></i><b data-i18n="tcLegendRed">working now</b></span>
              <span><i class="lg gold"></i><b data-i18n="tcLegendGold">shared across projects</b></span>
              <span><i class="lg user"></i><b data-i18n="tcLegendUser">colour = teammate</b></span>
            </div>
            <p class="tc-demo" data-i18n="tcDemo">Illustrative demo &mdash; a sample team, not live data.</p>
          </div>
        </div>"""


def landing_html(stats: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Agent Memory Galaxy is a Claude Code skill that merges every machine's agent_memory.md into one private, searchable map — a single static HTML page.">
<title>Agent Memory Galaxy</title>
<link rel="stylesheet" href="assets/landing.css">
<script>
/* Cinematic FLIP intro (self-contained). Decide BEFORE first paint whether to play, so
   the settled hero never flashes under the veil. If it plays: the demo galaxy fades in
   big & centered on a deep-space veil, holds, then SHRINKS + FLIES — a runtime FLIP
   transform measured against the live hero galaxy_card — into that card's slot and
   crossfades into the real interactive card. Honest defaults: reduced-motion, repeat
   visits (sessionStorage amg_intro_cine) and ?intro=skip present the finished hero
   immediately with no overlay; ?intro=play forces it for capture/regression. Safety
   timers guarantee teardown even if anything throws, so content is never permanently
   covered. Total show+fly+land ~3.8s. */
(function () {{
  try {{
    var d = document.documentElement;
    var mq = window.matchMedia;
    var reduce = !!(mq && mq('(prefers-reduced-motion: reduce)').matches);
    var qs = location.search || '';
    var forceSkip = /[?&]intro=skip/.test(qs);
    var forcePlay = /[?&]intro=play/.test(qs);
    var played = false;
    try {{ played = sessionStorage.getItem('amg_intro_cine') === '1'; }} catch (e) {{}}
    var shouldPlay = !reduce && (forcePlay || (!played && !forceSkip));
    if (!forcePlay) {{ try {{ sessionStorage.setItem('amg_intro_cine', '1'); }} catch (e) {{}} }}

    var ended = false;
    var end = function () {{
      if (ended) return; ended = true;
      d.classList.remove('intro-cine', 'intro-flying', 'intro-landed');
    }};
    d.__amgIntroEnd = end;

    /* Skip works from the very first frame, before landing.js parses: a capturing
       delegated listener catches the click no matter when the button is inserted. */
    document.addEventListener('click', function (ev) {{
      var t = ev.target;
      if (t && t.closest && t.closest('[data-intro-skip]')) {{ ev.preventDefault(); end(); }}
    }}, true);

    if (!shouldPlay) return;

    /* Cinematic hold, then a slow eased shrink-and-fly, then a short crossfade. */
    var SHOW_MS = 1900, FLY_MS = 1600, LAND_MS = 300;

    /* FLIP: measure the big centered overlay galaxy and the live hero card at fly time
       (layout is final by SHOW_MS), then transform the overlay so its centre and width
       land exactly on the card's slot. Returns false if elements/layout aren't ready, so
       the caller can degrade gracefully (galaxy just fades without flying). */
    var applyFlip = function () {{
      var g = document.querySelector('[data-cine-galaxy]');
      var card = document.getElementById('after-galaxy');
      if (!g || !card) return false;
      g.style.animation = 'none';
      g.style.transition = 'none';
      g.style.transform = 'none';
      var src = g.getBoundingClientRect();   /* untransformed rect (reflow committed) */
      var tgt = card.getBoundingClientRect();
      if (!src.width || !tgt.width) return false;
      var s = tgt.width / src.width;
      var tx = (tgt.left + tgt.width / 2) - (src.left + src.width / 2);
      var ty = (tgt.top + tgt.height / 2) - (src.top + src.height / 2);
      g.style.transformOrigin = '50% 50%';
      void g.offsetWidth;
      g.style.transition = 'transform ' + FLY_MS + 'ms cubic-bezier(.45,.05,.2,1), opacity 320ms ease';
      g.style.transform = 'translate(' + tx.toFixed(1) + 'px,' + ty.toFixed(1) + 'px) scale(' + s.toFixed(4) + ')';
      return true;
    }};

    var land = function () {{
      if (ended) return;
      try {{
        d.classList.add('intro-landed');   /* reveal the real interactive card */
        var g = document.querySelector('[data-cine-galaxy]');
        if (g) g.style.opacity = '0';      /* crossfade the flown still out — masks any delta */
      }} catch (e) {{}}
      setTimeout(end, LAND_MS);
    }};
    var fly = function () {{
      if (ended) return;
      try {{
        d.classList.add('intro-flying');   /* reveal hero behind, dissolve veil, fade caption */
        applyFlip();
      }} catch (e) {{}}
      setTimeout(land, FLY_MS);
    }};

    d.classList.add('intro-cine');
    setTimeout(fly, SHOW_MS);
    setTimeout(end, 4200);   /* hard safety net — content is never blocked past this */
  }} catch (e) {{}}
}})();
</script>
</head>
<body class="theme-bento landing-v2">
{nav("", "concepts/index.html", archive=False)}
<main class="page">
  <header class="hero-intro hero-split">
    <div class="hero-copy">
      <div class="kicker" data-i18n="heroKicker">FOR RESEARCHERS AND TEAMS RUNNING MANY AGENTS</div>
      <h1 data-i18n="heroTitle">Which agent did that?</h1>
      <p class="lead hero-def" data-i18n="heroDef">See what every teammate&rsquo;s agents shipped today: a Claude Code skill that merges every machine&rsquo;s agent_memory.md into one private, searchable map &mdash; a single static HTML page.</p>
      <p class="lead hero-scene" data-i18n="heroLead">Claude on your laptop, a trainer on the GPU node, Codex on CI. By 11 pm none of them knows what the others did.</p>
      <div class="actions">
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos" data-i18n="openDemo">Open the demo</button>
        <a class="btn" href="#install" data-i18n="installSkill">Install as skill</a>
        <a class="btn" href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
      </div>
      <p class="demo-note" data-i18n="demoNote">Demo uses fictional data.</p>
      <div class="hero-spec">
        <span class="spec-num" data-i18n="heroSpec">0 daemons &middot; 1 static HTML file &middot; 2 commands</span>
        <span class="spec-privacy" data-i18n="heroSpecPrivacy">Private by default &mdash; publishing ships ciphertext only.</span>
      </div>
    </div>
    <div class="hero-stage">
      <div class="stage-frame">
{galaxy_card("", stats, element_id="after-galaxy")}
        <span class="stage-hint" data-i18n="stageHint">Interactive demo &mdash; drag, zoom, click a node.</span>
      </div>
    </div>
  </header>

  <section class="section pillars" id="why">
    <div class="section-head">
      <h2 data-i18n="whyHeading">Why teams pick it</h2>
      <p data-i18n="whyBody">One private graph of everything your agents remember &mdash; built to be trusted, cheap to run, and readable at a glance by the whole team.</p>
    </div>
    <div class="pillar-grid">
      <article class="pillar">
        <span class="pillar-tag" data-i18n="p1Badge">New this week</span>
        <span class="pillar-ico">{PILLAR_ICONS['team']}</span>
        <h3 data-i18n="p1Title">Your whole team&rsquo;s memory, one graph</h3>
        <p class="pillar-how" data-i18n="p1How">Every teammate&rsquo;s machines push fragments into one private hub; filter and color by user to see who did what, on which machine.</p>
      </article>
      <article class="pillar">
        <span class="pillar-ico">{PILLAR_ICONS['lock']}</span>
        <h3 data-i18n="p2Title">Plaintext stays local or in your private hub</h3>
        <p class="pillar-how" data-i18n="p2How">Plaintext lives on your machines, or in a private repo only your collaborators can read; only a public Pages deploy is encrypted &mdash; client-side AES-256-GCM with PBKDF2 and a dual password, and nothing phones home.</p>
      </article>
      <article class="pillar">
        <span class="pillar-ico">{PILLAR_ICONS['plug']}</span>
        <h3 data-i18n="p3Title">Works with the coding agents you already run</h3>
        <p class="pillar-how" data-i18n="p3How">Native today for Claude Code, Codex, and Cursor. agent_memory.md is plain markdown, so any tool that writes it joins the graph too.</p>
      </article>
      <article class="pillar">
        <span class="pillar-ico">{PILLAR_ICONS['bolt']}</span>
        <h3 data-i18n="p4Title">The memory layer barely adds tokens</h3>
        <p class="pillar-how" data-i18n="p4How">The graph is built by zero-dependency Python &mdash; heuristics by default, LLM optional and off. Indexing your agents&rsquo; work doesn&rsquo;t burn tokens.</p>
      </article>
      <article class="pillar">
        <span class="pillar-ico">{PILLAR_ICONS['auto']}</span>
        <h3 data-i18n="p5Title">It refreshes itself and lights up live work</h3>
        <p class="pillar-how" data-i18n="p5How">A cron job rebuilds the graph on a schedule; auto-presence detects working agents and pulses them red &mdash; no manual heartbeat.</p>
      </article>
      <article class="pillar">
        <span class="pillar-ico">{PILLAR_ICONS['dash']}</span>
        <h3 data-i18n="p6Title">A live map for team leads</h3>
        <p class="pillar-how" data-i18n="p6How">See who&rsquo;s on which machine and project at a glance &mdash; red means working now, gold lines mean cross-project references.</p>
      </article>
    </div>
  </section>

  <section class="contrast" id="contrast" aria-label="Before and after: scattered agents vs one shared memory galaxy">
    <div class="contrast-grid">
      <div class="contrast-side">
        <div class="contrast-tag"><span data-i18n="beforeTag">WITHOUT SHARED MEMORY</span></div>
{chaos_board_markup()}
        <p class="contrast-caption" data-i18n="beforeCaption">Five machines, zero shared context. Every window remembers a different slice of the day, and it all evaporates when the terminal closes.</p>
      </div>
      <div class="contrast-arrow" aria-hidden="true"><span>&#8594;</span></div>
      <div class="contrast-side">
        <div class="contrast-tag gold"><span data-i18n="afterTag">WITH AGENT MEMORY GALAXY</span></div>
{galaxy_still_markup(stats)}
        <p class="contrast-caption" data-i18n="afterCaption">One day of work across five machines, resolved into one graph &mdash; the same interactive map you can open at the top of the page.</p>
        <div class="actions contrast-actions">
          <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos" data-i18n="openDemo">Open the demo</button>
        </div>
      </div>
    </div>
  </section>

  <section class="section audiences" id="audiences">
    <div class="section-head">
      <h2 data-i18n="audHeading">One map, two jobs.</h2>
      <p data-i18n="audBody">The same graph answers a different question depending on who is looking at it.</p>
    </div>
    <div class="audience-grid">
      <article class="audience res">
        <span class="audience-tag" data-i18n="audResTag">FOR RESEARCHERS</span>
        <h3 data-i18n="audResTitle">Stop losing track of your own agents</h3>
        <ul class="aud-list">
          <li data-i18n="r1">Who changed what &mdash; every entry carries the agent, machine, files, and the reason, so &ldquo;why did this change?&rdquo; always has an answer.</li>
          <li data-i18n="r2">No duplicate afternoons &mdash; spot a fix that already landed on another machine before you chase the same bug again.</li>
          <li data-i18n="r3">Real handoff &mdash; the next session, and the next agent, start from what already happened instead of a cold terminal.</li>
        </ul>
      </article>
      <article class="audience pm">
        <span class="audience-tag" data-i18n="audPmTag">FOR TEAM LEADS &amp; PM</span>
        <h3 data-i18n="audPmTitle">Monitor the whole team from one map</h3>
        <p class="aud-lead" data-i18n="audPmLead">Open the page and read the whole team in seconds &mdash; who is on which machine and project, and what is live right now.</p>
{team_console_markup()}
        <p class="tc-bridge" data-i18n="tcBridge">The live product renders this same team data as an interactive galaxy &mdash; the demo opens that map, not a list like this.</p>
      </article>
    </div>
  </section>

  <section class="gh-band" id="github" aria-label="All you need is a GitHub account">
    <h2 data-i18n="ghHeading">All you need is a GitHub account.</h2>
    <p class="gh-body" data-i18n="ghBody">No server to run, no database, no SaaS to sign up for &mdash; just a git repo and the Python standard library. Collaborate by adding a teammate as a GitHub collaborator and pushing.</p>
    <div class="gh-chips">
      <span data-i18n="ghNoServer">No server</span>
      <span data-i18n="ghNoDb">No database</span>
      <span data-i18n="ghNoSaas">No SaaS signup</span>
      <span data-i18n="ghNoKey">No API key</span>
    </div>
    <p class="gh-foot" data-i18n="ghFoot">You&rsquo;ll need git and python3 on the machine &mdash; most dev machines already have both.</p>
  </section>

  <section class="section" id="how">
    <div class="section-head">
      <h2 data-i18n="howHeading">From scattered traces to one galaxy.</h2>
      <p data-i18n="howBody">Plain files and static HTML &mdash; here&rsquo;s how one day of agent work becomes one graph.</p>
    </div>
    <div class="timeline">
      <div class="tl-item"><span class="tl-step" data-i18n="tl1Tag">STEP 01 &middot; IN EVERY PROJECT</span><h3 data-i18n="tl1Title">Agents write memory as they work</h3><p data-i18n="tl1Body">Each project keeps an agent_memory.md: what changed, why, and which files. Agents read it when a session starts and append after meaningful changes.</p></div>
      <div class="tl-item"><span class="tl-step" data-i18n="tl2Tag">STEP 02 &middot; ON EVERY MACHINE</span><h3 data-i18n="tl2Title">Each machine contributes a fragment</h3><p data-i18n="tl2Body">contribute.sh scans reviewed notes and safe session metadata &mdash; never raw conversations &mdash; into fragments/&lt;machine&gt;.json.</p></div>
      <div class="tl-item"><span class="tl-step" data-i18n="tl3Tag">STEP 03 &middot; ON THE AGGREGATOR</span><h3 data-i18n="tl3Title">One aggregator merges the graph</h3><p data-i18n="tl3Body">Shared files, datasets, models, and servers connect projects across machines. A gold reference skeleton emerges between project hubs.</p></div>
      <div class="tl-item live"><span class="tl-step" data-i18n="tl4Tag">STEP 04 &middot; LIVE, EVERY FEW MINUTES</span><h3 data-i18n="tl4Title">Working agents light up red</h3><p data-i18n="tl4Body">Agents that are mid-task show a red pulse plus a one-line status of what they&rsquo;re working on &mdash; so you and every other agent see the overlap before it happens.</p></div>
      <div class="tl-item"><span class="tl-step" data-i18n="tl5Tag">STEP 05 &middot; ONLY IF YOU PUBLISH</span><h3 data-i18n="tl5Title">Encryption before anything leaves</h3><p data-i18n="tl5Body">Plaintext graphs stay local or in a private hub. A public Pages deploy ships the viewer shell plus ciphertext only, unlocked client-side.</p></div>
    </div>
  </section>

  <section class="section" id="install">
    <div class="section-head">
      <h2 data-i18n="installHeading">Install with two Claude Code commands.</h2>
      <p data-i18n="installBody">The repo ships a Claude Code plugin. The skill sets up a private hub, pulls in each machine, merges their memory into one graph, and runs a privacy review before anything is published.</p>
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
        <h3 data-i18n="localDemo">Try the demo locally</h3>
        <pre class="code"><code>git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git
cd agent-memory-galaxy
python3 scripts/build-public-demo.py
python3 -m http.server 8765 --directory docs</code></pre>
        <button class="copy-btn" type="button" data-copy="git clone https://github.com/RenyunLi0116/agent-memory-galaxy.git&#10;cd agent-memory-galaxy&#10;python3 scripts/build-public-demo.py&#10;python3 -m http.server 8765 --directory docs"><span data-i18n="copyDemo">Copy demo commands</span></button>
      </article>
    </div>
  </section>

  <section class="section" id="preview">
    <div class="section-head">
      <h2 data-i18n="previewHeading">Search, filter, click through evidence.</h2>
      <p data-i18n="previewBody">The demo runs the same viewer as the real thing &mdash; search, filters, and node details, in your browser.</p>
    </div>
    <div class="evidence-row">
      <figure class="evidence-card" aria-label="Example node detail panel from the demo">
        <div class="ev-head"><span class="ev-kind">ENTRY</span><span class="ev-title">Project Aurora Loom &middot; fragment merge fix</span></div>
        <dl class="ev-fields">
          <div class="ev-field"><dt data-i18n="evWho">who</dt><dd>claude</dd></div>
          <div class="ev-field"><dt data-i18n="evWhen">when</dt><dd>2026-07-02 21:14</dd></div>
          <div class="ev-field"><dt data-i18n="evMachine">machine</dt><dd>demo-workstation-a</dd></div>
          <div class="ev-field"><dt data-i18n="evFiles">files</dt><dd>graph_loader.py &middot; fragment_merge_tests.py</dd></div>
          <div class="ev-field"><dt data-i18n="evWhy">why</dt><dd>fragment merge dropped duplicate file nodes; deduped by id and added a regression test</dd></div>
          <div class="ev-field"><dt data-i18n="evStatus">status</dt><dd class="ev-ok">done</dd></div>
        </dl>
      </figure>
      <div class="evidence-aside">
        <p class="evidence-lead" data-i18n="evidenceCaption">This is what evidence looks like.</p>
        <p class="evidence-sub" data-i18n="evidenceCaptionSub">Click any node in the demo and a panel like this opens &mdash; who, when, on which machine, which files, and why.</p>
        <div class="actions">
          <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos" data-i18n="openDemo">Open the demo</button>
        </div>
      </div>
    </div>
    <div class="grid">
      <article class="tile"><div class="mini-label" data-i18n="searchLabel">Search</div><h3 data-i18n="searchTitle">Find a project or artifact</h3><p data-i18n="searchBody">Search across projects, agents, files, models, servers, and derived facts.</p></article>
      <article class="tile"><div class="mini-label" data-i18n="filterLabel">Filter</div><h3 data-i18n="filterTitle">Focus by machine or activity</h3><p data-i18n="filterBody">Switch from the full graph to one machine, one project, recent work, or what agents are doing right now.</p></article>
      <article class="tile"><div class="mini-label" data-i18n="inspectLabel">Inspect</div><h3 data-i18n="inspectTitle">Click through evidence</h3><p data-i18n="inspectBody">Open a node&rsquo;s detail panel, inspect neighbors, and follow inheritance or publishing edges.</p></article>
    </div>
    <div class="stat-band" id="numbers">
      <span class="mini-label" data-i18n="statBandTitle">The demo graph, by the numbers</span>
      <div class="stat-band-grid">
        <div class="stat-cell"><b>{stats['nodes']}</b><span data-i18n="statNodes">nodes</span></div>
        <div class="stat-cell"><b>{stats['edges']}</b><span data-i18n="statLinks">links</span></div>
        <div class="stat-cell"><b>{stats['entries']}</b><span data-i18n="statEntries">memory entries</span></div>
        <div class="stat-cell"><b>{stats['projects']}</b><span data-i18n="statProjects">projects</span></div>
        <div class="stat-cell"><b>{stats['machines']}</b><span data-i18n="statMachines">machines</span></div>
        <div class="stat-cell"><b>{stats['live']}</b><span data-i18n="statLive">simulated agents active</span></div>
      </div>
      <p class="stat-honest" data-i18n="statHonest">The numbers above come straight from the demo&rsquo;s graph.json. Every project, machine, agent, and file in it is fictional &mdash; no real memory is published here.</p>
    </div>
  </section>

  <section class="section" id="privacy">
    <div class="section-head">
      <h2 data-i18n="privacyHeading">Public framework. Private memory.</h2>
      <p data-i18n="privacyBody">Working solo, your agent_memory.md and fragments never leave your machine &mdash; nothing phones home. GitHub Pages carries only the open framework and this demo.</p>
    </div>
    <p class="privacy-team" data-i18n="privacyTeam">On a team, distilled fragments &mdash; safe session metadata, never raw conversations &mdash; sync as plaintext inside your private GitHub repo, readable only by the collaborators you add. The only thing that ever leaves that repo is a public Pages deploy, and that ships AES-256-GCM ciphertext, unlocked in the browser.</p>
    <p class="privacy-more"><a href="https://github.com/RenyunLi0116/agent-memory-galaxy#readme"><span data-i18n="privacyMore">Full privacy model, roles, and URL map &mdash; see the README.</span></a></p>
  </section>

  <section class="cta-band" id="cta">
    <h2 data-i18n="ctaTitle">Stop asking &ldquo;which agent did that?&rdquo;</h2>
    <p data-i18n="ctaBody">Install the skill and point it at your projects. Tomorrow, you &mdash; and every agent &mdash; look in one place.</p>
    <div class="actions">
      <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos" data-i18n="openDemo">Open the demo</button>
      <a class="btn" href="#install" data-i18n="installSkill">Install as skill</a>
      <a class="btn" href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
    </div>
  </section>
</main>
<footer class="footer"><div class="page">
  <span>Agent Memory Galaxy</span>
  <span><a href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a> &middot; <a href="concepts/index.html" data-i18n="navConcepts">Design archive</a></span>
  <span data-i18n="footerPrivacy">Demo data fictional. Real memory private.</span>
</div></footer>
{intro_cine_markup(stats)}
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
