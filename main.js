const BRAND = { name: null, logo: null };

const COPY = {
  zh: {
    meta: "在 Mac 上实时补帧。识别窗口里的真实帧率，用本地 AI 补出中间帧，画面不离开这台 Mac。",
    ariaNav: "页面章节",
    ariaFoot: "页脚",
    ariaLang: "切换语言",
    navHow: "怎么工作",
    navUses: "使用场景",
    navFaq: "常见问题",
    h1a: "让 Mac 上的画面",
    h1b: "流畅一倍",
    sub: "实时识别窗口里的真实帧率，用本地 AI 补出中间帧。24 帧的电影变 48 帧，30 帧变 60 帧，片源不用改，画面不出这台 Mac。",
    download: "下载 Mac 版（即将推出）",
    seeHow: "看看原理",
    demoTitle: "预览",
    srcLabel: "原始 24 fps",
    outLabel: "补帧后 48 fps",
    demoNote: "示意动画，非实机录屏",
    howTitle: "它是怎么工作的",
    howBefore: "选一个窗口，",
    howAfter: "在它上面叠一层输出画面。采集、识别帧率、补帧、显示，全部在你的 Mac 上完成。",
    how1t: "识别真实帧率",
    how1d: "只数画面真正变化的帧，24 帧的视频按 24 帧算，不会被 120 Hz 刷新率骗到。",
    how2t: "2 倍、3 倍补帧",
    how2d: "24 → 48、30 → 60，也可以试试 24 → 72。",
    how3t: "算力不够自动降档",
    how3d: "跟不上时退到更低倍率，避免画面忽快忽慢。",
    how4t: "到屏幕上限就直通",
    how4d: "内容乘倍率超过屏幕刷新率时直接显示原画，不让显卡白忙。",
    how5t: "跟着窗口走",
    how5d: "输出贴在原窗口的位置，窗口挪到哪里跟到哪里。",
    how6t: "全部本地处理",
    how6d: "采集和模型都在本机运行，画面不上传。",
    how7t: "帧率一眼看清",
    how7d: "角落的小面板实时显示内容帧率、输出帧率和当前倍率。",
    usesTitle: "适合用在哪",
    usesLede: "只要是窗口里在动的画面，都可以试试。",
    use1t: "网页视频",
    use1d: "浏览器里的视频网站，普通窗口或网页全屏都行。",
    use2t: "本地电影",
    use2d: "播放器里的 24 帧电影，镜头平移不再一顿一顿。",
    use3t: "动画番剧",
    use3d: "帧数低的动画，动作更连贯。",
    use4t: "录屏与教程",
    use4d: "30 帧的录屏回放，滚动和拖动更顺。",
    use5t: "慢节奏游戏",
    use5d: "锁 30 帧的单机游戏。补帧会增加一点延迟，不适合竞技对战。",
    use6t: "任意窗口",
    use6d: "别的窗口也能选，效果自己看。",
    faqTitle: "常见问题",
    faqLede: "还有别的问题？",
    faqContact: "〔联系方式待定〕",
    faq1before: "",
    faq1after: "是什么？",
    faq1a: "一款 Mac 上的实时补帧应用。它识别窗口里画面的真实帧率，用本地 AI 模型在两帧之间补出新画面，让视频和动画更流畅。",
    faq2q: "需要什么样的 Mac？",
    faq2a: "〔系统版本和芯片要求待定〕",
    faq3q: "会增加延迟吗？",
    faq3a: "会。补帧要等到下一帧画面才能算中间帧。2 倍补帧时，从采集到显示实测约 70–80 毫秒，看视频没问题，不适合竞技游戏。",
    faq4q: "支持全屏吗？",
    faq4a: "目前支持普通窗口和网页全屏。macOS 原生全屏还在开发中。",
    faq5q: "画面会上传吗？",
    faq5a: "不会。采集、识别和补帧都在你的 Mac 上完成。",
    faq6q: "多少钱？",
    faq6a: "〔价格待定〕",
    getTitle: "想第一时间用上？",
    getAfter: "正在打磨中，Mac 版即将推出。",
    privacy: "隐私",
    contact: "联系我们",
  },
  en: {
    meta: "Real-time frame interpolation on Mac. It reads the real frame rate in a window and draws the in-between frames with on-device AI. The picture stays on this Mac.",
    ariaNav: "Sections",
    ariaFoot: "Footer",
    ariaLang: "Switch language",
    navHow: "How it works",
    navUses: "Use cases",
    navFaq: "Questions",
    h1a: "Make the picture on Mac",
    h1b: "twice as smooth",
    sub: "It reads the real frame rate inside a window and uses on-device AI to draw the frames in between. A 24 fps film becomes 48, and 30 becomes 60. The source stays unchanged, and the picture never leaves this Mac.",
    download: "Download for Mac (coming soon)",
    seeHow: "See how it works",
    demoTitle: "Preview",
    srcLabel: "Source 24 fps",
    outLabel: "Interpolated 48 fps",
    demoNote: "Illustrative animation, not a real screen recording.",
    howTitle: "How it works",
    howBefore: "Pick a window, and ",
    howAfter: " lays an output picture over it. Capture, frame-rate detection, interpolation, and display all happen on your Mac.",
    how1t: "Read the real frame rate",
    how1d: "It counts only frames where the picture actually changes. A 24 fps video stays 24 fps, and a 120 Hz refresh rate does not fool it.",
    how2t: "2× and 3× interpolation",
    how2d: "24 → 48, 30 → 60, or try 24 → 72.",
    how3t: "Steps down when the Mac falls behind",
    how3d: "If it cannot keep up, it drops to a lower multiple so the picture does not speed up and slow down.",
    how4t: "Passes through at the screen limit",
    how4d: "When the content times the multiple would pass the display refresh rate, it shows the original picture and does not keep the GPU busy for nothing.",
    how5t: "Follows the window",
    how5d: "The output sits on the original window and moves wherever that window moves.",
    how6t: "Processed entirely on device",
    how6d: "Capture and the model both run on this Mac. The picture is not uploaded.",
    how7t: "Frame rate in the corner",
    how7d: "A small panel shows the content frame rate, the output frame rate, and the current multiple, live.",
    usesTitle: "Where it fits",
    usesLede: "If a window has a moving picture, it is worth a try.",
    use1t: "Web video",
    use1d: "Video sites in the browser, in a normal window or in web fullscreen.",
    use2t: "Local films",
    use2d: "24 fps films in a player. Camera pans no longer step along.",
    use3t: "Animation",
    use3d: "Low-frame-rate animation, with motion that connects more smoothly.",
    use4t: "Recordings and tutorials",
    use4d: "Playback of 30 fps recordings. Scrolling and dragging look smoother.",
    use5t: "Slower games",
    use5d: "Single-player games locked to 30 fps. Interpolation adds a little latency, so it is a poor fit for competitive play.",
    use6t: "Any window",
    use6d: "Other windows can be selected too. Judge the result yourself.",
    faqTitle: "Common questions",
    faqLede: "Other questions?",
    faqContact: "[Contact to be decided]",
    faq1before: "What is ",
    faq1after: "?",
    faq1a: "A real-time frame interpolation app for Mac. It reads the real frame rate of the picture in a window and uses an on-device AI model to draw new frames between two frames, so video and animation look smoother.",
    faq2q: "What kind of Mac does it need?",
    faq2a: "[System version and chip requirements to be decided]",
    faq3q: "Does it add latency?",
    faq3a: "Yes. Interpolation has to wait for the next frame before it can draw the one in between. At 2×, the measured time from capture to display is about 70–80 milliseconds. Fine for watching video, and a poor fit for competitive games.",
    faq4q: "Does fullscreen work?",
    faq4a: "Normal windows and web fullscreen work today. Native macOS fullscreen is still in development.",
    faq5q: "Is the picture uploaded?",
    faq5a: "No. Capture, detection, and interpolation all happen on your Mac.",
    faq6q: "How much does it cost?",
    faq6a: "[Price to be decided]",
    getTitle: "Want it as soon as it is ready?",
    getAfter: " is still being polished. The Mac version is coming soon.",
    privacy: "Privacy",
    contact: "Contact",
  },
};

function brandName() {
  if (typeof BRAND.name === "string" && BRAND.name.trim() !== "") return BRAND.name;
  return "〔产品名〕";
}

function resolvedTheme() {
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit === "dark" || explicit === "light") return explicit;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyBrand() {
  const name = brandName();
  document.querySelectorAll("[data-brand-name]").forEach((el) => {
    el.textContent = name;
  });
  const logo = typeof BRAND.logo === "string" ? BRAND.logo.trim() : "";
  document.querySelectorAll(".logo-slot").forEach((slot) => {
    slot.replaceChildren();
    slot.classList.toggle("has-logo", logo !== "");
    if (!logo) return;
    const img = document.createElement("img");
    img.src = logo;
    img.alt = "";
    slot.append(img);
  });
}

function applyThemeLabel() {
  const btn = document.querySelector('[data-action="theme"]');
  if (!btn) return;
  const toDark = resolvedTheme() !== "dark";
  const en = document.documentElement.lang === "en";
  btn.setAttribute(
    "aria-label",
    en ? (toDark ? "Switch to dark" : "Switch to light") : (toDark ? "切换到深色" : "切换到浅色"),
  );
}

function applyLang(next) {
  const dict = COPY[next] || COPY.zh;
  document.documentElement.lang = next === "en" ? "en" : "zh-CN";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] != null) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const key = el.getAttribute("data-i18n-aria");
    if (dict[key] != null) el.setAttribute("aria-label", dict[key]);
  });
  applyBrand();
  const name = brandName();
  document.title = next === "en"
    ? `${name} · Real-time frame interpolation for Mac`
    : `${name} · Mac 实时补帧`;
  const meta = document.querySelector('meta[name="description"]');
  if (meta && dict.meta) meta.setAttribute("content", dict.meta);
  const langBtn = document.querySelector('[data-action="lang"]');
  if (langBtn) {
    langBtn.textContent = next === "en" ? "EN / ZH" : "中 / EN";
    if (dict.ariaLang) langBtn.setAttribute("aria-label", dict.ariaLang);
  }
  applyThemeLabel();
}

function bindControls() {
  const langBtn = document.querySelector('[data-action="lang"]');
  if (langBtn) {
    langBtn.addEventListener("click", () => {
      applyLang(document.documentElement.lang === "en" ? "zh" : "en");
    });
  }
  const themeBtn = document.querySelector('[data-action="theme"]');
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const next = resolvedTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      applyThemeLabel();
    });
  }
  document.querySelectorAll('[data-cta="download"]').forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.preventDefault();
    });
  });
  const faq = document.querySelector("#faq");
  if (!faq) return;
  faq.addEventListener("click", (event) => {
    const button = event.target.closest("[data-faq] button");
    if (!button || !faq.contains(button)) return;
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", expanded ? "false" : "true");
    const panel = document.getElementById(button.getAttribute("aria-controls"));
    if (panel) panel.setAttribute("aria-hidden", expanded ? "true" : "false");
    const item = button.closest("[data-faq]");
    if (item) item.classList.toggle("open", !expanded);
  });
}

function startDemo() {
  const source = document.querySelector('[data-demo="source"]');
  const output = document.querySelector('[data-demo="output"]');
  if (!source || !output) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const SOURCE_FPS = 24;
  const CYCLE_MS = 2000;
  const SOURCE_FRAMES = SOURCE_FPS * (CYCLE_MS / 1000);
  const TRAIL = 6;

  function makeGhosts(ball) {
    const ghosts = [];
    for (let i = 0; i < TRAIL; i += 1) {
      const ghost = document.createElement("span");
      ghost.className = "ghost";
      ghost.setAttribute("aria-hidden", "true");
      ball.parentElement.insertBefore(ghost, ball);
      ghosts.push(ghost);
    }
    return ghosts;
  }

  const sourceGhosts = makeGhosts(source);
  const outputGhosts = makeGhosts(output);

  function move(el, phase, opacity) {
    const stage = el.parentElement;
    const width = stage.clientWidth;
    const inset = 18;
    const travel = Math.max(0, width - el.offsetWidth - inset * 2);
    el.style.transform = `translateX(${(inset + travel * phase).toFixed(2)}px)`;
    if (opacity != null) el.style.opacity = String(opacity);
  }

  function paintTrail(ghosts, hist) {
    ghosts.forEach((ghost, index) => {
      const phase = hist[index];
      if (phase == null) {
        ghost.style.opacity = "0";
        return;
      }
      move(ghost, phase, 0.34 * Math.pow(0.62, index));
    });
  }

  function park() {
    move(source, 0.42);
    move(output, 0.42);
    sourceGhosts.concat(outputGhosts).forEach((ghost) => {
      ghost.style.opacity = "0";
    });
  }

  let running = false;
  function loop() {
    if (running) return;
    if (reduce.matches) {
      park();
      return;
    }
    running = true;
    const origin = performance.now();
    let lastFrame = -1;
    const sourceHist = [];
    const outputHist = [];

    function push(hist, phase) {
      if (hist.length && phase + 0.25 < hist[0]) hist.length = 0;
      hist.unshift(phase);
      if (hist.length > TRAIL) hist.length = TRAIL;
    }

    function frame(now) {
      if (reduce.matches) {
        running = false;
        park();
        return;
      }
      const elapsed = now - origin;
      const outPhase = (elapsed % CYCLE_MS) / CYCLE_MS;
      const sourceFrame = Math.floor(elapsed / (1000 / SOURCE_FPS));
      const srcPhase = (sourceFrame % SOURCE_FRAMES) / SOURCE_FRAMES;
      move(output, outPhase);
      move(source, srcPhase);
      push(outputHist, outPhase);
      if (sourceFrame !== lastFrame) {
        push(sourceHist, srcPhase);
        lastFrame = sourceFrame;
      }
      paintTrail(outputGhosts, outputHist);
      paintTrail(sourceGhosts, sourceHist);
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  reduce.addEventListener("change", () => {
    running = false;
    loop();
  });
  loop();
}

applyLang("zh");
bindControls();
startDemo();
