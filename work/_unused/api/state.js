import { put, get } from '@vercel/blob';

// Musical English 학습 상태. 로그인 없이 private blob 한 개에 저장한다.
const PATH = 'musical/state.json';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.method === 'GET') {
      let r = null;
      try {
        r = await get(PATH, { access: 'private', useCache: false });
      } catch (e) {
        if (!/not.?found|404|BlobNotFound/i.test(String(e))) throw e;
      }
      if (!r || r.statusCode !== 200 || !r.stream) return res.status(200).json({ data: null, updated: null });
      const text = await new Response(r.stream).text();
      res.setHeader('Content-Type', 'application/json; charset=utf-8');
      return res.status(200).send(text);
    }
    if (req.method === 'PUT' || req.method === 'POST') {
      let body = req.body;
      if (typeof body === 'string') body = JSON.parse(body);
      if (!body || typeof body !== 'object') return res.status(400).json({ error: 'bad body' });
      const doc = { data: body, updated: new Date().toISOString() };
      await put(PATH, JSON.stringify(doc), {
        access: 'private', allowOverwrite: true, addRandomSuffix: false,
        contentType: 'application/json', cacheControlMaxAge: 60,
      });
      return res.status(200).json({ ok: true, updated: doc.updated });
    }
    res.setHeader('Allow', 'GET, PUT, POST');
    return res.status(405).end();
  } catch (e) {
    return res.status(500).json({ error: String(e && e.message || e) });
  }
}
