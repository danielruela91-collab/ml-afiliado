export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const firebaseUrl = process.env.FIREBASE_URL;
  if (!firebaseUrl) return res.status(503).json({ error: 'FIREBASE_URL not configured' });

  const url = `${firebaseUrl}/expenses.json`;

  if (req.method === 'GET') {
    const r = await fetch(url);
    const d = await r.json();
    return res.status(200).json(d || {});
  }

  if (req.method === 'POST') {
    const r = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const d = await r.json();
    return res.status(200).json(d);
  }

  res.status(405).end();
}
