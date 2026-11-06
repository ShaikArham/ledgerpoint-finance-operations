/* Minimal, first-party activity notifications. No cookies, fingerprinting, or IP collection. */
(() => {
  if (navigator.webdriver || /bot|crawler|spider|headless|preview/i.test(navigator.userAgent)) return;
  const sent = new Set();
  const notify = (event, detail) => {
    const key = event + ':' + (detail || '');
    if (sent.has(key)) return;
    sent.add(key);
    fetch('/api/notify', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event, detail: detail || '', page: location.pathname}),
      keepalive: true,
      credentials: 'same-origin'
    }).catch(() => {});
  };
  document.addEventListener('DOMContentLoaded', () => {
    notify('website_visit', '');
    const video = document.getElementById('intro-video');
    if (video) {
      video.addEventListener('playing', () => notify('video_play', 'Introduction film'));
    }
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href]');
      if (!a) return;
      const href = a.getAttribute('href') || '';
      if (/Shaik_Arham_Saquib_DataPoint\\.pdf/i.test(href)) {
        notify('cv_click', a.hasAttribute('download') ? 'Download CV' : 'View CV');
      }
    });
  });
})();
