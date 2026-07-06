(function () {
  var modal = document.querySelector('[data-galaxy-modal]');
  var frame = modal ? modal.querySelector('iframe') : null;
  var close = modal ? modal.querySelector('[data-modal-close]') : null;
  var lastFocus = null;
  var dict = {
    en: {
      navConcepts: 'Design archive', navDemo: 'Demo', navPrivacy: 'Privacy', navInstall: 'Install',
      previewTitle: 'synthetic graph preview', previewNote: 'Compressed public preview. Open the full demo for search, filters, zoom, and readouts.',
      expandGalaxy: 'Expand galaxy', miniSideTitle: 'NODE TYPES', miniReadoutTitle: 'ONLINE HUD', miniReadout: 'multi-server handoff / live agents / encrypted boundary',
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
      expandGalaxy: '展开图谱', miniSideTitle: '节点类型', miniReadoutTitle: '在线 HUD', miniReadout: '多服务器交接 / 在线 agent / 加密边界',
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
    if (!url.searchParams.get('style')) url.searchParams.set('style', 'jarvis');
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
}());
