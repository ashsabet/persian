/* Lightweight exercise engine for the lesson player.
   Steps through exercises, plays audio, validates answers against the server.
   - "slow" (🐢) plays the SAME clip at reduced playbackRate (pitch preserved).
   - Wrong answers let the learner try again until correct (no advance, no reveal). */
(function () {
  "use strict";
  const cfg = window.LESSON;
  const data = JSON.parse(document.getElementById("exercises-data").textContent);

  const elExercise = document.getElementById("exercise");
  const elCheck = document.getElementById("check-btn");
  const elFeedback = document.getElementById("feedback");
  const elFeedbackMsg = document.getElementById("feedback-msg");
  const elContinue = document.getElementById("continue-btn");
  const elBar = document.getElementById("progress-bar");

  let idx = 0;
  let getAnswer = () => null;
  let resetAnswer = () => {};
  let answered = false;      // true only after a CORRECT answer
  let speakMode = false;

  function audioUrl(key) { return cfg.mediaBase + key + ".wav"; }
  function playAudio(key, slow) {
    if (!key) return;
    const a = new Audio(audioUrl(key));
    try { a.preservesPitch = true; a.mozPreservesPitch = true; a.webkitPreservesPitch = true; } catch (_) {}
    a.playbackRate = slow ? 0.6 : 1.0;   // slow = same clip, slower, natural pitch
    a.play().catch(() => {/* file missing or autoplay blocked — ignore */});
  }

  function audioButton(key, opts) {
    opts = opts || {};
    const wrap = document.createElement("div");
    wrap.className = "audio-row";
    const b = document.createElement("button");
    b.type = "button"; b.className = "audio-btn"; b.textContent = "🔊";
    b.onclick = () => playAudio(key, false);
    wrap.appendChild(b);
    if (opts.slow) {
      const s = document.createElement("button");
      s.type = "button"; s.className = "audio-btn small"; s.textContent = "🐢"; s.title = "Play slowly";
      s.onclick = () => playAudio(key, true);
      wrap.appendChild(s);
    }
    if (opts.autoplay) setTimeout(() => playAudio(key, false), 250);
    return wrap;
  }

  function setReady(ready) { elCheck.disabled = !ready; }
  function hideFeedback() { elFeedback.style.display = "none"; }
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function renderOptionGrid(ex, optionClassFa) {
    const grid = el("div", "options");
    let selected = null;
    ex.options.forEach((opt) => {
      const o = el("div", "option" + (optionClassFa ? " fa" : ""), opt.text);
      o.onclick = () => {
        if (answered || o.classList.contains("wrong")) return;   // wrong = disabled
        hideFeedback();
        grid.querySelectorAll(".option").forEach((n) => n.classList.remove("selected"));
        o.classList.add("selected");
        selected = opt.text;
        setReady(true);
      };
      grid.appendChild(o);
    });
    getAnswer = () => selected;
    resetAnswer = () => { selected = null; grid.querySelectorAll(".option.selected").forEach((n) => n.classList.remove("selected")); setReady(false); };
    return grid;
  }

  function render() {
    answered = false; speakMode = false;
    setReady(false); hideFeedback();
    elCheck.style.display = "block"; elCheck.textContent = "Check";
    elContinue.style.display = ""; elContinue.textContent = "Continue";
    resetAnswer = () => {};
    elExercise.innerHTML = "";
    const ex = data[idx];
    elBar.style.width = Math.round((idx / data.length) * 100) + "%";
    if (ex.instruction) elExercise.appendChild(el("div", "instruction", ex.instruction));

    if (ex.kind === "mc") {
      if (ex.image) { const img = el("img", "media-img"); img.src = "/static/" + ex.image; elExercise.appendChild(img); }
      if (ex.prompt_fa) elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (ex.audio) elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: !ex.image }));
      elExercise.appendChild(renderOptionGrid(ex, true));
    } else if (ex.kind === "listen") {
      elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: true }));
      elExercise.appendChild(renderOptionGrid(ex, true));
    } else if (ex.kind === "script") {
      if (ex.prompt_fa) elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (ex.audio) elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: true }));
      elExercise.appendChild(renderOptionGrid(ex, true));
    } else if (ex.kind === "translate") {
      const faFirst = ex.direction !== "en_fa";
      if (faFirst) {
        elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
        if (cfg.showTranslit && ex.translit) elExercise.appendChild(el("div", "translit center", ex.translit));
        if (ex.audio) elExercise.appendChild(audioButton(ex.audio, { slow: true }));
      } else {
        elExercise.appendChild(el("div", "prompt-en", ex.prompt_en));
      }
      const answerArea = el("div", "answer-area");
      const bank = el("div", "bank");
      (ex.tokens || []).forEach((tok) => {
        const t = el("div", "token" + (faFirst ? "" : " fa"), tok);
        t.onclick = () => {
          if (answered || t.classList.contains("used")) return;
          hideFeedback();
          t.classList.add("used");
          const placed = el("div", "token" + (faFirst ? "" : " fa"), tok);
          placed.onclick = () => { if (answered) return; placed.remove(); t.classList.remove("used"); sync(); };
          answerArea.appendChild(placed); sync();
        };
        bank.appendChild(t);
      });
      function sync() { setReady(answerArea.children.length > 0); }
      getAnswer = () => Array.from(answerArea.children).map((c) => c.textContent).join(" ");
      resetAnswer = () => {
        Array.from(answerArea.children).forEach((c) => c.remove());
        bank.querySelectorAll(".token.used").forEach((t) => t.classList.remove("used"));
        setReady(false);
      };
      elExercise.appendChild(answerArea); elExercise.appendChild(bank);
    } else if (ex.kind === "speak") {
      elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (cfg.showTranslit && ex.translit) elExercise.appendChild(el("div", "translit center", ex.translit));
      if (ex.english) elExercise.appendChild(el("div", "center muted", ex.english));
      elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: true }));
      const hint = el("div", "center muted"); hint.style.margin = "16px 0";
      hint.textContent = "🗣️ Listen, then say it aloud — then continue.";
      elExercise.appendChild(hint);
      speakMode = true; elCheck.textContent = "Continue"; setReady(true);
    }
  }

  function showCorrect() {
    answered = true;
    elCheck.style.display = "none";
    const sel = elExercise.querySelector(".option.selected");
    if (sel) sel.classList.add("correct");
    elFeedback.className = "feedback ok";
    elFeedbackMsg.textContent = "Correct!";
    elContinue.style.display = ""; elContinue.textContent = "Continue";
    elFeedback.style.display = "block";
  }

  function showWrong() {
    // mark the chosen option wrong + disabled, clear the answer, let them try again
    const sel = elExercise.querySelector(".option.selected");
    if (sel) { sel.classList.remove("selected"); sel.classList.add("wrong"); }
    resetAnswer();
    elFeedback.className = "feedback no";
    elFeedbackMsg.textContent = "Not quite — try again.";
    elContinue.style.display = "none";      // no Continue on a wrong answer
    elFeedback.style.display = "block";
    setReady(false);
  }

  function advance() {
    idx += 1;
    if (idx >= data.length) { elBar.style.width = "100%"; document.getElementById("finish-form").submit(); }
    else render();
  }

  elCheck.onclick = function () {
    if (speakMode) { advance(); return; }
    const ex = data[idx];
    const body = new URLSearchParams(); body.append("answer", getAnswer() == null ? "" : getAnswer());
    fetch(cfg.checkUrlTemplate.replace("__ID__", ex.id), {
      method: "POST",
      headers: { "X-CSRFToken": cfg.csrfToken, "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    }).then((r) => r.json()).then((d) => { if (d.correct) showCorrect(); else showWrong(); })
      .catch(() => showWrong());
  };
  elContinue.onclick = advance;   // only shown after a correct answer

  if (data.length === 0) {
    elExercise.appendChild(el("div", "center", "This lesson has no exercises yet."));
    elCheck.style.display = "none";
  } else { render(); }
})();
