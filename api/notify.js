/* Server-only Resend notification endpoint. Never expose RESEND_API_KEY to the browser. */
const EVENTS = {website_visit:'Website opened',video_play:'Introduction video played',cv_click:'CV link clicked'};
const clean = (v, max=120) => String(v || '').replace(/[<>\\r\\n]/g, ' ').slice(0,max);
module.exports = async (req, res) => {
  res.setHeader('Cache-Control','no-store');
  if (req.method !== 'POST') { res.setHeader('Allow','POST'); return res.status(405).json({ok:false}); }
  const origin = req.headers.origin || '';
  const host = req.headers.host || '';
  if (!origin || !host || (() => {try {return new URL(origin).host !== host;}catch{return true;}})()) return res.status(403).json({ok:false});
  const ua = String(req.headers['user-agent'] || '');
  if (/bot|crawler|spider|headless|preview|vercel-screenshot/i.test(ua)) return res.status(204).end();
  const body = typeof req.body === 'object' && req.body !== null ? req.body : {};
  const event = body.event;
  if (!Object.prototype.hasOwnProperty.call(EVENTS,event)) return res.status(400).json({ok:false});
  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(503).json({ok:false,reason:'Email provider not configured'});
  const title = EVENTS[event];
  const time = new Intl.DateTimeFormat('en-IE',{timeZone:'Europe/Dublin',dateStyle:'medium',timeStyle:'medium'}).format(new Date());
  const device = /Mobile|Android|iPhone/i.test(ua) ? 'Mobile' : 'Desktop / other';
  const browser = ua.includes('Edg/') ? 'Edge' : ua.includes('Chrome/') ? 'Chrome' : ua.includes('Firefox/') ? 'Firefox' : ua.includes('Safari/') ? 'Safari' : 'Unknown';
  const page = clean(body.page,100);
  const detail = clean(body.detail,100);
  const message = [title,'Time (Ireland): '+time,'Page: '+page,'Detail: '+(detail || 'Not applicable'),'Device: '+device,'Browser: '+browser,'Visitor identity: Not available','Note: Visits and clicks do not prove a human read the content.'].join('\\n');
  try {
    const r = await fetch('https://api.resend.com/emails',{
      method:'POST',
      headers:{Authorization:'Bearer '+key,'Content-Type':'application/json'},
      body:JSON.stringify({from:'LedgerPoint Alerts <onboarding@resend.dev>',to:['shaikarhamsaquib1181113@gmail.com'],subject:'LedgerPoint | '+title,text:message})
    });
    if (!r.ok) {console.error('Resend failed',r.status,(await r.text()).slice(0,300));return res.status(502).json({ok:false,reason:'Delivery provider rejected request'});}
    return res.status(200).json({ok:true});
  } catch(e) {console.error('Notification failed',String(e));return res.status(502).json({ok:false});}
};
