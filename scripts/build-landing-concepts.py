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


JS = r"""
(function () {
  var modal = document.querySelector('[data-galaxy-modal]');
  if (!modal) return;
  var frame = modal.querySelector('iframe');
  var close = modal.querySelector('[data-modal-close]');
  var lastFocus = null;

  function openModal(src) {
    lastFocus = document.activeElement;
    frame.src = src;
    modal.classList.add('open');
    modal.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
    close.focus();
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('hidden', '');
    frame.src = 'about:blank';
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

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

  modal.addEventListener('click', function (event) {
    if (event.target === modal) closeModal();
  });
  close.addEventListener('click', closeModal);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modal.classList.contains('open')) closeModal();
  });

  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', async function () {
      var text = button.getAttribute('data-copy') || '';
      try {
        await navigator.clipboard.writeText(text);
        var old = button.textContent;
        button.textContent = 'Copied';
        setTimeout(function () { button.textContent = old; }, 1200);
      } catch (err) {
        button.textContent = 'Copy failed';
      }
    });
  });
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
      <span class="muted">Synthetic demo. Drag, zoom, filter, and inspect nodes.</span>
      <a class="btn" href="{prefix}demo/?style=galaxy">Open full demo</a>
      <button class="modal-close" type="button" data-modal-close>Close</button>
    </div>
    <iframe title="Expanded Agent Memory Galaxy synthetic demo" src="about:blank"></iframe>
  </div>
</div>
"""


def galaxy_card(prefix: str, stats: dict, compact: bool = False) -> str:
    demo = f"{prefix}demo/?style=galaxy"
    compact_class = " compact" if compact else ""
    return f"""
<div class="galaxy-card{compact_class}" id="preview" data-demo-src="{demo}" role="button" tabindex="0" aria-label="Expand the interactive synthetic Agent Memory Galaxy demo">
  <div class="framebar">
    <span class="lights"><i></i><i></i><i></i></span>
    <span class="mono">synthetic graph preview</span>
    <span class="status mono">{stats['nodes']} nodes / {stats['edges']} links / {stats['machines']} machines</span>
  </div>
  <iframe title="Agent Memory Galaxy synthetic demo" src="{demo}" loading="lazy"></iframe>
  <p class="preview-note">This is live synthetic data, not a screenshot and not real memory.</p>
  <button class="expand-galaxy" type="button" data-expand-galaxy>Expand galaxy</button>
</div>
"""


def nav(prefix: str, compare_href: str) -> str:
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a class="brand" href="{prefix}index.html">Agent Memory Galaxy</a>
    <div class="nav-links">
      <a href="{compare_href}">Concepts</a>
      <a href="#preview">Demo</a>
      <a href="#privacy">Privacy</a>
      <a href="#install">Install</a>
      <a href="https://github.com/RenyunLi0116/agent-memory-galaxy">GitHub</a>
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
        <button class="btn primary" type="button" data-expand-galaxy data-demo-src="../demo/?style=galaxy">{esc(concept['primary'])}</button>
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
      <h2>Collect, distill, merge, encrypt, view.</h2>
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
      <h2>Public framework. Private memory.</h2>
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
        <button class="copy-btn" type="button" data-copy="/plugin marketplace add https://github.com/RenyunLi0116/agent-memory-galaxy">Copy marketplace command</button>
        <pre class="code"><code>/plugin install agent-memory-galaxy@agent-memory-galaxy</code></pre>
        <button class="copy-btn" type="button" data-copy="/plugin install agent-memory-galaxy@agent-memory-galaxy">Copy install command</button>
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
<footer class="footer"><div class="page"><span>Agent Memory Galaxy</span><span>Synthetic demo public. Real memory private.</span></div></footer>
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
      <button class="btn" type="button" data-expand-galaxy data-demo-src="{prefix}demo/?style=galaxy">Expand synthetic galaxy</button>
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


def main():
    stats = graph_meta()
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "landing.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (ASSETS / "landing.js").write_text(JS.strip() + "\n", encoding="utf-8")
    (DOCS / "index.html").write_text(
        gallery_html("", "concepts/", stats, "Concept Gallery"), encoding="utf-8"
    )
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
