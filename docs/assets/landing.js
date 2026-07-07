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
      skipIntro: 'Skip intro', stageHint: 'Interactive demo — drag, zoom, click a node.', stillTitle: 'one graph, settled',
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
      skipIntro: '跳过', stageHint: '可交互 demo——拖拽、缩放、点击节点。', stillTitle: '一张图，已汇合',
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
  /* Intro reveal is orchestrated by the head script (self-contained, always completes).
     Here we only progressively enhance it with a Skip control that fast-forwards the
     in-place reveal to its settled state. No skip button, or JS off => the head script
     still finishes the reveal on its own. */
  function wireIntroSkip() {
    var d = document.documentElement;
    var btn = document.querySelector('[data-intro-skip]');
    if (!btn) return;
    btn.addEventListener('click', function () {
      d.classList.add('intro-go', 'intro-fast');
      setTimeout(function () {
        if (typeof d.__amgIntroEnd === 'function') d.__amgIntroEnd();
        else d.classList.remove('intro-run', 'intro-go', 'intro-fast');
      }, 240);
    });
  }

  applyLang(lang);
  startMiniGalaxy();
  hydrateMiniPreview();
  wireIntroSkip();
}());
