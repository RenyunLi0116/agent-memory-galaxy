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
