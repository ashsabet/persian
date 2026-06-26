/* Lightweight exercise engine for the lesson player.
   Steps through exercises, plays audio, validates answers against the server. */
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
  let getAnswer = () => null;     // set by each renderer
  let answered = false;

  function audioUrl(key, slow) {
    return cfg.mediaBase + key + (slow ? "-slow" : "") + ".wav";
  }
  function playAudio(key, slow) {
    if (!key) return;
    const a = new Audio(audioUrl(key, slow));
    a.play().catch(() => {/* audio not generated yet — ignore */});
  }

  function audioButton(key, opts) {
    opts = opts || {};
    const wrap = document.createElement("div");
    wrap.className = "audio-row";
    const b = document.createElement("button");
    b.type = "button";
    b.className = "audio-btn";
    b.textContent = "🔊";
    b.onclick = () => playAudio(key, false);
    wrap.appendChild(b);
    if (opts.slow) {
      const s = document.createElement("button");
      s.type = "button";
      s.className = "audio-btn small";
      s.textContent = "🐢";
      s.onclick = () => playAudio(key, true);
      wrap.appendChild(s);
    }
    if (opts.autoplay) setTimeout(() => playAudio(key, false), 250);
    return wrap;
  }

  function setReady(ready) {
    elCheck.disabled = !ready;
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function renderOptionGrid(ex, optionClassFa) {
    const grid = el("div", "options");
    let selected = null;
    ex.options.forEach((opt, i) => {
      const o = el("div", "option" + (optionClassFa ? " fa" : ""), opt.text);
      o.onclick = () => {
        if (answered) return;
        grid.querySelectorAll(".option").forEach((n) => n.classList.remove("selected"));
        o.classList.add("selected");
        selected = i;
        setReady(true);
      };
      grid.appendChild(o);
    });
    getAnswer = () => selected;
    return grid;
  }

  function render() {
    answered = false;
    setReady(false);
    elFeedback.style.display = "none";
    elCheck.style.display = "block";
    elExercise.innerHTML = "";
    const ex = data[idx];
    elBar.style.width = Math.round((idx / data.length) * 100) + "%";

    if (ex.instruction) elExercise.appendChild(el("div", "instruction", ex.instruction));

    if (ex.kind === "mc") {
      if (ex.image) {
        const img = el("img", "media-img");
        img.src = ("/static/" + ex.image);
        elExercise.appendChild(img);
      }
      if (ex.prompt_fa) elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (ex.audio) elExercise.appendChild(audioButton(ex.audio, { autoplay: !ex.image }));
      elExercise.appendChild(renderOptionGrid(ex, true));

    } else if (ex.kind === "listen") {
      elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: true }));
      elExercise.appendChild(renderOptionGrid(ex, true));

    } else if (ex.kind === "script") {
      if (ex.prompt_fa) elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (ex.audio) elExercise.appendChild(audioButton(ex.audio, { autoplay: true }));
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
      const chosen = [];
      (ex.tokens || []).forEach((tok) => {
        const t = el("div", "token" + (faFirst ? "" : " fa"), tok);
        t.onclick = () => {
          if (answered) return;
          if (t.classList.contains("used")) return;
          t.classList.add("used");
          const placed = el("div", "token" + (faFirst ? "" : " fa"), tok);
          placed.onclick = () => {
            if (answered) return;
            placed.remove();
            t.classList.remove("used");
            sync();
          };
          answerArea.appendChild(placed);
          chosen.push(placed);
          sync();
        };
        bank.appendChild(t);
      });
      function sync() {
        const words = Array.from(answerArea.children).map((c) => c.textContent);
        setReady(words.length > 0);
      }
      getAnswer = () => Array.from(answerArea.children).map((c) => c.textContent).join(" ");
      elExercise.appendChild(answerArea);
      elExercise.appendChild(bank);

    } else if (ex.kind === "speak") {
      elExercise.appendChild(el("div", "prompt-fa fa", ex.prompt_fa));
      if (cfg.showTranslit && ex.translit) elExercise.appendChild(el("div", "translit center", ex.translit));
      if (ex.english) elExercise.appendChild(el("div", "center muted", ex.english));
      elExercise.appendChild(audioButton(ex.audio, { slow: true, autoplay: true }));
      const mic = el("div", "center");
      const b = el("button", "audio-btn", "🎙");
      b.type = "button";
      b.style.margin = "16px auto";
      b.onclick = () => setReady(true);
      mic.appendChild(b);
      mic.appendChild(el("div", "muted", "Tap the mic, say it aloud, then Check"));
      elExercise.appendChild(mic);
      getAnswer = () => "spoken";
    }
  }

  function showFeedback(correct, correctAnswer) {
    answered = true;
    elCheck.style.display = "none";
    elFeedback.className = "feedback " + (correct ? "ok" : "no");
    elFeedback.style.display = "block";
    elFeedbackMsg.textContent = correct
      ? "Correct!"
      : "Answer: " + (correctAnswer || "");
    // Mark options when present
    const opts = elExercise.querySelectorAll(".option");
    const ex = data[idx];
    if (opts.length && ex.options) {
      opts.forEach((node, i) => {
        if (ex.options[i] && ex.options[i].correct) node.classList.add("correct");
        if (node.classList.contains("selected") && !(ex.options[i] && ex.options[i].correct))
          node.classList.add("wrong");
      });
    }
  }

  elCheck.onclick = function () {
    const ex = data[idx];
    const answer = getAnswer();
    const url = cfg.checkUrlTemplate.replace("__ID__", ex.id);
    const body = new URLSearchParams();
    body.append("answer", answer == null ? "" : answer);
    fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": cfg.csrfToken, "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    })
      .then((r) => r.json())
      .then((d) => showFeedback(d.correct, d.correct_answer))
      .catch(() => showFeedback(false, ""));
  };

  elContinue.onclick = function () {
    idx += 1;
    if (idx >= data.length) {
      elBar.style.width = "100%";
      document.getElementById("finish-form").submit();
    } else {
      render();
    }
  };

  if (data.length === 0) {
    elExercise.appendChild(el("div", "center", "This lesson has no exercises yet."));
    elCheck.style.display = "none";
  } else {
    render();
  }
})();
