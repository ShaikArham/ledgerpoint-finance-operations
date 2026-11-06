/* One privacy-conscious activity summary per page session. No visitor identification. */
(() => {
  if (navigator.webdriver || /bot|crawler|spider|headless|preview/i.test(navigator.userAgent)) return;
  const events = { website_visit: true, video_play: false, cv_view: false, cv_download: false };
  let timer;
  let submitted = false;
  const flush = () => {
    if (submitted) return;
    submitted = true;
    fetch('/api/notify', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event: 'activity_summary', events, page: location.pathname}),
      keepalive: true,
      credentials: 'same-origin'
    }).then(r => {
      if (!r.ok) console.warn('LedgerPoint activity summary failed:', r.status);
    }).catch(e => console.warn('LedgerPoint activity summary network error:', e));
  };
  const schedule = () => {
    if (submitted) return;
    clearTimeout(timer);
    timer = setTimeout(flush, 90000);
  };
  const mark = (name) => {
    if (submitted) return;
    events[name] = true;
    schedule();
  };
  document.addEventListener('DOMContentLoaded', () => {
    schedule();
    const video = document.getElementById('intro-video');
    if (video) video.addEventListener('playing', () => mark('video_play'));
    document.addEventListener('click', e => {
      const a = e.target.closest('a[href]');
      if (!a) return;
      const href = (a.getAttribute('href') || '').toLowerCase();
      if (!href.includes('shaik_arham_saquib_datapoint.pdf')) return;
      mark(a.hasAttribute('download') ? 'cv_download' : 'cv_view');
    });
    window.addEventListener('pagehide', flush);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !submitted) schedule();
    });
  });
})();