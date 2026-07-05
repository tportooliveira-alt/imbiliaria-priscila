require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

const PORT = process.env.PORT || 3001;

function _unauthorized(res) {
  res.status(401).json({ error: 'unauthorized' });
}

function checkAuth(req, res) {
  if (process.env.DEV_SKIP_AUTH === '1') return true;
  const token = req.header('X-CLIENT-TOKEN');
  if (!token || !process.env.CLIENT_TOKEN || token !== process.env.CLIENT_TOKEN) {
    _unauthorized(res);
    return false;
  }
  return true;
}

async function proxyStream(upstreamUrl, options, req, res) {
  try {
    const upstream = await fetch(upstreamUrl, options);
    res.status(upstream.status || 200);
    // forward safe headers
    upstream.headers.forEach((v, k) => {
      if (k.toLowerCase() === 'transfer-encoding') return;
      res.setHeader(k, v);
    });

    if (!upstream.body) {
      const txt = await upstream.text();
      return res.send(txt);
    }

    // upstream.body is a Node Readable stream in Node 18+
    upstream.body.pipe(res);
  } catch (err) {
    console.error('proxy error', err);
    if (!res.headersSent) res.status(502).json({ error: 'upstream_error', message: String(err) });
    else res.end();
  }
}

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

app.post('/mcp', async (req, res) => {
  if (!checkAuth(req, res)) return;
  const upstream = process.env.CODEX_API_URL;
  const key = process.env.CODEX_API_KEY;
  if (!upstream || !key) return res.status(500).json({ error: 'upstream_not_configured' });

  const init = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req.body),
  };
  await proxyStream(upstream, init, req, res);
});

app.get('/mcp', async (req, res) => {
  if (!checkAuth(req, res)) return;
  const upstream = process.env.CODEX_API_URL;
  const key = process.env.CODEX_API_KEY;
  if (!upstream || !key) return res.status(500).json({ error: 'upstream_not_configured' });

  const url = new URL(upstream);
  Object.keys(req.query || {}).forEach(k => url.searchParams.set(k, req.query[k]));

  const init = { method: 'GET', headers: { 'Authorization': `Bearer ${key}` } };
  await proxyStream(url.toString(), init, req, res);
});

app.listen(PORT, () => console.log(`MCP SSE proxy listening on ${PORT}`));

module.exports = app;
