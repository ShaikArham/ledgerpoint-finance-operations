/* Server-only Resend activity summary. No IP address or visitor fingerprint is collected. */
const clean = (value, max = 120) => String(value || '').replace(/[<>\r\n]/g, ' ').slice(0, max);
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ok:false}); }
  const origin = req.headers.origin || '';
  const host = req.headers.host || '';
  if (!origin || !host || (() => { try { return new URL(origin).host !== host; } catch { return true; } })()) return res.status(403).json({ok:false});
  const ua = String(req.headers['user-agent'] || '');
  if (/bot|crawler|spider|headless|preview|vercel-screenshot/i.test(ua)) return res.status(204).end();
  const body = typeof req.body === 'object' && req.body !== null ? req.body : {};
  if (body.event !== 'activity_summary' || !body.events || typeof body.events !== 'object') return res.status(400).json({ok:false});
  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(503).json({ok:false,reason:'Email provider not configured'});
  const flags = body.events;
  const yesNo = value => value === true ? 'Yes' : 'No';
  const time = new Intl.DateTimeFormat('en-IE', {timeZone:'Europe/Dublin',dateStyle:'medium',timeStyle:'medium'}).format(new Date());
  const device = /Mobile|Android|iPhone/i.test(ua) ? 'Mobile' : 'Desktop / other';
  const browser = ua.includes('Edg/') ? 'Edge' : ua.includes('Chrome/') ? 'Chrome' : ua.includes('Firefox/') ? 'Firefox' : ua.includes('Safari/') ? 'Safari' : 'Unknown';
  const geoPart = header => clean(req.headers[header] || '', 80);
  const locationParts = [geoPart('x-vercel-ip-city'), geoPart('x-vercel-ip-country-region'), geoPart('x-vercel-ip-country')].filter(Boolean);
  const approximateLocation = locationParts.length ? locationParts.join(', ') : 'Unavailable';
  const message = [
    'LedgerPoint activity summary', '',
    'Website opened: ' + yesNo(flags.website_visit),
    'Introduction video played: ' + yesNo(flags.video_play),
    'View CV clicked: ' + yesNo(flags.cv_view),
    'Download CV clicked: ' + yesNo(flags.cv_download), '',
    'Time (Ireland): ' + time,
    'Page: ' + clean(body.page, 100),
    'Approximate location (network-derived): ' + approximateLocation,
    'Device: ' + device,
    'Browser: ' + browser, '',
    'A click does not confirm the PDF was read or saved.',
    'Network-derived location is approximate, not a street address.',
    'Visitor identity is not available.'
  ].join('\n');
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method:'POST',
      headers:{Authorization:'Bearer ' + key,'Content-Type':'application/json'},
      body:JSON.stringify({
        from:'LedgerPoint Alerts <onboarding@resend.dev>',
        to:['shaikarhamsaquib1188113@gmail.com'],
        subject:'LedgerPoint | Activity summary',
        text:message
      })
    });
    if (!r.ok) { console.error('Resend failed',r.status,(await r.text()).slice(0,300)); return res.status(502).json({ok:false}); }
    return res.status(200).json({ok:true});
  } catch(e) { console.error('Notification failed',String(e)); return res.status(502).json({ok:false}); }
};