const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

const prompts = [
  "A luxury AI workstation floating above a neon ocean, cinematic, ultra detailed",
  "A restored vintage family portrait with soft studio light and natural skin detail",
  "Cyberpunk fashion editorial in rainy Tokyo, reflective streets, 85mm photography",
  "Fantasy glass palace inside a mountain, sunrise, magical particles, epic scale",
  "A premium skincare product on black marble with cyan holographic lighting"
];

let selectedRatio = "1:1";
let selectedTarget = "2k";
let lastEnhanceFile = null;

window.addEventListener("load", () => {
  setTimeout(() => $("#loader")?.classList.add("hide"), 450);
  initTheme();
  initAnimations();
  initCounters();
  initGenerator();
  initEnhancer();
  initAuth();
});

function initTheme() {
  const saved = localStorage.getItem("hijjaze-theme");
  if (saved === "light") document.body.classList.add("light");
  $("#themeToggle")?.addEventListener("click", () => {
    document.body.classList.toggle("light");
    localStorage.setItem("hijjaze-theme", document.body.classList.contains("light") ? "light" : "dark");
  });
}

function initAnimations() {
  if (!window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);
  gsap.from(".hero .eyebrow, .hero h1, .hero-copy, .hero-actions, .trusted", {
    opacity: 0,
    y: 28,
    stagger: .09,
    duration: .8,
    ease: "power3.out"
  });
  gsap.from(".glass-card", {
    scrollTrigger: { trigger: ".feature-grid", start: "top 80%" },
    opacity: 0,
    y: 24,
    stagger: .04,
    duration: .65,
    ease: "power2.out"
  });
  $$(".section-head").forEach((head) => {
    gsap.from(head, {
      scrollTrigger: { trigger: head, start: "top 82%" },
      opacity: 0,
      y: 24,
      duration: .65
    });
  });
}

function initCounters() {
  const counters = $$("[data-counter]");
  if (!counters.length) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const max = Number(el.dataset.counter);
      let current = 0;
      const timer = setInterval(() => {
        current += Math.max(1, Math.ceil(max / 30));
        if (current >= max) {
          current = max;
          clearInterval(timer);
        }
        el.textContent = current;
      }, 28);
      obs.unobserve(el);
    });
  }, { threshold: .5 });
  counters.forEach((el) => obs.observe(el));
}

function setBusy(button, busyText) {
  const original = button.innerHTML;
  button.disabled = true;
  button.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> ${busyText}`;
  return () => {
    button.disabled = false;
    button.innerHTML = original;
  };
}

function initGenerator() {
  const prompt = $("#prompt");
  const frame = $("#generatedFrame");
  const download = $("#downloadGenerated");
  if (!prompt || !frame) return;

  $$("#ratioGroup button").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$("#ratioGroup button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedRatio = btn.dataset.ratio;
    });
  });

  $("#randomPrompt").addEventListener("click", () => {
    prompt.value = prompts[Math.floor(Math.random() * prompts.length)];
  });
  $("#copyPrompt").addEventListener("click", async () => {
    await navigator.clipboard?.writeText(prompt.value || "");
    $("#copyPrompt").textContent = "Copied";
    setTimeout(() => $("#copyPrompt").textContent = "Copy prompt", 900);
  });
  $("#generateBtn").addEventListener("click", async () => {
    if (!prompt.value.trim()) {
      prompt.focus();
      return;
    }
    const done = setBusy($("#generateBtn"), "Generating");
    frame.classList.add("skeleton");
    frame.innerHTML = "<span>Rendering neural image...</span>";
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.value,
          negative_prompt: $("#negativePrompt").value,
          style: $("#style").value,
          ratio: selectedRatio
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Generation failed");
      frame.classList.remove("skeleton");
      frame.innerHTML = `<img src="${data.url}" alt="Generated AI image" loading="lazy">`;
      $("#generationEngine").textContent = data.engine;
      download.href = data.url;
      download.classList.remove("disabled");
      const item = document.createElement("li");
      item.textContent = prompt.value;
      $("#promptHistory").prepend(item);
    } catch (error) {
      frame.innerHTML = `<span>${error.message}</span>`;
    } finally {
      done();
    }
  });
}

function initEnhancer() {
  const input = $("#enhanceInput");
  const box = $("#uploadBox");
  if (!input || !box) return;

  $$("#targetGroup button").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$("#targetGroup button").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedTarget = btn.dataset.target;
    });
  });

  ["dragenter", "dragover"].forEach((eventName) => box.addEventListener(eventName, (event) => {
    event.preventDefault();
    box.classList.add("dragging");
  }));
  ["dragleave", "drop"].forEach((eventName) => box.addEventListener(eventName, (event) => {
    event.preventDefault();
    box.classList.remove("dragging");
  }));
  box.addEventListener("drop", (event) => {
    input.files = event.dataTransfer.files;
    previewSelected(input.files[0]);
  });
  input.addEventListener("change", () => previewSelected(input.files[0]));

  $("#compareRange").addEventListener("input", (event) => {
    $("#afterPane").style.clipPath = `inset(0 ${100 - event.target.value}% 0 0)`;
  });
  $("#zoomRange").addEventListener("input", (event) => {
    $(".compare").style.transform = `scale(${event.target.value})`;
    $(".compare").style.transformOrigin = "center";
  });

  $("#enhanceBtn").addEventListener("click", () => runEnhance("/api/enhance"));
  $("#bgRemoveBtn").addEventListener("click", () => runEnhance("/api/remove-background", true));
}

function previewSelected(file) {
  if (!file) return;
  lastEnhanceFile = file;
  const url = URL.createObjectURL(file);
  $(".before-pane").style.backgroundImage = `url(${url})`;
  $(".before-pane").textContent = "";
  $("#uploadBox span").textContent = file.name;
}

async function runEnhance(endpoint, backgroundOnly = false) {
  if (!lastEnhanceFile) {
    $("#uploadBox span").textContent = "Choose an image first";
    return;
  }
  const button = backgroundOnly ? $("#bgRemoveBtn") : $("#enhanceBtn");
  const done = setBusy(button, backgroundOnly ? "Removing" : "Enhancing");
  const form = new FormData();
  form.append("image", lastEnhanceFile);
  form.append("target", selectedTarget);
  form.append("denoise", $("#denoise").checked);
  form.append("faces", $("#faces").checked);
  form.append("restore", $("#restore").checked);
  try {
    const response = await fetch(endpoint, { method: "POST", body: form });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Processing failed");
    $(".before-pane").style.backgroundImage = `url(${data.original})`;
    $("#afterPane").style.backgroundImage = `url(${data.url})`;
    $("#afterPane").textContent = "";
    $("#enhanceEngine").textContent = data.engine;
    $("#downloadEnhanced").href = data.url;
    $("#downloadEnhanced").classList.remove("disabled");
  } catch (error) {
    $("#enhanceEngine").textContent = error.message;
  } finally {
    done();
  }
}

function initAuth() {
  const form = $("#authForm");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    payload.mode = form.dataset.mode;
    const response = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    alert(data.message);
    if (data.ok) window.location.href = "/";
  });
}
