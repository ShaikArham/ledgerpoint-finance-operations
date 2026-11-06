/* Serve the CV as an attachment from the server, rather than relying on Safari's PDF viewer. */
const fs = require('node:fs');
const path = require('node:path');
const cvPath = path.join(process.cwd(), 'assets', 'Shaik_Arham_Saquib_DataPoint.pdf');
module.exports = (req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).end();
  }
  try {
    const file = fs.readFileSync(cvPath);
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', 'attachment; filename="Shaik_Arham_Saquib_DataPoint.pdf"; filename*=UTF-8\'\'Shaik_Arham_Saquib_DataPoint.pdf');
    res.setHeader('Content-Length', String(file.length));
    res.setHeader('Cache-Control', 'public, max-age=300');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    return res.status(200).end(req.method === 'HEAD' ? undefined : file);
  } catch (error) {
    console.error('CV download unavailable', error.code || 'unknown');
    return res.status(503).send('CV download temporarily unavailable');
  }
};
