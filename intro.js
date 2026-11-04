(() => {
  "use strict";
  const gate = document.getElementById("film-gate"),
    enter = document.getElementById("intro-enter");
  if (!gate || !enter) return;
  const main = document.getElementById("main"),
    shell = document.getElementById("app-shell"),
    video = document.getElementById("intro-video"),
    play = document.getElementById("intro-play"),
    poster = document.getElementById("intro-poster"),
    status = document.getElementById("intro-status");
  if (!main || !shell || !video || !play || !poster || !status) return;
  let timer;
  let closing = false;
  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  video.defaultPlaybackRate = 1;
  video.playbackRate = 1;
  video.addEventListener("loadedmetadata", () => { video.playbackRate = 1; });
  function finishClose() {
    gate.hidden = true;
    gate.classList.remove("film-exiting");
    shell.classList.remove("app-revealing");
    shell.inert = false;
    document.body.classList.remove("intro-open");
    closing = false;
    try { sessionStorage.setItem("ledgerpoint-intro-seen", "1"); } catch {}
    main?.focus({ preventScroll: true });
  }
  function close() {
    clearTimeout(timer);
    video.pause();
    if (closing) return;
    closing = true;
    if (reducedMotion()) { finishClose(); return; }
    gate.classList.add("film-exiting");
    shell.classList.add("app-revealing");
    window.setTimeout(finishClose, 620);
  }
  enter.addEventListener("click", close);
  play.addEventListener("click", async () => {
    clearTimeout(timer);
    timer = setTimeout(() => { if (video.readyState < 2 && video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) fallback(); }, 15000);
    status.textContent = "Loading film…";
    play.hidden = true;
    video.hidden = false;
    poster.hidden = true;
    try {
      video.load();
      video.playbackRate = 1;
      await video.play();
      clearTimeout(timer);
      status.textContent =
        "Playing at normal speed. Use the player controls to pause, seek or enable captions.";
    } catch {
      if (video.error) {
        fallback();
      } else {
        status.textContent = "Press play in the video controls to begin.";
      }
    }
  });
  function fallback() {
    clearTimeout(timer);
    video.pause();
    video.hidden = true;
    poster.hidden = false;
    play.hidden = false;
    play.textContent = "Retry film";
    play.setAttribute("aria-label", "Retry film");
    status.textContent =
      "The film could not load. Retry or explore the reconciliation case below.";
  }
  video.addEventListener("error", fallback);
  video.addEventListener("loadeddata", () => { if (!video.paused) status.textContent = "Playing at normal speed (1×)."; });
  video.addEventListener("ratechange", () => { if (video.playbackRate !== 1) video.playbackRate = 1; });
  video.addEventListener("playing", () => { clearTimeout(timer); status.textContent = "Playing at normal speed (1×)."; });
  video.addEventListener("waiting", () => { status.textContent = "Buffering film…"; });
  video.addEventListener("stalled", () => { status.textContent = "Connection interrupted. The film will resume when enough data loads."; });
  video.addEventListener("ended", () => {
    status.textContent =
      "Film complete. Replay using the player controls or explore LedgerPoint.";
  });
  document.addEventListener(
    "keydown",
    (e) => {
      if (gate.hidden) return;
      if (e.key === "Escape") {
        e.preventDefault();
        close();
      }
      if (e.key === "Tab") {
        const nodes = [
          ...gate.querySelectorAll("button,video[controls],a[href]"),
        ].filter((n) => !n.hidden && n.getClientRects().length);
        const first = nodes[0],
          last = nodes.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    },
    true,
  );
  document.querySelectorAll("[data-replay-film]").forEach((button) =>
    button.addEventListener("click", () => {
      gate.classList.remove("film-exiting");
      shell.classList.remove("app-revealing");
      video.pause();
      video.currentTime = 0;
      video.playbackRate = 1;
      video.hidden = true;
      poster.hidden = false;
      gate.hidden = false;
      shell.inert = true;
      document.body.classList.add("intro-open");
      play.hidden = false;
      play.textContent = "▶ Play";
      play.setAttribute("aria-label", "Play LedgerPoint film");
      play.focus();
    }),
  );
  let seen = false;
  try {
    seen = sessionStorage.getItem("ledgerpoint-intro-seen") === "1";
  } catch {}
  if ((location.hash && location.hash !== "#intro") || seen) {
    gate.hidden = true;
  } else {
    gate.hidden = false;
    shell.inert = true;
    document.body.classList.add("intro-open");
    play.focus({ preventScroll: true });
  }
})();
