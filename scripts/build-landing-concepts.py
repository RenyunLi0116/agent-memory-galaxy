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
.mini-galaxy-preview {
  position: absolute;
  inset: 38px 0 0;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(56,225,255,.08) 1px, transparent 1px),
    linear-gradient(180deg, rgba(56,225,255,.08) 1px, transparent 1px),
    radial-gradient(circle at 50% 42%, rgba(13,64,96,.62), rgba(2,6,16,.98) 68%);
  background-size: 34px 34px, 34px 34px, auto;
}
.mini-grid {
  position: absolute;
  inset: 10%;
  border: 1px solid rgba(138, 180, 255, .16);
  transform: perspective(680px) rotateX(58deg);
  opacity: .65;
}
.mini-ring {
  position: absolute;
  left: 50%; top: 50%;
  border: 1px dashed rgba(255, 207, 107, .55);
  border-radius: 999px;
  transform: translate(-50%, -50%);
  animation: mini-spin 18s linear infinite;
}
.ring-a { width: min(62cqw, 360px); aspect-ratio: 1; }
.ring-b { width: min(42cqw, 250px); aspect-ratio: 1; animation-direction: reverse; border-color: rgba(138, 180, 255, .42); }
.mini-node {
  position: absolute;
  width: 12px; height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 16px currentColor, 0 0 36px color-mix(in srgb, currentColor 50%, transparent);
  background: currentColor;
  animation: mini-pulse 2.8s ease-in-out infinite;
}
.mini-node.project { color: #ff5d73; width: 16px; height: 16px; }
.mini-node.server { color: #ff5fa2; }
.mini-node.agent { color: #ff3b4e; width: 10px; height: 10px; animation-duration: 1.5s; }
.mini-node.boundary { color: #f5b642; width: 14px; height: 14px; border-radius: 3px; }
.mini-node.artifact { color: #7df3c4; width: 13px; height: 13px; border-radius: 4px; }
.n1 { left: 46%; top: 44%; }.n2 { left: 62%; top: 31%; }.n3 { left: 28%; top: 30%; }.n4 { left: 70%; top: 62%; }
.n5 { left: 40%; top: 64%; }.n6 { left: 57%; top: 54%; }.n7 { left: 22%; top: 63%; }.n8 { left: 78%; top: 39%; }
.mini-link {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(138, 180, 255, .78), transparent);
  transform-origin: left center;
  opacity: .76;
}
.link-a { left: 47%; top: 47%; width: 17%; transform: rotate(-28deg); }
.link-b { left: 31%; top: 34%; width: 20%; transform: rotate(34deg); }
.link-c { left: 58%; top: 56%; width: 18%; transform: rotate(20deg); }
.link-d { left: 26%; top: 65%; width: 22%; transform: rotate(-14deg); background: linear-gradient(90deg, transparent, rgba(245,182,66,.88), transparent); }
.link-e { left: 61%; top: 35%; width: 19%; transform: rotate(14deg); background: linear-gradient(90deg, transparent, rgba(125,243,196,.8), transparent); }
.mini-side,
.mini-readout {
  position: absolute;
  z-index: 2;
  border: 1px solid rgba(138, 180, 255, .20);
  border-radius: 5px;
  background: rgba(8, 14, 28, .72);
  color: #dbe4ff;
  backdrop-filter: blur(8px);
  box-shadow: inset 0 0 24px rgba(56,225,255,.05);
}
.mini-side {
  left: 12px; top: 12px;
  width: min(170px, 40cqw);
  padding: 9px;
  display: grid;
  gap: 5px;
  font: 10px/1.2 "JetBrains Mono", monospace;
  text-transform: uppercase;
}
.mini-side b { color: #8ab4ff; }
.mini-side span { color: #8ea6d0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mini-readout {
  right: 12px; top: 12px;
  max-width: min(260px, 45cqw);
  padding: 10px 11px;
  font: 11px/1.45 "JetBrains Mono", monospace;
}
.mini-readout b { display: block; color: #ffcf6b; margin-bottom: 5px; }
.mini-readout span { color: #9fb2da; }
@keyframes mini-spin { to { transform: translate(-50%, -50%) rotate(360deg); } }
@keyframes mini-pulse { 50% { transform: scale(1.28); opacity: .72; } }
@container (max-width: 560px) {
  .framebar .status { display: none; }
  .mini-readout { display: none; }
  .mini-side { width: 128px; font-size: 9px; }
}
@container (max-width: 420px) {
  .mini-side { display: none; }
  .expand-galaxy { left: 12px; right: 12px; text-align: center; }
}

/* Animated public-safe galaxy thumbnail. This intentionally stays lighter than the full viewer. */
.mini-galaxy-preview {
  position: absolute;
  inset: 38px 0 0;
  overflow: hidden;
  background:
    radial-gradient(ellipse at 50% 46%, rgba(255, 216, 145, .20), transparent 28%),
    radial-gradient(ellipse at 50% 46%, rgba(110, 142, 255, .20), transparent 52%),
    radial-gradient(circle at 50% 42%, rgba(5, 14, 34, .95), rgba(1, 2, 10, .99) 70%);
}
.mini-galaxy-preview::before {
  content: "";
  position: absolute;
  inset: -18%;
  background:
    linear-gradient(90deg, rgba(138,180,255,.07) 1px, transparent 1px),
    linear-gradient(180deg, rgba(138,180,255,.06) 1px, transparent 1px);
  background-size: 34px 34px;
  transform: perspective(780px) rotateX(58deg) translateY(14%);
  opacity: .56;
}
.mini-galaxy-preview::after {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 48%, transparent 34%, rgba(1,4,12,.45) 82%);
  pointer-events: none;
}
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
.mini-side,
.mini-readout { z-index: 3; }
.mini-side span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.mini-side span::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 9px currentColor;
  flex: none;
}
.mini-side [data-mini-type="project"] { color: #ff7282; }
.mini-side [data-mini-type="server"] { color: #ff6faa; }
.mini-side [data-mini-type="agent"] { color: #ff3b4e; }
.mini-side [data-mini-type="boundary"] { color: #f5b642; }
.mini-side [data-mini-type="artifact"] { color: #7df3c4; }
.mini-readout span {
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
@media (prefers-reduced-motion: reduce) {
  .mini-edge, .mini-scan, .mini-orbit, .mini-dust, .mini-star .core { animation: none !important; }
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
      if (preview.dataset.hydrated) return;
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
      <a class="btn" href="{prefix}demo/?style=cosmos&lang=en" data-demo-link data-i18n="openFullDemo">Open full demo</a>
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
    demo = f"{prefix}demo/?style=cosmos&lang=en"
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
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="../demo/?style=cosmos&lang=en">{esc(concept['primary'])}</button>
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
      <button class="btn" type="button" data-expand-galaxy data-demo-src="{prefix}demo/?style=cosmos&lang=en">Expand synthetic galaxy</button>
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
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="demo/?style=cosmos&lang=en" data-i18n="openDemo">Open synthetic demo</button>
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
